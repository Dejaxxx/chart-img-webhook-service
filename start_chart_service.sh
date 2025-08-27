#!/bin/bash
# Start Chart-IMG Service - Production Version

echo "Chart-IMG Service Launcher - Production"
echo "======================================="

# Navigate to the production directory
cd /Users/abdulaziznahas/trading-factory/chart-img-production

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r chart_requirements.txt

# Create output directory
mkdir -p /Users/abdulaziznahas/chart-img-outputs

# Kill any existing service on port 5002
echo "Checking for existing service on port 5002..."
lsof -ti:5002 | xargs kill -9 2>/dev/null

# Start the service
echo "Starting Chart-IMG Service v7.0 (Hybrid Production)..."
python3 chart_img_service_v7_hybrid.py
