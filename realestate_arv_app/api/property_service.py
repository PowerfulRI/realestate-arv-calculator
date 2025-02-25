"""
Property service for fetching and analyzing real estate data.
"""
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from ..models.property import Property

logger = logging.getLogger(__name__)

class PropertyService:
    """Service for retrieving property data from various sources."""
    
    def __init__(self, headless: bool = True, use_api: bool = True):
        """
        Initialize the property service.
        
        Args:
            headless: Whether to run the browser in headless mode
            use_api: Whether to use the paid API if available
        """
        self.headless = headless
        self.use_api = use_api
        # In a real implementation, we would initialize API clients and web scrapers here
        logger.info(f"Initialized PropertyService (headless={headless}, use_api={use_api})")
    
    def get_property_details(self, address: str) -> Optional[Property]:
        """
        Get property details from the API or web scraping.
        
        Args:
            address: Property address to look up
            
        Returns:
            Property object or None if not found
        """
        try:
            # This is a placeholder implementation
            # In a real implementation, we would first try the API if use_api is True
            # and fall back to web scraping if needed
            
            # Parse the address more intelligently
            # First, try to split by commas if they exist
            parts = address.split(",")
            
            if len(parts) >= 3:
                # This is likely a well-formatted address like "123 Main St, Anytown, CA 12345"
                street = parts[0].strip()
                city = parts[1].strip()
                state_zip = parts[2].strip().split()
                state = state_zip[0] if state_zip else "CA"
                zip_code = state_zip[1] if len(state_zip) > 1 else "12345"
            else:
                # Try to parse addresses like "101 heron rd east hartford connecticut" or "50 main street new york ny"
                words = address.lower().split()
                # Detect the state - in this case "connecticut" or "ny"
                known_states = {
                    "connecticut": "CT", "california": "CA", "texas": "TX", "florida": "FL", 
                    "new york": "NY", "massachusetts": "MA", "pennsylvania": "PA"
                }
                
                # State abbreviations
                state_abbrs = {
                    "al": "AL", "ak": "AK", "az": "AZ", "ar": "AR", "ca": "CA", "co": "CO", "ct": "CT", "de": "DE",
                    "fl": "FL", "ga": "GA", "hi": "HI", "id": "ID", "il": "IL", "in": "IN", "ia": "IA", "ks": "KS",
                    "ky": "KY", "la": "LA", "me": "ME", "md": "MD", "ma": "MA", "mi": "MI", "mn": "MN", "ms": "MS",
                    "mo": "MO", "mt": "MT", "ne": "NE", "nv": "NV", "nh": "NH", "nj": "NJ", "nm": "NM", "ny": "NY",
                    "nc": "NC", "nd": "ND", "oh": "OH", "ok": "OK", "or": "OR", "pa": "PA", "ri": "RI", "sc": "SC",
                    "sd": "SD", "tn": "TN", "tx": "TX", "ut": "UT", "vt": "VT", "va": "VA", "wa": "WA", "wv": "WV",
                    "wi": "WI", "wy": "WY"
                }
                
                state = "CA"  # Default
                city = "Anytown"  # Default
                zip_code = "12345"  # Default
                street = address  # Default to the full address
                state_found = False
                
                # First check for state abbreviations at the end
                if len(words) >= 2 and words[-1] in state_abbrs:
                    state = state_abbrs[words[-1]]
                    state_found = True
                    
                    # Handle "new york ny" case
                    if words[-1] == "ny" and len(words) >= 3 and words[-3] == "new" and words[-2] == "york":
                        city = "New York"
                        street = " ".join(words[:-3])
                    else:
                        # Assume the word before the state abbr is the city
                        city = words[-2]
                        if len(words) >= 3:
                            # Check if we need to combine two words for city (e.g., "east hartford")
                            if words[-3] in ["east", "west", "north", "south", "new"]:
                                city = f"{words[-3]} {city}"
                                street = " ".join(words[:-3])
                            else:
                                street = " ".join(words[:-2])
                        else:
                            street = " ".join(words[:-2])
                
                # If no state abbreviation found, try full state names
                if not state_found:
                    for i, word in enumerate(words):
                        # Check for full state name
                        if word in known_states:
                            state = known_states[word]
                            state_found = True
                            # Assume the city is 1-2 words before the state
                            if i > 0:
                                if i > 1 and words[i-2] in ["east", "west", "north", "south", "new"]:
                                    city = f"{words[i-2]} {words[i-1]}"
                                    street = " ".join(words[:i-2])
                                else:
                                    city = words[i-1]
                                    street = " ".join(words[:i-1])
                            break
                        
                        # Check for compound state names like "new york"
                        if i < len(words) - 1:
                            state_check = f"{word} {words[i+1]}"
                            if state_check in known_states:
                                state = known_states[state_check]
                                state_found = True
                                # Assume the city is 1-2 words before the compound state
                                if i > 0:
                                    city = words[i-1]
                                    if i > 1 and words[i-2] in ["east", "west", "north", "south", "new"]:
                                        city = f"{words[i-2]} {city}"
                                        street = " ".join(words[:i-2])
                                    else:
                                        street = " ".join(words[:i-1])
                                else:
                                    street = " ".join(words[:max(0, i-1)])
                                break
                
                # Capitalize the street and city properly
                street = " ".join(w.capitalize() for w in street.split())
                city = " ".join(w.capitalize() for w in city.split())
            
            # Create a sample property object
            property_obj = Property(
                property_id="sample-123",
                address=street,
                city=city,
                state=state,
                zip_code=zip_code,
                bedrooms=3,
                bathrooms=2.0,
                square_footage=1800,
                lot_size=0.25,
                year_built=1985,
                last_sale_date=datetime(2020, 6, 15),
                last_sale_price=350000,
                estimated_value=380000,
                latitude=37.7749,
                longitude=-122.4194
            )
            
            return property_obj
            
        except Exception as e:
            logger.error(f"Error getting property details: {str(e)}")
            return None
    
    def find_comparable_properties(self, property_obj: Property, radius_miles: float = 2.0, 
                                  months_back: int = 6, min_similar_properties: int = 3) -> List[Property]:
        """
        Find comparable properties for the given property.
        
        Args:
            property_obj: The target property
            radius_miles: Radius in miles to search for comps
            months_back: How many months back to look for sales
            min_similar_properties: Minimum number of comparable properties to find
            
        Returns:
            List of comparable Property objects
        """
        # This is a placeholder implementation
        # In a real implementation, we would search for actual comparable properties
        comps = []
        
        # Generate some sample comparable properties based on the input property
        for i in range(4):
            # Vary the square footage, price, etc.
            sqft_variance = 100 * (i - 1.5)  # -150, -50, 50, 150
            price_variance = 25000 * (i - 1.5)  # -37500, -12500, 12500, 37500
            
            # Sale date in the past few months
            sale_date = datetime.now() - timedelta(days=(30 * i))
            
            # Slightly different locations
            lat_variance = 0.001 * i
            lng_variance = 0.001 * i
            
            comp = Property(
                property_id=f"comp-{i+1}",
                address=f"{100 + i*10} {['Main St', 'Oak Ave', 'Elm St', 'Pine Rd'][i]}",
                city=property_obj.city,
                state=property_obj.state,
                zip_code=property_obj.zip_code,
                bedrooms=property_obj.bedrooms + (1 if i == 3 else 0) - (1 if i == 2 else 0),
                bathrooms=property_obj.bathrooms + (0.5 if i == 1 or i == 3 else 0),
                square_footage=int(property_obj.square_footage + sqft_variance),
                lot_size=property_obj.lot_size + (0.05 * (i - 1.5)),
                year_built=property_obj.year_built + (i - 1) * 3,
                last_sale_date=sale_date,
                last_sale_price=int(property_obj.estimated_value + price_variance),
                estimated_value=int(property_obj.estimated_value + price_variance + 5000),
                latitude=property_obj.latitude + lat_variance,
                longitude=property_obj.longitude + lng_variance
            )
            comps.append(comp)
        
        return comps
    
    def get_property_valuation(self, property_obj: Property) -> Optional[Dict[str, Any]]:
        """
        Get property valuation data from the API.
        
        Args:
            property_obj: The property to get valuation for
            
        Returns:
            Dictionary with valuation data or None if not available
        """
        # This is a placeholder implementation
        # In a real implementation, we would call a valuation API
        valuation_data = {
            "value": property_obj.estimated_value,
            "value_range_low": property_obj.estimated_value * 0.9,
            "value_range_high": property_obj.estimated_value * 1.1,
            "confidence": "medium",
            "valuation_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return valuation_data
    
    def close(self):
        """Close any open resources."""
        # In a real implementation, we would close web drivers, API clients, etc.
        logger.info("Closed PropertyService resources")