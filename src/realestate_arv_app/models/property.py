"""
Property model for storing and managing property data.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class Property:
    """Property model class for storing property information."""
    
    property_id: str
    address: str
    city: str
    state: str
    zip_code: str
    bedrooms: int
    bathrooms: float
    square_footage: float
    lot_size: float
    year_built: int
    last_sale_date: Optional[datetime] = None
    last_sale_price: Optional[float] = None
    estimated_value: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    features: Optional[Dict] = None
    
    def __post_init__(self):
        """Initialize calculated fields after initialization."""
        self.price_per_sqft = self.calculate_price_per_sqft()
    
    def calculate_price_per_sqft(self) -> Optional[float]:
        """Calculate the price per square foot based on last sale price."""
        if self.last_sale_price and self.square_footage:
            return round(self.last_sale_price / self.square_footage, 2)
        return None


@dataclass
class ComparableProperty(Property):
    """Extends Property class with fields specific to comparable properties."""
    
    similarity_score: float = 0.0
    distance_miles: float = 0.0
    days_since_sold: int = 0
    adjustments: Dict[str, float] = None
    adjusted_value: Optional[float] = None

    def __init__(
        self,
        property_id: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        bedrooms: int,
        bathrooms: float,
        square_footage: float,
        lot_size: float,
        year_built: int,
        last_sale_date: Optional[datetime] = None,
        last_sale_price: Optional[float] = None,
        estimated_value: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ):
        super().__init__(
            property_id,
            address,
            city,
            state,
            zip_code,
            bedrooms,
            bathrooms,
            square_footage,
            lot_size,
            year_built,
            last_sale_date,
            last_sale_price,
            estimated_value,
            latitude,
            longitude
        )