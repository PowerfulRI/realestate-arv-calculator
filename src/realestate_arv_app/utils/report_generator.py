"""
Report generator for ARV analysis results.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


def format_currency(value: float) -> str:
    """Format a value as currency."""
    return f"${value:,.0f}"


def format_percentage(value: float) -> str:
    """Format a value as percentage."""
    return f"{value:.2f}%"


def format_date(date_obj: datetime) -> str:
    """Format a date object."""
    return date_obj.strftime("%m/%d/%Y")


def generate_markdown_report(results: Dict[str, Any], address: str, output_path: Optional[str] = None) -> str:
    """
    Generate a markdown report from the analysis results.
    
    Args:
        results: Dictionary containing analysis results
        address: The property address
        output_path: Path to save the report, if None, the report is returned as a string
        
    Returns:
        The report content as a string if output_path is None, otherwise None
    """
    property_obj = results["property"]
    arv_result = results["arv_result"]
    renovation_costs = results["renovation_costs"]
    roi_metrics = results["roi_metrics"]
    ai_analysis = results.get("ai_analysis", {})
    
    # Parse address into a clean form for the filename
    clean_address = property_obj.address.replace(",", "").replace(" ", "_").lower()
    if not output_path:
        output_path = f"{clean_address}_arv_report.md"
    
    # Format the current date
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Build the markdown report
    report = []
    report.append("# Real Estate ARV Analysis Report\n")
    
    full_address = f"{property_obj.address}, {property_obj.city}, {property_obj.state} {property_obj.zip_code}"
    report.append(f"## Property: {full_address}\n")
    report.append(f"*Analysis Date: {current_date}*\n")
    
    # Property Details
    report.append("## Property Details\n")
    report.append("| Feature | Value |")
    report.append("|---------|-------|")
    report.append(f"| Address | {full_address} |")
    report.append(f"| Bedrooms | {property_obj.bedrooms} |")
    report.append(f"| Bathrooms | {property_obj.bathrooms} |")
    report.append(f"| Square Footage | {property_obj.square_footage:,} sq ft |")
    report.append(f"| Year Built | {property_obj.year_built} |")
    
    if property_obj.last_sale_date and property_obj.last_sale_price:
        sale_date = format_date(property_obj.last_sale_date)
        sale_price = format_currency(property_obj.last_sale_price)
        report.append(f"| Last Sale | {sale_price} ({sale_date}) |")
    elif property_obj.estimated_value:
        report.append(f"| Estimated Value | {format_currency(property_obj.estimated_value)} |")
    
    report.append("\n## After Repair Value (ARV) Analysis\n")
    report.append("The property has been analyzed using comparable properties in the area to determine its potential After Repair Value.\n")
    
    report.append(f"**ARV Estimate: {format_currency(arv_result['arv'])}**\n")
    
    confidence = arv_result.get('confidence', 'unknown').upper()
    report.append(f"*Confidence Level: {confidence}*\n")
    
    arv_range = arv_result.get('arv_range', (0, 0))
    report.append(f"ARV Range: {format_currency(arv_range[0])} - {format_currency(arv_range[1])}\n")
    
    if arv_result.get('price_per_sqft'):
        report.append(f"Median Price per Square Foot: ${arv_result['price_per_sqft']:.2f}\n")
    
    # Renovation Costs
    report.append("## Renovation Cost Breakdown\n")
    report.append("| Category | Cost |")
    report.append("|----------|------|")
    report.append(f"| Base Renovation | {format_currency(renovation_costs['base_renovation_cost'])} |")
    report.append(f"| Additional Costs | {format_currency(renovation_costs['additional_costs'])} |")
    # Use a safe default of 10% if renovation_calculator is not available
    contingency_percent = 10
    if "renovation_calculator" in results and results["renovation_calculator"] is not None:
        if hasattr(results["renovation_calculator"], "contingency_percent"):
            contingency_percent = results["renovation_calculator"].contingency_percent
    report.append(f"| Contingency ({contingency_percent}%) | {format_currency(renovation_costs['contingency'])} |")
    report.append(f"| **Total Renovation** | **{format_currency(renovation_costs['total'])}** |\n")
    
    # Investment Analysis
    report.append("## Investment Analysis\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Purchase Price | {format_currency(roi_metrics['purchase_price'])} |")
    report.append(f"| Renovation Cost | {format_currency(roi_metrics['renovation_cost'])} |")
    report.append(f"| Total Investment | {format_currency(roi_metrics['total_investment'])} |")
    report.append(f"| After Repair Value | {format_currency(roi_metrics['arv'])} |")
    report.append(f"| Potential Profit | {format_currency(roi_metrics['profit'])} |")
    report.append(f"| Return on Investment | {format_percentage(roi_metrics['roi_percentage'])} |\n")
    
    # 70% Rule Analysis
    report.append("### 70% Rule Analysis\n")
    report.append("According to the 70% rule in real estate investing, the maximum purchase price should be:\n")
    report.append(f"**Maximum Purchase Price (70% Rule): {format_currency(roi_metrics['rule_70_max_price'])}**\n")
    
    current_percentage = (roi_metrics['purchase_price'] / roi_metrics['arv']) * 100
    report.append(f"Current purchase price is {format_percentage(current_percentage)} of ARV, which is {'significantly higher than' if current_percentage > 75 else 'close to'} the recommended 70%.\n")
    
    # AI Investment Analysis
    if ai_analysis:
        report.append("## AI Investment Analysis\n")
        
        if 'investment_rating' in ai_analysis:
            report.append(f"**Investment Rating: {ai_analysis.get('investment_rating', 'N/A').upper()}**\n")
        
        if 'recommendation' in ai_analysis:
            report.append(f"**Recommendation:** {ai_analysis.get('recommendation', 'N/A')}\n")
            
        if 'suggested_max_price' in ai_analysis:
            report.append(f"**Suggested Maximum Purchase Price:** {format_currency(float(ai_analysis.get('suggested_max_price', 0)))}\n")
            
        if 'expected_roi' in ai_analysis:
            report.append(f"**Expected ROI:** {format_percentage(float(ai_analysis.get('expected_roi', 0)))}\n")
            
        if 'key_concerns' in ai_analysis and isinstance(ai_analysis['key_concerns'], list):
            report.append("### Key Concerns")
            for concern in ai_analysis['key_concerns'][:3]:  # Show top 3 concerns
                report.append(f"- {concern}")
            report.append("")
        
        if 'opportunities' in ai_analysis and isinstance(ai_analysis['opportunities'], list):
            report.append("### Opportunities")
            for opportunity in ai_analysis['opportunities'][:3]:  # Show top 3 opportunities
                report.append(f"- {opportunity}")
            report.append("")
    
    # Conclusion
    report.append("## Conclusion\n")
    
    # Determine if it's a good investment
    is_good_investment = roi_metrics['roi_percentage'] > 15 and roi_metrics['purchase_price'] <= roi_metrics['rule_70_max_price'] * 1.1
    
    if is_good_investment:
        report.append(f"This property appears to be a promising investment at the current price of {format_currency(roi_metrics['purchase_price'])}. The analysis indicates:\n")
        positives = []
        if roi_metrics['roi_percentage'] > 15:
            positives.append(f"The projected ROI is positive at {format_percentage(roi_metrics['roi_percentage'])}")
        if roi_metrics['purchase_price'] <= roi_metrics['rule_70_max_price'] * 1.1:
            positives.append(f"The purchase price is within 10% of the 70% rule recommendation ({format_currency(roi_metrics['rule_70_max_price'])})")
        if ai_analysis and 'investment_rating' in ai_analysis and ai_analysis['investment_rating'].upper() in ['GOOD', 'EXCELLENT', 'HIGH']:
            positives.append(f"The AI analysis rates this as a {ai_analysis['investment_rating'].upper()} investment")
        
        for i, positive in enumerate(positives, 1):
            report.append(f"{i}. {positive}")
    else:
        report.append(f"This property does not appear to be a good investment at the current price of {format_currency(roi_metrics['purchase_price'])}. The analysis suggests:\n")
        
        issues = []
        if current_percentage > 75:
            issues.append(f"The purchase price is too high relative to the ARV ({format_percentage(current_percentage)} vs. recommended 70%)")
        if roi_metrics['roi_percentage'] < 0:
            issues.append(f"The projected ROI is negative ({format_percentage(roi_metrics['roi_percentage'])})")
        else:
            if roi_metrics['roi_percentage'] < 15:
                issues.append(f"The projected ROI is lower than the target of 15% ({format_percentage(roi_metrics['roi_percentage'])})")
        if roi_metrics['purchase_price'] > roi_metrics['rule_70_max_price'] * 1.1:
            issues.append(f"The 70% rule indicates a maximum purchase price of {format_currency(roi_metrics['rule_70_max_price'])}, which is significantly lower than the current price")
        
        for i, issue in enumerate(issues, 1):
            report.append(f"{i}. {issue}")
        
        # Recommendation
        if ai_analysis and 'suggested_max_price' in ai_analysis:
            report.append(f"\nIf you are interested in pursuing this property, consider negotiating the purchase price down to closer to the AI-suggested maximum of {format_currency(float(ai_analysis['suggested_max_price']))}, or preferably closer to the 70% rule recommendation of {format_currency(roi_metrics['rule_70_max_price'])}.")
        else:
            report.append(f"\nIf you are interested in pursuing this property, consider negotiating the purchase price down closer to the 70% rule recommendation of {format_currency(roi_metrics['rule_70_max_price'])}.")
    
    report.append(f"\n*This report was generated automatically by the Real Estate ARV Calculator application on {current_date}.*")
    
    # Join all lines
    report_content = "\n".join(report)
    
    # Write to file if output_path is provided
    if output_path:
        with open(output_path, 'w') as f:
            f.write(report_content)
        return output_path
    
    return report_content


def generate_json_report(results: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Generate a JSON report from the analysis results.
    
    Args:
        results: Dictionary containing analysis results
        output_path: Path to save the report, if None, the report is returned as a string
        
    Returns:
        The report content as a string if output_path is None, otherwise None
    """
    # Create a serializable copy of the results
    serializable_results = {
        "arv_result": results["arv_result"],
        "renovation_costs": results["renovation_costs"],
        "roi_metrics": results["roi_metrics"]
    }
    
    if results.get("ai_analysis"):
        serializable_results["ai_analysis"] = results["ai_analysis"]
        
    if results.get("valuation_data"):
        serializable_results["valuation_data"] = results["valuation_data"]
    
    # Convert to JSON
    json_content = json.dumps(serializable_results, indent=2)
    
    # Write to file if output_path is provided
    if output_path:
        with open(output_path, 'w') as f:
            f.write(json_content)
        return output_path
    
    return json_content