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
    lemmas = [t.lemma_ for t in doc if t.pos_ == "VERB"]
    if not lemmas and len(doc):  # fallback raisonnable
        lemmas = [doc[0].lemma_]
    return {"infinitifs": lemmas}
