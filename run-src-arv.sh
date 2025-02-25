#!/bin/bash

# Navigate to the project directory
cd /Users/rome/code/claudecodev1

# Activate the virtual environment
source venv/bin/activate

# Add the src directory to the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the application with any arguments passed to this script
python -m src.realestate_arv_app.main "$@"

# Print usage instructions if no arguments are provided
if [ $# -eq 0 ]; then
    echo ""
    echo "Usage examples:"
    echo "  ./run-src-arv.sh --sample                                        # Run with sample data"
    echo "  ./run-src-arv.sh --address \"123 Main St, Anytown, CA 12345\"      # Analyze specific address"
    echo "  ./run-src-arv.sh --sample --json                                 # Output as JSON"
    echo "  ./run-src-arv.sh --address \"50 Main St, New York, NY\" --report   # Generate detailed report"
    echo "  ./run-src-arv.sh --address \"123 Main St\" --report --output \"my_report.md\"  # Save report to file"
    echo "  ./run-src-arv.sh --help                                          # Show all options"
    echo ""
fi
