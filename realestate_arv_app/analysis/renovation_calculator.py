"""
Renovation cost calculator for estimating repair costs and ROI.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RenovationItem:
    """Renovation item with cost details."""
    
    name: str
    category: str
    unit_cost: float
    quantity: float
    total_cost: Optional[float] = None
    
    def __post_init__(self):
        """Calculate total cost after initialization."""
        self.total_cost = self.unit_cost * self.quantity


class RenovationCalculator:
    """Calculator for estimating renovation costs."""
    
    # Default cost estimates for common renovation items
    DEFAULT_COSTS = {
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
    
    def __init__(self, property_sqft: float, contingency_percent: float = 10):
        self.property_sqft = property_sqft
        self.contingency_percent = contingency_percent
        self.costs = {}
        self.additional_costs = {}
        
    def add_kitchen_renovation(self, quality: str):
        self.costs["kitchen"] = 25000 if quality == "mid-range" else 40000
        
    def add_bathroom_renovation(self, quality: str, count: int):
        cost_per_bath = 10000 if quality == "mid-range" else 15000
        self.costs["bathroom"] = cost_per_bath * count
        
    def add_flooring(self, type_key: str):
        self.costs["flooring"] = self.property_sqft * 8
        
    def add_paint(self, type_key: str):
        self.costs["paint"] = self.property_sqft * 3
        
    def set_additional_cost(self, key: str, amount: float):
        self.additional_costs[key] = amount
        
    def calculate_total_renovation_cost(self) -> Dict[str, float]:
        base_cost = sum(self.costs.values())
        additional = sum(self.additional_costs.values())
        contingency = (base_cost + additional) * (self.contingency_percent / 100)
        
        return {
            "base_renovation_cost": base_cost,
            "additional_costs": additional,
            "contingency": contingency,
            "total": base_cost + additional + contingency
        }
        
    def calculate_roi(self, purchase_price: float, arv: float) -> Dict[str, float]:
        renovation_cost = self.calculate_total_renovation_cost()["total"]
        total_investment = purchase_price + renovation_cost
        profit = arv - total_investment
        roi_percentage = (profit / total_investment) * 100
        rule_70_max = (arv * 0.7) - renovation_cost
        
        return {
            "purchase_price": purchase_price,
            "renovation_cost": renovation_cost,
            "total_investment": total_investment,
            "arv": arv,
            "profit": profit,
            "roi_percentage": roi_percentage,
            "rule_70_max_price": rule_70_max
        }