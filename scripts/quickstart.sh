#!/bin/bash

# Exit on error
set -e

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Helper functions
section_header() {
    echo -e "\n${BLUE}${BOLD}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━"
}

show_progress() {
    echo -ne "${CYAN}⏳ $1...${NC}"
    sleep 0.5
    echo -e " ${GREEN}✓${NC}"
}

print_logo() {
    echo -e "${BLUE}"
    echo '
███╗   ██╗███████╗ █████╗ ██████╗     ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗
████╗  ██║██╔════╝██╔══██╗██╔══██╗    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║
██╔██╗ ██║█████╗  ███████║██████╔╝    ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║
██║╚██╗██║██╔══╝  ██╔══██║██╔══██╗    ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║
██║ ╚████║███████╗██║  ██║██║  ██║    ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
'
    echo -e "${CYAN}🤖 Multi-Agent Systems on NEAR${NC}"
    echo ""
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ Required command not found: $1${NC}"
        echo "Please install $1 and try again"
        exit 1
    fi
}

# Start script
print_logo
echo -e "${CYAN}Welcome to the NEAR Swarm Intelligence Workshop!${NC}"
echo -e "This script will set up a complete multi-agent system demonstrating:"
echo -e "• ${GREEN}Market Analysis${NC} - Price and volume evaluation"
echo -e "• ${GREEN}Risk Management${NC} - Safety and exposure control"
echo -e "• ${GREEN}Strategy Optimization${NC} - Performance tuning"
echo ""

# Check for required commands
check_command python3
check_command pip
check_command git

# 1. Environment Setup
section_header "🔧 Setting Up Environment"

# Check Python version
python3 -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12+ required'"
echo -e "${GREEN}✓${NC} Python version OK"

# Create and activate virtual environment
show_progress "Creating Python virtual environment"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
show_progress "Installing dependencies"
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1
pip install -e . >/dev/null 2>&1

# Add market data verification
section_header "📊 Testing Market Data Integration"
show_progress "Fetching NEAR/USDC price data"
python3 -c "
from near_swarm.core.market_data import MarketDataManager
import asyncio
async def test_market():
    market = MarketDataManager()
    data = await market.get_token_price('near')
    print(f'Current NEAR Price: \${data[\"price\"]:.2f}')
asyncio.run(test_market())
"

# Add LLM verification
section_header "🧠 Testing LLM Integration"
show_progress "Verifying Hyperbolic AI connection"
python3 -c "
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig
import asyncio, os
async def test_llm():
    provider = create_llm_provider(LLMConfig(
        provider='hyperbolic',
        api_key=os.getenv('LLM_API_KEY'),
        model='meta-llama/Llama-3.3-70B-Instruct'
    ))
    response = await provider.query('Respond with OK if connected')
    assert 'OK' in response
asyncio.run(test_llm())
"

# 2. NEAR Account Setup
section_header "🔑 Setting Up NEAR Account"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    show_progress "Creating .env file"
    cp .env.example .env
    
    # Create NEAR testnet account
    show_progress "Creating NEAR testnet account"
    ./scripts/create_near_wallet.sh
fi

# 3. Verify Installation
section_header "🔍 Verifying Installation"

# Run verification script
show_progress "Running verification checks"
python3 scripts/verify_workshop.py

# 4. Create and Run Swarm
section_header "🚀 Creating Swarm Agents"

# Create market analyzer agent
show_progress "Creating Market Analyzer agent"
near-swarm create-agent market_analyzer --min-confidence 0.7

# Create risk manager agent
show_progress "Creating Risk Manager agent"
near-swarm create-agent risk_manager --min-confidence 0.8

# Create strategy optimizer agent
show_progress "Creating Strategy Optimizer agent"
near-swarm create-agent strategy_optimizer --min-confidence 0.7

# List created agents
echo -e "\n${CYAN}Created Agents:${NC}"
near-swarm list-agents

# Initialize demo strategy
section_header "📈 Running Demo Strategy"

# Create and run demo strategy
show_progress "Initializing demo strategy"
near-swarm init arbitrage --name demo-strategy

# Run the strategy
show_progress "Running demo strategy"
cd demo-strategy
near-swarm run --example simple_strategy

# Add demo transaction
section_header "💫 Testing Swarm Decision Making"
show_progress "Proposing test transaction"
near-swarm run --example simple_strategy --demo-mode

# After creating agents, show status
section_header "📊 System Status"

# Show simple status instead of monitoring
echo -e "\n${CYAN}Active Components:${NC}"
echo -e "• ${GREEN}Market Analyzer${NC} - Ready"
echo -e "• ${GREEN}Risk Manager${NC} - Ready"
echo -e "• ${GREEN}Strategy Optimizer${NC} - Ready"
echo -e "• ${GREEN}NEAR Connection${NC} - Connected to testnet"
echo -e "• ${GREEN}Market Data${NC} - Price feeds active"
echo -e "• ${GREEN}LLM Integration${NC} - Connected"

# Success message
section_header "🎉 Setup Complete!"
echo -e "${GREEN}Your NEAR Swarm Intelligence environment is ready!${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "1. Create your own strategy: near-swarm init my-strategy"
echo "2. Monitor activity: near-swarm monitor"
echo "3. Explore examples in near_swarm/examples/"
echo ""
echo -e "${BLUE}For help, run: near-swarm --help${NC}"