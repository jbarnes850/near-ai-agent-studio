#!/bin/bash

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Helper functions
section_header() {
    echo -e "\n${BLUE}${BOLD}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━"
}

show_progress() {
    local message=$1
    local duration=${2:-1}
    echo -n "$message..."
    sleep $duration
    echo -e " ${GREEN}✓${NC}"
}

print_logo() {
    echo '
███╗   ██╗███████╗ █████╗ ██████╗     ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗
████╗  ██║██╔════╝██╔══██╗██╔══██╗    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║
██╔██╗ ██║█████╗  ███████║██████╔╝    ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║
██║╚██╗██║██╔══╝  ██╔══██║██╔══██╗    ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║
██║ ╚████║███████╗██║  ██║██║  ██║    ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
                                                                                    
🤖 Multi-Agent Systems on NEAR
'
}

# Start script
print_logo

# Create log directory
mkdir -p logs
LOG_FILE="logs/quickstart_$(date +%s).log"
exec 3>&1 1>>${LOG_FILE} 2>&1

# 1. Environment Setup
section_header "🔧 Setting Up Environment"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create and activate virtual environment
show_progress "Creating Python virtual environment"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
show_progress "Installing dependencies"
pip install -r requirements.txt > /dev/null 2>&1
pip install -e . > /dev/null 2>&1

# 2. NEAR Account Setup
section_header "🔑 Setting Up NEAR Account"

if [ ! -f .env ]; then
    show_progress "Creating NEAR testnet account"
    ./scripts/create_near_wallet.sh
else
    echo "✅ NEAR account already configured"
fi

# 3. Verify Installation
section_header "🔍 Verifying Installation"

# Run verification script
if python3 scripts/verify_workshop.py > /dev/null 2>&1; then
    echo "✅ All components verified"
else
    echo "❌ Verification failed. Check logs for details."
    exit 1
fi

# Create example strategy
section_header "📝 Creating Example Strategy"
show_progress "Initializing example strategy"
./scripts/near-swarm init example-strategy > /dev/null 2>&1

# Run test strategy
section_header "🚀 Testing Default Strategy"
show_progress "Running strategy test"
if python3 -m near_swarm.examples.simple_strategy > /dev/null 2>&1; then
    echo "✅ Default strategy verified"
else
    echo "❌ Strategy test failed"
    echo "Please check the logs for details"
    exit 1
fi

# Success message
section_header "🎉 Setup Complete!"
echo "Your NEAR Swarm Intelligence environment is ready!"
echo ""
echo "Next steps:"
echo "1. Review the documentation in docs/"
echo "2. Try running: near-swarm init my-first-strategy"
echo "3. Explore example strategies in near_swarm/examples/"
echo ""
echo "For help, run: near-swarm --help"

# Restore stdout/stderr
exec 1>&3 3>&-               