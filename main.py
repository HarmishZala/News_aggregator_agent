from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from starlette.responses import JSONResponse
import os
import datetime
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="News Aggregator Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    model_provider: str = "groq"  # Default to groq

@app.post("/query")
async def query_news_agent(query: QueryRequest):
    """
    Query the news aggregation agent with a question.
    
    Args:
        query: Contains the question and optional model provider
        
    Returns:
        JSON response with the agent's answer
    """
    try:
        print(f"Processing query: {query.question}")
        
        # Initialize the news aggregation agent
        graph = GraphBuilder(model_provider=query.model_provider)
        react_app = graph()

        # Generate graph visualization (optional)
        try:
            png_graph = react_app.get_graph().draw_mermaid_png()
            with open("news_agent_graph.png", "wb") as f:
                f.write(png_graph)
            print(f"Graph saved as 'news_agent_graph.png' in {os.getcwd()}")
        except Exception as graph_error:
            print(f"Warning: Could not generate graph: {graph_error}")

        # Process the query
        messages = {"messages": [query.question]}
        output = react_app.invoke(messages)

        # Extract the final response
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  # Last AI response
        else:
            final_output = str(output)
        
        return {
            "answer": final_output,
            "timestamp": datetime.datetime.now().isoformat(),
            "model_provider": query.model_provider
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "News Aggregator Agent API",
        "version": "1.0.0",
        "description": "AI-powered news aggregation from multiple reputable sources",
        "endpoints": {
            "/query": "POST - Query the news agent",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "news-aggregator-agent"
    }