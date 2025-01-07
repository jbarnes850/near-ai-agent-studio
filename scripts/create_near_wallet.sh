#!/bin/bash

# Exit on error
set -e

# Colors for better visibility
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔑 NEAR Wallet Creation Helper${NC}"
echo "This script will create a new NEAR testnet account for your agents."

# Function to generate a random string
generate_random_string() {
    # Generate 8 random characters
    LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom | head -c 8
}

# Function to check if near-cli is installed
check_near_cli() {
    if ! command -v near &> /dev/null; then
        echo -e "${CYAN}📦 Installing NEAR CLI...${NC}"
        if ! command -v npm &> /dev/null; then
            echo -e "${RED}❌ npm is required but not installed${NC}"
            echo "Please install Node.js and npm first:"
            echo "https://nodejs.org/en/download/"
            exit 1
        fi
        npm install -g near-cli
        echo -e "${GREEN}✓ NEAR CLI installed successfully${NC}"
    fi
}

# Function to create testnet account
create_testnet_account() {
    local account_id="$1"

    echo -e "\n${CYAN}🚀 Creating NEAR testnet account: $account_id${NC}"
    echo "This may take a few moments..."

    # Create a new key pair and account using NEAR CLI with faucet
    if NEAR_ENV=testnet near create-account "$account_id" \
        --useFaucet \
        --networkId testnet; then
        echo -e "${GREEN}✅ Account created successfully!${NC}"
        echo "Account ID: $account_id"
        echo "Network: testnet"
        echo "Initial Balance: Funded by testnet faucet"
    else
        echo -e "${RED}❌ Failed to create account${NC}"
        echo "Please try again or create an account manually at:"
        echo "https://wallet.testnet.near.org"
        exit 1
    fi
}

# Function to extract credentials
extract_credentials() {
    local account_id="$1"
    local creds_file=~/.near-credentials/testnet/"$account_id".json

    if [ -f "$creds_file" ]; then
        echo -e "\n${CYAN}📝 Extracting credentials...${NC}"
        
        # Extract account ID and private key
        local extracted_account_id=$(jq -r '.account_id' "$creds_file")
        local private_key=$(jq -r '.private_key' "$creds_file")

        # Update .env file
        if [ -f .env ]; then
            # Use portable sed syntax that works on both Linux and macOS
            sed -i.bak "s|NEAR_ACCOUNT_ID=.*|NEAR_ACCOUNT_ID=$extracted_account_id|" .env && rm -f .env.bak
            sed -i.bak "s|NEAR_PRIVATE_KEY=.*|NEAR_PRIVATE_KEY=$private_key|" .env && rm -f .env.bak
            echo -e "${GREEN}✅ Credentials updated in .env file${NC}"
        else
            echo -e "${CYAN}⚠️  .env file not found. Creating with credentials...${NC}"
            cp .env.example .env
            sed -i.bak "s|NEAR_ACCOUNT_ID=.*|NEAR_ACCOUNT_ID=$extracted_account_id|" .env && rm -f .env.bak
            sed -i.bak "s|NEAR_PRIVATE_KEY=.*|NEAR_PRIVATE_KEY=$private_key|" .env && rm -f .env.bak
        fi

        echo -e "\n${GREEN}✅ Credentials saved:${NC}"
        echo "• Account ID: $extracted_account_id"
        echo "• Credentials file: $creds_file"
        
        # Verify the account
        echo -e "\n${CYAN}🔍 Verifying account...${NC}"
        if NEAR_ENV=testnet near state "$extracted_account_id" &>/dev/null; then
            echo -e "${GREEN}✅ Account verified and active${NC}"
        else
            echo -e "${RED}❌ Account verification failed${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Credentials file not found${NC}"
        exit 1
    fi
}

main() {
    echo -e "\n${CYAN}🔧 Checking dependencies...${NC}"
    
    # Check dependencies
    check_near_cli

    # Generate unique account name
    local timestamp=$(date +%s)
    local random_string=$(generate_random_string)
    local account_id="agent-${random_string}-${timestamp}.testnet"

    # Create account
    create_testnet_account "$account_id"

    # Extract and save credentials
    extract_credentials "$account_id"

    echo -e "\n${GREEN}🎉 NEAR Wallet Setup Complete!${NC}"
    echo "Your agent's NEAR wallet is ready to use."
    echo -e "\n${CYAN}Next Steps:${NC}"
    echo "1. Review your .env file"
    echo "2. Run './scripts/verify_setup.sh' to verify everything"
    echo "3. Start developing your strategy!"
}

# Run main function
main
