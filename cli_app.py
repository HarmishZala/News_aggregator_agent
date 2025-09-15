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

# Load environment variables
load_dotenv()

class NewsAggregatorCLI:
    """Command-line interface for the News Aggregator Agent"""
    
    def __init__(self, model_provider: str = "groq"):
        """Initialize the CLI with the specified model provider"""
        self.model_provider = model_provider
        self.agent = None
        self.session_active = True
        
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
            
            # Prepare the message for the agent
            messages = {"messages": [query]}
            
            # Get response from the agent
            output = self.react_app.invoke(messages)
            
            # Extract the final response
            if isinstance(output, dict) and "messages" in output:
                final_output = output["messages"][-1].content
            else:
                final_output = str(output)
            
            return final_output
            
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
                
                elif user_input.lower() == 'clear':
                    self.clear_screen()
                    self.display_welcome()
                    continue
                
                elif not user_input:
                    print("Please enter a question or command.")
                    continue
                
                # Process the query
                print("\n🔄 Searching for news... Please wait...")
                response = self.process_query(user_input)
                
                # Display the formatted response
                formatted_response = self.format_response(response)
                print(formatted_response)
                
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
