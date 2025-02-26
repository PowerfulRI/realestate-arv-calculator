# Real Estate ARV Calculator

A comprehensive tool for real estate investors, particularly those focusing on house flipping, to calculate accurate After Repair Value (ARV) and make informed investment decisions.

## Features

- **Property Data Collection**:
  - Web scraping from real estate websites (Zillow) with advanced anti-detection measures
  - Paid API integration with ATTOM Data Solutions for reliable property data
  - Comprehensive property details including current value, size, and features
  - Geospatial property analysis for location-based comparables

- **Comparable Property Analysis ("Comps")**:
  - Identify similar properties within 2 miles radius
  - Filter comps based on similarity in size, condition, and sale date (within 3-6 months)
  - Calculate accurate price per square foot from high-quality comps

- **AI-Powered Analysis**:
  - Claude AI integration for advanced property and market analysis
  - Renovation recommendations with ROI calculations
  - Investment risk assessment and opportunity identification
  - Market trend analysis for specific zip codes and property types

- **Renovation Cost Estimation**:
  - Calculate expected repair costs with itemized breakdown
  - Include contingency buffers (10-20%)
  - Track holding costs, permitting fees, and contractor markups

- **ARV Calculation**:
  - Implement multiple pricing methods including adjusted comparable sales
  - Provide confidence range approach (best-case, expected, worst-case ARV)
  - AI-enhanced value predictions

- **Investment Feasibility**:
  - Apply the 70% Rule to determine maximum purchase price
  - Generate risk assessment scores for potential investments
  - Calculate potential ROI and profit margins

## Installation

```bash
# Clone the repository
git clone https://github.com/PowerfulRI/realestate-arv-calculator.git
cd realestate-arv-calculator

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API keys for AI and property data services (optional)
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"  # For Claude AI features
export ATTOM_API_KEY="your_attom_api_key_here"  # For ATTOM Data Solutions API
```

## Usage

### Web Interface (Recommended for most users)

The easiest way to use the calculator is through the web interface:

```bash
# Using Docker (recommended)
docker-compose up

# Or run locally
export FLASK_APP=src.realestate_arv_app.ui.web_app
export FLASK_ENV=development
flask run
```

Then open your browser to http://localhost:5000 to access the web interface.

### Deploying to a Hosting Service

To deploy to a hosting service like Heroku:

1. Create an account on the hosting service
2. Connect your GitHub repository
3. Set the environment variables:
   - ANTHROPIC_API_KEY: Your Claude API key (optional)
   - ATTOM_API_KEY: Your ATTOM Data API key (optional)
4. Deploy the application
5. Open the provided URL to access the web interface

### Command Line Usage

Using the convenience script:
```bash
# Run with sample data for demonstration
./run-arv.sh --sample

# Analyze a specific property by address
./run-arv.sh --address "123 Main St, Anytown, CA 12345"

# Output results in JSON format
./run-arv.sh --sample --json

# Get help
./run-arv.sh --help
```

Or using Python directly:
```bash
# Run with sample data
python -m src.realestate_arv_app.main --sample

# With specific address and non-headless browser
python -m src.realestate_arv_app.main --address "123 Main St, Anytown, CA 12345" --headless=false

# Debug mode with verbose logging
python -m src.realestate_arv_app.main --sample --debug
```

## Docker Deployment

The easiest way to run the application is using Docker:

```bash
# Build and run with Docker Compose
docker-compose up

# Or build and run manually
docker build -t arv-calculator .
docker run -p 5000:5000 \
  -e ANTHROPIC_API_KEY=your_api_key \
  -e ATTOM_API_KEY=your_api_key \
  arv-calculator
```

Then access the web interface at http://localhost:5000

## Project Structure

```
src/realestate_arv_app/
├── __init__.py
├── api/
│   ├── zillow_scraper.py       # Enhanced web scraping for Zillow
│   ├── paid_api_client.py      # Integration with paid real estate APIs
│   ├── ai_analyzer.py          # AI analysis with Claude
│   └── property_service.py     # Combined data service layer
├── models/
│   └── property.py             # Property data models
├── analysis/
│   ├── comps_analyzer.py       # Comparable property analysis
│   └── renovation_calculator.py # Renovation cost estimation
├── ui/
│   ├── web_app.py              # Flask web application
│   └── templates/              # HTML templates
├── utils/
│   └── geospatial.py           # Geospatial calculation utilities
├── scripts/
│   └── browser_setup.py        # Advanced browser configuration for scraping
├── config/
│   └── settings.py             # Application settings and configuration
└── main.py                     # Main application entry point
```

## Required Tools & Dependencies

- Python 3.8+
- Selenium for web scraping
- Chrome WebDriver (automatically installed by webdriver-manager)
- Anthropic API key for Claude AI integration (optional)
- ATTOM Data Solutions API key for property data (optional)
- BeautifulSoup for HTML parsing
- Flask for web interface
- Pandas, NumPy for data analysis

## Dealing with Anti-Scraping Measures

This application includes advanced techniques to overcome anti-scraping measures:

- Randomized user agents and browser fingerprints
- Delayed and randomized interactions to mimic human behavior
- JavaScript overrides to prevent automation detection
- Robust error handling and retry mechanisms

## Paid API Integration

For more reliable data access, the application supports the ATTOM Data Solutions API:
- Set up an account at [ATTOM Data Solutions](https://www.attomdata.com/)
- Obtain an API key and set the ATTOM_API_KEY environment variable
- The application will automatically use the API when available or fall back to web scraping

## License

MIT

## Contributors

- Your Name (@PowerfulRI)