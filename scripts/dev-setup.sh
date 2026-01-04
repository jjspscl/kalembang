#!/bin/bash
# Quick development setup script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "========================================"
echo "  Kalembang Dev Setup"
echo "========================================"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi
echo "✓ Python 3 found"

# Check for pipenv
if ! command -v pipenv &> /dev/null; then
    echo "⚠️  pipenv not found. Installing..."
    pip install --user pipenv
fi
echo "✓ pipenv found"

# Check for Bun
if ! command -v bun &> /dev/null; then
    echo "⚠️  Bun not found. Install it with: curl -fsSL https://bun.sh/install | bash"
else
    echo "✓ Bun found"
fi

# Setup API
echo ""
echo "Setting up API with pipenv..."
cd api
pipenv install -r requirements.txt
echo "✓ API dependencies installed"
cd ..

# Setup Client
echo ""
echo "Setting up Client with bun..."
cd client
if command -v bun &> /dev/null; then
    bun install
    echo "✓ Client dependencies installed"
else
    echo "⚠️  Skipping client setup (Bun not installed)"
fi
cd ..

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To run the API (mock mode):"
echo "  cd api && ./scripts/dev-run.sh"
echo "  or: cd api && pipenv run uvicorn kalembang.main:app --reload"
echo ""
echo "To run the client:"
echo "  cd client && bun run dev"
echo ""
