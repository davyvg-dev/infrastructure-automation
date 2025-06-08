"""
Unit tests for AWS inventory generation.
"""

import json
import pytest
import boto3
from unittest.mock import Mock, patch
from python.src.inventory.aws_inventory import AWSInventoryGenerator
from python.src.utils.exceptions import CloudProviderError, ResourceNotFoundError

@pytest.fixture
def mock_ec2_client():
    """Mock EC2 client fixture."""
    with patch('boto3.client') as mock_client:
        yield mock_client

@pytest.fixture
def mock_ec2_resource():
    """Mock EC2 resource fixture."""
    with patch('boto3.resource') as mock_resource:
        yield mock_resource

@pytest.fixture
def sample_instances():
    """Sample EC2 instances data."""
    return {
        'Reservations': [
            {
                'Instances': [
                    {
                        'InstanceId': 'i-1234567890abcdef0',
                        'InstanceType': 't2.micro',
                        'State': {'Name': 'running'},
                        'PrivateIpAddress': '10.0.0.1',
                        'PublicIpAddress': '54.0.0.1',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'test-instance'},
                            {'Key': 'Role', 'Value': 'webserver'}
                        ]
                    },
                    {
                        'InstanceId': 'i-0987654321fedcba0',
                        'InstanceType': 't2.small',
                        'State': {'Name': 'running'},
                        'PrivateIpAddress': '10.0.0.2',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'test-instance-2'}
                        ]
                    }
                ]
            }
        ]
    }

def test_aws_inventory_generator_initialization():
    """Test AWSInventoryGenerator initialization."""
    generator = AWSInventoryGenerator('us-west-2')
    assert generator.region == 'us-west-2'

def test_get_instances(mock_ec2_client, sample_instances):
    """Test getting EC2 instances."""
    mock_ec2_client.return_value.describe_instances.return_value = sample_instances
    
    generator = AWSInventoryGenerator('us-west-2')
    instances = generator.get_instances()
    
    assert len(instances) == 2
    assert instances[0]['id'] == 'i-1234567890abcdef0'
    assert instances[0]['type'] == 't2.micro'
    assert instances[0]['private_ip'] == '10.0.0.1'
    assert instances[0]['public_ip'] == '54.0.0.1'
    assert instances[0]['tags']['Role'] == 'webserver'

def test_generate_inventory(mock_ec2_client, sample_instances, tmp_path):
    """Test inventory generation."""
    mock_ec2_client.return_value.describe_instances.return_value = sample_instances
    
    output_file = tmp_path / "inventory.json"
    generator = AWSInventoryGenerator('us-west-2')
    generator.generate_inventory(str(output_file))
    
    with open(output_file) as f:
        inventory = json.load(f)
    
    assert 'all' in inventory
    assert 'hosts' in inventory['all']
    assert 'children' in inventory['all']
    assert 'webservers' in inventory['all']['children']
    
    # Check webserver instance
    webserver = inventory['all']['children']['webservers']['hosts']['i-1234567890abcdef0']
    assert webserver['ansible_host'] == '54.0.0.1'
    assert webserver['instance_type'] == 't2.micro'
    
    # Check non-webserver instance
    other = inventory['all']['hosts']['i-0987654321fedcba0']
    assert other['ansible_host'] == '10.0.0.2'
    assert other['instance_type'] == 't2.small'

def test_get_instances_error(mock_ec2_client):
    """Test error handling in get_instances."""
    mock_ec2_client.return_value.describe_instances.side_effect = Exception("API Error")
    
    generator = AWSInventoryGenerator('us-west-2')
    with pytest.raises(Exception) as exc_info:
        generator.get_instances()
    
    assert str(exc_info.value) == "API Error"

def test_generate_inventory_error(mock_ec2_client, tmp_path):
    """Test error handling in generate_inventory."""
    mock_ec2_client.return_value.describe_instances.side_effect = Exception("API Error")
    
    output_file = tmp_path / "inventory.json"
    generator = AWSInventoryGenerator('us-west-2')
    
    with pytest.raises(Exception) as exc_info:
        generator.generate_inventory(str(output_file))
    
    assert str(exc_info.value) == "API Error" 