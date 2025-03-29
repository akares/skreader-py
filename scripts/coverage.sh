#!/bin/bash
set -e

echo "Running tests with coverage..."
python -m pytest --cov=skreader --cov-report=term --cov-report=html

echo -e "\nCoverage report generated in htmlcov/index.html"
