# /sophia/agent.py
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END

# On importe les fonctions décorées directement, elles agissent comme des outils
from tools import extract_id_tool, get_transcript_tool, summarize_text_tool

# 1. Définition de l'état du graphe (inchangé)
class GraphState(TypedDict):
    youtube_url: str
    video_id: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    error_message: Optional[str] = None
    log: List[str]
    status_message: str

# 2. Définition des nœuds (inchangés, sauf un ajout)
def node_extract_id(state: GraphState) -> dict:
    print("---NŒUD: EXTRACTION DE L'ID---")
    current_log = state.get("log", [])
    
    url = state['youtube_url']
    video_id = extract_id_tool.invoke({"youtube_url": url})
    
    if not video_id:
        error_message = "URL YouTube invalide ou ID non trouvé."
        return {
            "error_message": error_message,
            "log": current_log + [f"❌ {error_message}"],
            "status_message": "❌ Échec de l'extraction."
        }
    
    success_message = f"✅ ID de la vidéo trouvé : {video_id}"
    return {
        "video_id": video_id,
        "log": current_log + [success_message],
        "status_message": "📝 Récupération de la transcription..."
    }

def node_get_transcript(state: GraphState) -> dict:
    print("---NŒUD: RÉCUPÉRATION DE LA TRANSCRIPTION---")
    current_log = state.get("log", [])
    
    video_id = state['video_id']
    transcript, error = get_transcript_tool.invoke({"video_id": video_id})
    
    if error:
        return {
            "error_message": error,
            "log": current_log + [f"❌ Erreur de transcription : {error}"],
            "status_message": "❌ Échec de la transcription."
        }
    
    success_message = f"✅ Transcription récupérée ({len(transcript):,} caractères)."
    return {
        "transcript": transcript,
        "log": current_log + [success_message],
        "status_message": "🧠 Lancement de la synthèse..."
    }

def node_summarize(state: GraphState) -> dict:
    print("---NŒUD: GÉNÉRATION DU RÉSUMÉ---")
    current_log = state.get("log", [])
    
    transcript = state['transcript']
    summary, error = summarize_text_tool.invoke({"transcript": transcript})
    
    if error:
        return {
            "error_message": error,
            "log": current_log + [f"❌ {error}"],
            "status_message": "❌ Échec de la synthèse."
        }

    success_message = "✅ Résumé généré avec succès !"
    return {
        "summary": summary,
        "log": current_log + [success_message],
        "status_message": "🎉 Travail terminé !"
    }

# NOUVEAU NŒUD FINAL : Il ne fait rien, mais sert de point de terminaison stable.
def node_final_step(state: GraphState) -> dict:
    print("---NŒUD: ÉTAPE FINALE---")
    return {
        "summary": state.get("summary"),
        "transcript": state.get("transcript"),
        "error_message": state.get("error_message"),
        "log": state.get("log"),
        "status_message": "🎉 Travail terminé !"
    }



# 3. Construction et compilation du graphe (VERSION CORRIGÉE)
workflow = StateGraph(GraphState)

workflow.add_node("extract_id", node_extract_id)
workflow.add_node("get_transcript", node_get_transcript)
workflow.add_node("summarize", node_summarize)
workflow.add_node("final_step", node_final_step)


workflow.set_entry_point("extract_id")

def should_continue(state: GraphState) -> str:
    """Détermine s'il faut continuer le processus ou s'arrêter à cause d'une erreur."""
    if state.get("error_message"):
        return "end_with_error"
    else:
        return "continue"

# Arête 1 : Après l'extraction d'ID
workflow.add_edge("extract_id", "get_transcript")

# Arête 2 : Après la récupération de la transcription
workflow.add_edge("get_transcript", "summarize")

# Arête 3 : Après la synthèse, on passe au nœud final
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