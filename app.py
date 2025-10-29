import streamlit as st
import genanki
import random
from pathlib import Path

st.title("Mon Générateur Anki")

sujet = st.text_input("Sujet :", "équations second degré")
nb = st.slider("Cartes :", 50, 300, 100, 50)

if st.button("Générer !"):
    deck = genanki.Deck(12345, f"{sujet} - {nb} cartes")
    model = genanki.Model(999, 'Simple', fields=[{'name':'f'}, {'name':'b'}],
                          templates=[{'name':'Card', 'qfmt':'{{f}}', 'afmt':'{{b}}'}])
    
    for i in range(nb):
        q = f"Question {i+1} sur {sujet}"
        r = f"Réponse {i+1}"
        deck.add_note(genanki.Note(model=model, fields=[q, r]))
    
    file = Path("deck.apkg")
    genanki.Package(deck).write_to_file(str(file))
    
    with open(file, "rb") as f:
        st.download_button("Télécharge ton deck !", f, "mon_deck.apkg")
    
    st.success("Prêt !")
