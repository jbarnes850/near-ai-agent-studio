"""Test CLI functionality."""
import os
import subprocess
from pathlib import Path

def test_cli_commands():
    """Test all CLI commands in sequence."""
    try:
        # 1. Test init
        print("\nTesting 'init' command...")
        result = subprocess.run(['near-swarm', 'init', 'test-strategy'], check=True)
        assert result.returncode == 0
        assert Path('test-strategy').exists()
        assert Path('test-strategy/config.json').exists()
        
        # 2. Test run with example
        print("\nTesting 'run --example' command...")
        result = subprocess.run(['near-swarm', 'run', '--example', 'simple_strategy'], check=True)
        assert result.returncode == 0
        
        # 3. Test monitor
        print("\nTesting 'monitor' command...")
        result = subprocess.run(['near-swarm', 'monitor'], check=True)
        assert result.returncode == 0
        
        print("\n✅ All CLI commands tested successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed: {e.cmd}")
        print(f"Return code: {e.returncode}")
        raise
        
if __name__ == "__main__":
    test_cli_commands() 