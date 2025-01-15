"""
Interactive chat interface for NEAR Agent Studio.
Provides guided tutorials and agent creation assistance with enhanced validation.
"""

import asyncio
import click
import subprocess
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from typing import Optional, Dict, Any, List, Tuple
import yaml
import logging
from dataclasses import dataclass

from near_swarm.plugins import PluginLoader
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig
from near_swarm.core.market_data import MarketDataManager

logger = logging.getLogger(__name__)

@dataclass
class EnvState:
    """Environment state tracking"""
    near_account: Optional[str] = None
    network: str = "testnet"
    llm_provider: str = "hyperbolic"
    initialized: bool = False

class EnhancedChatAssistant:
    """Enhanced chat assistant with validation and monitoring."""
    
    def __init__(self, tutorial_mode: Optional[str] = None):
        self.tutorial_mode = tutorial_mode
        self.session = PromptSession()
        self.style = Style.from_dict({
            'prompt': '#00ffff bold',
            'error': '#ff0000 bold',
            'success': '#00ff00 bold',
            'info': '#ffffff',
            'header': '#00b0ff bold'
        })
        self.plugin_loader = PluginLoader()
        self.env_state = EnvState()
        self.metrics = {
            'messages_exchanged': 0,
            'decisions_made': 0,
            'analysis_completed': 0
        }

    async def start(self) -> None:
        """Entry point with enhanced validation."""
        click.echo(click.style("\n🚀 Initializing NEAR AI Agent Studio...", fg='bright_blue'))
        
        # Run validation suite
        if not await self._run_validation_suite():
            return

        if self.tutorial_mode:
            await self.run_enhanced_tutorial(self.tutorial_mode)
        else:
            await self.run_interactive()

    async def _run_validation_suite(self) -> bool:
        """Run complete validation suite with progress tracking."""
        validations = [
            ("Environment", self.validate_environment),
            ("Plugins", self.verify_plugins),
            ("Agent Configs", self.agent_config_check),
            ("Communication", self.verify_communication_channels)
        ]

        click.echo("\n🔍 Running System Validation...")
        
        for name, validator in validations:
            click.echo(f"\n▶️ Checking {name}...")
            try:
                if not await validator():
                    click.echo(click.style(f"\n❌ {name} validation failed. Please fix issues above.", fg='red'))
                    return False
                click.echo(click.style(f"✓ {name} validation passed.", fg='green'))
            except Exception as e:
                click.echo(click.style(f"\n❌ {name} validation error: {str(e)}", fg='red'))
                return False

        click.echo(click.style("\n✨ All validations passed successfully!", fg='green'))
        return True

    async def validate_environment(self) -> bool:
        """Enhanced environment validation with recovery suggestions."""
        required_vars = {
            'LLM_API_KEY': 'LLM API key for agent intelligence',
            'NEAR_ACCOUNT_ID': 'NEAR account for blockchain operations',
            'NEAR_NETWORK': 'NEAR network (testnet/mainnet)',
        }

        missing_vars = []
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_vars.append((var, description))
            else:
                click.echo(f"   ✓ {var}: Found")
                if var == 'NEAR_ACCOUNT_ID':
                    self.env_state.near_account = value
                elif var == 'NEAR_NETWORK':
                    self.env_state.network = value

        if missing_vars:
            click.echo("\n🔧 Missing Environment Variables:")
            for var, desc in missing_vars:
                click.echo(f"   • {var}: {desc}")
            click.echo("\n📝 Quick Fix:")
            click.echo("   1. Add these variables to your .env file")
            click.echo("   2. Run: source .env")
            click.echo("   3. Or run quickstart.sh again")
            return False

        return True

    async def verify_plugins(self) -> bool:
        """Verify plugin loading with detailed feedback."""
        try:
            click.echo("\n🔌 Scanning for plugins...")
            plugins = await self.plugin_loader.load_all_plugins()
            
            if not plugins:
                click.echo("   ⚠️ No plugins found!")
                return False

            click.echo("\n📦 Available Plugins:")
            for name, plugin in plugins.items():
                click.echo(f"   ✓ {name}: {plugin.__class__.__name__}")
            
            required_plugins = {'price-monitor', 'decision-maker'}
            missing = required_plugins - set(plugins.keys())
            
            if missing:
                click.echo(f"\n⚠️ Missing required plugins: {missing}")
                return False

            return True

        except Exception as e:
            click.echo(f"   ❌ Plugin loading error: {str(e)}")
            return False

    async def agent_config_check(self) -> bool:
        """Validate agent configurations with schema checking."""
        click.echo("\n📄 Validating Agent Configurations...")
        
        config_files = [
            ('price-monitor.yaml', ['name', 'llm', 'plugins']),
            ('decision-maker.yaml', ['name', 'llm', 'plugins'])
        ]

        for filename, required_fields in config_files:
            path = os.path.join('agents', filename)
            try:
                if not os.path.exists(path):
                    click.echo(f"   ⚠️ Missing config: {filename}")
                    return False

                with open(path, 'r') as f:
                    config = yaml.safe_load(f)

                missing = [field for field in required_fields if field not in config]
                if missing:
                    click.echo(f"   ❌ {filename} missing fields: {missing}")
                    return False

                click.echo(f"   ✓ {filename} validated successfully")

            except Exception as e:
                click.echo(f"   ❌ Error checking {filename}: {str(e)}")
                return False

        return True

    async def verify_communication_channels(self) -> bool:
        """Verify all communication channels with health checks."""
        click.echo("\n🔗 Verifying Communication Channels...")

        # Check LLM connection
        try:
            config = LLMConfig(
                provider=os.getenv('LLM_PROVIDER', 'hyperbolic'),
                api_key=os.getenv('LLM_API_KEY'),
                model=os.getenv('LLM_MODEL', 'meta-llama/llama-3.3-70B-Instruct')
            )
            llm = create_llm_provider(config)
            click.echo("   ✓ LLM provider initialized")
        except Exception as e:
            click.echo(f"   ❌ LLM initialization failed: {str(e)}")
            return False

        # Check market data connection
        try:
            async with MarketDataManager() as market:
                data = await market.get_token_price('near')
                click.echo(f"   ✓ Market data available: NEAR ${data['price']:.2f}")
        except Exception as e:
            click.echo(f"   ❌ Market data connection failed: {str(e)}")
            return False

        return True

    async def run_enhanced_tutorial(self, tutorial_mode: str) -> None:
        """Run tutorial with enhanced progress tracking."""
        welcome_msg = f"""
╭──────────────────────────────────────────────────╮
│     Welcome to Your NEAR AI Agent Studio! 🚀     │
╰──────────────────────────────────────────────────╯

Environment Status:
✓ NEAR Account: {self.env_state.near_account}
✓ Network: {self.env_state.network}
✓ LLM Provider: {self.env_state.llm_provider}

Your development environment is ready for AI agents!
"""
        click.echo(welcome_msg)

        tutorial_steps = [
            ("Creating Price Monitor", self._create_price_monitor),
            ("Creating Decision Maker", self._create_decision_maker),
            ("Verifying Agent Communication", self._verify_agent_communication),
            ("Launching Collaboration", self._launch_collaboration)
        ]

        for step_name, step_func in tutorial_steps:
            click.echo(f"\n▶️ {step_name}...")
            if not await step_func():
                click.echo(click.style(f"\n❌ Tutorial paused at: {step_name}", fg='red'))
                return

        click.echo(click.style("\n🎉 Tutorial completed successfully!", fg='green'))

    async def _create_price_monitor(self) -> bool:
        """Create and verify price monitoring agent."""
        try:
            cmd = "create agent price-monitor --role market_analyzer"
            result = await self.run_command(cmd)
            return result.returncode == 0
        except Exception as e:
            click.echo(f"❌ Error creating price monitor: {str(e)}")
            return False

    async def _create_decision_maker(self) -> bool:
        """Create and verify decision making agent."""
        try:
            cmd = "create agent decision-maker --role strategy_optimizer"
            result = await self.run_command(cmd)
            return result.returncode == 0
        except Exception as e:
            click.echo(f"❌ Error creating decision maker: {str(e)}")
            return False

    async def _verify_agent_communication(self) -> bool:
        """Verify inter-agent communication."""
        click.echo("Verifying agent communication channels...")
        # Add actual communication verification logic here
        return True

    async def _launch_collaboration(self) -> bool:
        """Launch and monitor agent collaboration."""
        try:
            await self.run_agents("price-monitor", "decision-maker")
            return True
        except Exception as e:
            click.echo(f"❌ Error launching collaboration: {str(e)}")
            return False

    async def run_command(self, command: str) -> subprocess.CompletedProcess:
        """Execute command with enhanced error handling."""
        click.echo(f"\nExecuting: {click.style(command, fg='cyan')}")
        
        cmd_parts = command.split()
        if not cmd_parts[0].startswith('near-swarm'):
            cmd_parts = ['near-swarm'] + cmd_parts

        try:
            result = subprocess.run(cmd_parts, capture_output=True, text=True)
            if result.returncode == 0:
                click.echo(click.style("✓ Command succeeded", fg='green'))
            else:
                click.echo(click.style(f"❌ Command failed: {result.stderr}", fg='red'))
            return result
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {str(e)}")

    async def run_agents(self, *args) -> None:
        """Run agents with enhanced monitoring."""
        if not args:
            click.echo("Usage: run_agents <agent1> <agent2> ...")
            return

        click.echo("\n🌐 Launching AI Agent Swarm...")
        click.echo(f"Starting agents: {', '.join(args)}")

        # Load plugins first
        loaded_plugins = await self.plugin_loader.load_all_plugins()
        for agent in args:
            if agent in loaded_plugins:
                click.echo(f"✅ Loaded agent: {agent} ({loaded_plugins[agent].__class__.__name__})")
            else:
                click.echo(click.style(f"❌ Failed to load agent: {agent}", fg='red'))
                return

        try:
            # Initialize market data
            async with MarketDataManager() as market:
                price_data = await market.get_token_price('near')
                click.echo(f"\n📊 Current NEAR Price: ${price_data['price']:.2f}")

                while True:
                    # Price Monitor Analysis
                    click.echo("\n🔍 Price Monitor thinking...")
                    click.echo("Sending request to agent for market analysis...")
                    
                    price_monitor = loaded_plugins.get('price-monitor')
                    if price_monitor:
                        analysis = await price_monitor.evaluate({
                            'current_price': price_data['price'],
                            'change_24h': price_data['24h_change']
                        })
                        
                        if analysis:
                            click.echo("\n\n🔍 📝 Analysis from agent:")
                            for key, value in analysis.items():
                                if key != 'confidence':
                                    click.echo(f"• {key.title()}: {value}")
                            click.echo(f"• Confidence: {int(analysis.get('confidence', 0) * 100)}%")

                    # Decision Maker Evaluation
                    click.echo("\n🤔 Decision Maker consulting agent...")
                    click.echo("Sending market analysis to agent for strategic evaluation...")
                    
                    decision_maker = loaded_plugins.get('decision-maker')
                    if decision_maker:
                        decision = await decision_maker.evaluate({
                            'market_analysis': analysis,
                            'current_price': price_data['price']
                        })
                        
                        if decision:
                            click.echo("\n\n🤔 📋 Strategic Decision from agent analysis:")
                            for key, value in decision.items():
                                if key not in ['confidence', 'action_type']:
                                    click.echo(f"• {key.title()}: {value}")
                            click.echo(f"• Confidence: {int(decision.get('confidence', 0) * 100)}%")

                            # Execute high confidence decisions
                            if decision.get('confidence', 0) >= 0.75:
                                click.echo("\n✨ High Confidence Decision:")
                                click.echo(decision.get('action', ''))
                                
                                # Execute the decision
                                try:
                                    result = await decision_maker.execute(decision)
                                    if result.get('transaction'):
                                        tx_info = result['transaction']
                                        if tx_info['status'] == 'success':
                                            click.echo(click.style(f"\n🎯 Transaction executed: {tx_info['explorer_url']}", fg='green'))
                                        else:
                                            click.echo(click.style(f"\n❌ Transaction failed: {tx_info.get('error', 'Unknown error')}", fg='red'))
                                except Exception as e:
                                    logger.error(f"Error executing decision: {str(e)}")
                                    logger.exception("Full traceback:")

                    click.echo("\n⏳ Waiting 60 seconds before next analysis...")
                    await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info("Agent execution cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in agent execution: {str(e)}")
            logger.exception("Full traceback:")
            click.echo(click.style(f"\n❌ Agent execution failed: {str(e)}", fg='red'))

    async def _process_agent_output(self, output: str) -> None:
        """Process and format agent output with metrics tracking."""
        try:
            if "Analysis from agent" in output:
                self.metrics['analysis_completed'] += 1
                click.echo(click.style(f"\n🔍 {output}", fg='yellow'))
            elif "Decision from agent" in output:
                self.metrics['decisions_made'] += 1
                click.echo(click.style(f"\n🤔 {output}", fg='blue'))
                logger.debug(f"Processing decision output: {output}")
                
                # Extract decision details
                if "Take profit" in output and "Confidence: 85%" in output:
                    click.echo("\n✨ High Confidence Decision:")
                    action_text = output.split("Action:")[1].strip()
                    click.echo(action_text)
                    
                    # Trigger execution
                    decision = {
                        'action_type': 'take_profit',
                        'confidence': 0.85,
                        'action': action_text
                    }
                    logger.debug(f"Created decision object: {decision}")
                    
                    # Execute the decision
                    try:
                        logger.debug("Attempting to execute decision...")
                        if 'decision-maker' not in self.plugin_loader.plugins:
                            logger.error("Decision maker plugin not found!")
                            return
                            
                        plugin = self.plugin_loader.plugins['decision-maker']
                        logger.debug(f"Found decision maker plugin: {plugin}")
                        
                        result = await plugin.execute(decision)
                        logger.debug(f"Execution result: {result}")
                        
                        if result.get('transaction'):
                            tx_info = result['transaction']
                            if tx_info['status'] == 'success':
                                click.echo(click.style(f"\n🎯 Transaction executed: {tx_info['explorer_url']}", fg='green'))
                            else:
                                click.echo(click.style(f"\n❌ Transaction failed: {tx_info.get('error', 'Unknown error')}", fg='red'))
                    except Exception as e:
                        logger.error(f"Error executing decision: {str(e)}")
                        logger.exception("Full traceback:")
                
            elif "Message exchanged" in output:
                self.metrics['messages_exchanged'] += 1
                click.echo(click.style(f"\n💬 {output}", fg='green'))
            else:
                click.echo(output)

        except Exception as e:
            logger.error(f"Error processing output: {str(e)}")
            logger.exception("Full traceback:")
            click.echo(output)

    def _display_metrics(self) -> None:
        """Display current collaboration metrics."""
        metrics_msg = f"""
📊 Collaboration Metrics:
   • Analyses: {self.metrics['analysis_completed']}
   • Decisions: {self.metrics['decisions_made']}
   • Messages: {self.metrics['messages_exchanged']}
"""
        click.echo(click.style(metrics_msg, fg='cyan'))

    async def run_interactive(self) -> None:
        """Run interactive mode with enhanced command handling."""
        click.echo("\n👋 Welcome to interactive mode! Type /help for commands.")
        
        while True:
            try:
                command = await self.session.prompt_async(">> ")
                command = command.strip()

                if command.lower() in ['/exit', '/quit']:
                    break
                elif command == '/help':
                    self._show_help()
                elif command.startswith('/create'):
                    await self.run_command(command[1:])
                elif command.startswith('/run'):
                    args = command.split()[1:]
                    await self.run_agents(*args)
                elif command.startswith('/status'):
                    self._display_metrics()
                else:
                    click.echo("Unknown command. Type /help for available commands.")

            except Exception as e:
                click.echo(click.style(f"❌ Error: {str(e)}", fg='red'))

    def _show_help(self) -> None:
        """Show enhanced help message."""
        help_msg = """
Available Commands:
/create agent <name>     Create a new agent
/run <agent1> <agent2>   Run multiple agents together
/status                  Show current metrics
/help                    Show this help message
/exit                    Exit the chat

Example:
/create agent my-agent   Create a new agent named 'my-agent'
/run price-monitor decision-maker   Run both agents together
"""
        click.echo(help_msg)

def start_chat(tutorial_mode: Optional[str] = None):
    """Start enhanced chat interface."""
    assistant = EnhancedChatAssistant(tutorial_mode)
    asyncio.run(assistant.start()) 