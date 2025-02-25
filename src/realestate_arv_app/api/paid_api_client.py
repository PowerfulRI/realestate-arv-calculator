"""
Clients for paid real estate data API services.
"""
import os
import json
import logging
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import requests
from datetime import datetime

from ..models.property import Property
from ..config.settings import DEFAULT_SEARCH_RADIUS_MILES, DEFAULT_MONTHS_BACK, MIN_COMPARABLE_PROPERTIES

logger = logging.getLogger(__name__)


class RealEstateApiClient(ABC):
    """Abstract base class for real estate API clients."""
    
    @abstractmethod
    def get_property_details(self, address: str) -> Optional[Property]:
        """
        Get details for a property by address.
        
        Args:
            address: Full property address
            
        Returns:
            Property object if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_comparable_properties(self, 
                                  property_obj: Property, 
                                  radius_miles: float = DEFAULT_SEARCH_RADIUS_MILES, 
                                  months_back: int = DEFAULT_MONTHS_BACK, 
                                  min_similar_properties: int = MIN_COMPARABLE_PROPERTIES) -> List[Property]:
        """
        Find comparable properties based on given property.
        
        Args:
            property_obj: Property to find comparables for
            radius_miles: Search radius in miles
            months_back: Limit to properties sold in the past X months
            min_similar_properties: Minimum number of similar properties to return
            
        Returns:
            List of comparable property objects
        """
        pass
    
    @abstractmethod
    def get_property_valuation(self, property_obj: Property) -> Dict[str, Any]:
        """
        Get valuation data for a property.
        
        Args:
            property_obj: Property to get valuation for
            
        Returns:
            Dictionary with valuation data
        """
        pass


class AttomApiClient(RealEstateApiClient):
    """Client for ATTOM Data Solutions API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ATTOM API client.
        
        Args:
            api_key: API key for ATTOM Data Solutions
        """
        self.api_key = api_key or os.environ.get("ATTOM_API_KEY")
        if not self.api_key:
            logger.warning("ATTOM API key not provided. Set ATTOM_API_KEY environment variable.")
            
        self.base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"
        self.headers = {
            "apikey": self.api_key,
            "Accept": "application/json",
        }
        
    def get_property_details(self, address: str) -> Optional[Property]:
        """
        Get details for a property by address using ATTOM API.
        
        Args:
            address: Full property address
            
        Returns:
            Property object if found, None otherwise
        """
        if not self.api_key:
            logger.error("ATTOM API key is required")
            return None
            
        try:
            # Parse address
            address_parts = address.split(',')
            street = address_parts[0].strip()
            
            city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else ""
            city_state_zip_parts = city_state_zip.split()
            
            # Extract zip code and city from address
            zip_code = city_state_zip_parts[-1] if city_state_zip_parts else ""
            city = ' '.join(city_state_zip_parts[:-2]) if len(city_state_zip_parts) > 2 else ""
            
            # Endpoint for property ID lookup
            endpoint = f"{self.base_url}/property/basicprofile"
            
            params = {
                "address1": street,
                "address2": city_state_zip
            }
            
            # Make API request
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"ATTOM API error: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            
            # Extract property data
            if "property" not in data or not data["property"]:
                logger.warning(f"No property found for address: {address}")
                return None
                
            property_data = data["property"][0]
            
            # Extract property details
            property_id = property_data.get("identifier", {}).get("attomId", f"attom-{int(time.time())}")
            address = property_data.get("address", {}).get("line1", street)
            city = property_data.get("address", {}).get("locality", city)
            state = property_data.get("address", {}).get("countrySubd", "")
            zip_code = property_data.get("address", {}).get("postal1", zip_code)
            
            # Extract building details
            building = property_data.get("building", {})
            beds = building.get("rooms", {}).get("beds", 0)
            baths = building.get("rooms", {}).get("bathsTotal", 0)
            year_built = building.get("yearBuilt", 0)
            square_footage = building.get("size", {}).get("universalsize", 0)
            
            # Extract lot details
            lot = property_data.get("lot", {})
            lot_size_acres = lot.get("acres", 0)
            
            # Extract valuation details
            valuation = property_data.get("avm", {})
            estimated_value = valuation.get("amount", {}).get("value", 0)
            
            # Extract sale details
            sale = property_data.get("sale", {})
            last_sale_price = sale.get("amount", {}).get("saleAmt", 0)
            last_sale_date_str = sale.get("salesDate", "")
            
            # Parse sale date if available
            last_sale_date = None
            if last_sale_date_str:
                try:
                    last_sale_date = datetime.strptime(last_sale_date_str, "%Y-%m-%d")
                except ValueError:
                    last_sale_date = datetime.now()
            else:
                last_sale_date = datetime.now()
            
            # Extract location details
            latitude = property_data.get("location", {}).get("latitude", None)
            longitude = property_data.get("location", {}).get("longitude", None)
            
            # Create Property object
            property_obj = Property(
                property_id=str(property_id),
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                bedrooms=int(beds) if beds else 0,
                bathrooms=float(baths) if baths else 0,
                square_footage=int(square_footage) if square_footage else 0,
                lot_size=float(lot_size_acres) if lot_size_acres else 0,
                year_built=int(year_built) if year_built else 0,
                last_sale_date=last_sale_date,
                last_sale_price=float(last_sale_price) if last_sale_price else None,
                estimated_value=float(estimated_value) if estimated_value else None,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None
            )
            
            return property_obj
            
        except Exception as e:
            logger.error(f"Error getting property details from ATTOM API: {str(e)}")
            return None
    
    def find_comparable_properties(self, 
                                  property_obj: Property, 
                                  radius_miles: float = DEFAULT_SEARCH_RADIUS_MILES, 
                                  months_back: int = DEFAULT_MONTHS_BACK,
                                  min_similar_properties: int = MIN_COMPARABLE_PROPERTIES) -> List[Property]:
        """
        Find comparable properties using ATTOM API.
        
        Args:
            property_obj: Property to find comparables for
            radius_miles: Search radius in miles
            months_back: Limit to properties sold in the past X months
            min_similar_properties: Minimum number of similar properties to return
            
        Returns:
            List of comparable property objects
        """
        if not self.api_key:
            logger.error("ATTOM API key is required")
            return []
            
        try:
            # Get property AVM (Automated Valuation Model) with comps
            endpoint = f"{self.base_url}/property/avm"
            
            params = {
                "address1": property_obj.address,
                "address2": f"{property_obj.city}, {property_obj.state} {property_obj.zip_code}",
                "radius": radius_miles,
                "includecomparables": "true",
                "compPropertyCount": max(10, min_similar_properties)
            }
            
            # Make API request
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"ATTOM API error: {response.status_code} - {response.text}")
                return []
                
            data = response.json()
            
            # Extract comparable properties
            if "property" not in data or not data["property"]:
                logger.warning(f"No property found for address: {property_obj.address}")
                return []
                
            property_data = data["property"][0]
            
            comps = []
            if "comparables" in property_data:
                comp_properties = property_data["comparables"].get("compproperty", [])
                
                for comp_data in comp_properties:
                    try:
                        # Extract comp property details
                        comp_id = comp_data.get("identifier", {}).get("attomId", f"attom-comp-{int(time.time())}")
                        address = comp_data.get("address", {}).get("line1", "")
                        city = comp_data.get("address", {}).get("locality", "")
                        state = comp_data.get("address", {}).get("countrySubd", "")
                        zip_code = comp_data.get("address", {}).get("postal1", "")
                        
                        # Extract building details
                        building = comp_data.get("building", {})
                        beds = building.get("rooms", {}).get("beds", 0)
                        baths = building.get("rooms", {}).get("bathsTotal", 0)
                        year_built = building.get("yearBuilt", 0)
                        square_footage = building.get("size", {}).get("universalsize", 0)
                        
                        # Extract lot details
                        lot = comp_data.get("lot", {})
                        lot_size_acres = lot.get("acres", 0)
                        
                        # Extract sale details
                        sale = comp_data.get("sale", {})
                        sale_price = sale.get("amount", {}).get("saleAmt", 0)
                        sale_date_str = sale.get("salesDate", "")
                        
                        # Parse sale date if available
                        sale_date = None
                        if sale_date_str:
                            try:
                                sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d")
                            except ValueError:
                                sale_date = datetime.now()
                        else:
                            sale_date = datetime.now()
                        
                        # Extract location details
                        latitude = comp_data.get("location", {}).get("latitude", None)
                        longitude = comp_data.get("location", {}).get("longitude", None)
                        
                        # Create Property object
                        comp_property = Property(
                            property_id=str(comp_id),
                            address=address,
                            city=city,
                            state=state,
                            zip_code=zip_code,
                            bedrooms=int(beds) if beds else 0,
                            bathrooms=float(baths) if baths else 0,
                            square_footage=int(square_footage) if square_footage else 0,
                            lot_size=float(lot_size_acres) if lot_size_acres else 0,
                            year_built=int(year_built) if year_built else 0,
                            last_sale_date=sale_date,
                            last_sale_price=float(sale_price) if sale_price else None,
                            estimated_value=float(sale_price) if sale_price else None,
                            latitude=float(latitude) if latitude else None,
                            longitude=float(longitude) if longitude else None
                        )
                        
                        comps.append(comp_property)
                        
                    except Exception as e:
                        logger.error(f"Error processing comparable property: {str(e)}")
                        continue
                        
            logger.info(f"Found {len(comps)} comparable properties via ATTOM API")
            return comps
            
        except Exception as e:
            logger.error(f"Error finding comparable properties from ATTOM API: {str(e)}")
            return []
    
    def get_property_valuation(self, property_obj: Property) -> Dict[str, Any]:
        """
        Get valuation data for a property using ATTOM API.
        
        Args:
            property_obj: Property to get valuation for
            
        Returns:
            Dictionary with valuation data
        """
        if not self.api_key:
            logger.error("ATTOM API key is required")
            return {}
            
        try:
            # Get property AVM (Automated Valuation Model)
            endpoint = f"{self.base_url}/property/avm"
            
            params = {
                "address1": property_obj.address,
                "address2": f"{property_obj.city}, {property_obj.state} {property_obj.zip_code}"
            }
            
            # Make API request
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"ATTOM API error: {response.status_code} - {response.text}")
                return {}
                
            data = response.json()
            
            # Extract valuation data
            if "property" not in data or not data["property"]:
                logger.warning(f"No valuation data found for address: {property_obj.address}")
                return {}
                
            property_data = data["property"][0]
            avm_data = property_data.get("avm", {})
            
            # Extract valuation details
            valuation = {
                "value": avm_data.get("amount", {}).get("value", 0),
                "high_value": avm_data.get("amount", {}).get("highValue", 0),
                "low_value": avm_data.get("amount", {}).get("lowValue", 0),
                "confidence_score": avm_data.get("confidenceScore", {}).get("score", 0),
                "confidence_range": avm_data.get("confidenceRange", 0),
                "forecast_standard_deviation": avm_data.get("forecastStandardDeviation", 0),
                "valuation_date": avm_data.get("valuationDate", "")
            }
            
            return valuation
            
        except Exception as e:
            logger.error(f"Error getting property valuation from ATTOM API: {str(e)}")
            return {}


class ApiClientFactory:
    """Factory for creating API clients."""
    
    @staticmethod
    def get_client(api_type: str, api_key: Optional[str] = None) -> Optional[RealEstateApiClient]:
        """
        Get API client of the specified type.
        
        Args:
            api_type: Type of API client ("attom", etc.)
            api_key: API key for the service
            
        Returns:
            RealEstateApiClient instance or None if invalid type
        """
        if api_type.lower() == "attom":
            return AttomApiClient(api_key)
        else:
            logger.error(f"Unknown API client type: {api_type}")
            return None