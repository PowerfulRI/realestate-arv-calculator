"""
Web scraper for fetching property data from real estate websites.
"""
import time
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from ..models.property import Property


class WebScraper:
    """Base web scraper for real estate websites."""
    
    def __init__(self, headless: bool = True):
        """Initialize the web scraper with browser settings."""
        self.logger = logging.getLogger(__name__)
        self.setup_browser(headless)
        
    def setup_browser(self, headless: bool) -> None:
        """Setup the browser for web scraping."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)
        
    def close(self) -> None:
        """Close the browser."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            
    def __del__(self) -> None:
        """Ensure browser is closed when object is deleted."""
        self.close()
        

class ZillowScraper(WebScraper):
    """Web scraper for Zillow website."""
    
    def __init__(self, headless: bool = True):
        """Initialize the Zillow scraper."""
        super().__init__(headless)
        self.base_url = "https://www.zillow.com"
    
    def search_property(self, address: str) -> Optional[str]:
        """
        Search for a property on Zillow by address and return the detail page URL.
        
        Args:
            address: Full property address
            
        Returns:
            URL of the property detail page if found, None otherwise
        """
        encoded_address = quote(address)
        search_url = f"{self.base_url}/homes/{encoded_address}_rb/"
        
        try:
            self.driver.get(search_url)
            time.sleep(3)  # Allow time for page to load and redirects to occur
            
            # Check if we landed on a property detail page
            if "/homedetails/" in self.driver.current_url:
                return self.driver.current_url
                
            # If we're on a search results page, try to find the first result
            try:
                property_card = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.property-card-link"))
                )
                return property_card.get_attribute("href")
            except (TimeoutException, NoSuchElementException):
                self.logger.warning(f"No property found for address: {address}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error searching for property: {str(e)}")
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
        if not url and address:
            url = self.search_property(address)
            
        if not url:
            return None
            
        try:
            self.driver.get(url)
            
            # Wait for the page to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ds-address-container"))
            )
            
            # Extract property data from the page
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract address components
            address_container = soup.select_one("h1.ds-address-container")
            if not address_container:
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
            
            # Extract price
            price_elem = soup.select_one("span[data-testid='price']")
            price_text = price_elem.text if price_elem else ""
            price = self.extract_number(price_text)
            
            # Extract basic facts (beds, baths, sqft)
            beds = 0
            baths = 0
            sqft = 0
            
            summary_elements = soup.select("span[data-testid='bed-bath-beyond']")
            for elem in summary_elements:
                text = elem.text.lower()
                if "bed" in text:
                    beds = self.extract_number(text)
                elif "bath" in text:
                    baths = self.extract_number(text)
                elif "sqft" in text:
                    sqft = self.extract_number(text)
            
            # Extract year built
            year_built = 0
            home_facts = soup.select("div.ds-home-fact-list > div")
            for fact in home_facts:
                if "year built" in fact.text.lower():
                    year_built = self.extract_number(fact.text)
                    break
            
            # Extract lot size (if available)
            lot_size = 0.0
            lot_elem = soup.select_one("span[data-testid='lot-size']")
            if lot_elem:
                lot_size_text = lot_elem.text
                lot_size_acres = self.extract_number(lot_size_text)
                if lot_size_acres:
                    lot_size = lot_size_acres
            
            # Create and return Property object
            return Property(
                property_id=property_id,
                address=street_address,
                city=city,
                state=state,
                zip_code=zip_code,
                bedrooms=beds,
                bathrooms=baths,
                square_footage=sqft,
                lot_size=lot_size,
                year_built=year_built,
                last_sale_price=price,
                last_sale_date=datetime.now(),  # Using current date as a placeholder
                estimated_value=price,  # Using listing price as estimated value
                latitude=None,  # Would need additional parsing to extract
                longitude=None  # Would need additional parsing to extract
            )
            
        except Exception as e:
            self.logger.error(f"Error getting property details: {str(e)}")
            return None
    
    def find_comparable_properties(self, 
                                 property_obj: Property, 
                                 radius_miles: float = 2.0, 
                                 months_back: int = 6, 
                                 min_similar_properties: int = 3) -> List[Property]:
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
        zip_code = property_obj.zip_code
        beds = property_obj.bedrooms
        baths = property_obj.bathrooms
        
        # Adjust bedroom range for search
        min_beds = max(1, beds - 1)
        max_beds = beds + 1
        
        # Adjust bathroom range for search
        min_baths = max(1, int(baths - 1))
        max_baths = int(baths + 1)
        
        # Calculate square footage range (±20%)
        min_sqft = int(property_obj.square_footage * 0.8)
        max_sqft = int(property_obj.square_footage * 1.2)
        
        # Build the search URL for recently sold properties
        search_url = (
            f"{self.base_url}/homes/recently-sold/{zip_code}/"
            f"{min_beds}-{max_beds}_beds/{min_baths}-{max_baths}_baths/"
            f"{min_sqft}-{max_sqft}_sqft/"
        )
        
        comparable_properties = []
        
        try:
            self.driver.get(search_url)
            
            # Wait for search results
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.photo-cards"))
            )
            
            # Extract property cards
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            property_cards = soup.select("div.list-card")
            
            for card in property_cards[:10]:  # Limit to first 10 results for efficiency
                try:
                    # Extract property URL
                    link_elem = card.select_one("a.list-card-link")
                    if not link_elem:
                        continue
                        
                    property_url = link_elem.get('href')
                    if not property_url.startswith('http'):
                        property_url = f"{self.base_url}{property_url}"
                    
                    # Get detailed property information
                    comp_property = self.get_property_details(url=property_url)
                    if comp_property:
                        comparable_properties.append(comp_property)
                    
                    # Stop if we have enough comps
                    if len(comparable_properties) >= min_similar_properties:
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error processing comp property: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error finding comparable properties: {str(e)}")
        
        return comparable_properties
    
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


class RealtyScrapingService:
    """Service for coordinating web scraping across multiple real estate sites."""
    
    def __init__(self, headless: bool = True):
        """Initialize the realty scraping service."""
        self.zillow_scraper = ZillowScraper(headless)
        
    def close(self):
        """Close all scrapers."""
        self.zillow_scraper.close()
        
    def get_property_details(self, address: str) -> Optional[Property]:
        """
        Get property details from available sources.
        
        Args:
            address: The full property address
            
        Returns:
            Property object with details if found, None otherwise
        """
        # Try Zillow first
        property_obj = self.zillow_scraper.get_property_details(address=address)
        
        # Could try other sources if Zillow fails
        
        return property_obj
        
    def find_comparable_properties(self, 
                                 property_obj: Property, 
                                 radius_miles: float = 2.0, 
                                 months_back: int = 6, 
                                 min_similar_properties: int = 3) -> List[Property]:
        """
        Find comparable properties from available sources.
        
        Args:
            property_obj: The target property to find comps for
            radius_miles: Search radius in miles
            months_back: Look for properties sold in the last X months
            min_similar_properties: Minimum number of comps to return
            
        Returns:
            List of comparable properties
        """
        # Try Zillow first
        comps = self.zillow_scraper.find_comparable_properties(
            property_obj, radius_miles, months_back, min_similar_properties
        )
        
        # Could try other sources if needed
        
        return comps