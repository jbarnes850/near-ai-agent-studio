#!/bin/bash

# Exit on error
set -e

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
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

check_python_version() {
    if command -v python3.12 &> /dev/null; then
        local python_version=$(python3.12 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        echo -e "${GREEN}✓ Python $python_version detected${NC}"
        return 0
    elif command -v python3 &> /dev/null; then
        local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if (( $(echo "$python_version >= 3.12" | bc -l) )); then
            echo -e "${GREEN}✓ Python $python_version detected${NC}"
            return 0
        fi
    fi
    return 1
}

install_python() {
    local os_type=$(uname)
    echo -e "${YELLOW}Python 3.12+ is required. Attempting to install...${NC}"
    
    case "$os_type" in
        "Darwin") # macOS
            if ! command -v brew &> /dev/null; then
                echo -e "${YELLOW}Installing Homebrew...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            echo -e "${YELLOW}Installing Python 3.12 via Homebrew...${NC}"
            if brew list python@3.12 &>/dev/null; then
                brew unlink python@3.12 && brew link python@3.12
                # Add Python 3.12 to PATH
                export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"
            else
                brew install python@3.12
                brew link python@3.12
                # Add Python 3.12 to PATH
                export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"
            fi
            ;;
        "Linux")
            if command -v apt-get &> /dev/null; then
                echo -e "${YELLOW}Installing Python 3.12 via apt...${NC}"
                sudo add-apt-repository ppa:deadsnakes/ppa -y
                sudo apt-get update
                sudo apt-get install -y python3.12 python3.12-venv
            elif command -v dnf &> /dev/null; then
                echo -e "${YELLOW}Installing Python 3.12 via dnf...${NC}"
                sudo dnf install -y python3.12
            else
                echo -e "${RED}Unsupported Linux distribution. Please install Python 3.12+ manually.${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}Unsupported operating system. Please install Python 3.12+ manually.${NC}"
            exit 1
            ;;
    esac
    
    # Verify installation
    if ! check_python_version; then
        echo -e "${RED}Failed to install Python 3.12+. Please install it manually.${NC}"
        exit 1
    fi
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

# 1. Environment Setup
section_header "🔧 Setting Up Environment"

# Check and install Python 3.12+ if needed
if ! check_python_version; then
    install_python
fi

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    show_progress "Creating virtual environment"
    python3.12 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
show_progress "Installing dependencies"
pip install --upgrade pip
pip install -e .

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
import asyncio

async def verify_llm():
    load_dotenv()
    api_key = os.getenv('LLM_API_KEY')
    provider = os.getenv('LLM_PROVIDER', 'hyperbolic')
    model = os.getenv('LLM_MODEL', 'meta-llama/llama-3.3-70B-instruct')

    if not api_key:
        print('⚠️  LLM API key not found')
        exit(1)
    
    try:
        config = LLMConfig(
            provider=provider,
            api_key=api_key,
            model=model
        )
        llm = create_llm_provider(config)
        response = await llm.query('Hello! Please respond with OK to verify the connection.')
        if 'OK' in response.upper():
            print(f'✓ {provider.title()} LLM connection verified')
        else:
            print(f'⚠️  Unexpected response from LLM')
            exit(1)
    except Exception as e:
        print(f'⚠️  LLM verification failed: {str(e)}')
        exit(1)
    finally:
        if llm:
            await llm.close()

asyncio.run(verify_llm())
"

# 2. NEAR Account Setup
section_header "🔑 Setting Up NEAR Account"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    show_progress "Creating .env file"
    cp .env.example .env
    
    # Create NEAR testnet account
    show_progress "Creating NEAR testnet account"
    if ! ./scripts/create_near_wallet.sh; then
        echo -e "${RED}Failed to create NEAR testnet account. Please try again or create one manually at https://wallet.testnet.near.org${NC}"
        exit 1
    fi
fi

# Verify NEAR configuration
if ! grep -q "NEAR_ACCOUNT_ID=" .env || ! grep -q "NEAR_PRIVATE_KEY=" .env; then
    echo -e "${RED}⚠️  NEAR account configuration not found in .env${NC}"
    echo "Please add your NEAR account details to .env:"
    echo "NEAR_ACCOUNT_ID=your-account.testnet"
    echo "NEAR_PRIVATE_KEY=your-private-key"
    exit 1
fi

# 3. Verify Installation
section_header "🔍 Verifying Installation"

# Run verification script
show_progress "Running verification checks"
if ! python3 scripts/verify_workshop.py; then
    echo -e "${RED}⚠️  Verification failed. Please check the error messages above.${NC}"
    exit 1
fi

# 4. Create and Run Plugins
section_header "🚀 Setting Up Agent Plugins"

# Install example plugins
show_progress "Installing token transfer plugin"
if ! python -m near_swarm.cli plugins install near_swarm/examples/token_transfer_strategy.py --name token-transfer; then
    echo -e "${RED}⚠️  Failed to install token transfer plugin${NC}"
    exit 1
fi

show_progress "Installing arbitrage plugin"
if ! python -m near_swarm.cli plugins install near_swarm/examples/arbitrage_strategy.py --name arbitrage-agent; then
    echo -e "${RED}⚠️  Failed to install arbitrage plugin${NC}"
    exit 1
fi

# List installed plugins
echo -e "\n${CYAN}Installed Plugins:${NC}"
python -m near_swarm.cli plugins list

# Initialize demo
section_header "📈 Running Demo"

# Run the token transfer demo
show_progress "Running token transfer demo"
if ! python -m near_swarm.cli execute token-transfer --operation balance; then
    echo -e "${RED}⚠️  Token transfer demo failed${NC}"
    exit 1
fi

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

python -m near_swarm.cli chat --tutorial create-first-agent

echo -e "\n${CYAN}Next steps:${NC}"
echo "1. Explore more agent templates: python -m near_swarm.cli plugins list"
echo "2. Create custom agents: python -m near_swarm.cli create agent my-agent"
echo "3. Run advanced demos:"
echo "   • Multi-agent trading: python -m near_swarm.cli demo trading"
echo "   • Portfolio management: python -m near_swarm.cli demo portfolio"
echo ""
echo -e "${BLUE}Documentation: https://github.com/jbarnes850/near-ai-agent-studio${NC}"