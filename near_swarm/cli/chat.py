"""
Chat Command Module
Implements interactive chat functionality for NEAR Swarm agents
"""

import os
import sys
import cmd
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
import typer
from pydantic import BaseModel, Field
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit.history import InMemoryHistory

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.market_data import MarketDataManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for pretty printing
console = Console()

class AgentType(str, Enum):
    """Available agent types"""
    CHAT_ASSISTANT = "chat_assistant"  # Default conversational agent
    MARKET_ANALYZER = "market_analyzer"
    RISK_MANAGER = "risk_manager"
    STRATEGY_OPTIMIZER = "strategy_optimizer"

# System prompts for different agent types
AGENT_PROMPTS = {
    AgentType.CHAT_ASSISTANT: """You are a helpful AI assistant for the NEAR Swarm Intelligence framework.
Your role is to:
1. Help users understand and use the system's capabilities
2. Provide clear explanations of available commands and features
3. Guide users through complex operations
4. Answer questions about the NEAR ecosystem and trading concepts
5. Maintain a friendly, conversational tone while being informative

You have access to:
- Market analysis tools (/market, /trend, /volume)
- Risk management features (/risk, /balance, /positions)
- Strategy optimization (/strategy, /portfolio)
- System management (/agents, /workspace, /config)

When users need specific analysis or operations, you can:
1. Explain which specialized agent would be best suited
2. Help them switch to that agent using the /agents command
3. Guide them through using the appropriate commands

Remember to:
- Be conversational and engaging
- Provide context for technical terms
- Suggest relevant commands when appropriate
- Help users understand the system's architecture""",
    AgentType.MARKET_ANALYZER: """You are a market analysis expert...""",  # Existing prompt
    AgentType.RISK_MANAGER: """You are a risk management specialist...""",  # Existing prompt
    AgentType.STRATEGY_OPTIMIZER: """You are a trading strategy expert..."""  # Existing prompt
}

# Prompt styling
style = Style.from_dict({
    'prompt': '#00aa00 bold',
    'agent': '#00aa00',
    'command': '#884444',
    'error': '#ff0000'
})

# Response Models
class MarketAnalysis(BaseModel):
    """Structured market analysis response"""
    price: float = Field(..., description="Current price of the token")
    sentiment: str = Field(..., description="Market sentiment: bullish, bearish, or neutral")
    volume_24h: str = Field(..., description="24-hour trading volume")
    trend: str = Field(..., description="Current market trend")
    confidence: float = Field(..., description="Confidence score of the analysis", ge=0, le=1)
    reasoning: str = Field(..., description="Detailed reasoning for the analysis")
    recommendations: List[str] = Field(..., description="List of actionable recommendations")

class RiskAssessment(BaseModel):
    """Structured risk assessment response"""
    risk_level: str = Field(..., description="Overall risk level: low, medium, high")
    exposure: float = Field(..., description="Current portfolio exposure")
    max_drawdown: float = Field(..., description="Maximum potential drawdown")
    risk_factors: List[Dict[str, float]] = Field(..., description="Identified risk factors and their weights")
    mitigation_strategies: List[str] = Field(..., description="Suggested risk mitigation strategies")

class StrategyProposal(BaseModel):
    """Structured strategy proposal"""
    name: str = Field(..., description="Strategy name")
    type: str = Field(..., description="Strategy type: arbitrage, trend-following, etc.")
    timeframe: str = Field(..., description="Recommended timeframe")
    entry_conditions: List[str] = Field(..., description="Entry conditions")
    exit_conditions: List[str] = Field(..., description="Exit conditions")
    risk_parameters: Dict[str, float] = Field(..., description="Risk management parameters")
    expected_returns: str = Field(..., description="Expected returns estimate")
    code_example: Optional[str] = Field(None, description="Example implementation code")

