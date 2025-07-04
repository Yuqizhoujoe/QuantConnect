#!/bin/bash

# Options Backtesting Strategy - Quick Setup Script
# This script sets up the complete project environment

set -e  # Exit on any error

echo "🚀 Setting up Options Backtesting Strategy Project"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "lean.json" ]; then
    print_error "lean.json not found. Please run this script from the project root directory."
    exit 1
fi

# Check if LEAN CLI is installed
if ! command -v lean &> /dev/null; then
    print_warning "LEAN CLI not found in PATH. Attempting to add to PATH..."
    export PATH="/Library/Frameworks/Python.framework/Versions/3.10/bin:$PATH"
    
    if ! command -v lean &> /dev/null; then
        print_error "LEAN CLI not found. Please install it first: pip install lean"
        exit 1
    fi
fi

print_success "LEAN CLI found: $(lean --version)"

# Check if project directory exists
if [ ! -d "Options Backtesting Strategy" ]; then
    print_error "Project directory not found. Please ensure the project is properly set up."
    exit 1
fi

# Navigate to project directory
cd "Options Backtesting Strategy"

print_status "Installing project dependencies..."
if pip install -r requirements.txt; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

print_status "Validating project structure..."
if python manage.py validate; then
    print_success "Project structure is valid"
else
    print_error "Project validation failed"
    exit 1
fi

print_status "Showing project information..."
python manage.py info

echo ""
echo "🎯 Setup Complete! Here's what you can do next:"
echo ""
echo "📊 Run a local backtest:"
echo "   lean backtest \"Options Backtesting Strategy\""
echo ""
echo "☁️ Run a cloud backtest:"
echo "   lean cloud push \"Options Backtesting Strategy\""
echo "   lean cloud backtest \"Options Backtesting Strategy\""
echo ""
echo "🔧 Use the management script:"
echo "   python manage.py backtest          # Run local backtest"
echo "   python manage.py cloud-backtest    # Run cloud backtest"
echo "   python manage.py create-variant --name \"Apple Strategy\" --ticker AAPL"
echo ""
echo "📚 Read the documentation:"
echo "   cat README.md"
echo ""
echo "⚠️ Important Notes:"
echo "   - Ensure your QuantConnect account has options data access"
echo "   - The strategy is configured for AVGO (Broadcom) by default"
echo "   - Modify main.py to change the underlying stock or parameters"
echo "   - This is for educational purposes only - consult a financial advisor"
echo ""

# Ask if user wants to run a backtest
read -p "Would you like to run a local backtest now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Running local backtest..."
    lean backtest "Options Backtesting Strategy"
fi

print_success "Setup complete! Happy backtesting! 🎉" 