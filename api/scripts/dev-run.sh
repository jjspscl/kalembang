#!/bin/bash
# Kalembang Development Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(dirname "$SCRIPT_DIR")"

cd "$API_DIR"

# Ensure pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo "❌ pipenv not found. Install it with: pip install pipenv"
    exit 1
fi

# Install dependencies if needed
if [ ! -f "Pipfile.lock" ]; then
    echo "Installing dependencies with pipenv..."
    pipenv install -r requirements.txt
fi

# Check if we're on Orange Pi (has wiringOP)
if ! command -v gpio &> /dev/null; then
    echo ""
    echo "⚠️  wiringOP 'gpio' command not found."
    echo "   Running with MOCK GPIO backend for development."
    echo ""
    export KALEMBANG_MOCK_GPIO=1
fi

# Run development server
echo ""
echo "Starting Kalembang API server..."
echo "API will be available at http://0.0.0.0:8088"
echo ""

pipenv run uvicorn kalembang.main:app --host 0.0.0.0 --port 8088 --reload
