#!/bin/bash

# Real Estate ARV Calculator Deployment Script
# This script deploys the ARV Calculator application

set -e  # Exit immediately if a command exits with a non-zero status

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

# Check for Python 3.8 or higher
print_yellow "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_red "Python 3.8 or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

print_green "Python $PYTHON_VERSION detected ✓"

# Create a virtual environment
print_yellow "Creating a virtual environment..."
VENV_DIR="arv_venv"

if [ -d "$VENV_DIR" ]; then
    print_yellow "Virtual environment already exists. Removing..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
print_green "Virtual environment created ✓"

# Activate the virtual environment
print_yellow "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
print_green "Virtual environment activated ✓"

# Upgrade pip
print_yellow "Upgrading pip..."
pip install --upgrade pip
print_green "Pip upgraded ✓"

# Install wheel
print_yellow "Installing wheel..."
pip install wheel
print_green "Wheel installed ✓"

# Install the package from the wheel
print_yellow "Installing Real Estate ARV Calculator..."
pip install dist/realestate_arv_app-1.0.0-py3-none-any.whl
print_green "Real Estate ARV Calculator installed ✓"

# Create a config file for API keys
print_yellow "Creating config file..."
CONFIG_DIR="$HOME/.arv_calculator"
mkdir -p "$CONFIG_DIR"

CONFIG_FILE="$CONFIG_DIR/config.env"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << EOF
# Real Estate ARV Calculator Configuration
# API keys and configuration settings

# Anthropic API for AI features
ANTHROPIC_API_KEY=

# ATTOM Data Solutions API for property data
ATTOM_API_KEY=

# Default settings
DEFAULT_SEARCH_RADIUS_MILES=2.0
DEFAULT_MONTHS_BACK=6
MIN_COMPARABLE_PROPERTIES=3
DEFAULT_CONTINGENCY_PERCENT=15
EOF
    
    print_green "Config file created at $CONFIG_FILE ✓"
    print_yellow "Please add your API keys to the config file."
else
    print_yellow "Config file already exists at $CONFIG_FILE."
fi

# Create an executable wrapper script
print_yellow "Creating executable wrapper script..."
WRAPPER_SCRIPT="/usr/local/bin/arv-calculator"

# Check if we have permission to write to /usr/local/bin
if [ -w "/usr/local/bin" ]; then
    cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Real Estate ARV Calculator Wrapper

# Load environment variables from config
if [ -f "$CONFIG_DIR/config.env" ]; then
    set -a
    source "$CONFIG_DIR/config.env"
    set +a
fi

# Activate the virtual environment and run the calculator
source "$(pwd)/$VENV_DIR/bin/activate"
arv-calculator "\$@"
EOF
    
    # Make the wrapper script executable
    chmod +x "$WRAPPER_SCRIPT"
    print_green "Wrapper script created at $WRAPPER_SCRIPT ✓"
else
    print_yellow "Cannot create wrapper script in /usr/local/bin (permission denied)."
    print_yellow "To run the calculator, activate the virtual environment and run 'arv-calculator':"
    print_yellow "source $VENV_DIR/bin/activate && arv-calculator"
fi

# Print final instructions
print_green "\n✅ Real Estate ARV Calculator has been successfully deployed!"
print_yellow "\nTo use the calculator, run:"
if [ -f "$WRAPPER_SCRIPT" ]; then
    print_green "arv-calculator --address \"123 Main St, Anytown, CA\" --report"
else
    print_green "source $VENV_DIR/bin/activate && arv-calculator --address \"123 Main St, Anytown, CA\" --report"
fi

print_yellow "\nAdditional options:"
print_green "  --sample             # Run with sample data"
print_green "  --json               # Output results in JSON format"
print_green "  --report             # Generate a detailed markdown report"
print_green "  --output FILE        # Save report to a file"
print_green "  --help               # Show all options\n"

# Deactivate the virtual environment
deactivate