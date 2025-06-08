"""
Unit tests for SSH key management.
"""

import os
import pytest
from unittest.mock import patch, mock_open, Mock
from python.src.utils.ssh_manager import SSHManager
from python.src.utils.exceptions import SSHManagerError, ResourceNotFoundError

@pytest.fixture
def ssh_manager(tmp_path):
    """Create SSHManager instance with temporary directory."""
    return SSHManager(str(tmp_path))

@pytest.fixture
def mock_subprocess():
    """Mock subprocess module."""
    with patch('subprocess.run') as mock_run:
        yield mock_run

def test_ssh_manager_initialization(tmp_path):
    """Test SSHManager initialization."""
    manager = SSHManager(str(tmp_path))
    assert os.path.exists(tmp_path)
    assert oct(os.stat(tmp_path).st_mode)[-3:] == '700'

def test_generate_key_pair(ssh_manager, mock_subprocess):
    """Test SSH key pair generation."""
    mock_subprocess.return_value.returncode = 0
    
    private_key, public_key = ssh_manager.generate_key_pair('test_key')
    
    assert os.path.basename(private_key) == 'test_key'
    assert os.path.basename(public_key) == 'test_key.pub'
    mock_subprocess.assert_called_once()

def test_generate_key_pair_existing(ssh_manager, tmp_path):
    """Test generating key pair when it already exists."""
    key_path = os.path.join(tmp_path, 'test_key')
    with open(key_path, 'w') as f:
        f.write('existing key')
    
    private_key, public_key = ssh_manager.generate_key_pair('test_key')
    
    assert private_key == key_path
    assert public_key == f"{key_path}.pub"

def test_generate_key_pair_error(ssh_manager, mock_subprocess):
    """Test error handling in key pair generation."""
    mock_subprocess.side_effect = Exception("SSH keygen failed")
    
    with pytest.raises(Exception) as exc_info:
        ssh_manager.generate_key_pair('test_key')
    
    assert str(exc_info.value) == "SSH keygen failed"

def test_get_public_key(ssh_manager):
    """Test getting public key content."""
    key_content = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... test@example.com"
    
    with patch('builtins.open', mock_open(read_data=key_content)):
        content = ssh_manager.get_public_key('test_key')
    
    assert content == key_content

def test_get_public_key_not_found(ssh_manager):
    """Test getting non-existent public key."""
    with pytest.raises(FileNotFoundError):
        ssh_manager.get_public_key('nonexistent_key')

def test_verify_connectivity_success(ssh_manager, mock_subprocess):
    """Test successful SSH connectivity verification."""
    mock_subprocess.return_value.returncode = 0
    
    result = ssh_manager.verify_connectivity('test-host', 'test-user', 'test-key')
    
    assert result is True
    mock_subprocess.assert_called_once()

def test_verify_connectivity_failure(ssh_manager, mock_subprocess):
    """Test failed SSH connectivity verification."""
    mock_subprocess.return_value.returncode = 1
    mock_subprocess.return_value.stderr = "Connection refused"
    
    result = ssh_manager.verify_connectivity('test-host', 'test-user', 'test-key')
    
    assert result is False

def test_verify_connectivity_timeout(ssh_manager, mock_subprocess):
    """Test SSH connectivity verification timeout."""
    mock_subprocess.side_effect = TimeoutError("Connection timed out")
    
    result = ssh_manager.verify_connectivity('test-host', 'test-user', 'test-key')
    
    assert result is False

def test_add_to_known_hosts(ssh_manager, mock_subprocess):
    """Test adding host to known_hosts."""
    mock_subprocess.return_value.stdout = "test-host ssh-rsa AAAAB3NzaC1yc2E..."
    
    ssh_manager.add_to_known_hosts('test-host')
    
    mock_subprocess.assert_called_once()
    assert os.path.exists(os.path.join(ssh_manager.key_dir, 'known_hosts'))

def test_add_to_known_hosts_error(ssh_manager, mock_subprocess):
    """Test error handling in adding host to known_hosts."""
    mock_subprocess.side_effect = Exception("ssh-keyscan failed")
    
    with pytest.raises(Exception) as exc_info:
        ssh_manager.add_to_known_hosts('test-host')
    
    assert str(exc_info.value) == "ssh-keyscan failed" 