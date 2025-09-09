# app.py (version finale avec lefff)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lefff import Lefff
import spacy

# Initialiser les outils
nlp = spacy.load("fr_core_news_sm")
lemmatizer = Lefff()

app = FastAPI(title="API de Lemmatisation (Robuste)")

class In(BaseModel):
    text: str

@app.post("/infinitif")
def infinitif(inp: In):
    if not inp.text.strip():
        raise HTTPException(status_code=400, detail="Le champ 'text' ne peut pas être vide.")

    mot = inp.text.strip().split()[0] # On ne prend que le premier mot
    
    # 1. On essaie d'abord avec le spécialiste de la conjugaison
    lemme_verbe = lemmatizer.lemmatize(mot, 'v')

    if lemme_verbe:
        # Lefff retourne parfois une liste, on prend le premier
        return {"infinitifs": [lemme_verbe[0]]}

    # 2. Si Lefff échoue, on utilise le lemme de spaCy comme plan B
    doc = nlp(mot)
    if len(doc) > 0:
        return {"infinitifs": [doc[0].lemma_]}
    
    # 3. En dernier recours, si tout échoue
    return {"infinitifs": [mot]}

