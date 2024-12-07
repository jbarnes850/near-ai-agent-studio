#!/bin/bash

# Exit on error
set -e

clear

# Terminal width (default 80 if can't be detected)
TERM_WIDTH=$(tput cols 2>/dev/null || echo 80)

# Function to center text
center_text() {
    local text="$1"
    local width="${2:-$TERM_WIDTH}"
    local padding=$(( (width - ${#text}) / 2 ))
    printf "%${padding}s%s%${padding}s\n" "" "$text" ""
}

# NEAR brand color (blue)
echo -e "\033[38;5;75m"

# Top border
center_text "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Empty line
echo ""

# ASCII art logo (using heredoc for reliable formatting)
cat << 'EOF'
                 ███    ██ ███████  █████  ██████  
                 ████   ██ ██      ██   ██ ██   ██ 
                 ██ ██  ██ █████   ███████ ██████  
                 ██  ██ ██ ██      ██   ██ ██   ██ 
                 ██   ████ ███████ ██   ██ ██   ██ 
EOF

echo ""

cat << 'EOF'
            ███████ ██     ██  █████  ██████  ███    ███
            ██      ██     ██ ██   ██ ██   ██ ████  ████
            ███████ ██  █  ██ ███████ ██████  ██ ████ ██
                 ██ ██ ███ ██ ██   ██ ██   ██ ██  ██  ██
            ███████  ███ ███  ██   ██ ██   ██ ██      ██
EOF

echo ""
center_text "AI Swarm Intelligence Framework for NEAR Protocol"
echo ""

# Reset color
echo -e "\033[0m"

# Bottom border
center_text "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Warning section in yellow
echo ""
echo -e "\033[1;33m$(center_text "⚠️  TESTNET MODE - For Development Only")\033[0m"
center_text "This template runs on NEAR testnet for safe development and testing."
center_text "Do not use real funds or deploy to mainnet without thorough testing."

# Bottom border
center_text "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to show progress with centered text
show_progress() {
    local message="$1"
    local duration="$2"
    local width=50
    local progress=0
    
    # Center the progress bar
    local total_width=$(( ${#message} + width + 3 ))  # +3 for space and brackets
    local padding=$(( (TERM_WIDTH - total_width) / 2 ))
    
    printf "%${padding}s%s " "" "$message"
    while [ $progress -lt $width ]; do
        echo -n "▱"
        ((progress++))
    done
    echo -ne "\r%${padding}s%s " "" "$message"
    progress=0
    while [ $progress -lt $width ]; do
        echo -n "▰"
        sleep $(bc <<< "scale=3; $duration/$width")
        ((progress++))
    done
    echo ""
}

# Section headers in NEAR blue
section_header() {
    echo ""
    echo -e "\033[38;5;75m$1\033[0m"
    echo "$(center_text "━━━━━━━━━━━━━━━━━━━━━")"
}

section_header "🔍 Checking Prerequisites"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3 and try again."
    exit 1
else
    python_version=$(python3 --version)
    center_text "✅ $python_version found"
fi

section_header "🛠️  Setting Up Development Environment"

# Create virtual environment
center_text "📦 Creating Python virtual environment..."
show_progress "Creating virtual environment" 2
python3 -m venv venv
source venv/bin/activate
center_text "✅ Virtual environment created and activated"

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
show_progress "Installing required packages" 3
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

# Copy environment template if not exists
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  Setting up environment configuration..."
    show_progress "Creating environment file" 1
    cp .env.example .env
    echo "✅ Environment file created"
fi

echo ""
echo "🔑 NEAR Wallet Setup (Testnet)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if NEAR account exists, if not create one
if [ ! -f ~/.near-credentials/testnet/*.json ]; then
    echo "Creating new NEAR testnet wallet..."
    show_progress "Setting up NEAR wallet" 3
    ./scripts/create_near_wallet.sh
else
    echo "✅ Existing NEAR testnet wallet found"
    # Update .env with existing credentials
    CREDS_FILE=$(ls ~/.near-credentials/testnet/*.json | head -n 1)
    if [ -f "$CREDS_FILE" ]; then
        ACCOUNT_ID=$(jq -r '.account_id' "$CREDS_FILE")
        PRIVATE_KEY=$(jq -r '.private_key' "$CREDS_FILE")
        
        # Update .env file
        sed -i '' "s/NEAR_ACCOUNT_ID=.*/NEAR_ACCOUNT_ID=$ACCOUNT_ID/" .env
        sed -i '' "s/NEAR_PRIVATE_KEY=.*/NEAR_PRIVATE_KEY=$PRIVATE_KEY/" .env
        echo "✅ Credentials updated in environment file"
    fi
fi

echo ""
echo "🧪 Running Tests"
echo "━━━━━━━━━━━━━"
show_progress "Running test suite" 2
python -m pytest tests/ > /dev/null 2>&1
echo "✅ All tests passed"

echo ""
echo "📝 Creating Example Strategy"
echo "━━━━━━━━━━━━━━━━━━━━━━"
show_progress "Initializing example strategy" 2
./scripts/near-swarm init arbitrage --name example-strategy > /dev/null 2>&1
echo "✅ Example strategy created"

echo ""
echo "🎉 Setup Complete!"
echo "━━━━━━━━━━━━━━"
echo "Your development environment is ready:"
echo "✅ Python virtual environment"
echo "✅ All dependencies installed"
echo "✅ NEAR testnet wallet configured"
echo "✅ Example strategy created"
echo ""
echo "⚠️  Remember: This is a testnet environment for development"
echo "   Do not use real funds or deploy to mainnet without thorough testing"
echo ""

# Interactive CLI tutorial
echo "Would you like to try the NEAR Swarm CLI? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    clear
    echo "🚀 Welcome to the NEAR Swarm CLI Tutorial"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Let's create and run a simple arbitrage strategy."
    echo ""
    echo "Press Enter to continue..."
    read -r
    
    # Show available commands
    echo "1️⃣ First, let's see what commands are available:"
    echo ""
    ./scripts/near-swarm --help
    echo ""
    echo "Press Enter to continue..."
    read -r
    
    # Create new strategy
    echo "2️⃣ Let's create a new arbitrage strategy:"
    echo ""
    ./scripts/near-swarm init arbitrage --name my-first-strategy
    echo ""
    echo "Press Enter to continue..."
    read -r
    
    # Show strategy files
    echo "3️⃣ Let's look at what was created:"
    echo ""
    ls -la my-first-strategy
    echo ""
    echo "Press Enter to continue..."
    read -r
    
    # List strategies
    echo "4️⃣ Now let's list all available strategies:"
    echo ""
    ./scripts/near-swarm list
    echo ""
    echo "Press Enter to continue..."
    read -r
    
    # Show how to run
    echo "5️⃣ To run your strategy, use these commands:"
    echo ""
    echo "cd my-first-strategy"
    echo "./scripts/near-swarm run"
    echo ""
    echo "That's it! You're ready to start developing your own strategies."
else
    echo ""
    echo "📋 Quick Reference:"
    echo "1. Create strategy:  ./scripts/near-swarm init arbitrage --name my-strategy"
    echo "2. List strategies:  ./scripts/near-swarm list"
    echo "3. Run strategy:     ./scripts/near-swarm run"
    echo "4. Monitor status:   ./scripts/near-swarm monitor"
    echo ""
fi

echo "📚 Resources:"
echo "- Documentation: docs/"
echo "- Examples: examples/"
echo "- Support: https://discord.gg/near" 