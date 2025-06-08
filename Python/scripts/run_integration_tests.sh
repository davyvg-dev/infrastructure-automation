#!/bin/bash

# Exit on error
set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check for required environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Error: AWS credentials not set"
    echo "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
    exit 1
fi

# Check for required tools
for cmd in python3 pip pytest ansible-playbook; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is required but not installed"
        exit 1
    fi
done

# Create and activate virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-cov

# Add the project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run tests with coverage
echo "Running integration tests..."
pytest tests/test_integration.py -v --cov=src --cov-report=term-missing

# Deactivate virtual environment
deactivate

echo "Tests completed successfully!" 