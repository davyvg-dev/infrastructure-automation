#!/usr/bin/env python3
"""
Infrastructure Automation Tool - Main Entry Point

This module provides the command-line interface for the infrastructure automation tool,
handling inventory generation, server provisioning, and configuration management.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional
from python.src.inventory.aws_inventory import generate_aws_inventory
from python.src.utils.ssh_manager import setup_ssh_key
from python.src.utils.logging_config import setup_logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('infra_automation.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Configure and return the argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description='Infrastructure Automation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Inventory command
    inventory_parser = subparsers.add_parser('inventory', help='Generate inventory')
    inventory_parser.add_argument('--provider', required=True, choices=['aws', 'gcp', 'azure'],
                                help='Cloud provider')
    inventory_parser.add_argument('--region', required=True,
                                help='Region for inventory generation')
    inventory_parser.add_argument('--output', default='inventories/inventory.yml',
                                help='Output inventory file path')
    
    # Provision command
    provision_parser = subparsers.add_parser('provision', help='Provision servers')
    provision_parser.add_argument('--playbook', required=True,
                                help='Path to the Ansible playbook')
    provision_parser.add_argument('--inventory', required=True,
                                help='Path to the inventory file')
    provision_parser.add_argument('--extra-vars', nargs='+',
                                help='Extra variables for Ansible')
    
    # Configure command
    configure_parser = subparsers.add_parser('configure', help='Configure servers')
    configure_parser.add_argument('--playbook', required=True,
                                help='Path to the Ansible playbook')
    configure_parser.add_argument('--inventory', required=True,
                                help='Path to the inventory file')
    configure_parser.add_argument('--extra-vars', nargs='+',
                                help='Extra variables for Ansible')
    
    return parser

def validate_environment() -> None:
    """Validate the environment and required dependencies."""
    # Check Python version
    if sys.version_info < (3, 9):
        raise RuntimeError("Python 3.9 or higher is required")
    
    # Check required environment variables
    required_vars = {
        'AWS': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'],
        'GCP': ['GOOGLE_APPLICATION_CREDENTIALS'],
        'Azure': ['AZURE_SUBSCRIPTION_ID', 'AZURE_TENANT_ID', 
                 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET']
    }
    
    for provider, vars_list in required_vars.items():
        missing_vars = [var for var in vars_list if not os.getenv(var)]
        if missing_vars:
            logger.warning(f"Missing environment variables for {provider}: {', '.join(missing_vars)}")

def handle_inventory(args: argparse.Namespace) -> None:
    """Handle inventory generation command."""
    logger.info(f"Generating inventory for {args.provider} in {args.region}")
    # TODO: Implement inventory generation logic
    pass

def handle_provision(args: argparse.Namespace) -> None:
    """Handle server provisioning command."""
    logger.info(f"Provisioning servers using playbook: {args.playbook}")
    # TODO: Implement provisioning logic
    pass

def handle_configure(args: argparse.Namespace) -> None:
    """Handle server configuration command."""
    logger.info(f"Configuring servers using playbook: {args.playbook}")
    # TODO: Implement configuration logic
    pass

def main() -> Optional[int]:
    """Main entry point for the infrastructure automation tool."""
    try:
        parser = setup_argparse()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 1
        
        validate_environment()
        
        command_handlers = {
            'inventory': handle_inventory,
            'provision': handle_provision,
            'configure': handle_configure
        }
        
        handler = command_handlers.get(args.command)
        if handler:
            handler(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
        
        return 0
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 