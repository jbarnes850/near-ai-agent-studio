"""
Multi-modal NEAR Education Agent
Provides real-time voice interaction for learning about NEAR Protocol.
Uses:
- ElevenLabs Conversational AI for real-time voice interaction
- NEAR Protocol for blockchain interaction
- LLM for natural language understanding
"""

import os
import signal
from typing import Optional
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from near_swarm.core.agent import Agent, AgentConfig
from dotenv import load_dotenv

# System prompt for the education agent
NEAR_EDUCATOR_PROMPT = """You are an expert NEAR Protocol educator. Your role is to:
1. Explain NEAR concepts clearly and accurately
2. Provide real-world examples and use cases
3. Guide users through basic NEAR operations
4. Answer questions about NEAR's technology and ecosystem

Always maintain a helpful and encouraging tone. If you're unsure about something,
acknowledge it and suggest where to find accurate information."""

class NEAREducationAgent:
    def __init__(self):
        load_dotenv()
        
        # Initialize ElevenLabs client
        self.voice_client = ElevenLabs(
            api_key=os.getenv("ELEVEN_LABS_API_KEY")
        )
        
        # Initialize NEAR agent
        self.agent = Agent(
            AgentConfig(
                network="testnet",
                account_id=os.getenv("NEAR_ACCOUNT_ID"),
                private_key=os.getenv("NEAR_PRIVATE_KEY"),
                llm_provider="hyperbolic",
                llm_api_key=os.getenv("LLM_API_KEY"),
                llm_model="deepseek-ai/DeepSeek-V3",
                system_prompt=NEAR_EDUCATOR_PROMPT,
                rpc_url=os.getenv("NEAR_RPC_URL")
            )
        )
        
        # Initialize conversation
        self.conversation = None
        self.conversation_id = None
    
    async def start_conversation(self):
        """Start a real-time voice conversation."""
        try:
            # Start NEAR agent if not running
            if not self.agent.is_running():
                await self.agent.start()
            
            # Initialize conversation with real-time audio
            self.conversation = Conversation(
                # API client
                self.voice_client,
                # Use default audio interface (system mic/speakers)
                audio_interface=DefaultAudioInterface(),
                
                # Callbacks for conversation flow
                callback_agent_response=self._handle_agent_response,
                callback_agent_response_correction=self._handle_response_correction,
                callback_user_transcript=self._handle_user_input,
                callback_latency_measurement=self._handle_latency,
                
                # System prompt and context
                system_prompt=NEAR_EDUCATOR_PROMPT,
                initial_context=await self._get_near_context()
            )
            
            # Set up clean shutdown
            signal.signal(signal.SIGINT, lambda sig, frame: self.stop_conversation())
            
            # Start the conversation session
            print("\nStarting conversation - speak into your microphone...")
            print("(Press Ctrl+C to end the conversation)\n")
            
            self.conversation.start_session()
            
        except Exception as e:
            print(f"Error starting conversation: {e}")
            self.stop_conversation()
    
    def stop_conversation(self):
        """Stop the conversation gracefully."""
        if self.conversation:
            self.conversation_id = self.conversation.end_session()
            print(f"\nConversation ended. ID: {self.conversation_id}")
            self.conversation = None
    
    async def wait_for_completion(self):
        """Wait for conversation to complete."""
        if self.conversation:
            self.conversation_id = await self.conversation.wait_for_session_end()
            print(f"\nConversation completed. ID: {self.conversation_id}")
    
    async def _get_near_context(self) -> str:
        """Get current NEAR context for the conversation."""
        try:
            balance = await self.agent.check_balance()
            return f"Current testnet balance: {balance} NEAR"
        except Exception:
            return "Unable to fetch NEAR balance"
    
    def _handle_agent_response(self, response: str):
        """Handle agent's response."""
        print(f"Agent: {response}")
    
    def _handle_response_correction(self, original: str, corrected: str):
        """Handle corrections to agent's responses."""
        print(f"Agent correction: {original} -> {corrected}")
    
    def _handle_user_input(self, transcript: str):
        """Handle user's voice input transcript."""
        print(f"You: {transcript}")
    
    def _handle_latency(self, latency_ms: float):
        """Handle latency measurements."""
        if latency_ms > 1000:  # Only log if latency is high
            print(f"Response latency: {latency_ms:.0f}ms")

async def main():
    # Initialize the education agent
    educator = NEAREducationAgent()
    
    try:
        # Start real-time conversation
        await educator.start_conversation()
        
        # Wait for conversation to complete
        await educator.wait_for_completion()
        
    except KeyboardInterrupt:
        print("\nEnding conversation...")
        educator.stop_conversation()
    except Exception as e:
        print(f"Error during conversation: {e}")
        educator.stop_conversation()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 