#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "requirements.txt not found in $SCRIPT_DIR"
    exit 1
fi

# Create venv directory name
VENV_DIR="$SCRIPT_DIR/venv"

# Check if venv already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    read -p "Do you want to remove it and create a new one? (y/n): " REMOVE_VENV
    if [ "$REMOVE_VENV" = "y" ]; then
        rm -rf "$VENV_DIR"
        echo "Removed existing virtual environment"
    else
        echo "Exiting script. Try running the application with the existing virtual environment."
        exit 0
    fi
fi

echo "Creating virtual environment in $VENV_DIR"
python3 -m venv "$VENV_DIR"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing packages from requirements.txt..."
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "Virtual environment setup complete!"
echo "Would you like to start the application now? (y/n)"
read -p "Start application? (y/n): " START_APP

if [ "$START_APP" = "y" ] || [ "$START_APP" = "Y" ]; then
    echo "Starting application..."
    ./run_sat_unix.sh
else
    echo "Application not started"
fi