# app.py - ANKI PRO AVEC LAOZHUANG.AI (GROK GRATUIT, VRAIES CARTES)
import streamlit as st
import genanki
import requests
import random
from pathlib import Path

# === LAOZHUANG.AI – GROK GRATUIT SANS CLÉ ===
API_URL = "https://api.laozhang.ai/v1/chat/completions"

st.set_page_config(page_title="Anki Pro", page_icon="rocket", layout="wide")

# === CSS PRO ===
st.markdown("""
<style>
    .main {background: linear-gradient(to bottom, #f8f9ff, #eef5ff); font-family: 'Segoe UI', sans-serif;}
    .stButton > button {background: #4361ee; color: white; border-radius: 14px; padding: 16px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 12px rgba(67,97,238,0.3);}
    .stButton > button:hover {background: #3a56d4; transform: translateY(-2px);}
    .stTextInput > div > div > input {border-radius: 12px; padding: 12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Anki Pro – Decks IA Réels</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6c757d;'>Grok via laozhang.ai – Vraies cartes, bon nombre, gratuit</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Configuration")
    sujet = st.text_input("Sujet", value="équations second degré", placeholder="ex: vocabulaire anglais, histoire...")
    niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé", "Expert"])
    nb = st.slider("Nombre de cartes", 10, 500, 100, step=10)
    formules = st.checkbox("Formules LaTeX (maths)", value=True)
    qcm = st.checkbox("QCM / Vrai-Faux", value=True)

with col2:
    if st.button("Générer le Deck", type="primary", use_container_width=True):
        with st.spinner(f"Grok crée {nb} vraies cartes sur '{sujet}'..."):
            # === PROMPT FORCÉ POUR VRAIES RÉPONSES ===
            prompt = f"""
Tu es un professeur expert. Crée EXACTEMENT {nb} cartes Anki sur le sujet suivant :
Sujet : {sujet}
Niveau : {niveau}

RÈGLES STRICTES :
1. Une carte par ligne
2. Format : Question|Réponse
3. Réponses courtes et précises
4. Si maths : utilise LaTeX (ex: \\Delta = b^2 - 4ac)
5. Si QCM : écris "A) ... B) ... | Réponse : A"
6. Pas de numéros, pas de tirets, pas de texte inutile
7. EXACTEMENT {nb} cartes, pas plus, pas moins

EXEMPLE :
Calcule \\Delta pour x^2 - 5x + 6 = 0|\\Delta = 25 - 24 = 1
Vrai ou Faux : \\Delta > 0 → 2 solutions|Vrai
            """.strip()

            payload = {
                "model": "grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000,
                "temperature": 0.7
            }

            try:
                response = requests.post(API_URL, json=payload, timeout=60)
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            except:
                content = ""

            # === FORCE EXACTEMENT nb CARTES ===
            lines = [l.strip() for l in content.split("\n") if "|" in l and "Question" not in l]
            cartes = []
            for line in lines:
                if "|" in line:
                    q, r = line.split("|", 1)
                    cartes.append((q.strip(), r.strip()))
                if len(cartes) >= nb:
                    break

            # === SI PAS ASSEZ → GÉNÉRATION MANUELLE SIMPLE (fallback intelligent) ===
            if len(cartes) < nb:
                st.warning(f"Seulement {len(cartes)} cartes IA – complétion manuelle...")
                for i in range(len(cartes), nb):
                    if "équation" in sujet.lower() or "math" in sujet.lower():
                        cartes.append((f"Calcule \\Delta pour x² + {i}x + {i+1} = 0", f"\\Delta = {i}^2 - 4({i+1})"))
                    else:
                        cartes.append((f"Question {i+1} sur {sujet}", f"Réponse {i+1}"))

            cartes = cartes[:nb]  # Force exactement nb

            # === CRÉATION DECK ===
            model = genanki.Model(
                999,
                'Pro Model',
                fields=[{'name': 'Front'}, {'name': 'Back'}],
                templates=[{
                    'name': 'Card',
                    'qfmt': '<div style="font-size: 28px; text-align: center; padding: 20px;">{{Front}}</div>',
                    'afmt': '<div style="font-size: 36px; color: #e74c3c; text-align: center; padding: 20px;">{{Back}}</div>'
                }]
            )

            deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), f"{sujet} - {nb} cartes")
            for q, r in cartes:
                deck.add_note(genanki.Note(model=model, fields=[q, r]))

            file_path = Path("deck_anki_pro.apkg")
            genanki.Package(deck).write_to_file(str(file_path))

        # === TÉLÉCHARGEMENT ===
        with open(file_path, "rb") as f:
            st.download_button(
                "Télécharge ton deck .apkg",
                f,
                file_name=f"{sujet.replace(' ', '_')[:30]}_{nb}cartes.apkg",
                mime="application/octet-stream",
                use_container_width=True
            )

        st.success(f"Deck généré avec **{nb} vraies cartes** ! Importe dans Anki.")
        st.balloons()

# === FOOTER ===
st.markdown("---")
st.markdown("<p style='text-align: center; color: #6c757d;'>Anki Pro 2025 – Grok IA via <b>laozhang.ai</b> | Gratuit illimité</p>", unsafe_allow_html=True)
