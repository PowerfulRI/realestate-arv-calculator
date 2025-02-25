#!/usr/bin/env python3
"""
Real Estate ARV Calculator - Main application entry point.
"""
import argparse
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from realestate_arv_app.models.property import Property
from realestate_arv_app.api.property_service import PropertyService
from realestate_arv_app.api.ai_analyzer import AIAnalyzer
from realestate_arv_app.analysis.comps_analyzer import CompsAnalyzer
from realestate_arv_app.analysis.renovation_calculator import RenovationCalculator
from realestate_arv_app.utils.report_generator import generate_markdown_report, generate_json_report


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_SEARCH_RADIUS_MILES = 2.0
DEFAULT_MONTHS_BACK = 6
MIN_COMPARABLE_PROPERTIES = 3
DEFAULT_CONTINGENCY_PERCENT = 15


def format_currency(value: float) -> str:
    """Format a value as currency."""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format a value as percentage."""
    return f"{value:.2f}%"


def create_sample_property() -> Property:
    """Create a sample property for demonstration purposes."""
    return Property(
        property_id="sample-123",
        address="123 Main St",
        city="Anytown",
        state="CA",
        zip_code="12345",
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


def create_sample_comps() -> List[Property]:
    """Create sample comparable properties for demonstration purposes."""
    return [
        Property(
            property_id="comp-1",
            address="125 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            bedrooms=3,
            bathrooms=2.0,
            square_footage=1750,
            lot_size=0.22,
            year_built=1982,
            last_sale_date=datetime(2023, 2, 10),
            last_sale_price=425000,
            estimated_value=430000,
            latitude=37.7751,
            longitude=-122.4192
        ),
        Property(
            property_id="comp-2",
            address="130 Oak Ave",
            city="Anytown",
            state="CA",
            zip_code="12345",
            bedrooms=3,
            bathrooms=2.5,
            square_footage=1950,
            lot_size=0.28,
            year_built=1988,
            last_sale_date=datetime(2023, 1, 5),
            last_sale_price=450000,
            estimated_value=455000,
            latitude=37.7745,
            longitude=-122.4188
        ),
        Property(
            property_id="comp-3",
            address="118 Elm St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            bedrooms=2,
            bathrooms=2.0,
            square_footage=1600,
            lot_size=0.20,
            year_built=1980,
            last_sale_date=datetime(2022, 11, 20),
            last_sale_price=385000,
            estimated_value=395000,
            latitude=37.7755,
            longitude=-122.4198
        ),
        Property(
            property_id="comp-4",
            address="140 Pine Rd",
            city="Anytown",
            state="CA",
            zip_code="12345",
            bedrooms=4,
            bathrooms=2.5,
            square_footage=2100,
            lot_size=0.30,
            year_built=1990,
            last_sale_date=datetime(2023, 3, 15),
            last_sale_price=475000,
            estimated_value=480000,
            latitude=37.7740,
            longitude=-122.4185
        ),
    ]


def get_property_from_web(address: str) -> Optional[Dict[str, Any]]:
    """
    Get property details from web scraping.
    
    Args:
        address: Full property address
        
    Returns:
        Dictionary with property data and analysis results or None if not found
    """
    try:
        # Use PropertyService instead of RealtyScrapingService
        property_service = PropertyService(headless=True)
        
        try:
            # Try to get property details from the web
            logger.info(f"Searching for property: {address}")
            property_obj = property_service.get_property_details(address)
            
            if not property_obj:
                logger.error(f"Property not found: {address}")
                return None
                
            logger.info(f"Property found: {property_obj.address}, {property_obj.city}, {property_obj.state}")
            
            # Try to find comparable properties
            logger.info("Finding comparable properties...")
            comparable_properties = property_service.find_comparable_properties(
                property_obj=property_obj,
                radius_miles=DEFAULT_SEARCH_RADIUS_MILES,
                months_back=DEFAULT_MONTHS_BACK,
                min_similar_properties=MIN_COMPARABLE_PROPERTIES
            )
            
            logger.info(f"Found {len(comparable_properties)} comparable properties")
            
            # Analyze comparable properties
            comps_analyzer = CompsAnalyzer(property_obj, comparable_properties)
            filtered_comps = comps_analyzer.filter_comps()
            comps_analyzer.apply_adjustments()
            arv_result = comps_analyzer.calculate_arv()
            
            # Calculate renovation costs
            renovation_calculator = RenovationCalculator(property_sqft=property_obj.square_footage)
            renovation_calculator.add_kitchen_renovation(quality="mid-range")
            renovation_calculator.add_bathroom_renovation(quality="mid-range", count=2)
            renovation_calculator.add_flooring(type_key="hardwood")
            renovation_calculator.add_paint(type_key="interior")
            renovation_calculator.set_additional_cost("permits", 2500)
            renovation_calculator.set_additional_cost("holding_costs", 5000)
            renovation_costs = renovation_calculator.calculate_total_renovation_cost()
            
            # Calculate investment metrics
            purchase_price = property_obj.last_sale_price if property_obj.last_sale_price else property_obj.estimated_value
            arv = arv_result["arv"]
            roi_metrics = renovation_calculator.calculate_roi(purchase_price, arv)
            
            # Get AI analysis if API key is available
            ai_analysis = None
            if os.environ.get("ANTHROPIC_API_KEY"):
                logger.info("Getting AI analysis...")
                try:
                    ai_analyzer = AIAnalyzer()
                    
                    # Assuming we have a property description (in a real implementation, 
                    # this would be scraped from the property listing)
                    # For this example, we'll use a placeholder
                    property_description = f"Beautiful {property_obj.bedrooms} bedroom, {property_obj.bathrooms} bathroom home built in {property_obj.year_built}."
                    
                    # Investment evaluation
                    ai_analysis = ai_analyzer.evaluate_investment(
                        property_obj=property_obj,
                        purchase_price=purchase_price,
                        renovation_cost=renovation_costs["total"],
                        holding_months=6,
                        arv=arv,
                        comps=filtered_comps
                    )
                    
                    logger.info("AI analysis complete")
                except Exception as e:
                    logger.error(f"Error getting AI analysis: {str(e)}")
            
            return {
                "property": property_obj,
                "filtered_comps": filtered_comps,
                "arv_result": arv_result,
                "renovation_costs": renovation_costs,
                "roi_metrics": roi_metrics,
                "ai_analysis": ai_analysis
            }
            
        finally:
            # Ensure the service is closed
            property_service.close()
            
    except Exception as e:
        logger.error(f"Error getting property from web: {str(e)}")
        return None


def run_sample_analysis() -> Dict[str, Any]:
    """Run a sample property analysis for demonstration purposes."""
    # Create sample data
    target_property = create_sample_property()
    comparable_properties = create_sample_comps()
    
    # Analyze comparable properties
    comps_analyzer = CompsAnalyzer(target_property, comparable_properties)
    filtered_comps = comps_analyzer.filter_comps()
    comps_analyzer.apply_adjustments()
    arv_result = comps_analyzer.calculate_arv()
    
    # Set a default ARV if the calculation returns None
    if arv_result["arv"] is None:
        # Use the average of the comparable properties' prices as a fallback
        comp_prices = [comp.last_sale_price for comp in filtered_comps if comp.last_sale_price]
        if comp_prices:
            arv_result["arv"] = sum(comp_prices) / len(comp_prices)
        else:
            # If no comps with prices, use the target property's estimated value
            arv_result["arv"] = target_property.estimated_value or 450000
            arv_result["arv_range"] = (arv_result["arv"] * 0.9, arv_result["arv"] * 1.1)
            arv_result["confidence"] = "low"
            arv_result["price_per_sqft"] = arv_result["arv"] / target_property.square_footage
    
    # Calculate renovation costs
    renovation_calculator = RenovationCalculator(property_sqft=target_property.square_footage)
    renovation_calculator.add_kitchen_renovation(quality="mid-range")
    renovation_calculator.add_bathroom_renovation(quality="mid-range", count=2)
    renovation_calculator.add_flooring(type_key="hardwood")
    renovation_calculator.add_paint(type_key="interior")
    renovation_calculator.set_additional_cost("permits", 2500)
    renovation_calculator.set_additional_cost("holding_costs", 5000)
    renovation_costs = renovation_calculator.calculate_total_renovation_cost()
    
    # Calculate investment metrics
    purchase_price = target_property.last_sale_price
    arv = arv_result["arv"]
    roi_metrics = renovation_calculator.calculate_roi(purchase_price, arv)
    
    # Get AI analysis if API key is available
    ai_analysis = None
    if os.environ.get("ANTHROPIC_API_KEY"):
        logger.info("Getting AI analysis...")
        try:
            ai_analyzer = AIAnalyzer()
            
            # Sample property description
            property_description = f"Beautiful {target_property.bedrooms} bedroom, {target_property.bathrooms} bathroom home built in {target_property.year_built}. Features include a spacious kitchen, hardwood floors throughout, and a large backyard."
            
            # Investment evaluation
            ai_analysis = ai_analyzer.evaluate_investment(
                property_obj=target_property,
                purchase_price=purchase_price,
                renovation_cost=renovation_costs["total"],
                holding_months=6,
                arv=arv,
                comps=filtered_comps
            )
            
            logger.info("AI analysis complete")
        except Exception as e:
            logger.error(f"Error getting AI analysis: {str(e)}")
    
    return {
        "property": target_property,
        "filtered_comps": filtered_comps,
        "arv_result": arv_result,
        "renovation_costs": renovation_costs,
        "roi_metrics": roi_metrics,
        "ai_analysis": ai_analysis
    }


def print_analysis_results(results: Dict[str, Any]) -> None:
    """Print the analysis results in a readable format."""
    property_obj = results["property"]
    arv_result = results["arv_result"]
    renovation_costs = results["renovation_costs"]
    roi_metrics = results["roi_metrics"]
    ai_analysis = results.get("ai_analysis")
    
    print("\n===== REAL ESTATE ARV CALCULATOR =====\n")
    
    print("PROPERTY DETAILS")
    print(f"Address: {property_obj.address}, {property_obj.city}, {property_obj.state} {property_obj.zip_code}")
    print(f"Beds/Baths: {property_obj.bedrooms} bed / {property_obj.bathrooms} bath")
    print(f"Square Footage: {property_obj.square_footage} sq ft")
    print(f"Year Built: {property_obj.year_built}")
    
    if property_obj.last_sale_date and property_obj.last_sale_price:
        print(f"Last Sale: {format_currency(property_obj.last_sale_price)} ({property_obj.last_sale_date.strftime('%m/%d/%Y')})")
    elif property_obj.estimated_value:
        print(f"Estimated Value: {format_currency(property_obj.estimated_value)}")
    
    print("\nCOMPARABLE PROPERTIES ANALYSIS")
    print(f"Number of Comps: {arv_result['comp_count']}")
    print(f"Confidence Level: {arv_result['confidence'].upper()}")
    if arv_result["price_per_sqft"]:
        print(f"Median Price per Sq Ft: {format_currency(arv_result['price_per_sqft'])}")
    
    print("\nAFTER REPAIR VALUE (ARV)")
    print(f"Estimated ARV: {format_currency(arv_result['arv'])}")
    print(f"ARV Range: {format_currency(arv_result['arv_range'][0])} - {format_currency(arv_result['arv_range'][1])}")
    
    print("\nRENOVATION COSTS")
    print(f"Base Renovation Cost: {format_currency(renovation_costs['base_renovation_cost'])}")
    print(f"Additional Costs: {format_currency(renovation_costs['additional_costs'])}")
    print(f"Contingency ({renovation_calculator.contingency_percent}%): {format_currency(renovation_costs['contingency'])}")
    print(f"Total Renovation Cost: {format_currency(renovation_costs['total'])}")
    
    print("\nINVESTMENT ANALYSIS")
    print(f"Purchase Price: {format_currency(roi_metrics['purchase_price'])}")
    print(f"Renovation Cost: {format_currency(roi_metrics['renovation_cost'])}")
    print(f"Total Investment: {format_currency(roi_metrics['total_investment'])}")
    print(f"After Repair Value: {format_currency(roi_metrics['arv'])}")
    print(f"Potential Profit: {format_currency(roi_metrics['profit'])}")
    print(f"ROI: {format_percentage(roi_metrics['roi_percentage'])}")
    
    print("\n70% RULE ANALYSIS")
    print(f"Maximum Purchase Price (70% Rule): {format_currency(roi_metrics['rule_70_max_price'])}")
    current_percentage = (roi_metrics['purchase_price'] / roi_metrics['arv']) * 100
    print(f"Current Purchase Price is {format_percentage(current_percentage)} of ARV")
    
    # Display AI analysis if available
    if ai_analysis and 'error' not in ai_analysis:
        print("\nAI INVESTMENT ANALYSIS")
        try:
            if 'investment_rating' in ai_analysis:
                print(f"Investment Rating: {ai_analysis.get('investment_rating', 'N/A').upper()}")
            
            if 'recommendation' in ai_analysis:
                print(f"Recommendation: {ai_analysis.get('recommendation', 'N/A')}")
                
            if 'suggested_max_price' in ai_analysis:
                print(f"Suggested Max Purchase Price: {format_currency(float(ai_analysis.get('suggested_max_price', 0)))}")
                
            if 'expected_roi' in ai_analysis:
                print(f"Expected ROI: {format_percentage(float(ai_analysis.get('expected_roi', 0)))}")
                
            if 'key_concerns' in ai_analysis and isinstance(ai_analysis['key_concerns'], list):
                print("\nKey Concerns:")
                for concern in ai_analysis['key_concerns'][:3]:  # Show top 3 concerns
                    print(f"- {concern}")
            
            if 'opportunities' in ai_analysis and isinstance(ai_analysis['opportunities'], list):
                print("\nOpportunities:")
                for opportunity in ai_analysis['opportunities'][:3]:  # Show top 3 opportunities
                    print(f"- {opportunity}")
                    
        except Exception as e:
            print(f"\nError displaying AI analysis: {str(e)}")
    
    print("\n===== END OF ANALYSIS =====\n")


def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description="Real Estate ARV Calculator")
    parser.add_argument("--address", help="Property address to analyze")
    parser.add_argument("--sample", action="store_true", help="Run with sample data")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--report", action="store_true", help="Generate a detailed markdown report")
    parser.add_argument("--output", help="Output file path for report or JSON")
    parser.add_argument("--headless", type=lambda x: x.lower() not in ['false', 'no', '0'], 
                        help="Run browser in headless mode (true/false)", default=True)
    parser.add_argument("--no-api", action="store_true", help="Disable API usage and force web scraping")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    if args.sample:
        # Create a global renovation calculator for demonstration
        global renovation_calculator
        renovation_calculator = RenovationCalculator(property_sqft=1800)
        
        results = run_sample_analysis()
        # Add the renovation calculator to the results for use in reports
        results["renovation_calculator"] = renovation_calculator
        
        if args.json:
            # Generate JSON report
            if args.output:
                output_path = generate_json_report(results, args.output)
                logger.info(f"JSON report saved to: {output_path}")
            else:
                # Print to console
                json_content = generate_json_report(results)
                print(json_content)
        elif args.report:
            # Generate markdown report
            address = "123 Main St, Anytown, CA 12345"  # Sample address
            output_path = args.output
            report_path = generate_markdown_report(results, address, output_path)
            logger.info(f"Markdown report saved to: {report_path}")
            print(f"Analysis report saved to: {report_path}")
        else:
            # Print to console
            print_analysis_results(results)
    elif args.address:
        # Initialize the property service
        use_api = not args.no_api
        logger.info(f"Using API: {use_api}, Headless mode: {args.headless}")
        
        # Try to get property data
        property_service = PropertyService(headless=args.headless, use_api=use_api)
        try:
            # Try to get property details from API or web
            logger.info(f"Searching for property: {args.address}")
            property_obj = property_service.get_property_details(args.address)
            
            if not property_obj:
                logger.error(f"Property not found: {args.address}")
                print(f"Could not find property information for address: {args.address}")
                return
                
            logger.info(f"Property found: {property_obj.address}, {property_obj.city}, {property_obj.state}")
            
            # Try to find comparable properties
            logger.info("Finding comparable properties...")
            comparable_properties = property_service.find_comparable_properties(
                property_obj=property_obj,
                radius_miles=DEFAULT_SEARCH_RADIUS_MILES,
                months_back=DEFAULT_MONTHS_BACK,
                min_similar_properties=MIN_COMPARABLE_PROPERTIES
            )
            
            logger.info(f"Found {len(comparable_properties)} comparable properties")
            
            # Get valuation data if available
            valuation_data = None
            if use_api:
                valuation_data = property_service.get_property_valuation(property_obj)
                if valuation_data and "value" in valuation_data and valuation_data["value"]:
                    logger.info(f"Got valuation data: ${valuation_data['value']}")
                    # Update estimated value if we have API valuation
                    property_obj.estimated_value = valuation_data["value"]
            
            # Analyze comparable properties
            comps_analyzer = CompsAnalyzer(property_obj, comparable_properties)
            filtered_comps = comps_analyzer.filter_comps()
            comps_analyzer.apply_adjustments()
            arv_result = comps_analyzer.calculate_arv()
            
            # Set a default ARV if the calculation returns None
            if arv_result["arv"] is None:
                # Use the average of the comparable properties' prices as a fallback
                comp_prices = [comp.last_sale_price for comp in filtered_comps if comp.last_sale_price]
                if comp_prices:
                    arv_result["arv"] = sum(comp_prices) / len(comp_prices)
                elif property_obj.estimated_value:
                    # If no comps with prices, use the target property's estimated value
                    arv_result["arv"] = property_obj.estimated_value
                    arv_result["arv_range"] = (arv_result["arv"] * 0.9, arv_result["arv"] * 1.1)
                    arv_result["confidence"] = "low"
                    arv_result["price_per_sqft"] = arv_result["arv"] / property_obj.square_footage if property_obj.square_footage else 0
                else:
                    # Last resort: use a default value based on median home price
                    default_value = 350000  # Default median home price
                    arv_result["arv"] = default_value
                    arv_result["arv_range"] = (default_value * 0.9, default_value * 1.1)
                    arv_result["confidence"] = "very low"
                    arv_result["price_per_sqft"] = default_value / property_obj.square_footage if property_obj.square_footage else 0
                    logger.warning("Using default ARV due to lack of data")
            
            # Calculate renovation costs based on property size and condition
            try:
                # Determine appropriate renovation level based on property age
                renovation_quality = "basic"
                if property_obj.year_built:
                    years_old = datetime.now().year - property_obj.year_built
                    if years_old < 20:
                        renovation_quality = "basic"
                    elif years_old < 40:
                        renovation_quality = "mid-range"
                    else:
                        renovation_quality = "high-end"
                
                # Adjust bathroom count based on property size
                bathroom_count = property_obj.bathrooms if property_obj.bathrooms else 2
                
                renovation_calculator = RenovationCalculator(
                    property_sqft=property_obj.square_footage, 
                    contingency_percent=DEFAULT_CONTINGENCY_PERCENT
                )
                
                # Add standard renovations
                renovation_calculator.add_kitchen_renovation(quality=renovation_quality)
                renovation_calculator.add_bathroom_renovation(quality=renovation_quality, count=int(bathroom_count))
                renovation_calculator.add_flooring(type_key="hardwood")
                renovation_calculator.add_paint(type_key="interior")
                
                # Add additional costs
                renovation_calculator.set_additional_cost("permits", 2500)
                renovation_calculator.set_additional_cost("holding_costs", 5000)
                renovation_costs = renovation_calculator.calculate_total_renovation_cost()
            except Exception as e:
                logger.error(f"Error calculating renovation costs: {str(e)}")
                # Fallback to basic renovation calculation
                renovation_calculator = RenovationCalculator(
                    property_sqft=property_obj.square_footage or 1500, 
                    contingency_percent=DEFAULT_CONTINGENCY_PERCENT
                )
                renovation_calculator.add_kitchen_renovation(quality="mid-range")
                renovation_calculator.add_bathroom_renovation(quality="mid-range", count=2)
                renovation_costs = renovation_calculator.calculate_total_renovation_cost()
            
            # Calculate investment metrics
            purchase_price = property_obj.last_sale_price if property_obj.last_sale_price else property_obj.estimated_value
            if not purchase_price and valuation_data and "value" in valuation_data:
                purchase_price = valuation_data["value"]
            elif not purchase_price:
                purchase_price = arv_result["arv"] * 0.9  # Default to 90% of ARV
                
            arv = arv_result["arv"]
            roi_metrics = renovation_calculator.calculate_roi(purchase_price, arv)
            
            # Get AI analysis if API key is available
            ai_analysis = None
            if os.environ.get("ANTHROPIC_API_KEY"):
                logger.info("Getting AI analysis...")
                try:
                    ai_analyzer = AIAnalyzer(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                    
                    # Generate a property description based on available data
                    property_age = ""
                    if property_obj.year_built:
                        property_age = f"built in {property_obj.year_built}"
                        
                    property_description = (
                        f"Beautiful {property_obj.bedrooms}-bedroom, {property_obj.bathrooms}-bathroom home {property_age} "
                        f"with {property_obj.square_footage} square feet of living space. "
                        f"Located in {property_obj.city}, {property_obj.state}."
                    )
                    
                    # Investment evaluation
                    ai_analysis = ai_analyzer.evaluate_investment(
                        property_obj=property_obj,
                        purchase_price=purchase_price,
                        renovation_cost=renovation_costs["total"],
                        holding_months=6,
                        arv=arv,
                        comps=filtered_comps
                    )
                    
                    logger.info("AI analysis complete")
                except Exception as e:
                    logger.error(f"Error getting AI analysis: {str(e)}")
            
            results = {
                "property": property_obj,
                "filtered_comps": filtered_comps,
                "arv_result": arv_result,
                "renovation_costs": renovation_costs,
                "roi_metrics": roi_metrics,
                "ai_analysis": ai_analysis,
                "valuation_data": valuation_data
            }
            
            # Add the renovation calculator to the results for use in reports
            if 'renovation_calculator' in locals():
                results["renovation_calculator"] = renovation_calculator
            
            if args.json:
                # Generate JSON report
                if args.output:
                    output_path = generate_json_report(results, args.output)
                    logger.info(f"JSON report saved to: {output_path}")
                else:
                    # Print to console
                    json_content = generate_json_report(results)
                    print(json_content)
            elif args.report:
                # Generate markdown report
                address = args.address
                output_path = args.output
                report_path = generate_markdown_report(results, address, output_path)
                logger.info(f"Markdown report saved to: {report_path}")
                print(f"Analysis report saved to: {report_path}")
            else:
                # Print to console
                print_analysis_results(results)
                
        except Exception as e:
            logger.error(f"Error analyzing property: {str(e)}")
            print(f"Error analyzing property: {str(e)}")
        finally:
            # Ensure the property service is closed
            property_service.close()
    else:
        parser.print_help()


if __name__ == "__main__":
    # Create a global renovation calculator for demonstration
    renovation_calculator = RenovationCalculator(property_sqft=1800)
    main()