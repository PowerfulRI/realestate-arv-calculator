"""
AI analyzer for property description, renovation recommendations, and market analysis.
"""
import os
import json
from typing import Dict, List, Any, Optional

import anthropic
from anthropic import Anthropic

from ..models.property import Property


class AIAnalyzer:
    """Analyzer that uses Claude to provide insights about properties."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI analyzer."""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set the ANTHROPIC_API_KEY environment variable.")
        
        self.client = Anthropic(api_key=self.api_key)
    
    def analyze_property_description(self, description: str) -> Dict[str, Any]:
        """
        Analyze a property description to extract key features and condition.
        
        Args:
            description: Property description text
            
        Returns:
            Dictionary containing extracted features and condition assessment
        """
        prompt = f"""
        Please analyze this real estate property description and extract the following information:
        
        1. Key features of the property
        2. Condition assessment (excellent, good, fair, poor)
        3. Notable amenities
        4. Any mentioned issues or needed repairs
        5. Any recent renovations or upgrades mentioned
        6. Overall sentiment (positive, neutral, negative)
        
        Format the response as a JSON object with these keys: features, condition, amenities, issues, renovations, sentiment.
        
        Property Description:
        {description}
        """
        
        message = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            system="You are a real estate analysis expert. Analyze property descriptions accurately and objectively.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            # Try to parse JSON from the response
            response_text = message.content[0].text
            # Find JSON in the response (it might be surrounded by other text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # If no JSON found, return a structured version of the full response
                return {
                    "features": [],
                    "condition": "unknown",
                    "amenities": [],
                    "issues": [],
                    "renovations": [],
                    "sentiment": "neutral",
                    "raw_response": response_text
                }
        except Exception as e:
            return {
                "error": str(e),
                "raw_response": message.content[0].text
            }
    
    def suggest_renovations(self, property_obj: Property, description: str, budget: float) -> Dict[str, Any]:
        """
        Suggest renovations for a property based on its details and description.
        
        Args:
            property_obj: Property object with detailed information
            description: Property description text
            budget: Available renovation budget
            
        Returns:
            Dictionary containing renovation suggestions and estimated costs
        """
        prompt = f"""
        You are advising a real estate investor who is considering purchasing and renovating this property as a fix and flip.
        Please suggest the most profitable renovations that would increase the property's value, prioritizing by ROI.
        
        Property Details:
        - Address: {property_obj.address}, {property_obj.city}, {property_obj.state} {property_obj.zip_code}
        - Bedrooms: {property_obj.bedrooms}
        - Bathrooms: {property_obj.bathrooms}
        - Square Footage: {property_obj.square_footage}
        - Year Built: {property_obj.year_built}
        - Current Estimated Value: ${property_obj.estimated_value if property_obj.estimated_value else "Unknown"}
        
        Property Description:
        {description}
        
        Available Renovation Budget: ${budget}
        
        Provide a renovation plan that includes:
        1. Prioritized list of recommended renovations with estimated costs
        2. Expected ROI for each renovation
        3. Estimated timeline for each renovation
        4. Expected increase in property value after all renovations
        5. Any permits or special considerations needed
        
        Format the response as a JSON object with the following structure:
        {
          "total_budget": number,
          "total_timeline_days": number,
          "estimated_value_increase": number,
          "estimated_roi_percentage": number,
          "renovations": [
            {
              "name": string,
              "description": string,
              "cost": number,
              "timeline_days": number,
              "estimated_value_add": number,
              "roi_percentage": number,
              "priority": string (high, medium, low)
            }
          ],
          "permits_needed": [string],
          "special_considerations": [string]
        }
        """
        
        message = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0,
            system="You are a real estate renovation expert with extensive knowledge of construction costs and return on investment for various home improvements.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            # Try to parse JSON from the response
            response_text = message.content[0].text
            # Find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {
                    "error": "No valid JSON found in response",
                    "raw_response": response_text
                }
        except Exception as e:
            return {
                "error": str(e),
                "raw_response": message.content[0].text
            }
    
    def analyze_market_trends(self, zip_code: str, property_type: str) -> Dict[str, Any]:
        """
        Analyze market trends for a specific location and property type.
        
        Args:
            zip_code: ZIP code of the area to analyze
            property_type: Type of property (single-family, condo, etc.)
            
        Returns:
            Dictionary containing market analysis
        """
        prompt = f"""
        Please provide a detailed market analysis for {property_type} properties in the {zip_code} zip code area.

        Include in your analysis:
        1. Current market conditions (buyer's market, seller's market, neutral)
        2. Recent price trends (past 12 months)
        3. Average days on market
        4. Inventory levels
        5. Forecast for the next 6-12 months
        6. Demographics of the area
        7. Key factors affecting property values
        8. Investment outlook (strong, moderate, weak)
        
        Format the response as a JSON object with the following structure:
        {{
          "market_condition": string,
          "price_trend": {{
            "direction": string (increasing, decreasing, stable),
            "percentage_change": number,
            "notes": string
          }},
          "avg_days_on_market": number,
          "inventory_level": string (high, medium, low),
          "forecast": string,
          "demographics": {{
            "population": string,
            "median_age": string,
            "median_income": string,
            "notes": string
          }},
          "value_factors": [string],
          "investment_outlook": string,
          "summary": string
        }}
        """
        
        message = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0,
            system="You are a real estate market analyst with expertise in trends, demographics, and investment outlooks.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            # Try to parse JSON from the response
            response_text = message.content[0].text
            # Find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {
                    "error": "No valid JSON found in response",
                    "raw_response": response_text
                }
        except Exception as e:
            return {
                "error": str(e),
                "raw_response": message.content[0].text
            }
            
    def evaluate_investment(
        self,
        property_obj: Property,
        purchase_price: float,
        renovation_cost: float,
        holding_months: int,
        arv: float,
        comps: List[Property]
    ) -> Dict[str, Any]:
        # Placeholder implementation
        return {
            "investment_rating": "moderate",
            "recommendation": "Consider the investment carefully",
            "suggested_max_price": purchase_price * 0.95,
            "expected_roi": 15.0,
            "key_concerns": ["Market volatility", "Renovation timeline"],
            "opportunities": ["Strong rental market", "Growing neighborhood"]
        }