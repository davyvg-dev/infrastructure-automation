"""
SSH Key Management Utility

This module provides functionality for managing SSH keys and verifying SSH connectivity.
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from src.utils.exceptions import SSHManagerError, ResourceNotFoundError
from src.utils.logging_config import get_logger, LoggingContextManager, log_sensitive_data

logger = get_logger(__name__)

class SSHManager:
    """Manage SSH keys and verify SSH connectivity."""

    def __init__(self, key_dir: str = "~/.ssh"):
        """Initialize SSH manager.
        
        Args:
            key_dir: Directory containing SSH keys
            
        Raises:
            SSHManagerError: If key directory creation fails
        """
        try:
            self.key_dir = os.path.expanduser(key_dir)
            os.makedirs(self.key_dir, mode=0o700, exist_ok=True)
            logger.info(f"Initialized SSH manager with key directory: {self.key_dir}")
        except OSError as e:
            raise SSHManagerError(
                f"Failed to create SSH key directory: {str(e)}"
            ) from e

    def generate_key_pair(self, key_name: str, passphrase: Optional[str] = None) -> Tuple[str, str]:
        """Generate a new SSH key pair.
        
        Args:
            key_name: Name of the key pair
            passphrase: Optional passphrase for the private key
            
        Returns:
            Tuple of (private_key_path, public_key_path)
            
        Raises:
            SSHManagerError: If key generation fails
        """
        with LoggingContextManager(logger, f"generating SSH key pair: {key_name}"):
            private_key_path = os.path.join(self.key_dir, key_name)
            public_key_path = f"{private_key_path}.pub"
            
            if os.path.exists(private_key_path):
                logger.warning(f"SSH key {private_key_path} already exists")
                return private_key_path, public_key_path
            
            try:
                cmd = ["ssh-keygen", "-t", "ed25519", "-f", private_key_path, "-N", passphrase or ""]
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Set correct permissions
                os.chmod(private_key_path, 0o600)
                os.chmod(public_key_path, 0o644)
                
                logger.info(f"Generated SSH key pair: {private_key_path}")
                return private_key_path, public_key_path
                
            except subprocess.CalledProcessError as e:
                logger.error(f"SSH keygen failed: {e.stderr}")
                raise SSHManagerError(
                    f"Failed to generate SSH key pair: {e.stderr}"
                ) from e
            except OSError as e:
                logger.error(f"Failed to set key permissions: {str(e)}")
                raise SSHManagerError(
                    f"Failed to set key permissions: {str(e)}"
                ) from e

    def get_public_key(self, key_name: str) -> str:
        """Get the public key content.
        
        Args:
            key_name: Name of the key pair
            
        Returns:
            Public key content
            
        Raises:
            ResourceNotFoundError: If public key file doesn't exist
            SSHManagerError: If reading the key fails
        """
        public_key_path = os.path.join(self.key_dir, f"{key_name}.pub")
        
        try:
            with open(public_key_path, 'r') as f:
                content = f.read().strip()
            logger.debug(f"Read public key from: {public_key_path}")
            return content
        except FileNotFoundError:
            raise ResourceNotFoundError(
                f"Public key not found: {public_key_path}"
            )
        except IOError as e:
            raise SSHManagerError(
                f"Failed to read public key: {str(e)}"
            ) from e

    def verify_connectivity(self, host: str, user: str, key_name: str, port: int = 22) -> bool:
        """Verify SSH connectivity to a host.
        
        Args:
            host: Target host
            user: SSH user
            key_name: Name of the private key
            port: SSH port
            
        Returns:
            True if connection is successful, False otherwise
            
        Raises:
            SSHManagerError: If verification fails
        """
        with LoggingContextManager(logger, f"verifying SSH connectivity to {host}"):
            private_key_path = os.path.join(self.key_dir, key_name)
            
            if not os.path.exists(private_key_path):
                raise ResourceNotFoundError(
                    f"Private key not found: {private_key_path}"
                )
            
            cmd = [
                "ssh",
                "-i", private_key_path,
                "-p", str(port),
                "-o", "StrictHostKeyChecking=no",
                "-o", "BatchMode=yes",
                f"{user}@{host}",
                "echo 'SSH connection successful'"
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    logger.info(f"Successfully connected to {host}")
                    return True
                else:
                    logger.error(f"Failed to connect to {host}: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Connection to {host} timed out")
                return False
            except subprocess.CalledProcessError as e:
                logger.error(f"SSH command failed: {e.stderr}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error connecting to {host}", exc_info=True)
                raise SSHManagerError(
                    f"Unexpected error connecting to {host}: {str(e)}"
                ) from e

    def add_to_known_hosts(self, host: str, port: int = 22) -> None:
        """Add a host to known_hosts file.
        
        Args:
            host: Target host
            port: SSH port
            
        Raises:
            SSHManagerError: If adding to known_hosts fails
        """
        with LoggingContextManager(logger, f"adding {host} to known_hosts"):
            known_hosts_path = os.path.join(self.key_dir, "known_hosts")
            
            try:
                os.makedirs(os.path.dirname(known_hosts_path), mode=0o700, exist_ok=True)
                
                cmd = ["ssh-keyscan", "-p", str(port), host]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                with open(known_hosts_path, 'a') as f:
                    f.write(result.stdout)
                
                logger.info(f"Added {host} to known_hosts")
                
            except subprocess.CalledProcessError as e:
                raise SSHManagerError(
                    f"Failed to get host key: {e.stderr}"
                ) from e
            except OSError as e:
                raise SSHManagerError(
                    f"Failed to write to known_hosts: {str(e)}"
                ) from e

def setup_ssh_key(key_name: str, passphrase: Optional[str] = None) -> Tuple[str, str]:
    """Set up SSH key pair.
    
    Args:
        key_name: Name of the key pair
        passphrase: Optional passphrase for the private key
        
    Returns:
        Tuple of (private_key_path, public_key_path)
        
    Raises:
        SSHManagerError: If key setup fails
    """
    try:
        manager = SSHManager()
        return manager.generate_key_pair(key_name, passphrase)
    except Exception as e:
        logger.error("Failed to set up SSH key", exc_info=True)
        raise SSHManagerError(f"Failed to set up SSH key: {str(e)}") from e 