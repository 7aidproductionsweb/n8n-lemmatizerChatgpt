# app.py (version corrigée et simplifiée)
from fastapi import FastAPI
from pydantic import BaseModel
import spacy

nlp = spacy.load("fr_core_news_sm")
app = FastAPI()

class In(BaseModel):
    text: str

@app.post("/infinitif")
def infinitif(inp: In):
    doc = nlp(inp.text)
    
    # On prend simplement le lemme du premier mot. C'est tout.
    # C'est plus robuste car même si spaCy se trompe de catégorie (verbe/nom),
    # le lemme est souvent correct.
    if len(doc) > 0:
        lemmas = [doc[0].lemma_]
    else:
        lemmas = [] # Gère le cas où le texte est vide

    return {"infinitifs": lemmas}
