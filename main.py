from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from starlette.responses import JSONResponse
import os
import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from utils.config_loader import load_config
from utils.debug import enable_langsmith, open_langsmith_dashboard

load_dotenv()
# Normalize LANGSMITH_* to LANGCHAIN_* and enable tracing if requested
lm_trace = os.getenv('LANGSMITH_TRACING') or os.getenv('LANGCHAIN_TRACING_V2')
tracing_on = str(lm_trace).lower() in ['1', 'true', 'yes']
if tracing_on:
    api_key = os.getenv('LANGCHAIN_API_KEY') or os.getenv('LANGSMITH_API_KEY')
    project = os.getenv('LANGCHAIN_PROJECT') or os.getenv('LANGSMITH_PROJECT')
    enable_langsmith(api_key=api_key, project=project, enabled=True)
config = load_config()

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
    model_provider: str = config.get('default_model_provider', 'groq')
    thread_id: str | None = None
    audio_file_path: str | None = None  # Optional audio file for speech-to-text
    language: str = config.get('default_language', 'en-US')  # Language for speech recognition

@app.post("/query")
async def query_news_agent(query: QueryRequest):
    """
    Query the news aggregation agent with a question or audio file.
    
    Args:
        query: Contains the question, optional audio file, and model provider
        
    Returns:
        JSON response with the agent's answer
    """
    try:
        # Handle speech-to-text if audio file is provided
        if query.audio_file_path:
            from tools.speech_tools import transcribe_audio_file
            print(f"Processing audio file: {query.audio_file_path}")
            transcription_result = transcribe_audio_file(query.audio_file_path, query.language)
            
            if "Transcription successful" in transcription_result:
                # Extract the transcribed text
                transcribed_text = transcription_result.split("\n\n")[-1]
                query.question = f"Based on this transcribed audio: '{transcribed_text}', please provide relevant news information."
                print(f"Transcribed text: {transcribed_text}")
            else:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": f"Speech-to-text failed: {transcription_result}",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                )
        
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

        # Use helper that passes checkpointer config
        thread_id = query.thread_id or "api_default"
        result = graph.run_with_memory(query.question, thread_id=thread_id)

        if "error" in result:
            return JSONResponse(
                status_code=500, 
                content={
                    "error": result["error"],
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
        
        return {
            "answer": result.get("response", ""),
            "timestamp": result.get("timestamp", datetime.datetime.now().isoformat()),
            "model_provider": query.model_provider,
            "thread_id": thread_id,
            "memory_enabled": result.get("memory_enabled", False),
            "audio_processed": bool(query.audio_file_path),
            "language": query.language if query.audio_file_path else None
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

@app.post("/transcribe")
async def transcribe_audio(audio_file_path: str, language: str = None):
    """
    Transcribe audio file to text.
    
    Args:
        audio_file_path: Path to the audio file
        language: Language code for transcription (uses config default if not provided)
        
    Returns:
        JSON response with transcribed text
    """
    try:
        from tools.speech_tools import transcribe_audio_file
        
        # Use default language from config if not provided
        if not language:
            language = config.get('default_language', 'en-US')
        
        if not os.path.exists(audio_file_path):
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Audio file not found: {audio_file_path}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
        
        result = transcribe_audio_file(audio_file_path, language)
        
        if "Transcription successful" in result:
            # Extract the transcribed text
            transcribed_text = result.split("\n\n")[-1]
            return {
                "transcription": transcribed_text,
                "success": True,
                "language": language,
                "timestamp": datetime.datetime.now().isoformat()
            }
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": result,
                    "success": False,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "success": False,
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
            "/transcribe": "POST - Transcribe audio file to text",
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