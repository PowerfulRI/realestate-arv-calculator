# Deploying the Real Estate ARV Calculator

This guide provides instructions for deploying the Real Estate ARV Calculator application in different environments.

## Deployment Options

You can deploy the Real Estate ARV Calculator in three ways:

1. **Standard Installation**: Install directly on your system
2. **Docker Deployment**: Run in a Docker container
3. **Manual Installation**: Install from source

## 1. Standard Installation

The easiest way to deploy the application is using the included deployment script:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/yourusername/realestate-arv-calculator.git
cd realestate-arv-calculator

# Run the deployment script
./deploy.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Install the ARV Calculator application
- Create a configuration file for your API keys
- Add a convenient executable script

After installation, you can use the ARV Calculator with:

```bash
arv-calculator --address "123 Main St, Anytown, CA" --report
```

### Configuration

The configuration file is located at `~/.arv_calculator/config.env`. Open this file and add your API keys:

```bash
# Edit the configuration file
nano ~/.arv_calculator/config.env
```

## 2. Docker Deployment

To deploy using Docker:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/yourusername/realestate-arv-calculator.git
cd realestate-arv-calculator

# Create a config directory and environment file
mkdir -p config
cat > config/config.env << EOF
# Real Estate ARV Calculator Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ATTOM_API_KEY=your_attom_api_key_here
EOF

# Create a reports directory for output
mkdir -p reports

# Build and run with docker-compose
docker-compose up --build
```

### Custom Commands with Docker

To run a custom analysis:

```bash
docker-compose run --rm arv-calculator --address "50 Main Street, New York, NY" --report --output /reports/newyork_report.md
```

## 3. Manual Installation

For manual installation:

```bash
# Clone the repository
git clone https://github.com/yourusername/realestate-arv-calculator.git
cd realestate-arv-calculator

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install from the wheel file
pip install dist/realestate_arv_app-1.0.0-py3-none-any.whl

# Set up environment variables for API keys
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
export ATTOM_API_KEY="your_attom_api_key_here"

# Run the application
arv-calculator --address "123 Main St, Anytown, CA" --report
```

## Usage Examples

Once installed, you can use the ARV Calculator in various ways:

```bash
# Run with sample data
arv-calculator --sample

# Analyze a specific address
arv-calculator --address "123 Main St, Anytown, CA 12345"

# Generate a detailed markdown report
arv-calculator --address "50 Main St, New York, NY" --report --output report.md

# Output results in JSON format
arv-calculator --address "123 Main St, Anytown, CA" --json --output data.json

# Show all available options
arv-calculator --help
```

## Troubleshooting

If you encounter issues with the Chrome WebDriver, you might need to:

1. Ensure Chrome is installed on your system
2. Use the `--headless=false` option to see browser automation in action
3. Check that the Chrome WebDriver version matches your Chrome version

For API-related issues:
1. Verify your API keys are correctly set in the configuration file or environment variables
2. Use the `--no-api` flag to force web scraping instead of API usage
3. Check the debug logs with `--debug` option