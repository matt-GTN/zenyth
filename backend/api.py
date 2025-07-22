import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)
print(f"Attempting to load .env from: {dotenv_path}")

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import app as agent_graph, GraphState
import json
import asyncio


class SummarizeRequest(BaseModel):
    youtube_url: str
    language: str = "english"
    summary_length: str = "standard"

app = FastAPI()

# Le reste du fichier est inchangé
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def stream_generator(req):
    youtube_url = req["youtube_url"] if isinstance(req, dict) else req.youtube_url
    language = req["language"] if isinstance(req, dict) else req.language
    summary_length = req.get("summary_length", "standard") if isinstance(req, dict) else getattr(req, "summary_length", "standard")
    inputs: GraphState = {
        "youtube_url": youtube_url,
        "language": language,
        "summary_length": summary_length,
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
    print("Received method:", req.method)
    if req.method == "POST":
        try:
            body = await req.json()
            return StreamingResponse(stream_generator(body), media_type="text/event-stream")
        except json.JSONDecodeError:
            return JSONResponse({"error": "Invalid JSON in request body"}, status_code=400)
    return JSONResponse({"error": "Method not allowed"}, status_code=405)