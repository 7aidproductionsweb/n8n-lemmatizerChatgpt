# app.py (version finale corrigée)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
import spacy

# Initialiser les outils
nlp = spacy.load("fr_core_news_sm")
lemmatizer = FrenchLefffLemmatizer()

app = FastAPI(title="API de Lemmatisation Robuste")

class In(BaseModel):
    text: str

@app.post("/infinitif")
def infinitif(inp: In):
    if not inp.text.strip():
        raise HTTPException(status_code=400, detail="Le champ 'text' ne peut pas être vide.")

    mot = inp.text.strip().split()[0]
    
    # On utilise le nouveau lemmatiseur
    lemme = lemmatizer.lemmatize(mot, 'v')

    if lemme:
        return {"infinitifs": [lemme]}

    # Si le lemmatiseur échoue, on utilise spaCy comme plan B
    doc = nlp(mot)
    if len(doc) > 0:
        return {"infinitifs": [doc[0].lemma_]}
    
    # En dernier recours
    return {"infinitifs": [mot]}
    
