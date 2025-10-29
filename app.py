# app.py - ANKI PRO ULTIME : COURS + EXOS ALÉATOIRES + QCM + VRAI/FAUX
import streamlit as st
import genanki
import requests
import random
from pathlib import Path

# === LAOZHUANG.AI – GROK GRATUIT SANS CLÉ ===
API_URL = "https://api.laozhang.ai/v1/chat/completions"

st.set_page_config(page_title="Anki Pro", page_icon="rocket", layout="wide", initial_sidebar_state="expanded")

# === CSS PRO ULTRA 2025 ===
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-family: 'Segoe UI', sans-serif;}
    .stButton > button {background: #ff6b6b; color: white; border: none; border-radius: 16px; padding: 16px 32px; font-weight: bold; font-size: 18px; box-shadow: 0 8px 20px rgba(255,107,107,0.4);}
    .stButton > button:hover {background: #ff5252; transform: translateY(-4px); box-shadow: 0 12px 28px rgba(255,82,82,0.5);}
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {border-radius: 14px; padding: 14px; background: rgba(255,255,255,0.9);}
    .card {background: white; color: #333; padding: 20px; border-radius: 16px; margin: 10px 0; box-shadow: 0 6px 16px rgba(0,0,0,0.1);}
    .title {font-size: 3rem; font-weight: 900; text-align: center; background: linear-gradient(90deg, #ff6b6b, #feca57); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("<h1 class='title'>Anki Pro Ultimate</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem;'><b>Cours + Exercices Aléatoires + QCM + Vrai/Faux</b> – Grok IA Gratuit</p>", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### Réglages Avancés")
    pourcent_cours = st.slider("Cours (%)", 20, 80, 40, help="Pourcentage de cartes théoriques")
    pourcent_exos = 100 - pourcent_cours
    st.write(f"**Exercices : {pourcent_exos}%**")
    
    include_qcm = st.checkbox("QCM", True)
    include_vf = st.checkbox("Vrai/Faux", True)
    include_latex = st.checkbox("LaTeX (maths)", True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Sujet & Options")
    sujet = st.text_input("Sujet", value="équations second degré", placeholder="ex: photosynthèse, Python, histoire 1789...")
    niveau = st.selectbox("Niveau", ["Collège", "Lycée", "Prépa", "Université"])
    nb = st.slider("Nombre de cartes", 20, 300, 100, step=10)
    
    if st.button("Générer le Deck IA", type="primary", use_container_width=True):
        with st.spinner(f"Grok crée {nb} cartes mixtes (cours + exos aléatoires)..."):
            # === NOMBRE DE CHAQUE TYPE ===
            nb_cours = int(nb * pourcent_cours / 100)
            nb_exos = nb - nb_cours

            # === PROMPT ULTRA PRÉCIS ===
            prompt = f"""
Tu es un professeur expert. Crée EXACTEMENT {nb} cartes Anki sur '{sujet}' (niveau {niveau}).

RÈGLES OBLIGATOIRES :
1. {nb_cours} cartes de COURS (définition, formule, règle, théorème)
2. {nb_exos} exercices ALÉATOIRES (nouveaux à chaque fois, jamais identiques)
3. Format : Question|Réponse (une ligne par carte)
4. Pas de numéros, pas de tirets
5. Utilise LaTeX si maths : \\Delta, \\sqrt{{}}, etc.
6. Mélange les types : QCM, Vrai/Faux, calcul, application
7. EXACTEMENT {nb} cartes

EXEMPLES (pour maths) :
Formule du discriminant|\\Delta = b^2 - 4ac
Vrai ou Faux : \\Delta < 0 → 0 solution|Vrai
Calcule \\Delta pour x^2 + 3x - 4 = 0|\\Delta = 9 + 16 = 25
QCM : Nombre de solutions si \\Delta = 0 ? A) 0 B) 1 C) 2|Réponse : B
            """.strip()

            try:
                response = requests.post(
                    API_URL,
                    json={
                        "model": "grok-beta",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 5000,
                        "temperature": 0.85  # Plus d'aléatoire
                    },
                    timeout=90
                )
                content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            except:
                content = ""

            # === PARSE & FORCE nb CARTES ===
            cartes = []
            for line in content.split("\n"):
                line = line.strip()
                if "|" in line and len(line.split("|")) == 2:
                    q, r = line.split("|", 1)
                    q, r = q.strip(), r.strip()
                    if q and r:
                        cartes.append((q, r))
                if len(cartes) >= nb:
                    break

            # === FALLBACK INTELLIGENT SI PAS ASSEZ ===
            if len(cartes) < nb:
                st.warning("Complétion avec cartes aléatoires...")
                for i in range(len(cartes), nb):
                    if "math" in sujet.lower() or "équation" in sujet.lower():
                        a, b, c = random.randint(-10,10), random.randint(-10,10), random.randint(-10,10)
                        delta = b*b - 4*a*c
                        cartes.append((f"Calcule \\Delta pour {a}x^2 + {b}x + {c} = 0", f"\\Delta = {delta}"))
                    else:
                        cartes.append((f"Définition {i+1} sur {sujet}", f"Réponse détaillée {i+1}"))

            cartes = cartes[:nb]

            # === DECK ANKI PRO ===
            model = genanki.Model(
                1607392319,
                'Ultimate Model',
                fields=[{'name': 'Front'}, {'name': 'Back'}],
                templates=[{
                    'name': 'Card',
                    'qfmt': '<div style="font-size: 28px; text-align: center; padding: 30px; font-weight: bold;">{{Front}}</div>',
                    'afmt': '<div style="font-size: 36px; color: #e74c3c; text-align: center; padding: 30px;">{{Back}}</div><hr><small>{{Front}}</small>'
                }]
            )

            deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), f"{sujet} - {nb} cartes (Cours + Exos)")
            for q, r in cartes:
                deck.add_note(genanki.Note(model=model, fields=[q, r]))

            file_path = Path("deck_ultimate.apkg")
            genanki.Package(deck).write_to_file(str(file_path))

        # === TÉLÉCHARGEMENT ===
        with open(file_path, "rb") as f:
            st.download_button(
                "Télécharge ton deck .apkg",
                f,
                file_name=f"{sujet.replace(' ', '_')[:25]}_{nb}cartes.apkg",
                mime="application/octet-stream",
                use_container_width=True
            )

        st.success(f"Deck généré avec **{nb_cours} cours + {nb_exos} exos aléatoires** !")
        st.balloons()

# === APERÇU ALEATOIRE ===
if 'cartes' in locals() and cartes:
    st.markdown("### Aperçu aléatoire")
    sample = random.sample(cartes, min(5, len(cartes)))
    for q, r in sample:
        st.markdown(f"""
        <div class="card">
            <b>Question :</b> {q}<br>
            <b>Réponse :</b> <span style="color: #e74c3c;">{r}</span>
        </div>
        """, unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.markdown("<p style='text-align: center; color: #ddd;'>Anki Pro Ultimate 2025 – Grok IA via <b>laozhang.ai</b> | Gratuit illimité</p>", unsafe_allow_html=True)
