
from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from tools.news_aggregation_tools import news_tool_list
from typing import Dict, Any, List
import json
from datetime import datetime

class GraphBuilder():
    def __init__(self, model_provider: str = "groq", enable_memory: bool = True):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        # Initialize news aggregation tools
        self.tools = news_tool_list
        
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        self.graph = None
        self.enable_memory = enable_memory
        
        # Initialize memory if enabled
        if self.enable_memory:
            self.memory = MemorySaver()
        else:
            self.memory = None
        
        self.system_prompt = SYSTEM_PROMPT
    
    
    def agent_function(self, state: MessagesState):
        """Main agent function with enhanced context awareness"""
        messages = state["messages"]
        
        # Add system prompt if not already present
        if not messages or not isinstance(messages[0], dict) or messages[0].get("role") != "system":
            input_messages = [self.system_prompt] + messages
        else:
            input_messages = messages
        
        # Generate response with tools
        response = self.llm_with_tools.invoke(input_messages)
        
        # Add timestamp to response for better tracking
        if hasattr(response, 'content'):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response.additional_kwargs = getattr(response, 'additional_kwargs', {})
            response.additional_kwargs['timestamp'] = timestamp
        
        return {"messages": [response]}
    def build_graph(self):
        """Build the LangGraph with memory support"""
        graph_builder = StateGraph(MessagesState)
        
        # Add nodes
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        
        # Add edges
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        graph_builder.add_edge("agent", END)
        
        # Compile with memory if enabled
        if self.enable_memory and self.memory:
            self.graph = graph_builder.compile(checkpointer=self.memory)
        else:
            self.graph = graph_builder.compile()
        
        return self.graph
        
    def get_conversation_history(self, thread_id: str = "default") -> List[Dict]:
        """Get conversation history for a specific thread"""
        if not self.enable_memory or not self.memory:
            return []
        
        try:
            # Get the current state from memory
            config = {"configurable": {"thread_id": thread_id}}
            state = self.graph.get_state(config)
            
            if state and state.values and "messages" in state.values:
                messages = state.values["messages"]
                return [{"role": msg.type, "content": msg.content} for msg in messages if hasattr(msg, 'content')]
            return []
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def clear_conversation_history(self, thread_id: str = "default") -> bool:
        """Clear conversation history for a specific thread"""
        if not self.enable_memory or not self.memory:
            return False
        
        try:
            # Create a new thread to effectively clear history
            config = {"configurable": {"thread_id": f"{thread_id}_cleared_{datetime.now().timestamp()}"}}
            return True
        except Exception as e:
            print(f"Error clearing conversation history: {e}")
            return False
    
    def format_response(self, response: Any) -> str:
        """Format the agent response for better readability"""
        if hasattr(response, 'content'):
            content = response.content
            
            # Add timestamp if available
            timestamp = getattr(response, 'additional_kwargs', {}).get('timestamp', '')
            if timestamp:
                formatted_response = f"🕒 **Response Time:** {timestamp}\n\n"
            else:
                formatted_response = ""
            
            # Format the content with better structure
            formatted_response += content
            
            return formatted_response
        return str(response)
    
    def run_with_memory(self, query: str, thread_id: str = "default") -> Dict[str, Any]:
        """Run the agent with memory support and return formatted results"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            
            # Run the graph
            result = self.graph.invoke(
                {"messages": [{"role": "user", "content": query}]},
                config=config
            )
            
            # Format the response
            if result and "messages" in result:
                last_message = result["messages"][-1]
                formatted_response = self.format_response(last_message)
                
                return {
                    "response": formatted_response,
                    "thread_id": thread_id,
                    "timestamp": datetime.now().isoformat(),
                    "memory_enabled": self.enable_memory
                }
            
            return {"error": "No response generated"}
            
        except Exception as e:
            return {"error": f"Error running agent: {str(e)}"}
    
    def __call__(self):
        return self.build_graph()