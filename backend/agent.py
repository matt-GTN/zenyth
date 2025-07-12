# /zenyth/agent.py
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from tools import extract_id_tool, get_transcript_tool, summarize_text_tool, translate_text_tool
# from config import tavily_tool, youtube_search # Commenté pour le débogage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# 1. Définition de l'état du graphe
class GraphState(TypedDict):
    youtube_url: str
    language: str
    video_id: Optional[str]
    transcript: Optional[str]
    intermediate_summary: Optional[str]  # Clé pour le résumé partiel
    summary: Optional[str]               # Clé pour le résumé final
    error_message: Optional[str]
    log: List[str]
    status_message: str
    current_step: str
    step_progress: List[dict]

# 2. Définition des nœuds
def node_extract_id(state: GraphState) -> dict:
    print("---NODE: ID EXTRACTION---")
    current_log = state.get("log", [])
    current_step = "ID Extraction"
    step_progress = state.get("step_progress", [])
    
    url = state.get('youtube_url', '')
    video_id = extract_id_tool.invoke({"youtube_url": url})
    
    if not video_id:
        error_message = "Invalid YouTube URL or ID not found."
        return {
            "error_message": error_message,
            "log": current_log + [f"❌ {error_message}"],
            "status_message": "❌ Failed to extract ID.",
            "current_step": current_step,
            "step_progress": step_progress + [{"step": current_step, "status": "error", "message": error_message}]
        }
    
    success_message = f"Video ID found: {video_id}"
    return {
        "video_id": video_id,
        "log": current_log + [success_message],
        "status_message": "📝 Fetching transcript...",
        "current_step": current_step,
        "step_progress": step_progress + [{"step": current_step, "status": "success", "message": success_message}]
    }

def node_get_transcript(state: GraphState) -> dict:
    print("---NODE: TRANSCRIPT RETRIEVAL---")
    current_log = state.get("log", [])
    current_step = "Transcript Retrieval"
    step_progress = state.get("step_progress", [])
    
    video_id = state.get('video_id', '')
    transcript, error = get_transcript_tool.invoke({"video_id": video_id})
    
    if error:
        return {
            "error_message": error,
            "log": current_log + [f"❌ {error}"],
            "status_message": f"❌ Failed: {error}",
            "current_step": current_step,
            "step_progress": step_progress + [{"step": current_step, "status": "error", "message": error}]
        }
    
    success_message = f"Transcript fetched successfully ({len(transcript):,} characters)."
    return {
        "transcript": transcript,
        "log": current_log + [success_message],
        "status_message": "🧠 Creating the summary...",
        "current_step": current_step,
        "step_progress": step_progress + [{"step": current_step, "status": "success", "message": success_message}]
    }

def node_summarize(state: GraphState) -> dict:
    print("---NODE: SUMMARY CREATION---")
    current_log = state.get("log", [])
    current_step = "Summary Creation"
    step_progress = state.get("step_progress", [])
    
    transcript = state.get('transcript', '')
    language = state.get('language', 'english')
    
    print(f"Starting summary in '{language}'...")
    summary, error = summarize_text_tool.invoke({
        "transcript": transcript,
        "language": language
    })
    
    if error:
        return {
            "error_message": error,
            "log": current_log + [f"❌ {error}"],
            "status_message": f"❌ Failed to create the summary: {error}",
            "current_step": current_step,
            "step_progress": step_progress + [{"step": current_step, "status": "error", "message": error}]
        }
    
    success_message = "Summary created."
    # === MODIFICATION CORRIGÉE ===
    # On stocke le résultat dans 'intermediate_summary' et PAS dans 'summary'
    return {
        "intermediate_summary": summary, 
        "log": current_log + [success_message],
        "status_message": "🚀 Finalizing and formatting...",
        "current_step": current_step,
        "step_progress": step_progress + [{"step": current_step, "status": "success", "message": success_message}]
    }

def node_translate_summary(state: GraphState) -> dict:
    """Nœud qui assure que le résumé est dans la langue demandée (qualité)."""
    print("---NODE: SUMMARY LANGUAGE CHECK---")
    current_log = state.get("log", [])
    current_step = "Language Check"
    step_progress = state.get("step_progress", [])
    
    # === MODIFICATION CORRIGÉE ===
    # On lit depuis 'intermediate_summary'
    summary_to_translate = state.get('intermediate_summary', '')
    target_language = state.get('language', 'english')
    
    final_summary, error = translate_text_tool.invoke({
        "text": summary_to_translate,
        "target_language": target_language
    })
    
    if error:
        warning_message = f"⚠️ Final language check failed ({error}), using the original summary."
        print(warning_message)
        # On remplit 'summary' avec la version intermédiaire en cas d'échec de la traduction
        return {
            "summary": summary_to_translate, 
            "log": current_log + [warning_message],
            "status_message": "✅ Summary completed (with a warning)."
        }
    
    success_message = f"Summary language: '{target_language}'."
    # On remplit enfin 'summary' avec le résultat final.
    return {
        "summary": final_summary, 
        "log": current_log + [success_message],
        "status_message": "✅ Summary successfully completed!",
        "current_step": current_step,
        "step_progress": step_progress + [{"step": current_step, "status": "success", "message": success_message}]
    }

def node_final_step(state: GraphState) -> dict:
    print("---NŒUD: ÉTAPE FINALE---")
    return dict(state)

# 3. Construction et compilation du graphe
workflow = StateGraph(GraphState)

workflow.add_node("extract_id", node_extract_id)
workflow.add_node("get_transcript", node_get_transcript)
workflow.add_node("summarize", node_summarize)
workflow.add_node("translate_summary", node_translate_summary)
workflow.add_node("final_step", node_final_step)

workflow.set_entry_point("extract_id")

def check_for_error(state: GraphState) -> str:
    if state.get("error_message"):
        return "error"
    return "continue"

# Arêtes conditionnelles
workflow.add_conditional_edges("extract_id", check_for_error, {"continue": "get_transcript", "error": "final_step"})
workflow.add_conditional_edges("get_transcript", check_for_error, {"continue": "summarize", "error": "final_step"})
workflow.add_conditional_edges("summarize", check_for_error, {"continue": "translate_summary", "error": "final_step"})

# Arête finale
workflow.add_edge("translate_summary", "final_step")
workflow.add_edge("final_step", END)

# Compilation
app = workflow.compile()

# Visualisation du graphe
try:
    graph = app.get_graph()
    image_bytes = graph.draw_mermaid_png()
    with open("agent_workflow.png", "wb") as f:
        f.write(image_bytes)
    print("\nGraph visualization saved in the directory as agent_workflow.png\n")
except Exception as e:
    print(f"\nUnable to generate visualization. Run 'pip install playwright' and 'playwright install'. Error: {e}\n")