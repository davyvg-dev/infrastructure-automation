"""
AWS Inventory Generator

This module provides functionality to generate Ansible inventory from AWS EC2 instances.
"""

import boto3
import json
import logging
from typing import Dict, List, Optional
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from src.utils.exceptions import (
    CloudProviderError,
    InventoryError,
    AuthenticationError,
    ResourceNotFoundError
)
from src.utils.logging_config import get_logger, LoggingContextManager

logger = get_logger(__name__)

class AWSInventoryGenerator:
    """Generate Ansible inventory from AWS EC2 instances."""

    def __init__(self, region: str):
        """Initialize the AWS inventory generator.
        
        Args:
            region: AWS region name
            
        Raises:
            CloudProviderError: If region is invalid or AWS credentials are missing
        """
        try:
            self.region = region
            self.ec2_client = boto3.client('ec2', region_name=region)
            self.ec2_resource = boto3.resource('ec2', region_name=region)
            logger.info(f"Initialized AWS inventory generator for region: {region}")
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise AuthenticationError(
                "AWS credentials not found or incomplete. "
                "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
            ) from e
        except ClientError as e:
            raise CloudProviderError(f"Failed to initialize AWS client: {str(e)}") from e
        except Exception as e:
            raise CloudProviderError(f"Unexpected error initializing AWS client: {str(e)}") from e

    def get_instances(self, filters: Optional[List[Dict]] = None) -> List[Dict]:
        """Get EC2 instances matching the specified filters.
        
        Args:
            filters: List of filter dictionaries for EC2 instances
            
        Returns:
            List of instance information dictionaries
            
        Raises:
            CloudProviderError: If AWS API call fails
            ResourceNotFoundError: If no instances are found
        """
        with LoggingContextManager(logger, "fetching EC2 instances"):
            try:
                if filters is None:
                    filters = []
                
                response = self.ec2_client.describe_instances(Filters=filters)
                instances = []
                
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        if instance['State']['Name'] == 'running':
                            instance_info = {
                                'id': instance['InstanceId'],
                                'type': instance['InstanceType'],
                                'state': instance['State']['Name'],
                                'private_ip': instance.get('PrivateIpAddress'),
                                'public_ip': instance.get('PublicIpAddress'),
                                'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                            }
                            instances.append(instance_info)
                            logger.debug(f"Found instance: {instance_info['id']}")
                
                if not instances:
                    raise ResourceNotFoundError("No running EC2 instances found")
                
                logger.info(f"Found {len(instances)} running EC2 instances")
                return instances
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                logger.error(f"AWS API error: {error_code} - {error_message}")
                raise CloudProviderError(
                    f"Failed to get EC2 instances: {error_message}"
                ) from e
            except Exception as e:
                logger.error("Unexpected error getting EC2 instances", exc_info=True)
                raise CloudProviderError(
                    f"Unexpected error getting EC2 instances: {str(e)}"
                ) from e

    def generate_inventory(self, output_file: str) -> None:
        """Generate Ansible inventory file from EC2 instances.
        
        Args:
            output_file: Path to output inventory file
            
        Raises:
            InventoryError: If inventory generation fails
            CloudProviderError: If AWS API call fails
        """
        with LoggingContextManager(logger, "generating inventory"):
            try:
                instances = self.get_instances()
                
                inventory = {
                    'all': {
                        'hosts': {},
                        'children': {
                            'webservers': {
                                'hosts': {}
                            }
                        }
                    }
                }
                
                for instance in instances:
                    host_vars = {
                        'ansible_host': instance['public_ip'] or instance['private_ip'],
                        'ansible_user': 'ubuntu',  # Default user, can be overridden
                        'instance_id': instance['id'],
                        'instance_type': instance['type']
                    }
                    
                    # Add instance to all hosts
                    inventory['all']['hosts'][instance['id']] = host_vars
                    
                    # Add to webservers group if tagged appropriately
                    if instance['tags'].get('Role') == 'webserver':
                        inventory['all']['children']['webservers']['hosts'][instance['id']] = host_vars
                        logger.debug(f"Added instance {instance['id']} to webservers group")
                
                # Write inventory to file
                try:
                    with open(output_file, 'w') as f:
                        json.dump(inventory, f, indent=2)
                    logger.info(f"Inventory generated successfully: {output_file}")
                except (IOError, OSError) as e:
                    raise InventoryError(
                        f"Failed to write inventory file: {str(e)}"
                    ) from e
                
            except (CloudProviderError, ResourceNotFoundError) as e:
                raise InventoryError(f"Failed to generate inventory: {str(e)}") from e
            except Exception as e:
                logger.error("Unexpected error generating inventory", exc_info=True)
                raise InventoryError(
                    f"Unexpected error generating inventory: {str(e)}"
                ) from e

def generate_aws_inventory(region: str, output_file: str) -> None:
    """Generate AWS inventory file.
    
    Args:
        region: AWS region name
        output_file: Path to output inventory file
        
    Raises:
        CloudProviderError: If AWS client initialization fails
        InventoryError: If inventory generation fails
    """
    try:
        generator = AWSInventoryGenerator(region)
        generator.generate_inventory(output_file)
    except (CloudProviderError, InventoryError) as e:
        logger.error(f"Failed to generate AWS inventory: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error("Unexpected error in generate_aws_inventory", exc_info=True)
        raise InventoryError(f"Unexpected error: {str(e)}") from e 