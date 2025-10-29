# app.py - ANKI PRO GRATUIT AVEC OPENROUTER (GROK IA)
import streamlit as st
import genanki
import requests
import random
from pathlib import Path

# === TA CLÉ OPENROUTER (GRATUITE) ===
# → Remplace si besoin sur https://openrouter.ai/keys
OPENROUTER_KEY = "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"

# === CONFIG PAGE ===
st.set_page_config(
    page_title="Anki Pro Generator",
    page_icon="rocket",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS PRO MODERNE (2025) ===
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton > button {
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 4px 12px rgba(0,123,255,0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #0056b3;
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,123,255,0.4);
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #ced4da;
        padding: 10px;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        margin: 10px 0;
    }
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #007bff, #0056b3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER PRO ===
st.markdown("<h1 class='header-title'>Anki Pro Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6c757d; font-size: 1.2rem;'>"
            "<b>Grok IA</b> via OpenRouter – Decks intelligents générés en 20s</p>", 
            unsafe_allow_html=True)

# === LAYOUT PRINCIPAL ===
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Configuration du Deck")
    
    sujet = st.text_input(
        "Sujet",
        placeholder="ex: équations second degré, vocabulaire anglais B1, histoire de France...",
        value="équations second degré"
    )
    
    niveau = st.selectbox(
        "Niveau",
        ["Débutant", "Intermédiaire", "Avancé", "Expert"]
    )
    
    st.markdown("#### Nombre de cartes")
    nb = st.slider(
        "Cartes à générer",
        min_value=10,
        max_value=300,
        value=100,
        step=10,
        help="Gratuit jusqu'à 300 cartes"
    )
    
    st.markdown("#### Options avancées")
    formules = st.checkbox("Formules en LaTeX (pour les maths)", value=True)
    qcm = st.checkbox("QCM / Vrai-Faux", value=True)
    
    if st.button("Auto : Choisir le nombre optimal", key="auto"):
        nb = random.choice([80, 100, 120, 150, 200])
        st.success(f"Nombre optimal sélectionné : **{nb} cartes**")

with col2:
    st.markdown("### Aperçu & Génération")
    
    if st.button("Générer Deck IA", type="primary", use_container_width=True):
        if nb > 300:
            st.error("Limite gratuite : 300 cartes maximum")
            st.stop()
            
        with st.spinner("Grok IA génère vos cartes... (10-30s)"):
            # === PROMPT INTELLIGENT ===
            prompt = f"Crée exactement {nb} cartes Anki sur le sujet '{sujet}'. "
            prompt += f"Niveau : {niveau}. "
            if formules:
                prompt += "Utilise LaTeX pour les formules mathématiques (ex: \\Delta = b^2 - 4ac). "
            if qcm:
                prompt += "Inclue des questions QCM ou Vrai/Faux. "
            prompt += ("Format strict : une carte par ligne, séparée par | → "
                      "Question|Réponse. Exemple : Quel est Δ ?|\\Delta = b^2 - 4ac")

            # === APPEL OPENROUTER ===
            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://anki-deck-generator-morgan-dbs.streamlit.app",
                "X-Title": "Anki Pro Generator"
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

                # === DEBUG AFFICHÉ (en cas d'erreur) ===
                st.markdown("**Réponse API (debug) :**")
                try:
                    json_resp = response.json()
                    st.json(json_resp, expanded=False)
                except:
                    st.code(response.text, language="text")

                # === VÉRIFICATION ERREUR ===
                if response.status_code != 200:
                    st.error(f"Erreur API {response.status_code} : {response.text}")
                    st.stop()

                result = response.json()
                if "choices" not in result or not result["choices"]:
                    st.error("Aucune carte générée. Vérifiez votre clé OpenRouter.")
                    st.stop()

                content = result["choices"][0]["message"]["content"]

            except Exception as e:
                st.error(f"Erreur réseau ou timeout : {e}")
                st.stop()

            # === PARSE DES CARTES ===
            cartes = []
            for line in content.split("\n"):
                line = line.strip()
                if "|" in line and not line.startswith("#"):
                    parts = line.split("|", 1)
                    if len(parts) == 2:
                        q, r = parts[0].strip(), parts[1].strip()
                        if q and r:
                            cartes.append((q, r))
            
            cartes = cartes[:nb]  # Limite au nombre demandé
            if len(cartes) == 0:
                st.error("Aucune carte valide générée. Essayez un autre sujet.")
                st.stop()

            # === CRÉATION DU DECK ANKI ===
            model = genanki.Model(
                1607392319,
                'Anki Pro Model',
                fields=[{'name': 'Front'}, {'name': 'Back'}],
                templates=[{
                    'name': 'Card 1',
                    'qfmt': '<div style="font-size: 26px; text-align: center; padding: 20px;">{{Front}}</div>',
                    'afmt': '<div style="font-size: 34px; color: #e74c3c; text-align: center; padding: 20px;">{{Back}}</div><hr><small>{{Front}}</small>'
                }]
            )

            deck_id = random.randrange(1 << 30, 1 << 31)
            deck = genanki.Deck(deck_id, f"{sujet} - {len(cartes)} cartes (IA)")

            for q, r in cartes:
                note = genanki.Note(model=model, fields=[q, r])
                deck.add_note(note)

            file_path = Path("deck_anki_pro.apkg")
            genanki.Package(deck).write_to_file(str(file_path))

        # === TÉLÉCHARGEMENT ===
        with open(file_path, "rb") as f:
            st.download_button(
                label="Télécharge ton deck .apkg",
                data=f,
                file_name=f"{sujet.replace(' ', '_')[:25]}_{len(cartes)}cartes.apkg",
                mime="application/octet-stream",
                use_container_width=True
            )
        
        st.success(f"Deck généré avec **{len(cartes)} cartes IA** ! Importe dans Anki.")
        st.balloons()

# === FOOTER ===
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #6c757d; font-size: 0.9rem;'>"
    "Anki Pro 2025 – IA <b>Grok</b> via <a href='https://openrouter.ai' target='_blank'>OpenRouter</a> | "
    "Gratuit pour test | Prochainement : <b>Premium 4,99€/mois</b>"
    "</p>",
    unsafe_allow_html=True
)
