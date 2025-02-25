"""
Utility functions for geospatial calculations.
"""
import math
from typing import Tuple


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth (specified in decimal degrees).
    Uses the Haversine formula.
    
    Args:
        lat1: Latitude of point 1 (in decimal degrees)
        lon1: Longitude of point 1 (in decimal degrees)
        lat2: Latitude of point 2 (in decimal degrees)
        lon2: Longitude of point 2 (in decimal degrees)
        
    Returns:
        Distance between the points in miles
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 3956  # Radius of earth in miles
    
    return c * r


def get_bounding_box(lat: float, lon: float, radius_miles: float) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box around a point given a radius in miles.
    
    Args:
        lat: Latitude of center point (in decimal degrees)
        lon: Longitude of center point (in decimal degrees)
        radius_miles: Radius in miles
        
    Returns:
        Tuple containing (min_lat, min_lon, max_lat, max_lon)
    """
    # Approximate miles per degree of latitude
    miles_per_lat = 69.0
    
    # Approximate miles per degree of longitude (varies with latitude)
    miles_per_lon = 69.0 * math.cos(math.radians(lat))
    
    # Calculate the lat/lon deltas
    lat_delta = radius_miles / miles_per_lat
    lon_delta = radius_miles / miles_per_lon
    
    # Calculate the bounding box
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta
    
    return (min_lat, min_lon, max_lat, max_lon)


def is_point_in_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_miles: float) -> bool:
    """
    Check if a point is within a specified radius of another point.
    
    Args:
        lat1: Latitude of center point (in decimal degrees)
        lon1: Longitude of center point (in decimal degrees)
        lat2: Latitude of point to check (in decimal degrees)
        lon2: Longitude of point to check (in decimal degrees)
        radius_miles: Radius in miles
        
    Returns:
        True if the point is within the radius, False otherwise
    """
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_miles