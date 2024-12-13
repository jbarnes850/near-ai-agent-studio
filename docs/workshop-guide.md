# NEAR Swarm Intelligence Workshop - Instructor Checklist

## Environment Setup (1 day before)

- [ ] Clone fresh copy of repository to verify latest version

```bash
git clone https://github.com/jbarnes850/near_swarm_intelligence
cd near_swarm_intelligence
```

- [ ] Verify all scripts are executable

```bash
chmod +x scripts/*.sh
ls -la scripts/
```

- [ ] Test quickstart script

```bash
./scripts/quickstart.sh
```

- [ ] Verify required environment variables

```bash
cat .env.example
```

Required variables:

- NEAR_NETWORK
- NEAR_ACCOUNT_ID
- NEAR_PRIVATE_KEY
- LLM_PROVIDER
- LLM_API_KEY

## Dependencies Check (1 day before)

- [ ] Verify Python version (3.12+)

```bash
python --version
```

- [ ] Test dependency installation

```bash
pip install -r requirements.txt
```

- [ ] Verify key packages are installed:
  - near-api-py
  - aiohttp
  - hyperbolic
  - pytest
  - pytest-asyncio

## NEAR Testnet Setup (1 day before)

- [ ] Ensure testnet faucet is working

```bash
./scripts/create_near_wallet.sh
```

- [ ] Fund workshop test account

```bash
# Verify account has sufficient funds for workshop
near state your-account.testnet
```

## Example Code Verification (Morning of workshop)

- [ ] Test simple strategy example

```bash
python -m near_swarm.examples.simple_strategy
```

- [ ] Verify market data integration

```bash
python -m near_swarm.examples.token_transfer_strategy
```

- [ ] Run test suite

```bash
pytest tests/ -v
```

## Workshop Materials

- [ ] Verify tutorial.md is up to date
- [ ] Check all code snippets in tutorial match current codebase
- [ ] Ensure example files are accessible:
  - simple_strategy.py
  - token_transfer_strategy.py
  - swarm_trading.py

## CLI Tool Check

- [ ] Test CLI commands

```bash
# Initialize new strategy
near-swarm init test-strategy

# List strategies
near-swarm list

# Run strategy
near-swarm run --example simple_strategy

# Monitor mode
near-swarm monitor
```

## Backup Plans

- [ ] Download offline copy of NEAR documentation
- [ ] Prepare backup testnet accounts
- [ ] Have offline copies of example code
- [ ] Prepare fallback LLM API keys

## Workshop Flow Testing

1. [ ] Test complete workshop flow:

   ```bash
   # 1. Initial setup
   ./scripts/quickstart.sh
   
   # 2. Create first agent
   near-swarm init my-first-strategy
   
   # 3. Run example strategy
   near-swarm run --example simple_strategy
   
   # 4. Monitor execution
   near-swarm monitor
   ```

2. [ ] Verify error messages are helpful:

   ```bash
   # Test with missing config
   near-swarm run --config missing.json
   
   # Test with invalid NEAR account
   near-swarm create-agent --account invalid.testnet
   ```

## Common Issues to Prepare For

1. [ ] Network connectivity issues
   - Have offline NEAR node setup instructions ready
   - Prepare local LLM fallback if needed

2. [ ] Python environment issues
   - Document common venv problems
   - Have conda environment yml as backup

3. [ ] NEAR account issues
   - Have extra funded testnet accounts ready
   - Document account recovery process

## Final Checks (1 hour before)

- [ ] Test internet connection
- [ ] Verify NEAR testnet status
- [ ] Check LLM API status
- [ ] Run quick end-to-end test
- [ ] Have troubleshooting.md ready
- [ ] Prepare terminal with larger font size
- [ ] Clear terminal history for clean demo

## Workshop Start

- [ ] Share repository URL
- [ ] Share test account credentials (if needed)
- [ ] Have .env.example ready to share
- [ ] Open tutorial.md for reference
