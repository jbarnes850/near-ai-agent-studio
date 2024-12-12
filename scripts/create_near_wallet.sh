#!/bin/bash

# Exit on error
set -e

echo "🔑 NEAR Wallet Creation Helper"

# Function to generate a random string
generate_random_string() {
    # Generate 8 random characters
    LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom | head -c 8
}

# Function to check if near-cli is installed
check_near_cli() {
    if ! command -v near &> /dev/null; then
        echo "📦 Installing NEAR CLI..."
        npm install -g near-cli
    fi
}

# Function to create testnet account
create_testnet_account() {
    local account_id="$1"

    echo "🚀 Creating NEAR testnet account: $account_id"

    # Create a new key pair and account using NEAR CLI with faucet
    NEAR_ENV=testnet near create-account "$account_id" \
        --useFaucet \
        --networkId testnet

    echo "✅ Account created successfully!"
    echo "Account ID: $account_id"
    echo "Network: testnet"
    echo "Initial Balance: Funded by testnet faucet"
}

# Function to extract credentials
extract_credentials() {
    local account_id="$1"
    local creds_file=~/.near-credentials/testnet/"$account_id".json

    if [ -f "$creds_file" ]; then
        # Extract account ID and private key
        local extracted_account_id=$(jq -r '.account_id' "$creds_file")
        local private_key=$(jq -r '.private_key' "$creds_file")

        # Update .env file
        if [ -f .env ]; then
            # Use portable sed syntax that works on both Linux and macOS
            sed -i.bak "s|NEAR_ACCOUNT_ID=.*|NEAR_ACCOUNT_ID=$extracted_account_id|" .env && rm -f .env.bak
            sed -i.bak "s|NEAR_PRIVATE_KEY=.*|NEAR_PRIVATE_KEY=$private_key|" .env && rm -f .env.bak
            echo "✅ Credentials updated in .env file"
        else
            echo "⚠️  .env file not found. Creating with credentials..."
            cp .env.example .env
            sed -i.bak "s|NEAR_ACCOUNT_ID=.*|NEAR_ACCOUNT_ID=$extracted_account_id|" .env && rm -f .env.bak
            sed -i.bak "s|NEAR_PRIVATE_KEY=.*|NEAR_PRIVATE_KEY=$private_key|" .env && rm -f .env.bak
        fi

        echo "✅ Credentials saved:"
        echo "- Account ID: $extracted_account_id"
        echo "- Credentials file: $creds_file"
    else
        echo "❌ Credentials file not found"
        exit 1
    fi
}

main() {
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

    echo ""
    echo "🎉 NEAR Wallet Setup Complete!"
    echo "Your agent's NEAR wallet is ready to use."
    echo ""
    echo "Next Steps:"
    echo "1. Review your .env file"
    echo "2. Run './scripts/verify_setup.sh' to verify everything"
    echo "3. Start developing your strategy!"
}

# Run main function
main