class WorkspaceConfig(BaseModel):
    """Workspace configuration"""
    name: str = Field(..., description="Workspace name")
    description: str = Field(None, description="Workspace description")
    agents: List[str] = Field(default_factory=list, description="Active agents in workspace")
    strategies: List[str] = Field(default_factory=list, description="Available strategies")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Additional settings")

class SwarmChat(cmd.Cmd):
    """Interactive chat interface for NEAR Swarm agents."""
    
    intro = """
🤖 Welcome to NEAR Swarm Intelligence Chat!
Type 'help' or '?' to list commands.
Type 'quit' or 'exit' to exit.

Available Commands:
- /market [symbol]    : Get market analysis
- /trend [timeframe]  : Get trend analysis
- /volume [symbol]    : Volume analysis
- /risk [action]      : Risk assessment
- /strategy [action]  : Strategy suggestions
- /portfolio         : Portfolio overview
- /agents            : List active agents
- /balance          : Check portfolio balance
- /positions        : List open positions
"""
    
    def __init__(self, agent_type: str = "chat_assistant", verbose: bool = False, json_output: bool = False):
        """Initialize chat interface."""
        super().__init__()
        self.agent_type = agent_type
        self.verbose = verbose
        self.json_output = json_output
        self.agent: Optional[SwarmAgent] = None
        self.market_data: Optional[MarketDataManager] = None
        self.session = PromptSession(history=InMemoryHistory())
        self.prompt = self._get_prompt()
        self.history: list[Dict[str, Any]] = []
        self.reasoning_enabled: bool = False
        self.workspace: Optional[WorkspaceConfig] = None
        
        # Set appropriate intro based on agent type
        if agent_type == AgentType.CHAT_ASSISTANT:
            self.intro = """
👋 Welcome to NEAR Swarm Intelligence! I'm your AI assistant.
I'm here to help you navigate the system and answer any questions you have.

You can:
- Chat with me naturally about any topic
- Use commands (type 'help' to see them)
- Switch to specialized agents for specific tasks

How can I assist you today?
"""
        else:
            self.intro = """
🤖 Welcome to NEAR Swarm Intelligence Chat!
Type 'help' or '?' to list commands.
Type 'quit' or 'exit' to exit.

Available Commands:
- /market [symbol]    : Get market analysis
- /trend [timeframe]  : Get trend analysis
- /volume [symbol]    : Volume analysis
- /risk [action]      : Risk assessment
- /strategy [action]  : Strategy suggestions
- /portfolio         : Portfolio overview
- /agents            : List active agents
- /balance          : Check portfolio balance
- /positions        : List open positions
"""
        
        self.command_aliases = {
            '/m': 'market',
            '/t': 'trend',
            '/v': 'volume',
            '/r': 'risk',
            '/s': 'strategy',
            '/p': 'portfolio',
            '/a': 'agents',
            '/b': 'balance',
            '/pos': 'positions',
            '/h': 'help',
            '/c': 'clear',
            '/x': 'execute',
            '/reason': 'toggle_reasoning',
            '/ws': 'workspace',
            '/env': 'environment',
            '/config': 'config',
            '/export': 'export_workspace',
            '/import': 'import_workspace'
        }
        self.multiline_mode = False
        self.multiline_buffer = []
        
    def _get_prompt(self) -> str:
        """Get formatted prompt."""
        return f"near-swarm ({self.agent_type})> "

    def _format_output(self, data: Dict[str, Any]) -> None:
        """Format and display output based on settings"""
        if self.json_output:
            console.print_json(json.dumps(data))
        else:
            if isinstance(data.get("content"), str):
                console.print(Panel(Markdown(data["content"])))
            else:
                console.print(Panel(str(data)))
        
        # Store in history if verbose
        if self.verbose:
            self.history.append(data)
    
    async def setup(self):
        """Set up agent and market data."""
        try:
            # Initialize market data
            self.market_data = MarketDataManager()
            
            # Initialize agent
            config = AgentConfig(
                network=os.getenv("NEAR_NETWORK", "testnet"),
                account_id=os.getenv("NEAR_ACCOUNT_ID"),
                private_key=os.getenv("NEAR_PRIVATE_KEY"),
                llm_provider=os.getenv("LLM_PROVIDER", "hyperbolic"),
                llm_api_key=os.getenv("LLM_API_KEY"),
                llm_model=os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3"),
                api_url=os.getenv("LLM_API_URL", "https://api.hyperbolic.xyz/v1"),
                system_prompt=AGENT_PROMPTS[self.agent_type]
            )
            
            self.agent = SwarmAgent(
                config,
                SwarmConfig(
                    role=self.agent_type,
                    min_confidence=0.7,
                    min_votes=1  # Single agent mode
                )
            )
            
            # Start agent
            await self.agent.start()
            console.print(f"✅ Connected to {self.agent_type} agent")
            
        except Exception as e:
            console.print(f"[red]Error setting up agent: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up resources."""
        if self.agent:
            await self.agent.close()
        if self.market_data:
            await self.market_data.close()
    
    def do_market(self, arg: str):
        """Get market analysis for a symbol."""
        if not arg:
            console.print("[red]Please specify a symbol (e.g., market near)")
            return
        
        async def get_market_analysis(symbol: str):
            try:
                data = await self.market_data.get_token_price(symbol)
                console.print(Panel(f"""
[bold]Market Analysis for {symbol.upper()}[/bold]
Current Price: ${data['price']:.2f}
Confidence: {data['confidence']:.2%}
"""))
                
                # Get agent's market analysis
                analysis = await self.agent.evaluate_proposal({
                    "type": "market_analysis",
                    "params": {
                        "symbol": symbol,
                        "price": data['price'],
                        "market_context": {
                            "current_price": data['price'],
                            "24h_volume": "2.1M",  # TODO: Get real volume
                            "market_trend": "stable",
                            "network_load": "moderate"
                        }
                    }
                })
                
                console.print(Panel(Markdown(analysis["reasoning"])))
                
            except Exception as e:
                console.print(f"[red]Error getting market analysis: {str(e)}")
        
        asyncio.run(get_market_analysis(arg))
    
    def do_risk(self, arg: str):
        """Get risk assessment."""
        console.print("🔄 Risk assessment coming soon!")
    
    def do_strategy(self, arg: str):
        """Get strategy suggestions."""
        console.print("🔄 Strategy suggestions coming soon!")
    
    def do_portfolio(self, arg: str):
        """Get portfolio overview."""
        console.print("🔄 Portfolio overview coming soon!")
    
    def do_agents(self, arg: str):
        """List active agents."""
        console.print(Panel(f"""
[bold]Active Agent:[/bold]
Type: {self.agent_type}
Status: {'Running' if self.agent and self.agent.is_running() else 'Stopped'}
"""))
    
    def do_exit(self, arg: str):
        """Exit the chat interface."""
        return True
    
    def do_quit(self, arg: str):
        """Exit the chat interface."""
        return True

    def do_trend(self, arg: str):
        """Get trend analysis for a timeframe."""
        if not arg:
            console.print("[red]Please specify a timeframe (e.g., trend 24h)")
            return
        
        async def get_trend_analysis(timeframe: str):
            try:
                analysis = await self.agent.evaluate_proposal({
                    "type": "trend_analysis",
                    "params": {
                        "timeframe": timeframe,
                        "market_context": await self.market_data.get_market_context()
                    }
                })
                self._format_output(analysis)
            except Exception as e:
                console.print(f"[red]Error getting trend analysis: {str(e)}")
        
        asyncio.run(get_trend_analysis(arg))
    
    def do_volume(self, arg: str):
        """Get volume analysis for a symbol."""
        if not arg:
            console.print("[red]Please specify a symbol (e.g., volume near)")
            return
        
        async def get_volume_analysis(symbol: str):
            try:
                analysis = await self.agent.evaluate_proposal({
                    "type": "volume_analysis",
                    "params": {
                        "symbol": symbol,
                        "market_context": await self.market_data.get_market_context()
                    }
                })
                self._format_output(analysis)
            except Exception as e:
                console.print(f"[red]Error getting volume analysis: {str(e)}")
        
        asyncio.run(get_volume_analysis(arg))
    
    def do_balance(self, arg: str):
        """Get portfolio balance."""
        async def get_balance():
            try:
                balance = await self.agent.evaluate_proposal({
                    "type": "portfolio_balance",
                    "params": {}
                })
                self._format_output(balance)
            except Exception as e:
                console.print(f"[red]Error getting balance: {str(e)}")
        
        asyncio.run(get_balance())
    
    def do_positions(self, arg: str):
        """List open positions."""
        async def get_positions():
            try:
                positions = await self.agent.evaluate_proposal({
                    "type": "open_positions",
                    "params": {}
                })
                self._format_output(positions)
            except Exception as e:
                console.print(f"[red]Error getting positions: {str(e)}")
        
        asyncio.run(get_positions())

    def do_execute(self, arg: str):
        """Execute a command suggested by the agent."""
        if not arg:
            console.print("[red]Please specify a command to execute[/red]")
            return
        
        try:
            os.system(arg)
            console.print(f"[green]Executed: {arg}[/green]")
        except Exception as e:
            console.print(f"[red]Error executing command: {str(e)}[/red]")

    def do_multiline(self, arg: str):
        """Toggle multiline input mode."""
        self.multiline_mode = not self.multiline_mode
        status = "enabled" if self.multiline_mode else "disabled"
        console.print(f"[green]Multiline mode {status}[/green]")

    def do_save(self, arg: str):
        """Save chat history to a file."""
        filename = arg or "chat_history.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.history, f, indent=2)
            console.print(f"[green]Chat history saved to {filename}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving history: {str(e)}[/red]")

    def do_load(self, arg: str):
        """Load chat history from a file."""
        if not arg:
            console.print("[red]Please specify a file to load[/red]")
            return
        try:
            with open(arg, 'r') as f:
                self.history = json.load(f)
            console.print(f"[green]Chat history loaded from {arg}[/green]")
        except Exception as e:
            console.print(f"[red]Error loading history: {str(e)}[/red]")

    def do_capabilities(self, arg: str):
        """Show agent capabilities and examples."""
        console.print(Panel("""
[bold]NEAR Swarm Agent Capabilities[/bold]

[cyan]1. Market Analysis[/cyan]
- Real-time price analysis
- Trend detection
- Volume analysis
- Market sentiment analysis

[yellow]2. Risk Management[/yellow]
- Portfolio risk assessment
- Position sizing recommendations
- Risk exposure analysis
- Market condition monitoring

[green]3. Strategy Optimization[/green]
- Trading strategy suggestions
- Performance optimization
- Parameter tuning
- Backtest analysis

[magenta]4. Developer Tools[/magenta]
- Command execution
- Multi-agent coordination
- Natural language processing
- API integration

[blue]Example Interactions:[/blue]
1. "Can you analyze the NEAR market and suggest entry points?"
2. "What's the current risk level for my portfolio?"
3. "Help me optimize my trading strategy for the current market"
4. "Show me how to implement a simple arbitrage strategy"

[white]Tips:[/white]
- Use /help to see all available commands
- Start commands with '/' or use natural language
- Use multiline mode for complex inputs (/multiline)
- Save your chat history with /save
"""))

    def default(self, line: str):
        """Handle natural language input and command aliases."""
        # Check for command aliases
        if line.startswith('/'):
            cmd = line.split()[0]
            if cmd in self.command_aliases:
                return getattr(self, f'do_{self.command_aliases[cmd]}')(line[len(cmd):].strip())
        
        # Handle multiline input
        if self.multiline_mode:
            if line.strip() == '}':
                # Process accumulated input
                full_input = '\n'.join(self.multiline_buffer)
                self.multiline_buffer = []
                self.multiline_mode = False
                asyncio.run(self._process_input(full_input))
                return
            self.multiline_buffer.append(line)
            return
        
        # Handle natural language interaction
        asyncio.run(self._process_input(line))

    async def _process_input(self, text: str):
        """Process natural language input with enhanced reasoning."""
        try:
            # Add reasoning context if enabled
            context = {
                "agent_type": self.agent_type,
                "market_context": await self.market_data.get_market_context() if self.market_data else None,
                "history": self.history[-5:] if self.verbose else [],
                "capabilities": {
                    "can_execute_commands": True,
                    "available_commands": list(self.command_aliases.keys())
                }
            }
            
            if self.reasoning_enabled:
                context["reasoning_steps"] = [
                    "1. Analyze the user's request and identify key objectives",
                    "2. Gather relevant market data and context",
                    "3. Apply domain expertise and pattern recognition",
                    "4. Consider multiple scenarios and outcomes",
                    "5. Form recommendations with confidence scores",
                    "6. Suggest concrete actions or commands"
                ]
            
            response = await self.agent.evaluate_proposal({
                "type": "chat_interaction",
                "params": {
                    "input": text,
                    "context": context,
                    "response_model": {
                        "market_analysis": MarketAnalysis.model_json_schema(),
                        "risk_assessment": RiskAssessment.model_json_schema(),
                        "strategy_proposal": StrategyProposal.model_json_schema()
                    } if not self.json_output else None
                }
            })
            
            # Handle structured responses
            if not self.json_output and "type" in response:
                if response["type"] == "market_analysis":
                    response["content"] = MarketAnalysis(**response["data"]).json(indent=2)
                elif response["type"] == "risk_assessment":
                    response["content"] = RiskAssessment(**response["data"]).json(indent=2)
                elif response["type"] == "strategy_proposal":
                    response["content"] = StrategyProposal(**response["data"]).json(indent=2)
            
            # Check if response contains a command to execute
            if "command" in response:
                console.print(f"\n[yellow]Suggested command:[/yellow] {response['command']}")
                if input("Execute this command? [y/N] ").lower() == 'y':
                    self.do_execute(response['command'])
            
            self._format_output(response)
            
        except Exception as e:
            console.print(f"[red]Error processing input: {str(e)}[/red]")

    def do_help(self, arg: str):
        """Enhanced help command with examples."""
        if arg:
            # Detailed help for specific command
            super().do_help(arg)
            # Add examples
            if hasattr(self, f'do_{arg}'):
                examples = {
                    'market': 'Example: market near - Get NEAR token analysis',
                    'trend': 'Example: trend 24h - Get 24-hour trend analysis',
                    'volume': 'Example: volume near - Get NEAR trading volume',
                    'risk': 'Example: risk exposure - Check risk exposure',
                    'strategy': 'Example: strategy optimize - Get strategy optimization suggestions',
                }
                if arg in examples:
                    console.print(f"\n[green]{examples[arg]}[/green]")
        else:
            console.print(Panel("""
[bold]NEAR Swarm Intelligence Chat Commands[/bold]

[green]Market Analysis:[/green]
/market, /m [symbol]     : Get market analysis
/trend, /t [timeframe]   : Get trend analysis
/volume, /v [symbol]     : Get volume analysis

[yellow]Risk Management:[/yellow]
/risk, /r [action]       : Risk assessment
/balance, /b            : Check portfolio balance
/positions, /pos        : List open positions

[blue]Strategy:[/blue]
/strategy, /s [action]   : Strategy suggestions
/portfolio, /p          : Portfolio overview

[magenta]System:[/magenta]
/agents, /a             : List active agents
help [command]          : Show help for command
exit, quit             : Exit chat

[cyan]Natural Language:[/cyan]
You can also interact naturally with your agent:
- "What's the current market sentiment for NEAR?"
- "Should I adjust my portfolio based on current trends?"
- "Analyze the risk of increasing my NEAR position"
"""))

    def do_clear(self, arg: str):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(self.intro)

    def do_toggle_reasoning(self, arg: str):
        """Toggle step-by-step reasoning mode."""
        self.reasoning_enabled = not self.reasoning_enabled
        status = "enabled" if self.reasoning_enabled else "disabled"
        console.print(f"[green]Step-by-step reasoning {status}[/green]")

    def do_workspace(self, arg: str):
        """Manage workspace configuration."""
        if not arg:
            if self.workspace:
                console.print(Panel(f"""
[bold]Current Workspace:[/bold] {self.workspace.name}
[cyan]Description:[/cyan] {self.workspace.description or 'No description'}

[green]Active Agents:[/green]
{chr(10).join(f'- {agent}' for agent in self.workspace.agents)}

[yellow]Available Strategies:[/yellow]
{chr(10).join(f'- {strategy}' for strategy in self.workspace.strategies)}

[magenta]Environment:[/magenta]
{chr(10).join(f'- {k}={v}' for k, v in self.workspace.environment.items())}
"""))
            else:
                console.print("[yellow]No workspace configured. Use 'workspace create <name>' to create one.[/yellow]")
            return

        cmd, *args = arg.split(maxsplit=1)
        if cmd == "create":
            name = args[0] if args else input("Workspace name: ")
            description = input("Description (optional): ")
            self.workspace = WorkspaceConfig(
                name=name,
                description=description,
                agents=[self.agent_type],
                environment=dict(os.environ)
            )
            console.print(f"[green]Created workspace: {name}[/green]")
        elif cmd == "add":
            if not self.workspace:
                console.print("[red]No workspace configured[/red]")
                return
            what, *items = args[0].split()
            if what == "agent":
                self.workspace.agents.extend(items)
            elif what == "strategy":
                self.workspace.strategies.extend(items)
            console.print(f"[green]Added {what}: {', '.join(items)}[/green]")

    def do_environment(self, arg: str):
        """Manage environment variables."""
        if not self.workspace:
            console.print("[red]No workspace configured[/red]")
            return

        if not arg:
            console.print(Panel("\n".join(f"{k}={v}" for k, v in self.workspace.environment.items())))
            return

        cmd, *args = arg.split(maxsplit=1)
        if cmd == "set":
            key, value = args[0].split('=', 1)
            self.workspace.environment[key] = value
            os.environ[key] = value
            console.print(f"[green]Set {key}={value}[/green]")
        elif cmd == "unset":
            key = args[0]
            self.workspace.environment.pop(key, None)
            os.environ.pop(key, None)
            console.print(f"[green]Unset {key}[/green]")

    def do_export_workspace(self, arg: str):
        """Export workspace configuration."""
        if not self.workspace:
            console.print("[red]No workspace configured[/red]")
            return

        filename = arg or f"{self.workspace.name}_workspace.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.workspace.dict(), f, indent=2)
            console.print(f"[green]Workspace exported to {filename}[/green]")
        except Exception as e:
            console.print(f"[red]Error exporting workspace: {str(e)}[/red]")

    def do_import_workspace(self, arg: str):
        """Import workspace configuration."""
        if not arg:
            console.print("[red]Please specify a file to import[/red]")
            return

        try:
            with open(arg, 'r') as f:
                data = json.load(f)
                self.workspace = WorkspaceConfig(**data)
                # Update environment
                os.environ.update(self.workspace.environment)
            console.print(f"[green]Workspace imported from {arg}[/green]")
        except Exception as e:
            console.print(f"[red]Error importing workspace: {str(e)}[/red]")

    def do_config(self, arg: str):
        """View or modify configuration."""
        if not self.workspace:
            console.print("[red]No workspace configured[/red]")
            return

        if not arg:
            console.print(Panel(json.dumps(self.workspace.settings, indent=2)))
            return

        try:
            key, value = arg.split('=', 1)
            # Parse value as JSON if possible
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
            self.workspace.settings[key] = value
            console.print(f"[green]Set {key}={value}[/green]")
        except ValueError:
            console.print("[red]Invalid format. Use: config key=value[/red]")

    def do_quickstart(self, arg: str):
        """Interactive quickstart wizard"""
        console.print(Panel("""
        Welcome to NEAR Swarm! Let's get you started:
        
        1. Choose your use case
        2. Configure your agents
        3. Test your strategy
        4. Deploy to testnet
        """)) 

def chat(
    agent: AgentType = typer.Option(AgentType.CHAT_ASSISTANT, "--agent", "-a", help="Type of agent to chat with"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output responses in JSON format"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed agent reasoning"),
    command: Optional[str] = typer.Option(None, "--command", "-c", help="Direct command to execute (non-interactive mode)"),
    multi_agent: bool = typer.Option(False, "--multi-agent", "-m", help="Enable multi-agent mode"),
    agents: Optional[List[AgentType]] = typer.Option(None, "--agents", help="List of agents to use in multi-agent mode")
):
    """Start a chat session with NEAR Swarm agents. Simply run 'near-swarm chat' to begin."""
    try:
        # Default to interactive mode unless a specific command is provided
        interactive = command is None
        
        if interactive:
            if multi_agent and not agents:
                agents = [AgentType.MARKET_ANALYZER, AgentType.RISK_MANAGER, AgentType.STRATEGY_OPTIMIZER]
            
            chat_interface = SwarmChat(
                agent_type=agent if not multi_agent else "swarm",
                verbose=verbose,
                json_output=json_output
            )
            
            # Setup and start agents
            async def setup_agents():
                await chat_interface.setup()
                if multi_agent:
                    # Initialize additional agents
                    peer_agents = []
                    for agent_type in agents:
                        if agent_type != agent:  # Skip main agent type
                            config = AgentConfig(
                                network=os.getenv("NEAR_NETWORK", "testnet"),
                                account_id=os.getenv("NEAR_ACCOUNT_ID"),
                                private_key=os.getenv("NEAR_PRIVATE_KEY"),
                                llm_provider=os.getenv("LLM_PROVIDER", "hyperbolic"),
                                llm_api_key=os.getenv("LLM_API_KEY"),
                                llm_model=os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3"),
                                api_url=os.getenv("LLM_API_URL", "https://api.hyperbolic.xyz/v1")
                            )
                            peer_agent = SwarmAgent(
                                config,
                                SwarmConfig(
                                    role=agent_type,
                                    min_confidence=0.7,
                                    min_votes=1
                                )
                            )
                            await peer_agent.start()
                            peer_agents.append(peer_agent)
                    
                    # Join swarm
                    if chat_interface.agent:
                        await chat_interface.agent.join_swarm(peer_agents)
            
            asyncio.run(setup_agents())
            chat_interface.cmdloop()
        else:
            # Non-interactive mode
            if not command:
                console.print("[red]Error: --command is required in non-interactive mode[/red]")
                sys.exit(1)
            
            chat_interface = SwarmChat(agent, verbose, json_output)
            
            async def execute_command():
                await chat_interface.setup()
                # Parse command
                cmd_parts = command.split(maxsplit=1)
                cmd_name = cmd_parts[0].lstrip('/')
                cmd_args = cmd_parts[1] if len(cmd_parts) > 1 else ""
                
                # Execute command
                if hasattr(chat_interface, f'do_{cmd_name}'):
                    getattr(chat_interface, f'do_{cmd_name}')(cmd_args)
                else:
                    # Handle as natural language
                    await chat_interface.default(command)
                
                await chat_interface.cleanup()
            
            asyncio.run(execute_command())
            
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!")
    except Exception as e:
        console.print(f"[red]Error in chat session: {str(e)}")
        sys.exit(1) 