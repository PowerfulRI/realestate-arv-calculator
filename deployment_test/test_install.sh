#!/bin/bash

# Test script for verifying the installation of the ARV Calculator

# Define color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print with colors
print_green() {
    echo -e "${GREEN}$1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}$1${NC}"
}

print_red() {
    echo -e "${RED}$1${NC}"
}

print_yellow "Creating test virtual environment..."
python3 -m venv test_venv
source test_venv/bin/activate

print_yellow "Installing wheel from local file..."
pip install realestate_arv_app-1.0.0-py3-none-any.whl

if [ $? -eq 0 ]; then
    print_green "✅ Installation successful!"
    
    # Set environment variables for testing
    export ANTHROPIC_API_KEY="test_key_for_claude"
    export ATTOM_API_KEY="test_key_for_attom"
    
    print_yellow "Testing ARV Calculator command..."
    arv-calculator --help
    
    if [ $? -eq 0 ]; then
        print_green "✅ Command test successful!"
        
        print_yellow "Running a simple sample test..."
        arv-calculator --sample --json | head -n 10
        
        if [ $? -eq 0 ]; then
            print_green "✅ Sample test successful!"
        else
            print_red "❌ Sample test failed!"
        fi
    else
        print_red "❌ Command test failed!"
    fi
else
    print_red "❌ Installation failed!"
fi

# Clean up
print_yellow "Cleaning up test environment..."
deactivate
rm -rf test_venv

print_green "Test completed!"