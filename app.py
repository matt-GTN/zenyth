# /sophia/app.py
import streamlit as st
import os
import time
from dotenv import load_dotenv
from agent import app
from pytube import YouTube

load_dotenv(dotenv_path=".env", override=True)

@st.cache_data(show_spinner=False)
def run_agent_and_get_chunks(_youtube_url):
    """Lance l'agent et retourne la liste complète des chunks du stream."""
    inputs = {
        "youtube_url": _youtube_url, 
        "log": ["▶️ Lancement de l'agent..."],
        "status_message": "🔎 Extraction de l'ID de la vidéo..."
    }
    return list(app.stream(inputs))

st.set_page_config(page_title="Agent Résumé YouTube", page_icon="🤖", layout="wide")
st.title("🤖 Agent de Résumé de Vidéos YouTube")

youtube_url = st.text_input("Collez le lien d'une vidéo YouTube", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Générer le résumé"):
    if youtube_url:
        try:
            yt = YouTube(youtube_url)
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(yt.thumbnail_url, width=200)
            with col2:
                st.subheader(yt.title)
                st.caption(f"par {yt.author} | {round(yt.length / 60)} minutes")
        except Exception as e:
            st.warning("Impossible de récupérer les métadonnées de la vidéo. Lancement du résumé quand même...")

        chunks = run_agent_and_get_chunks(youtube_url)
        
        with st.status("L'agent Sophia travaille...", expanded=True) as status:
            last_log_state = []
            for chunk in chunks:
                # Débogage optionnel : afficher les clés reçues
                # st.write("Chunk keys:", chunk.keys())

                for node_name, state_update in chunk.items():
                    if not state_update:
                        continue
                    if "status_message" in state_update and state_update["status_message"]:
                        status.update(label=state_update["status_message"])
                    if "log" in state_update:
                        new_messages = state_update["log"][len(last_log_state):]
                        for msg in new_messages:
                            st.write(msg)
                        last_log_state = state_update["log"]
                time.sleep(0.05)
            
            status.update(label="🎉 Travail terminé !", state="complete", expanded=False)

        # --- Partie 2 : Récupération et affichage du RÉSULTAT FINAL ---
        final_state = None
        # 1. Tentative standard (si future version gère __end__)
        for chunk in reversed(chunks):
            if "__end__" in chunk:
                final_state = chunk["__end__"]
                break

        # 2. Fallback : on prend le dernier dict avec résumé ou erreur
        if not final_state:
            for chunk in reversed(chunks):
                for key, val in chunk.items():
                    if isinstance(val, dict) and (
                        "summary" in val or "transcript" in val or "error_message" in val
                    ):
                        final_state = val
                        break
                if final_state:
                    break



        if final_state:
            if final_state.get("error_message"):
                st.error(f"Une erreur est survenue : {final_state['error_message']}")
            
            elif final_state.get("summary"):
                st.subheader("📝 Résumé de la vidéo")
                st.markdown(final_state["summary"])
                
                if final_state.get("transcript"):
                    with st.expander("Afficher la transcription complète"):
                        st.text_area("", final_state["transcript"], height=300)
            else:
                st.warning("L'agent a terminé mais n'a pas pu générer de résumé.")
        else:
            st.error("L'agent n'a pas pu terminer son travail correctement car l'état final est introuvable.")
    else:
        st.warning("Veuillez fournir une URL YouTube.")
