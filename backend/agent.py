# /zenyth/agent.py
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from tools import extract_id_tool, get_transcript_tool, summarize_text_tool, translate_text_tool
# from config import tavily_tool, youtube_search # Commenté pour le débogage
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field

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
    print("---NŒUD: EXTRACTION DE L'ID---")
    current_log = state.get("log", [])
    current_step = "Extraction de l'ID"
    step_progress = state.get("step_progress", [])
    
    url = state.get('youtube_url', '')
    video_id = extract_id_tool.invoke({"youtube_url": url})
    
    if not video_id:
        error_message = "URL YouTube invalide ou ID non trouvé."
        return {
            "error_message": error_message,
            "log": current_log + [f"❌ {error_message}"],
            "status_message": "❌ Échec de l'extraction de l'ID.",
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
    print("---NŒUD: RÉCUPÉRATION DE LA TRANSCRIPTION---")
    current_log = state.get("log", [])
    current_step = "Récupération de la transcription"
    step_progress = state.get("step_progress", [])
    
    video_id = state.get('video_id', '')
    transcript, error = get_transcript_tool.invoke({"video_id": video_id})
    
    if error:
        return {
            "error_message": error,
            "log": current_log + [f"❌ {error}"],
            "status_message": f"❌ Échec: {error}",
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
    print("---NŒUD: CRÉATION DU RÉSUMÉ---")
    current_log = state.get("log", [])
    current_step = "Création du résumé"
    step_progress = state.get("step_progress", [])
    
    transcript = state.get('transcript', '')
    language = state.get('language', 'english')
    
    print(f"Lancement du résumé en '{language}'...")
    summary, error = summarize_text_tool.invoke({
        "transcript": transcript,
        "language": language
    })
    
    if error:
        return {
            "error_message": error,
            "log": current_log + [f"❌ {error}"],
            "status_message": f"❌ Échec de la création du résumé: {error}",
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
    print("---NŒUD: VÉRIFICATION DE LA LANGUE DU RÉSUMÉ---")
    current_log = state.get("log", [])
    current_step = "Vérification de la langue"
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
        warning_message = f"⚠️ La vérification finale de la langue a échoué ({error}), le résumé original est utilisé."
        print(warning_message)
        # On remplit 'summary' avec la version intermédiaire en cas d'échec de la traduction
        return {
            "summary": summary_to_translate, 
            "log": current_log + [warning_message],
            "status_message": "✅ Résumé terminé (avec un avertissement)."
        }
    
    success_message = f"Langue du résumé :'{target_language}'."
    # On remplit enfin 'summary' avec le résultat final.
    return {
        "summary": final_summary, 
        "log": current_log + [success_message],
        "status_message": "✅ Résumé terminé avec succès!",
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
    print("\nVisualisation du graphe sauvegardée dans le répertoire en tant que agent_workflow.png\n")
except Exception as e:
    print(f"\nImpossible de générer la visualisation. Lancez 'pip install playwright' et 'playwright install'. Erreur: {e}\n")