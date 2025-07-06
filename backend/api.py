from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import app as agent_graph, GraphState
from dotenv import load_dotenv
import os
import json
import asyncio

# Construire le chemin vers le fichier .env relatif au script actuel
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

# --- DEBUG: Vérifier les variables d'environnement LangSmith ---
print("--- Vérification des variables pour LangSmith ---")
print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
api_key = os.getenv('LANGCHAIN_API_KEY')
if api_key:
    print(f"LANGCHAIN_API_KEY est définie (commence par: {api_key[:4]}...)")
else:
    print("LANGCHAIN_API_KEY n'est PAS définie.")
print(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
print("-------------------------------------------------")

class SummarizeRequest(BaseModel):
    youtube_url: str
    language: str = "english"

fastapi_app = FastAPI()

# Autorise toutes les origines pour le développement local
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def stream_generator(req: SummarizeRequest):
    """
    This async generator function streams the agent's progress.
    It uses `app.astream` to get real-time updates from the LangGraph agent.
    """
    inputs: GraphState = {
        "youtube_url": req.youtube_url,
        "language": req.language,
        "video_id": None,
        "transcript": None,
        "summary": None,
        "error_message": None,
        "log": [],
        "status_message": "API: Starting...",
        "step_progress": [],
        "current_step": "Initialization"
    }

    async for chunk in agent_graph.astream(inputs):
        for key, value in chunk.items():
            if isinstance(value, dict):
                data_to_send = {"node": key, "data": value}
                yield f"data: {json.dumps(data_to_send)}\n\n"
                await asyncio.sleep(0.01)

@fastapi_app.post('/summarize')
async def summarize(req: SummarizeRequest):
    """
    Handles the /summarize request by streaming the agent's progress.
    Returns a StreamingResponse that sends server-sent events (SSE) to the client.
    """
    return StreamingResponse(stream_generator(req), media_type="text/event-stream")