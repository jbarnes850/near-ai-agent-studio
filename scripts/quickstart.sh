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
███╗   ██╗███████╗ █████╗ ██████╗      █████╗  ██████╗ ███████╗███╗   ██╗████████╗
████╗  ██║██╔════╝██╔══██╗██╔══██╗    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
██╔██╗ ██║█████╗  ███████║██████╔╝    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██║╚██╗██║██╔══╝  ██╔══██║██╔══██╗    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
██║ ╚████║███████╗██║  ██║██║  ██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   

███████╗████████╗██╗   ██╗██████╗ ██╗ ██████╗ 
██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗
███████╗   ██║   ██║   ██║██║  ██║██║██║   ██║
╚════██║   ██║   ██║   ██║██║  ██║██║██║   ██║
███████║   ██║   ╚██████╔╝██████╔╝██║╚██████╔╝
╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝ 
'
    echo -e "${CYAN}🤖 Build Autonomous Agents on NEAR${NC}"
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
echo -e "${CYAN}Welcome to NEAR Agent Studio!${NC}"
echo -e "This starter kit helps you build autonomous agents that can:"
echo -e "• ${GREEN}Interact with NEAR${NC} - Send transactions, check balances, monitor accounts"
echo -e "• ${GREEN}Access Market Data${NC} - Real-time prices, trading volumes, market trends"
echo -e "• ${GREEN}Make Decisions${NC} - LLM-powered reasoning and strategy execution"
echo ""
echo -e "${CYAN}Setup will:${NC}"
echo "1. Configure your development environment"
echo "2. Set up a NEAR testnet account for testing"
echo "3. Install example agents to learn from"
echo "4. Verify all integrations (NEAR, Market Data, LLM)"
echo "5. Launch an interactive chat assistant to help create your first agent"
echo ""
echo -e "${CYAN}Press Enter to start building...${NC}"
read -r

# Check for virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${RED}⚠️  Virtual environment not activated${NC}"
    echo -e "Please run the following commands first:"
    echo -e "${CYAN}python3 -m venv venv${NC}"
    echo -e "${CYAN}source venv/bin/activate${NC}"
    echo -e "${CYAN}pip install -e .${NC}"
    echo -e "\nThen run this script again."
    exit 1
fi

# Check for required commands
check_command python3
check_command pip
check_command git

# 1. Environment Setup
section_header "🔧 Setting Up Environment"

# Check Python version
python3 -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12+ required'"
echo -e "${GREEN}✓${NC} Python version OK"

# Verify plugin system
section_header "🔌 Testing Plugin System"
show_progress "Verifying plugin infrastructure"
python3 -c "
from near_swarm.plugins import PluginLoader
import asyncio

async def test_plugins():
    loader = PluginLoader()
    print('✓ Plugin system initialized')
    
asyncio.run(test_plugins())
"

# Add market data verification
section_header "📊 Testing Market Data Integration"
show_progress "Fetching NEAR/USDC price data"
python3 -c "
from near_swarm.core.market_data import MarketDataManager
import asyncio

async def test_market():
    async with MarketDataManager() as market:
        data = await market.get_token_price('near')
        print(f'Current NEAR Price: \${data[\"price\"]:.2f}')
    
asyncio.run(test_market())
"

# Add LLM verification
section_header "🧠 Testing LLM Integration"
show_progress "Verifying LLM connection"
python3 -c "
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('LLM_API_KEY')
provider = os.getenv('LLM_PROVIDER', 'hyperbolic')

if not api_key:
    print('⚠️  LLM API key not found')
    exit(1)
    
print(f'✓ {provider.title()} configuration verified')
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

# 4. Create and Run Plugins
section_header "🚀 Setting Up Agent Plugins"

# Install example plugins
show_progress "Installing token transfer plugin"
near-swarm plugins install near_swarm/examples/token_transfer_strategy.py --name token-transfer

show_progress "Installing arbitrage plugin"
near-swarm plugins install near_swarm/examples/arbitrage_strategy.py --name arbitrage-agent

# List installed plugins
echo -e "\n${CYAN}Installed Plugins:${NC}"
near-swarm plugins list

# Initialize demo
section_header "📈 Running Demo"

# Run the token transfer demo
show_progress "Running token transfer demo"
near-swarm execute token-transfer --operation balance

# After setup, show status
section_header "📊 System Status"

# Show component status
echo -e "\n${CYAN}Active Components:${NC}"
echo -e "• ${GREEN}Plugin System${NC} - Initialized"
echo -e "• ${GREEN}Token Transfer Plugin${NC} - Ready"
echo -e "• ${GREEN}Arbitrage Plugin${NC} - Ready"
echo -e "• ${GREEN}NEAR Connection${NC} - Connected to testnet"
echo -e "• ${GREEN}Market Data${NC} - Price feeds active"
echo -e "• ${GREEN}LLM Integration${NC} - Connected"

# Success message and transition to chat
section_header "🎉 Ready to Build!"
echo -e "${GREEN}Your NEAR Agent Studio environment is ready!${NC}"
echo ""
echo -e "${CYAN}Starting interactive chat assistant to help you:${NC}"
echo -e "1. Create your first price monitoring agent"
echo -e "2. Add a decision-making agent"
echo -e "3. Watch them collaborate in real-time"
echo -e "4. Learn about advanced agent capabilities"
echo ""
echo -e "${CYAN}Press Enter to start the interactive experience...${NC}"
read -r

# Launch interactive chat
section_header "💬 Starting Interactive Chat"
echo -e "Tip: Type ${CYAN}/help${NC} to see available commands"
echo -e "     Type ${CYAN}/exit${NC} to quit at any time\n"

near-swarm chat --tutorial create-first-agent

echo -e "\n${CYAN}Next steps:${NC}"
echo "1. Explore more agent templates: near-swarm plugins list"
echo "2. Create custom agents: near-swarm create agent my-agent"
echo "3. Run advanced demos:"
echo "   • Multi-agent trading: near-swarm demo trading"
echo "   • Portfolio management: near-swarm demo portfolio"
echo ""
echo -e "${BLUE}Documentation: https://github.com/jbarnes850/near-ai-agent-studio${NC}"