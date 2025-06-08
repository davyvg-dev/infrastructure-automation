"""
Custom exceptions for the infrastructure automation tool.
"""

class InfrastructureError(Exception):
    """Base exception for infrastructure automation errors."""
    pass

class InventoryError(InfrastructureError):
    """Exception raised for inventory-related errors."""
    pass

class CloudProviderError(InfrastructureError):
    """Exception raised for cloud provider-related errors."""
    pass

class SSHManagerError(InfrastructureError):
    """Exception raised for SSH management errors."""
    pass

class PlaybookError(InfrastructureError):
    """Exception raised for Ansible playbook errors."""
    pass

class ConfigurationError(InfrastructureError):
    """Exception raised for configuration-related errors."""
    pass

class ResourceNotFoundError(InfrastructureError):
    """Exception raised when a required resource is not found."""
    pass

class AuthenticationError(InfrastructureError):
    """Exception raised for authentication-related errors."""
    pass

class ValidationError(InfrastructureError):
    """Exception raised for validation-related errors."""
    pass 