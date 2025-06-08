"""
Integration tests for the infrastructure automation tool.

This module contains tests that verify the tool's functionality in a real AWS environment.
"""

import os
import time
import pytest
import boto3
import subprocess
import json
from typing import Dict, List
from botocore.exceptions import ClientError
from python.src.utils.ssh_manager import SSHManager
from python.src.inventory.aws_inventory import AWSInventoryGenerator
from python.src.utils.exceptions import SSHManagerError, CloudProviderError

# Test configuration
TEST_KEY_NAME = "test-infra-key"
TEST_INSTANCE_TYPE = "t2.micro"
TEST_AMI = "ami-0c55b159cbfafe1f0"  # Ubuntu 20.04 LTS
TEST_REGION = "us-west-2"
TEST_INVENTORY_FILE = "test_inventory.json"

class TestEnvironment:
    """Manage test environment setup and cleanup."""
    
    def __init__(self):
        """Initialize test environment."""
        self.ec2 = boto3.resource('ec2', region_name=TEST_REGION)
        self.ssh_manager = SSHManager()
        self.instance_ids: List[str] = []
        self.key_pair_name = f"{TEST_KEY_NAME}-{int(time.time())}"
        
    def setup(self):
        """Set up test environment."""
        # Generate SSH key pair
        private_key_path, public_key_path = self.ssh_manager.generate_key_pair(
            self.key_pair_name
        )
        
        # Import key pair to AWS
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()
            
        try:
            self.ec2.import_key_pair(
                KeyName=self.key_pair_name,
                PublicKeyMaterial=public_key.encode()
            )
        except ClientError as e:
            raise CloudProviderError(f"Failed to import key pair: {str(e)}") from e
            
        # Launch test instance
        try:
            instance = self.ec2.create_instances(
                ImageId=TEST_AMI,
                InstanceType=TEST_INSTANCE_TYPE,
                MinCount=1,
                MaxCount=1,
                KeyName=self.key_pair_name,
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'test-infra-instance'},
                        {'Key': 'Role', 'Value': 'webserver'}
                    ]
                }]
            )[0]
            
            # Wait for instance to be running
            instance.wait_until_running()
            instance.reload()
            
            self.instance_ids.append(instance.id)
            
            # Wait for SSH to be available
            self._wait_for_ssh(instance.public_ip_address)
            
        except ClientError as e:
            raise CloudProviderError(f"Failed to launch instance: {str(e)}") from e
            
    def cleanup(self):
        """Clean up test environment."""
        # Terminate instances
        if self.instance_ids:
            try:
                self.ec2.instances.filter(
                    InstanceIds=self.instance_ids
                ).terminate()
                
                # Wait for instances to terminate
                for instance_id in self.instance_ids:
                    instance = self.ec2.Instance(instance_id)
                    instance.wait_until_terminated()
                    
            except ClientError as e:
                print(f"Warning: Failed to terminate instances: {str(e)}")
                
        # Delete key pair
        try:
            self.ec2.KeyPair(self.key_pair_name).delete()
        except ClientError as e:
            print(f"Warning: Failed to delete key pair: {str(e)}")
            
        # Delete local SSH keys
        try:
            os.remove(os.path.expanduser(f"~/.ssh/{self.key_pair_name}"))
            os.remove(os.path.expanduser(f"~/.ssh/{self.key_pair_name}.pub"))
        except OSError as e:
            print(f"Warning: Failed to delete local SSH keys: {str(e)}")
            
        # Delete inventory file
        try:
            os.remove(TEST_INVENTORY_FILE)
        except OSError:
            pass
            
    def _wait_for_ssh(self, host: str, max_retries: int = 30, delay: int = 10):
        """Wait for SSH to be available on the instance."""
        for i in range(max_retries):
            try:
                if self.ssh_manager.verify_connectivity(
                    host=host,
                    user='ubuntu',
                    key_name=self.key_pair_name
                ):
                    return
            except SSHManagerError:
                pass
            time.sleep(delay)
        raise TimeoutError(f"SSH not available after {max_retries * delay} seconds")

@pytest.fixture(scope="module")
def test_env():
    """Create and manage test environment."""
    env = TestEnvironment()
    env.setup()
    yield env
    env.cleanup()

def test_ssh_key_management(test_env):
    """Test SSH key management functionality."""
    # Verify key pair exists
    assert os.path.exists(os.path.expanduser(f"~/.ssh/{test_env.key_pair_name}"))
    assert os.path.exists(os.path.expanduser(f"~/.ssh/{test_env.key_pair_name}.pub"))
    
    # Verify public key content
    public_key = test_env.ssh_manager.get_public_key(test_env.key_pair_name)
    assert public_key.startswith("ssh-ed25519")
    
    # Verify SSH connectivity
    instance = test_env.ec2.Instance(test_env.instance_ids[0])
    assert test_env.ssh_manager.verify_connectivity(
        host=instance.public_ip_address,
        user='ubuntu',
        key_name=test_env.key_pair_name
    )

def test_inventory_generation(test_env):
    """Test inventory generation functionality."""
    # Generate inventory
    generator = AWSInventoryGenerator(TEST_REGION)
    generator.generate_inventory(TEST_INVENTORY_FILE)
    
    # Verify inventory file exists
    assert os.path.exists(TEST_INVENTORY_FILE)
    
    # Verify inventory content
    with open(TEST_INVENTORY_FILE, 'r') as f:
        inventory = json.load(f)
        
    assert 'all' in inventory
    assert 'hosts' in inventory['all']
    assert 'children' in inventory['all']
    assert 'webservers' in inventory['all']['children']
    
    # Verify instance is in inventory
    instance = test_env.ec2.Instance(test_env.instance_ids[0])
    assert instance.id in inventory['all']['hosts']
    assert instance.id in inventory['all']['children']['webservers']['hosts']

def test_nginx_deployment(test_env):
    """Test Nginx deployment functionality."""
    instance = test_env.ec2.Instance(test_env.instance_ids[0])
    
    # Run Nginx playbook
    result = subprocess.run([
        "ansible-playbook",
        "-i", TEST_INVENTORY_FILE,
        "python/src/playbooks/webserver.yml",
        "--private-key", os.path.expanduser(f"~/.ssh/{test_env.key_pair_name}"),
        "--user", "ubuntu"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Playbook failed: {result.stderr}"
    
    # Verify Nginx is running
    verify_cmd = [
        "ssh",
        "-i", os.path.expanduser(f"~/.ssh/{test_env.key_pair_name}"),
        "-o", "StrictHostKeyChecking=no",
        f"ubuntu@{instance.public_ip_address}",
        "systemctl is-active nginx"
    ]
    
    result = subprocess.run(verify_cmd, capture_output=True, text=True)
    assert result.returncode == 0, "Nginx is not running"
    assert result.stdout.strip() == "active" 