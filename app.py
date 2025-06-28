# /sophia/app.py
import streamlit as st
import os
import time
from dotenv import load_dotenv
from agent import app

load_dotenv(dotenv_path=".env", override=True)

# CETTE FONCTION EST SUPPRIMÉE, NOUS APPELERONS L'AGENT DIRECTEMENT
# @st.cache_data(show_spinner=False)
# def run_agent_and_get_chunks(_youtube_url): ...

st.set_page_config(page_title="Agent Résumé YouTube", page_icon="🤖", layout="wide")
st.title("🤖 Agent de Résumé de Vidéos YouTube")
st.markdown("Collez le lien d'une vidéo YouTube et laissez l'agent Sophia analyser et résumer son contenu pour vous.")

youtube_url = st.text_input("Collez le lien d'une vidéo YouTube", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Générer le résumé"):
    if youtube_url:
        st.info(f"Lancement de l'analyse pour : {youtube_url}")

        # PRÉPARATION DE L'AGENT
        inputs = {
            "youtube_url": youtube_url,
            "log": [],
            "status_message": "🔎 Utilisation de `extract_id_tool` pour valider l'URL..."
        }
        
        # On va stocker les chunks ici au fur et à mesure
        all_chunks = []
        
        with st.status("L'agent Sophia travaille...", expanded=True) as status:
            last_log_state = []
            
            status.update(label="▶️ Lancement de l'agent...")
            time.sleep(0.5)
            
            # BOUCLE DE STREAMING EN TEMPS RÉEL
            # On appelle app.stream directement et on boucle sur le générateur
            for chunk in app.stream(inputs):
                # On stocke chaque chunk pour l'utiliser après la boucle
                all_chunks.append(chunk)

                for node_name, state_update in chunk.items():
                    if not state_update:
                        continue
                    
                    # Mise à jour du spinner/status
                    if "status_message" in state_update and state_update["status_message"]:
                        status.update(label=state_update["status_message"])
                    
                    # Affichage des logs en temps réel
                    if "log" in state_update:
                        new_messages = state_update["log"][len(last_log_state):]
                        for msg in new_messages:
                            st.write(msg)
                        last_log_state = state_update["log"]
                
                time.sleep(0.1) # Petite pause pour la fluidité
            
            status.update(label="🎉 Travail terminé !", state="complete", expanded=False)

        # --- Partie 2 : Récupération du RÉSULTAT FINAL ---
        # On utilise maintenant la liste `all_chunks` que nous avons construite
        final_state = None
        for chunk in reversed(all_chunks):
            if "__end__" in chunk:
                final_state = chunk["__end__"]
                break

        if not final_state:
            for chunk in reversed(all_chunks):
                for key, val in chunk.items():
                    if isinstance(val, dict) and (
                        "summary" in val or "transcript" in val or "error_message" in val
                    ):
                        final_state = val
                        break
                if final_state:
                    break

        # Affichage du résultat final
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