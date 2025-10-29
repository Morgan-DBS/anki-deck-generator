# app.py - ANKI PRO GRATUIT AVEC OPENROUTER (FIX 401 USER NOT FOUND)
import streamlit as st
import genanki
import requests
import random
from pathlib import Path

# === TA CLÉ OPENROUTER (GRATUITE) ===
OPENROUTER_KEY = "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"

# === CONFIG PAGE ===
st.set_page_config(
    page_title="Anki Pro Generator",
    page_icon="rocket",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS PRO MODERNE ===
st.markdown("""
<style>
    .main {background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif;}
    .stButton > button {background: linear-gradient(45deg, #007bff, #0056b3); color: white; border: none; border-radius: 12px; padding: 12px 24px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);}
    .stButton > button:hover {background: #0056b3; transform: translateY(-2px);}
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {border-radius: 10px; border: 1px solid #ced4da;}
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Anki Pro Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6c757d;'>Grok IA via OpenRouter – Decks intelligents gratuits</p>", unsafe_allow_html=True)

# === LAYOUT ===
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Configuration")
    
    sujet = st.text_input("Sujet", placeholder="ex: équations second degré", value="équations second degré")
    niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé", "Expert"])
    
    nb = st.slider("Cartes", 10, 300, 100, step=10)
    
    formules = st.checkbox("Formules LaTeX", value=True)
    qcm = st.checkbox("QCM / Vrai-Faux", value=True)
    
    if st.button("Auto Optimal"):
        nb = random.choice([80, 100, 150, 200])
        st.success(f"Optimal : {nb} cartes")

with col2:
    st.markdown("### Génération")
    
    if st.button("Générer Deck IA", type="primary", use_container_width=True):
        if nb > 300:
            st.error("Limite gratuite : 300 cartes max")
            st.stop()
            
        with st.spinner("Grok IA génère... (10-30s)"):
            # === PROMPT ===
            prompt = f"Crée {nb} cartes Anki sur '{sujet}'. Niveau {niveau}. "
            if formules: prompt += "LaTeX pour formules. "
            if qcm: prompt += "QCM/Vrai-Faux. "
            prompt += "Format : Question|Réponse par ligne. Ex: Δ ?|b²-4ac"

            # === HEADERS FIXÉS POUR 401 ===
            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://anki-deck-generator-morgan-dbs.streamlit.app",  # Ton URL exacte
                "X-Title": "Anki Pro Generator"  # Titre app
            }
            payload = {
                "model": "xai/grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000,
                "temperature": 0.7
            }

            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                # === DEBUG COMPLET ===
                st.markdown("**Réponse API (debug) :**")
                st.json(response.json() if response.status_code == 200 else {"error": response.text}, expanded=False)

                if response.status_code != 200:
                    st.error(f"Erreur {response.status_code}: {response.text}")
                    st.stop()

                result = response.json()
                if "choices" not in result or not result["choices"]:
                    st.error("Pas de cartes. Vérifie compte OpenRouter (crédits ?)")
                    st.stop()

                content = result["choices"][0]["message"]["content"]

            except Exception as e:
                st.error(f"Erreur : {e}")
                st.stop()

            # === PARSE CARTES ===
            cartes = []
            for line in content.split("\n"):
                line = line.strip()
                if "|" in line:
                    parts = line.split("|", 1)
                    if len(parts) == 2:
                        q, r = parts[0].strip(), parts[1].strip()
                        if q and r:
                            cartes.append((q, r))
            
            if not cartes:
                st.error("Aucune carte valide. Réessaie avec un sujet simple.")
                st.stop()

            # === DECK ANKI ===
            model = genanki.Model(
                1607392319,
                'Pro',
                fields=[{'name': 'Front'}, {'name': 'Back'}],
                templates=[{'name': 'Card', 'qfmt': '{{Front}}', 'afmt': '{{Back}}'}]
            )

            deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), f"{sujet} - {len(cartes)} cartes")
            for q, r in cartes[:nb]:
                deck.add_note(genanki.Note(model=model, fields=[q, r]))

            file_path = Path("deck.apkg")
            genanki.Package(deck).write_to_file(str(file_path))

        # === DOWNLOAD ===
        with open(file_path, "rb") as f:
            st.download_button("Télécharge .apkg", f, f"{sujet.replace(' ', '_')}.apkg")
        
        st.success(f"✅ {len(cartes)} cartes IA ! Importe dans Anki.")
        st.balloons()

# === FOOTER ===
st.markdown("---")
st.markdown("<p style='text-align: center; color: #6c757d;'>Anki Pro 2025 – Powered by Grok xAI via OpenRouter | Gratuit pour test</p>", unsafe_allow_html=True)
