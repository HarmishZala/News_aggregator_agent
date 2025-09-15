#!/usr/bin/env python3
"""
Test script to verify the News Aggregator Agent setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if required environment variables are set"""
    load_dotenv()
    
    print("🔍 Testing News Aggregator Agent Setup...")
    print("=" * 50)
    
    # Check for LLM provider
    groq_key = os.getenv('GROQ_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if groq_key:
        print("✅ GROQ_API_KEY found")
        llm_provider = "groq"
    elif openai_key:
        print("✅ OPENAI_API_KEY found")
        llm_provider = "openai"
    else:
        print("❌ No LLM API key found. Please set either GROQ_API_KEY or OPENAI_API_KEY")
        return False
    
    # Check optional API keys
    tavily_key = os.getenv('TAVILY_API_KEY')
    newsapi_key = os.getenv('NEWS_API_KEY')
    
    if tavily_key:
        print("✅ TAVILY_API_KEY found")
    else:
        print("⚠️  TAVILY_API_KEY not found (optional)")
    
    if newsapi_key:
        print("✅ NEWS_API_KEY found")
    else:
        print("⚠️  NEWS_API_KEY not found (optional)")
    
    print(f"\n🤖 Will use {llm_provider.upper()} as LLM provider")
    return True

def test_imports():
    """Test if all required packages can be imported"""
    print("\n📦 Testing package imports...")
    print("-" * 30)
    
    try:
        import langchain
        print("✅ langchain")
    except ImportError as e:
        print(f"❌ langchain: {e}")
        return False
    
    try:
        import langgraph
        print("✅ langgraph")
    except ImportError as e:
        print(f"❌ langgraph: {e}")
        return False
    
    try:
        import fastapi
        print("✅ fastapi")
    except ImportError as e:
        print(f"❌ fastapi: {e}")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    return True

def test_agent_initialization():
    """Test if the agent can be initialized"""
    print("\n🤖 Testing agent initialization...")
    print("-" * 35)
    
    try:
        from agent.agentic_workflow import GraphBuilder
        print("✅ GraphBuilder imported successfully")
        
        # Try to initialize with groq (most likely to be available)
        if os.getenv('GROQ_API_KEY'):
            agent = GraphBuilder(model_provider="groq")
            print("✅ Agent initialized with Groq")
        elif os.getenv('OPENAI_API_KEY'):
            agent = GraphBuilder(model_provider="openai")
            print("✅ Agent initialized with OpenAI")
        else:
            print("❌ No API keys available for agent initialization")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 News Aggregator Agent - Setup Test")
    print("=" * 50)
    
    # Test environment variables
    env_ok = test_environment()
    
    # Test package imports
    imports_ok = test_imports()
    
    # Test agent initialization
    agent_ok = test_agent_initialization()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Package Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Agent Initialization: {'✅ PASS' if agent_ok else '❌ FAIL'}")
    
    if env_ok and imports_ok and agent_ok:
        print("\n🎉 All tests passed! Your News Aggregator Agent is ready to use.")
        print("\nTo start the CLI interface, run:")
        print("python cli_app.py")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
