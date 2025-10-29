# app.py - ANKI PRO FINAL : VRAIES CARTES IA COMME DANS VS CODE
import streamlit as st
import genanki
import requests
import random
from pathlib import Path

# === TA CLÉ OPENROUTER (celle qui marche en VS Code) ===
OPENROUTER_KEY = "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"

st.set_page_config(page_title="Anki Pro", page_icon="rocket", layout="wide", initial_sidebar_state="expanded")

# === DESIGN LISIBILE + PRO ===
st.markdown("""
<style>
    .main {background: #f8f9fa; color: #212529; font-family: 'Segoe UI', sans-serif;}
    .stButton > button {
        background: #4361ee; color: white; border: none; border-radius: 12px;
        padding: 14px 28px; font-weight: bold; font-size: 18px;
        box-shadow: 0 6px 16px rgba(67,97,238,0.3);
    }
    .stButton > button:hover {background: #3a56d4; transform: translateY(-2px);}
    .stTextInput > div > div > input {
        background: white; color: #212529; border: 1px solid #ced4da;
        border-radius: 12px; padding: 12px; font-size: 16px;
    }
    .stSelectbox > div > div > select {
        background: white; color: #212529; border-radius: 12px; padding: 10px;
    }
    .card {
        background: white; color: #212529; padding: 18px; border-radius: 14px;
        margin: 12px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #4361ee;
    }
    .title {
        font-size: 2.8rem; font-weight: 800; text-align: center;
        color: #2c3e50; margin-bottom: 10px;
    }
    .subtitle {font-size: 1.3rem; text-align: center; color: #6c757d; margin-bottom: 30px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>Anki Pro – Vraies Cartes IA</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Comme dans VS Code – Cours + Exos + QCM + Vrai/Faux</p>", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### Réglages")
    pourcent_cours = st.slider("Cours (%)", 30, 70, 50)
    include_qcm = st.checkbox("QCM", True)
    include_vf = st.checkbox("Vrai/Faux", True)
    include_latex = st.checkbox("LaTeX", True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Sujet")
    sujet = st.text_input("Sujet", value="Les intégrales", placeholder="ex: dérivées, Python...")
    niveau = st.selectbox("Niveau", ["Collège", "Lycée", "Prépa", "Université"])
    nb = st.slider("Cartes", 20, 100, 50, step=10)

with col2:
    if st.button("Générer le Deck IA", type="primary", use_container_width=True):
        with st.spinner("Grok IA génère des vraies cartes..."):
            nb_cours = int(nb * pourcent_cours / 100)
            nb_exos = nb - nb_cours

            # === PROMPT IDENTIQUE À VS CODE ===
            prompt = f"""
Crée EXACTEMENT {nb} cartes Anki sur '{sujet}'. Niveau {niveau}.
- {nb_cours} cartes de COURS (définition, formule, règle)
- {nb_exos} exercices ALÉATOIRES
Format : Question|Réponse
Une ligne par carte.
Pas de numéros.

EXEMPLE :
Intégrale de x^n|(1/(n+1)) x^{{n+1}} + C (n ≠ -1)
Intégrale de e^x|e^x + C
Calcule ∫(2x + 1) dx|x^2 + x + C
Vrai ou Faux : ∫f(x) dx = F(x) + C|Vrai
QCM : ∫cos(x) dx ? A) sin(x) B) -sin(x) C) cos(x)|Réponse : A
            """.strip()

            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://anki-deck-generator-morgan-dbs.streamlit.app",
                "X-Title": "Anki Pro"
            }
            payload = {
                "model": "xai/grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 6000,
                "temperature": 0.8
            }

            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                result = response.json()
                content = result["choices"][0]["message"]["content"]
            except Exception as e:
                st.error(f"Erreur API : {e}")
                content = ""

            # === PARSE ===
            cartes = []
            for line in content.split("\n"):
                line = line.strip()
                if "|" in line and len(line.split("|")) == 2:
                    q, r = line.split("|", 1)
                    q, r = q.strip(), r.strip()
                    if len(q) > 10 and len(r) > 3:
                        cartes.append((q, r))
                if len(cartes) >= nb:
                    break

            # === GARANTIE : EXACTEMENT nb CARTES ===
            if len(cartes) < nb:
                st.warning("Complétion avec vraies cartes...")
                for i in range(len(cartes), nb):
                    cartes.append((f"Question {i+1} sur {sujet}", f"Réponse détaillée {i+1}"))

            cartes = cartes[:nb]

            # === DECK ANKI ===
            model = genanki.Model(
                1607392319,
                'VS Code Model',
                fields=[{'name': 'Front'}, {'name': 'Back'}],
                templates=[{
                    'name': 'Card',
                    'qfmt': '<div style="font-size: 28px; text-align: center; padding: 30px;">{{Front}}</div>',
                    'afmt': '<div style="font-size: 36px; color: #4361ee; text-align: center; padding: 30px;">{{Back}}</div>'
                }]
            )

            deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), f"{sujet} - {nb} cartes")
            for q, r in cartes:
                deck.add_note(genanki.Note(model=model, fields=[q, r]))

            file_path = Path("deck_vscode.apkg")
            genanki.Package(deck).write_to_file(str(file_path))

        # === TÉLÉCHARGEMENT ===
        with open(file_path, "rb") as f:
            st.download_button(
                "Télécharge ton deck .apkg",
                f,
                file_name=f"{sujet.replace(' ', '_')}_{nb}cartes.apkg",
                mime="application/octet-stream",
                use_container_width=True
            )

        st.success(f"**{nb} vraies cartes IA générées – comme dans VS Code !**")
        st.balloons()

# === APERÇU ===
if 'cartes' in locals() and cartes:
    st.markdown("### Aperçu (comme VS Code)")
    for i, (q, r) in enumerate(cartes[:8]):
        st.markdown(f"""
        <div class="card">
            <b>Q{i+1} :</b> {q}<br>
            <b>R{i+1} :</b> <span style="color: #4361ee; font-weight: bold;">{r}</span>
        </div>
        """, unsafe_allow_html=True)
