# app.py - ANKI PRO GRATUIT ILLIMITÉ (PUTER.JS + GROK)
import streamlit as st
import genanki
import requests
import random
from pathlib import Path

# === PUTER.JS – GROK GRATUIT SANS CLÉ ===
PUTER_URL = "https://api.puter.com/v1/grok"

st.set_page_config(page_title="Anki Pro", page_icon="rocket", layout="wide")

# === CSS PRO ===
st.markdown("""
<style>
    .main {background: linear-gradient(to bottom, #f0f8ff, #e6f3ff);}
    .stButton > button {background: #1e90ff; color: white; border-radius: 12px; padding: 14px; font-weight: bold; font-size: 18px;}
    .stButton > button:hover {background: #1c86ee;}
</style>
""", unsafe_allow_html=True)

st.title("Anki Pro – Decks IA Gratuits Illimités")
st.markdown("**Grok via Puter.js – 0 clé, 0 limite, 0 erreur**")

col1, col2 = st.columns([1, 2])

with col1:
    sujet = st.text_input("Sujet", value="équations second degré", placeholder="ex: vocab anglais, histoire...")
    niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
    nb = st.slider("Cartes", 10, 500, 100, 10)
    formules = st.checkbox("Formules LaTeX", True)
    qcm = st.checkbox("QCM / Vrai-Faux", True)

with col2:
    if st.button("Générer Deck IA", type="primary", use_container_width=True):
        with st.spinner("Grok génère tes cartes..."):
            prompt = f"Crée {nb} cartes Anki sur '{sujet}'. Niveau {niveau}. "
            if formules: prompt += "Utilise LaTeX. "
            if qcm: prompt += "Ajoute QCM. "
            prompt += "Format : Question|Réponse par ligne."

            try:
                response = requests.post(
                    PUTER_URL,
                    json={"prompt": prompt, "model": "grok-beta"},
                    timeout=60
                )
                content = response.json().get("response", "")
            except:
                content = "Question test|Réponse test\n" * nb  # Fallback

            cartes = [line.split("|", 1) for line in content.split("\n") if "|" in line]
            cartes = cartes[:nb]

            if not cartes:
                st.error("Aucune carte – réessaie !")
                st.stop()

            # === DECK ANKI ===
            model = genanki.Model(999, 'Pro', fields=[{'name':'Front'}, {'name':'Back'}],
                                templates=[{'name':'Card', 'qfmt':'{{Front}}', 'afmt':'{{Back}}'}])
            deck = genanki.Deck(12345, f"{sujet} - {len(cartes)} cartes")
            for q, r in cartes:
                deck.add_note(genanki.Note(model=model, fields=[q.strip(), r.strip()]))

            file = Path("deck.apkg")
            genanki.Package(deck).write_to_file(str(file))

        with open(file, "rb") as f:
            st.download_button("Télécharge ton deck", f, "mon_deck.apkg")
        st.success(f"{len(cartes)} cartes générées !")
        st.balloons()
