#!/usr/bin/env python3
"""
News Aggregator Agent CLI Interface
A command-line interface for interacting with the news aggregation agent.
"""

import os
import sys
import datetime
from typing import Optional
from dotenv import load_dotenv
from agent.agentic_workflow import GraphBuilder
from utils.config_loader import load_config
from tools.speech_tools import transcribe_audio_from_microphone, list_microphones
from tools.tts_tools import speak_text, list_tts_voices
from utils.debug import enable_langchain_debug, enable_langsmith, open_langsmith_dashboard

# Load environment variables
load_dotenv()

class NewsAggregatorCLI:
    """Command-line interface for the News Aggregator Agent"""
    
    def __init__(self, model_provider: str = "groq"):
        """Initialize the CLI with the specified model provider"""
        self.model_provider = model_provider
        self.agent = None
        self.react_app = None
        self.session_active = True
        self.thread_id = "cli_default"
        self.config = load_config()
        self.default_language = (
            self.config.get("speech_recognition", {}).get("default_language", "en-US")
        )
        
    def initialize_agent(self):
        """Initialize the news aggregation agent"""
        try:
            print("🔄 Initializing News Aggregator Agent...")
            self.agent = GraphBuilder(model_provider=self.model_provider)
            self.react_app = self.agent()
            print("✅ Agent initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Error initializing agent: {str(e)}")
            return False
    
    def display_welcome(self):
        """Display welcome message and instructions"""
        print("\n" + "="*60)
        print("📰 NEWS AGGREGATOR AGENT")
        print("="*60)
        print("Welcome to your intelligent news aggregation assistant!")
        print("\nI can help you find news and information from multiple sources:")
        print("• General news (AP, Reuters, BBC, CNN, etc.)")
        print("• Technology news (TechCrunch, Ars Technica, The Verge, etc.)")
        print("• Business news (Bloomberg, Reuters, CNBC, WSJ, etc.)")
        print("• Professional insights from LinkedIn")
        print("• In-depth articles from Medium")
        print("\nCommands:")
        print("• Type your question to search for news")
        print("• Type 'help' for more information")
        print("• Type 'quit' or 'exit' to end the session")
        print("• Type 'clear' to clear the screen")
        print("• Type 'thread <id>' to set conversation thread id")
        print("• Type 'listen [seconds] [lang] [device_index] [start_timeout]' to speak (e.g., 'listen 5 en-US 0 8')")
        print("• Type 'mics' to list available microphones")
        print("• Type 'speak' to play the last agent response")
        print("• Type 'voices' to list TTS voices")
        print("• Type 'debug on|off' to toggle LangChain debug logs")
        print("• Type 'trace on|off [project]' to toggle LangSmith tracing")
        print("• Type 'dashboard' to open the LangSmith dashboard")
        print("="*60)
    
    def display_help(self):
        """Display help information"""
        print("\n📖 HELP - News Aggregator Agent")
        print("-" * 40)
        print("Example queries:")
        print("• 'What are the latest AI developments?'")
        print("• 'Show me news about Tesla stock'")
        print("• 'What's happening in the tech industry?'")
        print("• 'Find news about climate change'")
        print("• 'What are the latest updates in machine learning?'")
        print("\nTips:")
        print("• Be specific about what you're looking for")
        print("• The agent will automatically choose the best sources")
        print("• Results include source attribution and publication dates")
        print("• You can ask follow-up questions for more details")
        print("-" * 40)
    
    def process_query(self, query: str) -> str:
        """Process a user query and return the agent's response"""
        try:
            if not self.agent:
                return "❌ Agent not initialized. Please restart the application."
            
            result = self.agent.run_with_memory(query, thread_id=self.thread_id)
            if "error" in result:
                return f"❌ {result['error']}"
            return result.get("response", "")
            
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"
    
    def format_response(self, response: str) -> str:
        """Format the agent's response for better display"""
        if not response:
            return "No response received from the agent."
        
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_response = f"\n📰 News Aggregator Response - {timestamp}\n"
        formatted_response += "=" * 60 + "\n"
        formatted_response += response
        formatted_response += "\n" + "=" * 60 + "\n"
        
        return formatted_response
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run(self):
        """Main CLI loop"""
        # Display welcome message
        self.display_welcome()
        
        # Initialize the agent
        if not self.initialize_agent():
            print("❌ Failed to initialize agent. Exiting...")
            return
        
        print(f"\n🤖 Agent ready! Using {self.model_provider.upper()} model.")
        print("Type your question or 'help' for assistance.\n")
        last_agent_response: Optional[str] = None
        # Auto-open dashboard if tracing is already enabled at start
        if os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true':
            open_langsmith_dashboard(os.getenv('LANGCHAIN_PROJECT'))
        
        # Main interaction loop
        while self.session_active:
            try:
                # Get user input
                user_input = input("🔍 You: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using News Aggregator Agent. Goodbye!")
                    self.session_active = False
                    break
                
                elif user_input.lower() == 'help':
                    self.display_help()
                    continue
                elif user_input.lower().startswith('listen'):
                    parts = user_input.split()
                    duration = 5
                    language = self.default_language
                    device_index = None
                    start_timeout = None
                    if len(parts) >= 2 and parts[1].isdigit():
                        duration = int(parts[1])
                    if len(parts) >= 3:
                        language = parts[2]
                    if len(parts) >= 4 and parts[3].isdigit():
                        device_index = int(parts[3])
                    if len(parts) >= 5:
                        try:
                            start_timeout = float(parts[4])
                        except ValueError:
                            start_timeout = None

                    device_msg = f", device={device_index}" if device_index is not None else ""
                    timeout_msg = f", start_timeout={start_timeout}" if start_timeout is not None else ""
                    print(f"\n🎙️  Microphone: ON  (listening for {duration}s, lang={language}{device_msg}{timeout_msg})")
                    print("(Adjusting for ambient noise, then listening...)")
                    payload = {"duration": duration, "language": language}
                    if device_index is not None:
                        payload["device_index"] = device_index
                    if start_timeout is not None:
                        payload["start_timeout"] = start_timeout
                    transcript = transcribe_audio_from_microphone.invoke(payload)
                    print("🔇 Microphone: OFF")

                    if "Transcription successful" in transcript:
                        spoken_text = transcript.split("\n\n")[-1]
                        print(f"🗣️  You said: {spoken_text}")
                        print("\n🔄 Processing your spoken query...")
                        response = self.process_query(spoken_text)
                        formatted_response = self.format_response(response)
                        print(formatted_response)
                        last_agent_response = response
                    else:
                        print(f"❌ {transcript}")
                    continue
                
                elif user_input.lower() == 'clear':
                    self.clear_screen()
                    self.display_welcome()
                    continue
                
                elif user_input.lower() == 'mics':
                    listing = list_microphones.invoke({})
                    print(listing)
                    continue
                
                elif user_input.lower() == 'voices':
                    listing = list_tts_voices.invoke({})
                    print(listing)
                    continue

                elif user_input.lower().startswith('debug '):
                    arg = user_input.split(' ', 1)[1].strip().lower()
                    enable_langchain_debug(arg == 'on')
                    print(f"LangChain debug is {'ON' if arg == 'on' else 'OFF'}")
                    continue

                elif user_input.lower().startswith('trace '):
                    parts = user_input.split()
                    on = parts[1].lower() == 'on' if len(parts) > 1 else False
                    project = parts[2] if len(parts) > 2 else None
                    api_key = os.getenv('LANGCHAIN_API_KEY') or os.getenv('LANGSMITH_API_KEY')
                    enable_langsmith(api_key=api_key, project=project, enabled=on)
                    if on and not api_key:
                        print("Tracing requested but LANGCHAIN_API_KEY/LANGSMITH_API_KEY not set.")
                    print(f"LangSmith tracing is {'ON' if on else 'OFF'}" + (f" (project: {project})" if on and project else ""))
                    if on:
                        open_langsmith_dashboard(project or os.getenv('LANGCHAIN_PROJECT'))
                    continue

                elif user_input.lower() == 'dashboard':
                    open_langsmith_dashboard(os.getenv('LANGCHAIN_PROJECT'))
                    continue
                
                elif user_input.lower().startswith('speak'):
                    parts = user_input.split()
                    # optional: voice_id, rate, volume
                    voice_id = parts[1] if len(parts) >= 2 else None
                    rate = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else None
                    volume = None
                    if len(parts) >= 4:
                        try:
                            volume = float(parts[3])
                        except ValueError:
                            volume = None
                    if not last_agent_response:
                        print("No agent response to speak yet.")
                        continue
                    print("🔊 Speaking last response...")
                    result_msg = speak_text.invoke({
                        "text": last_agent_response,
                        "voice_id": voice_id,
                        "rate": rate,
                        "volume": volume,
                    })
                    print(result_msg)
                    continue
                
                elif user_input.lower().startswith('thread '):
                    self.thread_id = user_input.split(' ', 1)[1].strip() or self.thread_id
                    print(f"✅ Thread set to: {self.thread_id}")
                    continue
                
                elif not user_input:
                    print("Please enter a question or command.")
                    continue
                
                # Process the query using memory-configured run
                print("\n🔄 Searching for news... Please wait...")
                response = self.process_query(user_input)
                
                # Display the formatted response
                formatted_response = self.format_response(response)
                print(formatted_response)
                last_agent_response = response
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                self.session_active = False
                break
            
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                print("Please try again or type 'help' for assistance.")

def main():
    """Main entry point for the CLI application"""
    # Check for model provider argument
    model_provider = "groq"  # Default
    if len(sys.argv) > 1:
        model_provider = sys.argv[1].lower()
        if model_provider not in ["groq", "openai"]:
            print("❌ Invalid model provider. Use 'groq' or 'openai'.")
            sys.exit(1)
    
    # Check for required environment variables
    required_vars = ["GROQ_API_KEY"] if model_provider == "groq" else ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file.")
        sys.exit(1)
    
    # Optional API keys for news sources
    optional_vars = ["TAVILY_API_KEY", "NEWS_API_KEY"]
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    if missing_optional:
        print(f"⚠️  Warning: Missing optional API keys: {', '.join(missing_optional)}")
        print("Some news sources may not be available.")
        print("Consider setting these for better news coverage.\n")
    
    # Start the CLI
    cli = NewsAggregatorCLI(model_provider=model_provider)
    cli.run()

if __name__ == "__main__":
    main()
