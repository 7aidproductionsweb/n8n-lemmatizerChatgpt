from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()

# Dictionnaire simple des terminaisons de verbes français
VERB_ENDINGS = {
    # Verbes du 1er groupe (-er)
    'ons': 'er', 'ez': 'er', 'ent': 'er', 'es': 'er', 'e': 'er',
    'ais': 'er', 'ait': 'er', 'ions': 'er', 'iez': 'er', 'aient': 'er',
    'ai': 'er', 'as': 'er', 'a': 'er', 'âmes': 'er', 'âtes': 'er', 'èrent': 'er',
    'erai': 'er', 'eras': 'er', 'era': 'er', 'erons': 'er', 'erez': 'er', 'eront': 'er',
    
    # Verbes du 2ème groupe (-ir)
    'is': 'ir', 'it': 'ir', 'issons': 'ir', 'issez': 'ir', 'issent': 'ir',
    'issais': 'ir', 'issait': 'ir', 'issions': 'ir', 'issiez': 'ir', 'issaient': 'ir',
    'irai': 'ir', 'iras': 'ir', 'ira': 'ir', 'irons': 'ir', 'irez': 'ir', 'iront': 'ir',
    
    # Verbes du 3ème groupe (irréguliers les plus courants)
    'ds': 're', 'd': 're', 'dons': 're', 'dez': 're', 'dent': 're',
    's': 're', 't': 're', 'vons': 'voir', 'vez': 'voir', 'vent': 'voir',
}

# Cas spéciaux fréquents
SPECIAL_CASES = {
    'suis': 'être', 'es': 'être', 'est': 'être', 'sommes': 'être', 'êtes': 'être', 'sont': 'être',
    'étais': 'être', 'était': 'être', 'étions': 'être', 'étiez': 'être', 'étaient': 'être',
    'fus': 'être', 'fut': 'être', 'fûmes': 'être', 'fûtes': 'être', 'furent': 'être',
    'ai': 'avoir', 'as': 'avoir', 'a': 'avoir', 'avons': 'avoir', 'avez': 'avoir', 'ont': 'avoir',
    'avais': 'avoir', 'avait': 'avoir', 'avions': 'avoir', 'aviez': 'avoir', 'avaient': 'avoir',
    'eus': 'avoir', 'eut': 'avoir', 'eûmes': 'avoir', 'eûtes': 'avoir', 'eurent': 'avoir',
    'vais': 'aller', 'va': 'aller', 'allons': 'aller', 'allez': 'aller', 'vont': 'aller',
    'fais': 'faire', 'fait': 'faire', 'faisons': 'faire', 'faites': 'faire', 'font': 'faire',
    'dis': 'dire', 'dit': 'dire', 'disons': 'dire', 'dites': 'dire', 'disent': 'dire',
    'veux': 'vouloir', 'veut': 'vouloir', 'voulons': 'vouloir', 'voulez': 'vouloir', 'veulent': 'vouloir',
    'peux': 'pouvoir', 'peut': 'pouvoir', 'pouvons': 'pouvoir', 'pouvez': 'pouvoir', 'peuvent': 'pouvoir',
    'sais': 'savoir', 'sait': 'savoir', 'savons': 'savoir', 'savez': 'savoir', 'savent': 'savoir',
    'mangeons': 'manger', 'mangez': 'manger', 'mangent': 'manger',
}

class WordRequest(BaseModel):
    word: str

class WordResponse(BaseModel):
    lemma: str

def lemmatize_french_verb(word: str) -> str:
    word = word.lower().strip()
    
    # Cas spéciaux
    if word in SPECIAL_CASES:
        return SPECIAL_CASES[word]
    
    # Recherche par terminaisons (du plus long au plus court)
    for ending in sorted(VERB_ENDINGS.keys(), key=len, reverse=True):
        if word.endswith(ending) and len(word) > len(ending):
            root = word[:-len(ending)]
            return root + VERB_ENDINGS[ending]
    
    # Si aucune règle ne s'applique, retourner le mot tel quel
    return word

@app.get("/")
async def root():
    return {"message": "API de lemmatisation française", "status": "active"}

@app.post("/lemmatize", response_model=WordResponse)
async def lemmatize_word(request: WordRequest):
    try:
        lemma = lemmatize_french_verb(request.word)
        return WordResponse(lemma=lemma)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
