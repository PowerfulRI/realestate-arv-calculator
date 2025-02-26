from flask import Flask, render_template, request, jsonify
import sys
import os
import json
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from realestate_arv_app.models.property import Property
from realestate_arv_app.api.property_service import PropertyService
from realestate_arv_app.analysis.comps_analyzer import CompsAnalyzer
from realestate_arv_app.analysis.renovation_calculator import RenovationCalculator
from realestate_arv_app.utils.report_generator import ReportGenerator

app = Flask(__name__)

# Create templates directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_property():
    data = request.form
    address = data.get('address')
    
    if not address:
        return jsonify({"error": "Address is required"}), 400
    
    try:
        # Initialize services
        property_service = PropertyService()
        comps_analyzer = CompsAnalyzer()
        renovation_calculator = RenovationCalculator()
        
        # Get property data
        property_data = property_service.get_property_by_address(address)
        
        # Analyze comparables
        comps = comps_analyzer.find_comparable_properties(property_data)
        arv = comps_analyzer.calculate_arv(property_data, comps)
        
        # Calculate renovation costs
        renovation_costs = renovation_calculator.estimate_renovation_costs(property_data)
        
        # Generate report
        report_generator = ReportGenerator()
        report = report_generator.generate_report(property_data, comps, arv, renovation_costs)
        
        # Return results
        return jsonify({
            "property": property_data.to_dict() if property_data else {},
            "arv": arv,
            "renovation_costs": renovation_costs,
            "report": report
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sample', methods=['GET'])
def analyze_sample():
    try:
        # Use sample data
        sample_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'report_50_main_st_ny.json')
        
        with open(sample_path, 'r') as f:
            sample_data = json.load(f)
            
        return jsonify(sample_data)
    except Exception as e:
        return jsonify({"error": f"Error loading sample data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)