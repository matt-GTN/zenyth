from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import app as agent_graph, GraphState
from dotenv import load_dotenv
import os
import json
import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse

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

app = FastAPI()

# Autorise toutes les origines pour le développement local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def stream_generator(req):
    """
    This async generator function streams the agent's progress.
    It uses `app.astream` to get real-time updates from the LangGraph agent.
    """
    # req peut être un dict (issu de await req.json()) ou un objet Pydantic
    youtube_url = req["youtube_url"] if isinstance(req, dict) else req.youtube_url
    language = req["language"] if isinstance(req, dict) else req.language
    inputs: GraphState = {
        "youtube_url": youtube_url,
        "language": language,
        "video_id": None,
        "transcript": None,
        "intermediate_summary": None,
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

@app.api_route('/summarize', methods=["GET", "POST"])
async def summarize(req: Request):
    """
    Handles the /summarize request by streaming the agent's progress.
    Returns a StreamingResponse that sends server-sent events (SSE) to the client.
    """
    print("Méthode reçue :", req.method)
    if req.method == "POST":
        return StreamingResponse(stream_generator(await req.json()), media_type="text/event-stream")
    return JSONResponse({"error": "Method not allowed"}, status_code=405)