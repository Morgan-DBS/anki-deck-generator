# app.py - ANKI PRO GRATUIT AVEC OPENROUTER (GROK IA)
import streamlit as st
import genanki
import requests
import random
from pathlib import Path

# === TA CLÉ OPENROUTER (gratuite) ===
# → Remplace par ta clé de https://openrouter.ai/keys
OPENROUTER_KEY = "5f38e9ee-2221-44ed-8dc2-e873c31264f3"  # ← CHANGE ÇA SI ERREUR

# === CONFIG PAGE ===
st.set_page_config(
    page_title="Anki Pro Generator",
    page_icon="rocket",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS PRO (bleu moderne) ===
st.markdown("""
<style>
    .main {background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif;}
    .stButton > button {
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white; border: none; border-radius: 12px;
        padding: 12px 24px; font-weight: bold; font-size: 16px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {background: #0056b3; transform: translateY(-2px);}
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 10px; border: 1px solid #ced4da;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Anki Pro – Decks IA Gratuits</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6c757d;'>Générés par <b>Grok</b> via OpenRouter – 100% gratuit pour tester</p>", unsafe_allow_html=True)

# === LAYOUT ===
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Configuration")
    
    sujet = st.text_input("Sujet", placeholder="ex: équations second degré, vocab anglais B1...", value="équations second degré")
    niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé", "Expert"])
    
    st.markdown("#### Nombre de cartes")
    nb = st.slider("Cartes", 10, 300, 100, step=10, help="Gratuit jusqu'à 300")
    
    st.markdown("#### Options")
    formules = st.checkbox("Formules en LaTeX (maths)", value=True)
    qcm = st.checkbox("QCM / Vrai-Faux", value=True)
    
    auto = st.button("Auto : Choisir le meilleur nombre")
    if auto:
        nb = random.choice([80, 100, 120, 150])
        st.success(f"Optimal : {nb} cartes")

with col2:
    st.markdown("### Aperçu & Génération")
    
    if st.button("Générer Deck IA", type="primary", use_container_width=True):
        if nb > 300:
            st.error("Limite gratuite : 300 cartes max")
            st.stop()
            
        with st.spinner("Grok IA génère tes cartes... (10-20s)"):
            # === PROMPT INTELLIGENT ===
            prompt = f"Crée exactement {nb} cartes Anki sur '{sujet}'. Niveau {niveau}. "
            if formules: prompt += "Utilise LaTeX pour formules. "
            if qcm: prompt += "Ajoute des QCM ou Vrai/Faux. "
            prompt += "Format strict : Question|Réponse (une ligne par carte). Exemple : Quel est Δ ?|Δ = b² - 4ac"

            # === APPEL OPENROUTER ===
            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://anki-deck-generator-morgan-dbs.streamlit.app",
                "X-Title": "Anki Pro"
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

                # === DEBUG AFFICHÉ ===
                st.markdown("**Réponse API (debug) :**")
                try:
                    json_resp = response.json()
                    st.json(json_resp, expanded=False)
                except:
                    st.code(response.text)

                # === VÉRIF SI ERREUR ===
                if response.status_code != 200:
                    st.error(f"Erreur {response.status_code} : {response.text}")
                    st.stop()

                result = response.json()
                if "choices" not in result or not result["choices"]:
                    st.error("Aucune carte générée. Clé invalide ou limite atteinte.")
                    st.stop()

                content = result["choices"][0]["message"]["content"]

            except Exception as e:
                st.error(f"Erreur réseau : {e}")
                st.stop()

            # === PARSE CARTES ===
            cartes = []
            for line in content.split("\n"):
                if "|" in line:
                    q, r = line.split("|", 1)
                    cartes.append((q.strip(), r.strip()))
            
            if len(cartes) < nb:
                st.warning(f"Seulement {len(cartes)} cartes générées (sur {nb} demandées)")

            # === CRÉATION DECK ANKI ===
            model = genanki.Model(
                1607392319,
                'Pro Model',
                fields=[{'name': 'Front'}, {'name': 'Back'}],
                templates=[{
                    'name': 'Card 1',
                    'qfmt': '<div style="font-size: 24px; text-align: center;">{{Front}}</div>',
                    'afmt': '<div style="font-size: 32px; color: #e74c3c; text-align: center;">{{Back}}</div>'
                }]
            )

            deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), f"{sujet} - {len(cartes)} cartes")
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
                file_name=f"{sujet.replace(' ', '_')[:30]}.apkg",
                mime="application/octet-stream",
                use_container_width=True
            )
        
        st.success(f"Deck généré avec {len(cartes)} cartes IA ! Importe dans Anki.")
        st.balloons()

# === FOOTER ===
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #6c757d;'>"
    "Anki Pro 2025 – IA Grok via <a href='https://openrouter.ai' target='_blank'>OpenRouter</a> | "
    "Gratuit pour test | Prochainement : abonnements Premium"
    "</p>",
    unsafe_allow_html=True
)
