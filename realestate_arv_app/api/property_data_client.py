"""
API client for fetching property data from various real estate data providers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from ..models.property import Property


class PropertyDataClient(ABC):
    """Abstract base class for property data API clients."""
    
    @abstractmethod
    def get_property_details(self, address: str) -> Optional[Property]:
        """Fetch property details by address."""
        pass
    
    @abstractmethod
    def find_comparable_properties(self, 
                                   property_obj: Property, 
                                   radius_miles: float = 2.0, 
                                   months_back: int = 6, 
                                   min_similar_properties: int = 3) -> List[Property]:
        """Find comparable properties within specified radius and time frame."""
        pass


class ZillowApiClient(PropertyDataClient):
    """Implementation of PropertyDataClient for Zillow API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.zillow.com/v1"
        
    def get_property_details(self, address: str) -> Optional[Property]:
        """Fetch property details from Zillow API."""
        # TODO: Implement actual API call to Zillow
        # This is a placeholder implementation
        return None
        
    def find_comparable_properties(self, 
                                   property_obj: Property, 
                                   radius_miles: float = 2.0, 
                                   months_back: int = 6, 
                                   min_similar_properties: int = 3) -> List[Property]:
        """Find comparable properties using Zillow API."""
        # TODO: Implement actual API call to Zillow
        # This is a placeholder implementation
        return []


class RedfinApiClient(PropertyDataClient):
    """Implementation of PropertyDataClient for Redfin API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.redfin.com/v1"
        
    def get_property_details(self, address: str) -> Optional[Property]:
        """Fetch property details from Redfin API."""
        # TODO: Implement actual API call to Redfin
        # This is a placeholder implementation
        return None
        
    def find_comparable_properties(self, 
                                   property_obj: Property, 
                                   radius_miles: float = 2.0, 
                                   months_back: int = 6, 
                                   min_similar_properties: int = 3) -> List[Property]:
        """Find comparable properties using Redfin API."""
        # TODO: Implement actual API call to Redfin
        # This is a placeholder implementation
        return []