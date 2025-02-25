"""
Zillow web scraper for fetching property data.
"""
import time
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import quote, urlencode

import os
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementNotInteractableException, StaleElementReferenceException
from bs4 import BeautifulSoup

from ..models.property import Property
from ..scripts.browser_setup import get_browser, safely_navigate
from ..config.settings import (
    SCRAPE_TIMEOUT, 
    SCRAPE_RETRY_COUNT, 
    DEFAULT_SEARCH_RADIUS_MILES, 
    DEFAULT_MONTHS_BACK, 
    MIN_COMPARABLE_PROPERTIES,
    MAX_COMPARABLE_PROPERTIES
)

logger = logging.getLogger(__name__)

class ZillowScraper:
    """Web scraper for Zillow website."""
    
    def __init__(self, headless: bool = True, browser_type: str = "chrome"):
        """Initialize the Zillow scraper."""
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.zillow.com"
        self.headless = headless
        self.browser_type = browser_type
        self.driver = None
        self.wait = None
        self.initialize_browser()
        
    def initialize_browser(self):
        """Initialize the web browser."""
        try:
            self.driver = get_browser(self.browser_type, self.headless)
            self.wait = WebDriverWait(self.driver, SCRAPE_TIMEOUT)
            self.logger.info(f"Browser initialized: {self.browser_type}")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
            self.logger.info("Browser closed")
            
    def __del__(self) -> None:
        """Ensure browser is closed when object is deleted."""
        self.close()
    
    def search_property(self, address: str) -> Optional[str]:
        """
        Search for a property on Zillow by address and return the detail page URL.
        
        Args:
            address: Full property address
            
        Returns:
            URL of the property detail page if found, None otherwise
        """
        if not self.driver:
            self.initialize_browser()
            
        # Use direct Zillow search URL format
        # First try using the direct search bar approach
        try:
            self.logger.info(f"Searching for property: {address}")
            
            # First navigate to Zillow homepage
            if not safely_navigate(self.driver, self.base_url, SCRAPE_RETRY_COUNT):
                self.logger.error(f"Failed to navigate to Zillow homepage")
                return None
                
            # Add human-like interaction
            self.driver.add_human_interaction(self.driver)
            
            # Let the page load fully and handle any popups
            time.sleep(random.uniform(3, 5))
            
            # Try to close any popups that might appear
            try:
                popup_selectors = [
                    "button[aria-label='Close']", 
                    ".modal-dialog .close",
                    "button.sign-in-sheet-close",
                    "button.gdpr-consent-close",
                    "button.cookie-consent-close",
                    "button[data-testid='dialog-close-button']"
                ]
                
                for selector in popup_selectors:
                    try:
                        close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for button in close_buttons:
                            if button.is_displayed():
                                button.click()
                                time.sleep(1)
                                break
                    except:
                        pass
            except:
                # Ignore errors in popup handling
                pass
                
            # Look for search input
            try:
                # Try different search input selectors
                search_input_selectors = [
                    "input[placeholder*='Enter an address']",
                    "input[placeholder*='Address']",
                    "input[data-testid='search-box-input']",
                    "input.react-autosuggest__input",
                    "input[type='search']",
                    "input[type='text']"
                ]
                
                search_input = None
                for selector in search_input_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                search_input = element
                                break
                        if search_input:
                            break
                    except:
                        continue
                
                if search_input:
                    # Clear any existing text
                    search_input.clear()
                    
                    # Type the address with realistic human typing pattern
                    for char in address:
                        search_input.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))  # Realistic typing delay
                    
                    # Let the auto-suggestion appear
                    time.sleep(random.uniform(2, 3))
                    
                    # Press Enter to search
                    search_input.send_keys(Keys.RETURN)
                    
                    # Wait for results or redirect
                    time.sleep(random.uniform(3, 5))
                    
                    # Add more human-like scrolling
                    self.driver.add_human_interaction(self.driver)
                    
                    # Check if we landed on a property detail page
                    current_url = self.driver.current_url
                    self.logger.info(f"Current URL after search: {current_url}")
                    
                    if "/homedetails/" in current_url:
                        self.logger.info(f"Direct match found: {current_url}")
                        return current_url
                else:
                    self.logger.warning("Could not find search input field")
            except Exception as e:
                self.logger.warning(f"Error using search input: {str(e)}")
            
            # If search input failed, try the direct URL approach as fallback
            self.logger.info("Trying direct URL approach")
            
            # Format address for URL
            formatted_address = address.replace(",", "").replace(" ", "-").lower()
            encoded_address = quote(address)
            
            # Try different URL patterns
            url_patterns = [
                f"{self.base_url}/homes/{encoded_address}_rb/",
                f"{self.base_url}/homes/for_sale/{formatted_address}",
                f"{self.base_url}/address/{formatted_address}",
                f"{self.base_url}/home/search/results?searchQueryState=%7B%22usersSearchTerm%22%3A%22{encoded_address}%22%7D"
            ]
            
            for url in url_patterns:
                try:
                    self.logger.info(f"Trying URL pattern: {url}")
                    if not safely_navigate(self.driver, url, SCRAPE_RETRY_COUNT):
                        continue
                    
                    # Add human-like interaction
                    self.driver.add_human_interaction(self.driver)
                    
                    # Check if we landed on a property detail page
                    current_url = self.driver.current_url
                    if "/homedetails/" in current_url:
                        self.logger.info(f"Direct match found: {current_url}")
                        return current_url
                        
                    # Wait for search results to load
                    time.sleep(random.uniform(3, 5))
                    
                    # Look for property cards in search results
                    self._find_property_in_search_results()
                except Exception as e:
                    self.logger.warning(f"Error with URL pattern {url}: {str(e)}")
            
            # If we reached here, we didn't find the property
            self.logger.warning(f"No property found for address: {address}")
            return None
                
        except Exception as e:
            self.logger.error(f"Error searching for property: {str(e)}")
            # Take a screenshot for debugging
            try:
                screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshots_dir, f"search_error_{int(time.time())}.png")
                self.driver.save_screenshot(screenshot_path)
                self.logger.info(f"Screenshot saved to {screenshot_path}")
            except:
                pass
            return None
            
    def _find_property_in_search_results(self) -> Optional[str]:
        """Helper method to find a property in search results."""
        try:
            # Try different result container selectors
            result_container_selectors = [
                "ul[data-testid='search-result-list-container']",
                "ul.photo-cards",
                "div.search-results-container",
                "div.search-results"
            ]
            
            # Add human-like scrolling
            self.driver.add_human_interaction(self.driver)
            
            for selector in result_container_selectors:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found results container with selector: {selector}")
                    break
                except:
                    continue
            
            # Try to find the first property card using different selectors
            card_selectors = [
                {"container": "article[data-test='property-card']", "link": "a[data-test='property-card-link']"},
                {"container": "div.list-card", "link": "a.list-card-link"},
                {"container": "li[data-test='search-result']", "link": "a"},
                {"container": "div.property-card", "link": "a"},
                {"container": "div.card", "link": "a"}
            ]
            
            for selector_pair in card_selectors:
                try:
                    property_cards = self.driver.find_elements(By.CSS_SELECTOR, selector_pair["container"])
                    if property_cards:
                        self.logger.info(f"Found {len(property_cards)} property cards with selector: {selector_pair['container']}")
                        for card in property_cards:
                            try:
                                # Add small delay between checking cards
                                time.sleep(random.uniform(0.2, 0.5))
                                
                                link = card.find_element(By.CSS_SELECTOR, selector_pair["link"])
                                href = link.get_attribute("href")
                                if href and "/homedetails/" in href:
                                    self.logger.info(f"Property found in search results: {href}")
                                    
                                    # Add human-like behavior - move mouse to the link and click
                                    try:
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        actions = ActionChains(self.driver)
                                        actions.move_to_element(link).pause(random.uniform(0.2, 0.8)).click().perform()
                                        time.sleep(random.uniform(3, 5))
                                        return self.driver.current_url
                                    except:
                                        # If the action chain fails, just return the href
                                        return href
                            except:
                                continue
                except:
                    continue
                
            # If we still haven't found a result, look for any link with homedetails
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and "/homedetails/" in href:
                        self.logger.info(f"Property found via generic link search: {href}")
                        return href
                except:
                    continue
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding property in search results: {str(e)}")
            return None
    
    def get_property_details(self, url: Optional[str] = None, address: Optional[str] = None) -> Optional[Property]:
        """
        Get property details from Zillow.
        
        Args:
            url: URL of the property detail page
            address: Property address (used if URL is not provided)
            
        Returns:
            Property object with details if found, None otherwise
        """
        if not self.driver:
            self.initialize_browser()
            
        if not url and address:
            url = self.search_property(address)
            
        if not url:
            return None
            
        try:
            self.logger.info(f"Getting property details from: {url}")
            
            # Navigate to property URL
            if not safely_navigate(self.driver, url, SCRAPE_RETRY_COUNT):
                self.logger.error(f"Failed to navigate to property URL: {url}")
                return None
                
            # Wait for the page to load
            try:
                # Modern Zillow UI
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-testid='ds-home-details-chip']"))
                )
            except TimeoutException:
                try:
                    # Legacy Zillow UI
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ds-address-container"))
                    )
                except TimeoutException:
                    try:
                        # Any heading as fallback
                        self.wait.until(
                            EC.presence_of_element_located((By.TAG_NAME, "h1"))
                        )
                    except TimeoutException:
                        self.logger.error("Timeout waiting for property page to load")
                        return None
            
            # Extract property data from the page
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract address components
            address_container = None
            
            # Try different selectors for address
            selectors = [
                "h1[data-testid='ds-home-details-chip']",
                "h1.ds-address-container",
                "h1[data-testid='property-title']",
                "h1"
            ]
            
            for selector in selectors:
                address_container = soup.select_one(selector)
                if address_container:
                    break
                    
            if not address_container:
                self.logger.error("Could not find address on the page")
                return None
                
            address_text = address_container.text.strip()
            address_parts = address_text.split(',')
            
            street_address = address_parts[0].strip()
            city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else ""
            
            # Extract city, state, zip
            city_state_zip_parts = city_state_zip.split()
            zip_code = city_state_zip_parts[-1] if city_state_zip_parts else ""
            state = city_state_zip_parts[-2] if len(city_state_zip_parts) > 1 else ""
            city = ' '.join(city_state_zip_parts[:-2]) if len(city_state_zip_parts) > 2 else ""
            
            # Generate a unique property ID
            property_id = f"zillow-{url.split('/')[-2]}"
            
            # Extract price - try different selectors
            price = None
            price_selectors = [
                "span[data-testid='price']",
                "span.ds-value",
                "div[data-testid='home-price']",
                ".ds-summary-row:contains('Price') span"
            ]
            
            for selector in price_selectors:
                try:
                    if selector.startswith(".ds-summary-row"):
                        # Handle special case for summary rows
                        price_rows = soup.select(".ds-summary-row")
                        for row in price_rows:
                            if "Price" in row.text:
                                price_elem = row.select_one("span")
                                if price_elem:
                                    price_text = price_elem.text
                                    price = self.extract_number(price_text)
                                    break
                    else:
                        # Standard selector
                        price_elem = soup.select_one(selector)
                        if price_elem:
                            price_text = price_elem.text
                            price = self.extract_number(price_text)
                            break
                except:
                    continue
            
            if not price:
                # Try to find any text that looks like a price
                price_pattern = re.compile(r'\$[\d,]+')
                price_matches = price_pattern.findall(html)
                if price_matches:
                    price_text = price_matches[0]
                    price = self.extract_number(price_text)
            
            # Extract basic facts (beds, baths, sqft)
            beds = 0
            baths = 0
            sqft = 0
            
            # Try different selectors for summary facts
            fact_containers = None
            fact_selectors = [
                "span[data-testid='bed-bath-beyond']",
                "ul.ds-home-fact-list span",
                "div.ds-bed-bath-living-area-container span"
            ]
            
            for selector in fact_selectors:
                fact_containers = soup.select(selector)
                if fact_containers:
                    break
            
            if fact_containers:
                for elem in fact_containers:
                    text = elem.text.lower()
                    if "bed" in text:
                        beds = self.extract_number(text)
                    elif "bath" in text:
                        baths = self.extract_number(text)
                    elif "sqft" in text or "sq ft" in text:
                        sqft = self.extract_number(text)
            
            # Extract year built
            year_built = 0
            year_built_found = False
            
            # Try different selectors for home facts
            fact_tables = None
            fact_table_selectors = [
                "div.ds-home-fact-list > div",
                "ul.ds-home-fact-list > li",
                "div[data-testid='facts-list'] div",
                "table.zsg-content-table tr"
            ]
            
            for selector in fact_table_selectors:
                fact_tables = soup.select(selector)
                if fact_tables:
                    for fact in fact_tables:
                        if "year built" in fact.text.lower():
                            year_built = self.extract_number(fact.text)
                            year_built_found = True
                            break
                if year_built_found:
                    break
            
            # Extract lot size (if available)
            lot_size = 0.0
            lot_size_found = False
            
            # Try different selectors for lot size
            lot_selectors = [
                "span[data-testid='lot-size']",
                "div:contains('Lot Size:') span",
                "li:contains('Lot:') span"
            ]
            
            for selector in lot_selectors:
                if selector.startswith("div:contains") or selector.startswith("li:contains"):
                    # Handle special case
                    for elem in fact_tables:
                        if "lot" in elem.text.lower() and "size" in elem.text.lower():
                            lot_size_text = elem.text
                            lot_size = self.extract_number(lot_size_text)
                            if "acre" in lot_size_text.lower():
                                lot_size_found = True
                                break
                else:
                    # Standard selector
                    lot_elem = soup.select_one(selector)
                    if lot_elem:
                        lot_size_text = lot_elem.text
                        lot_size = self.extract_number(lot_size_text)
                        if "acre" in lot_size_text.lower():
                            lot_size_found = True
                            break
            
            if not lot_size_found:
                # Convert sq ft to acres if necessary
                lot_size_sqft = 0
                for fact in fact_tables:
                    if "lot" in fact.text.lower() and "sq" in fact.text.lower():
                        lot_size_sqft = self.extract_number(fact.text)
                        break
                        
                if lot_size_sqft > 0:
                    # Convert sq ft to acres (43,560 sq ft = 1 acre)
                    lot_size = round(lot_size_sqft / 43560, 2)
            
            # Extract coordinates (if available)
            latitude = None
            longitude = None
            
            # Look for coordinates in the page source
            coord_pattern = re.compile(r'"latitude":\s*(-?\d+\.\d+).*?"longitude":\s*(-?\d+\.\d+)', re.DOTALL)
            coord_match = coord_pattern.search(html)
            if coord_match:
                latitude = float(coord_match.group(1))
                longitude = float(coord_match.group(2))
            
            # Extract last sale date (if available)
            last_sale_date = datetime.now()  # Default to current date
            
            # Look for sale history
            sale_date_pattern = re.compile(r'(sold|sold on|last sold).*?(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}/\d{1,2}/\d{2})', re.IGNORECASE)
            sale_date_match = sale_date_pattern.search(html)
            if sale_date_match:
                date_str = sale_date_match.group(2)
                try:
                    # Handle 2-digit and 4-digit year formats
                    if len(date_str.split('/')[-1]) == 2:
                        last_sale_date = datetime.strptime(date_str, '%m/%d/%y')
                    else:
                        last_sale_date = datetime.strptime(date_str, '%m/%d/%Y')
                except:
                    pass
            
            # Create and return Property object
            property_obj = Property(
                property_id=property_id,
                address=street_address,
                city=city,
                state=state,
                zip_code=zip_code,
                bedrooms=beds,
                bathrooms=baths,
                square_footage=int(sqft) if sqft else 0,
                lot_size=lot_size,
                year_built=int(year_built) if year_built else 0,
                last_sale_date=last_sale_date,
                last_sale_price=price,
                estimated_value=price,  # Using listing price as estimated value
                latitude=latitude,
                longitude=longitude
            )
            
            self.logger.info(f"Property details retrieved: {property_obj.address}, {property_obj.city}, {property_obj.state}")
            return property_obj
            
        except Exception as e:
            self.logger.error(f"Error getting property details: {str(e)}")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot(f"property_error_{int(time.time())}.png")
            except:
                pass
            return None
    
    def find_comparable_properties(self, 
                                 property_obj: Property, 
                                 radius_miles: float = DEFAULT_SEARCH_RADIUS_MILES, 
                                 months_back: int = DEFAULT_MONTHS_BACK, 
                                 min_similar_properties: int = MIN_COMPARABLE_PROPERTIES) -> List[Property]:
        """
        Find comparable properties on Zillow based on the given property.
        
        Args:
            property_obj: The target property to find comps for
            radius_miles: Search radius in miles
            months_back: Look for properties sold in the last X months
            min_similar_properties: Minimum number of comps to return
            
        Returns:
            List of comparable properties
        """
        if not self.driver:
            self.initialize_browser()
            
        zip_code = property_obj.zip_code
        beds = property_obj.bedrooms
        baths = property_obj.bathrooms
        
        self.logger.info(f"Finding comparable properties for: {property_obj.address}, {property_obj.city}, {property_obj.state}")
        
        # Adjust bedroom range for search
        min_beds = max(1, beds - 1)
        max_beds = beds + 1
        
        # Adjust bathroom range for search
        min_baths = max(1, int(baths - 1))
        max_baths = int(baths + 1)
        
        # Calculate square footage range (±20%)
        min_sqft = int(property_obj.square_footage * 0.8) if property_obj.square_footage else 0
        max_sqft = int(property_obj.square_footage * 1.2) if property_obj.square_footage else 0
        
        # Build the search URL for recently sold properties
        params = {
            "searchQueryState": json.dumps({
                "pagination": {},
                "usersSearchTerm": zip_code,
                "mapBounds": {
                    "west": -180,
                    "east": 180,
                    "south": -90,
                    "north": 90
                },
                "mapZoom": 12,
                "regionSelection": [{"regionId": 0, "regionType": 7}],
                "isMapVisible": True,
                "filterState": {
                    "sortSelection": {"value": "days"},
                    "isRecentlySold": {"value": True},
                    "isForSaleByAgent": {"value": False},
                    "isForSaleByOwner": {"value": False},
                    "isNewConstruction": {"value": False},
                    "isComingSoon": {"value": False},
                    "isAuction": {"value": False},
                    "isForSaleForeclosure": {"value": False},
                    "isPreMarketForeclosure": {"value": False},
                    "isPreMarketPreForeclosure": {"value": False},
                    "isMakeMeMove": {"value": False},
                    "beds": {"min": min_beds, "max": max_beds},
                    "baths": {"min": min_baths, "max": max_baths}
                },
                "isListVisible": True
            })
        }
        
        # Add square footage constraints if available
        if min_sqft > 0 and max_sqft > 0:
            params["searchQueryState"] = json.loads(params["searchQueryState"])
            params["searchQueryState"]["filterState"]["sqft"] = {"min": min_sqft, "max": max_sqft}
            params["searchQueryState"] = json.dumps(params["searchQueryState"])
        
        search_url = f"{self.base_url}/homes/recently-sold/{zip_code}/?" + urlencode(params)
        
        comparable_properties = []
        
        try:
            self.logger.info(f"Searching for comps with URL: {search_url}")
            
            # Navigate to search URL
            if not safely_navigate(self.driver, search_url, SCRAPE_RETRY_COUNT):
                self.logger.error(f"Failed to navigate to comps search URL")
                return []
                
            # Wait for search results
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul[data-testid='search-result-list-container']"))
                )
            except TimeoutException:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.photo-cards"))
                    )
                except TimeoutException:
                    self.logger.error("Timeout waiting for search results")
                    return []
            
            # Extract property cards
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try different selectors for property cards
            property_cards = None
            card_selectors = [
                "article[data-test='property-card']",
                "div.list-card",
                "li[data-test='search-result']",
                "div.property-card"
            ]
            
            for selector in card_selectors:
                property_cards = soup.select(selector)
                if property_cards:
                    break
            
            if not property_cards:
                self.logger.warning("No property cards found in search results")
                return []
                
            self.logger.info(f"Found {len(property_cards)} potential comps")
            
            # Limit to reasonable number to avoid excessive processing
            max_cards_to_process = min(len(property_cards), MAX_COMPARABLE_PROPERTIES)
            
            for i, card in enumerate(property_cards[:max_cards_to_process]):
                try:
                    # Extract property URL
                    property_url = None
                    
                    # Try different selectors for links
                    link_selectors = [
                        "a[data-test='property-card-link']",
                        "a.list-card-link",
                        "a[data-testid='property-card-link']",
                        "a"
                    ]
                    
                    for selector in link_selectors:
                        link_elem = card.select_one(selector)
                        if link_elem:
                            href = link_elem.get('href')
                            if href:
                                if not href.startswith('http'):
                                    href = f"{self.base_url}{href}"
                                property_url = href
                                break
                    
                    if not property_url or "/homedetails/" not in property_url:
                        continue
                    
                    self.logger.info(f"Processing comp {i+1}/{max_cards_to_process}: {property_url}")
                    
                    # Get detailed property information
                    comp_property = self.get_property_details(url=property_url)
                    if comp_property:
                        comparable_properties.append(comp_property)
                        self.logger.info(f"Added comp: {comp_property.address}")
                    
                    # Stop if we have enough comps
                    if len(comparable_properties) >= min_similar_properties:
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error processing comp property: {str(e)}")
                    continue
            
            self.logger.info(f"Found {len(comparable_properties)} comparable properties")
            return comparable_properties
            
        except Exception as e:
            self.logger.error(f"Error finding comparable properties: {str(e)}")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot(f"comps_error_{int(time.time())}.png")
            except:
                pass
            return []
    
    def extract_number(self, text: str) -> float:
        """Extract a numeric value from text."""
        if not text:
            return 0
            
        # Remove currency symbols and commas
        cleaned_text = text.replace('$', '').replace(',', '').replace('+', '')
        
        # Find all numbers in the text (including decimals)
        matches = re.findall(r'\d+\.?\d*', cleaned_text)
        if matches:
            return float(matches[0])
        return 0