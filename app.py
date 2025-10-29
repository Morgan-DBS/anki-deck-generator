# app.py - ANKI PRO GRATUIT AVEC OPENROUTER
import streamlit as st
import genanki
import requests
import random
from pathlib import Path

# === TA CLÉ OPENROUTER (gratuite) ===
OPENROUTER_KEY = "5f38e9ee-2221-44ed-8dc2-e873c31264f3"

st.set_page_config(page_title="Anki Pro", page_icon="rocket", layout="wide")

# CSS Pro
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stButton > button {background-color: #007bff; color: white; border-radius: 12px; font-weight: bold;}
    .stButton > button:hover {background-color: #0056b3;}
</style>
""", unsafe_allow_html=True)

st.title("Anki Pro – Decks IA Gratuits !")
st.markdown("**OpenRouter + Grok = cartes intelligentes gratuites**")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Options")
    sujet = st.text_input("Sujet :", "équations second degré")
    niveau = st.selectbox("Niveau :", ["Débutant", "Intermédiaire", "Avancé"])
    nb = st.slider("Cartes :", 50, 300, 100, 50)
    formules = st.checkbox("Formules LaTeX", True)
    qcm = st.checkbox("QCM", True)

with col2:
    st.markdown("### Aperçu")
    if st.button("Générer Deck IA"):
        with st.spinner("Grok crée tes cartes..."):
            # Appel OpenRouter
            prompt = f"Crée {nb} cartes Anki sur '{sujet}'. Niveau {niveau}. Format: Question|Réponse"
            if formules: prompt += ". Utilise LaTeX pour formules."
            if qcm: prompt += " Inclure QCM."
            
            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": st.session_state.get("url", "http://localhost"),
                "X-Title": "Anki Pro"
            }
            data = {
                "model": "xai/grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 3000
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            content = response.json()["choices"][0]["message"]["content"]
            
            # Parse cartes
            cartes = [line.split("|", 1) for line in content.split("\n") if "|" in line]
            
            # Crée deck
            model = genanki.Model(999, 'Pro', fields=[{'name':'f'}, {'name':'b'}],
                                templates=[{'name':'Card', 'qfmt':'{{f}}', 'afmt':'{{b}}'}])
            deck = genanki.Deck(12345, f"{sujet} - {nb} cartes")
            for q, r in cartes[:nb]:
                deck.add_note(genanki.Note(model=model, fields=[q.strip(), r.strip()]))
            
            file = Path("deck.apkg")
            genanki.Package(deck).write_to_file(str(file))
        
        with open(file, "rb") as f:
            st.download_button("Télécharge ton deck !", f, "mon_deck.apkg")
        st.success("Deck IA généré !")
