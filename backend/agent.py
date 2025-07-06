# /sophia/agent.py
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END

# On importe les fonctions décorées directement, elles agissent comme des outils
from .tools import extract_id_tool, get_transcript_tool, summarize_text_tool

# 1. Définition de l'état du graphe (corrigé)
class GraphState(TypedDict):
    youtube_url: str
    video_id: Optional[str]
    transcript: Optional[str]
    summary: Optional[str]
    error_message: Optional[str]
    log: List[str]
    status_message: str
    current_step: str
    step_progress: List[dict]

# 2. Définition des nœuds (messages de statut améliorés)
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
    
    success_message = f"ID de la vidéo trouvé : {video_id}"
    return {
        "video_id": video_id,
        "log": current_log + [success_message],
        "status_message": "📝 Utilisation de `get_transcript_tool` pour récupérer la transcription...",
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
            "status_message": "❌ Échec de la récupération de la transcription.",
            "current_step": current_step,
            "step_progress": step_progress + [{"step": current_step, "status": "error", "message": error}]
        }
    
    success_message = f"Transcription récupérée avec succès ({len(transcript):,} caractères)"
    return {
        "transcript": transcript,
        "log": current_log + [success_message],
        "status_message": "🧠 Utilisation de `summarize_text_tool` pour résumer le texte...",
        "current_step": current_step,
        "step_progress": step_progress + [{"step": current_step, "status": "success", "message": success_message}]
    }

def node_summarize(state: GraphState) -> dict:
    print("---NŒUD: CRÉATION DU RÉSUMÉ---")
    current_log = state.get("log", [])
    current_step = "Création du résumé"
    step_progress = state.get("step_progress", [])
    
    transcript = state.get('transcript', '')
    summary, error = summarize_text_tool.invoke({"transcript": transcript})
    
    if error:
        return {
            "error_message": error,
            "log": current_log + [f"❌ {error}"],
            "status_message": "❌ Échec de la création du résumé.",
            "current_step": current_step,
            "step_progress": step_progress + [{"step": current_step, "status": "error", "message": error}]
        }
    
    success_message = "Résumé créé avec succès"
    return {
        "summary": summary,
        "log": current_log + [success_message],
        "status_message": "✅ Résumé terminé avec succès!",
        "current_step": current_step,
        "step_progress": step_progress + [{"step": current_step, "status": "success", "message": success_message}]
    }

# Ce nœud sert de point de terminaison propre
def node_final_step(state: GraphState) -> dict:
    print("---NŒUD: ÉTAPE FINALE---")
    # L'état est simplement transmis
    return dict(state)

# 3. Construction et compilation du graphe (MODIFIÉ AVEC ROUTAGE CONDITIONNEL)
workflow = StateGraph(GraphState)

workflow.add_node("extract_id", node_extract_id)
workflow.add_node("get_transcript", node_get_transcript)
workflow.add_node("summarize", node_summarize)
workflow.add_node("final_step", node_final_step)

workflow.set_entry_point("extract_id")

# Logique de branchement en cas d'erreur
def check_for_error(state: GraphState) -> str:
    """Vérifie si un message d'erreur est présent dans l'état."""
    if state.get("error_message"):
        return "error"
    return "continue"

# Arêtes conditionnelles
workflow.add_conditional_edges(
    "extract_id",
    check_for_error,
    {
        "continue": "get_transcript",
        "error": "final_step",
    },
)
workflow.add_conditional_edges(
    "get_transcript",
    check_for_error,
    {
        "continue": "summarize",
        "error": "final_step",
    },
)

# Arête finale : Après la synthèse (réussie ou non), on passe au nœud final
workflow.add_edge("summarize", "final_step")
workflow.add_edge("final_step", END)

# On compile le graphe pour obtenir une application exécutable.
app = workflow.compile()

# Le reste du code est inchangé
try:
    graph = app.get_graph()
    image_bytes = graph.draw_mermaid_png()
    with open("agent_workflow.png", "wb") as f:
        f.write(image_bytes)
    print("\nVisualisation du graph sauvegardée dans le répertoire en tant que agent_workflow.png \n")
except Exception as e:
    print(f"\nJe n'ai pas pu générer la visualisation. Lancez 'pip install playwright' et 'playwright install'. Erreur: {e}\n")