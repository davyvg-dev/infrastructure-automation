@echo off
setlocal enabledelayedexpansion

:: Change to the project root directory
cd /d "%~dp0\.."

:: Check for required environment variables
if "%AWS_ACCESS_KEY_ID%"=="" (
    echo Error: AWS_ACCESS_KEY_ID not set
    echo Please set AWS_ACCESS_KEY_ID environment variable
    exit /b 1
)
if "%AWS_SECRET_ACCESS_KEY%"=="" (
    echo Error: AWS_SECRET_ACCESS_KEY not set
    echo Please set AWS_SECRET_ACCESS_KEY environment variable
    exit /b 1
)

:: Check for required tools
for %%c in (python pip pytest ansible-playbook) do (
    where %%c >nul 2>nul
    if errorlevel 1 (
        echo Error: %%c is required but not installed
        exit /b 1
    )
)

:: Create and activate virtual environment
echo Setting up virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pytest pytest-cov

:: Add the project root to PYTHONPATH
set "PYTHONPATH=%PYTHONPATH%;%CD%"

:: Run tests with coverage
echo Running integration tests...
pytest tests/test_integration.py -v --cov=src --cov-report=term-missing

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo Tests completed successfully! 