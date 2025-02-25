"""
Settings configuration for the RealEstate ARV Calculator application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent.parent.parent, '.env'))

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Web scraping settings
HEADLESS_BROWSER = True
BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
SCRAPE_TIMEOUT = 30  # Timeout in seconds
SCRAPE_RETRY_COUNT = 3  # Number of retries for web scraping

# Property analysis settings
DEFAULT_SEARCH_RADIUS_MILES = 2.0
DEFAULT_MONTHS_BACK = 6
MIN_COMPARABLE_PROPERTIES = 3
MAX_COMPARABLE_PROPERTIES = 10

# Renovation calculation settings
DEFAULT_CONTINGENCY_PERCENT = 15.0
RULE_70_PERCENT = 70.0

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Output settings
DEFAULT_OUTPUT_FORMAT = "text"  # Can be "text" or "json"

# Property types
PROPERTY_TYPES = [
    "single-family",
    "condo",
    "townhouse",
    "multi-family",
    "land",
    "other"
]

# Default renovation items and costs
DEFAULT_RENOVATION_COSTS = {
    "kitchen": {
        "basic": 15000,
        "mid-range": 30000,
        "high-end": 50000
    },
    "bathroom": {
        "basic": 7500,
        "mid-range": 15000,
        "high-end": 25000
    },
    "flooring": {
        "carpet": 4.5,  # per sq ft
        "laminate": 7,  # per sq ft
        "hardwood": 12,  # per sq ft
        "tile": 10  # per sq ft
    },
    "paint": {
        "interior": 3,  # per sq ft
        "exterior": 4  # per sq ft
    },
    "roof": {
        "asphalt": 4.5,  # per sq ft
        "metal": 10,  # per sq ft
        "tile": 15  # per sq ft
    },
    "windows": {
        "standard": 500,  # per window
        "energy-efficient": 750  # per window
    },
    "hvac": {
        "repair": 2500,
        "replace": 7500
    },
    "electrical": {
        "update": 5000,
        "rewire": 15000
    },
    "plumbing": {
        "update": 5000,
        "replace": 15000
    }
}