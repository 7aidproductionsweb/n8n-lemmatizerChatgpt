from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

try:
    from verbe import Verbe
    VERBE_AVAILABLE = True
except ImportError:
    VERBE_AVAILABLE = False

app = FastAPI()

# Dictionnaires de lemmatisation (corrigés)
VERB_ENDINGS = {
    'ons': 'er', 'ez': 'er', 'ent': 'er', 'es': 'er', 'e': 'er',
    'ais': 'er', 'ait': 'er', 'ions': 'er', 'iez': 'er', 'aient': 'er',
    'ai': 'er', 'as': 'er', 'a': 'er', 'âmes': 'er', 'âtes': 'er', 'èrent': 'er',
    'erai': 'er', 'eras': 'er', 'era': 'er', 'erons': 'er', 'erez': 'er', 'eront': 'er',
    'is': 'ir', 'it': 'ir', 'issons': 'ir', 'issez': 'ir', 'issent': 'ir',
    'issais': 'ir', 'issait': 'ir', 'issions': 'ir', 'issiez': 'ir', 'issaient': 'ir',
    'irai': 'ir', 'iras': 'ir', 'ira': 'ir', 'irons': 'ir', 'irez': 'ir', 'iront': 'ir',
    'ds': 're', 'd': 're', 'dons': 're', 'dez': 're', 'dent': 're',
    's': 're', 't': 're', 'vons': 'voir', 'vez': 'voir', 'vent': 'voir',
}

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

def lemmatize_french_verb(word: str) -> str:
    word = word.lower().strip()
    if word in SPECIAL_CASES:
        return SPECIAL_CASES[word]
    for ending in sorted(VERB_ENDINGS.keys(), key=len, reverse=True):
        if word.endswith(ending) and len(word) > len(ending):
            root = word[:-len(ending)]
            return root + VERB_ENDINGS[ending]
    return word

def detect_verb_tense(word: str) -> dict:
    """Détecte le temps, mode et personne avec fallback sur règles simples."""
    word_clean = word.lower().strip()
    
    # Essai avec bibliothèque verbe d'abord
    if VERBE_AVAILABLE:
        try:
            results = Verbe.search(word_clean)
            if results:
                first_result = results[0]
                return {
                    "temps": first_result.temps,
                    "mode": first_result.mode,
                    "personne": first_result.personne
                }
        except Exception:
            pass
    
    # Fallback : règles basiques par terminaisons
    tense_patterns = {
        # Présent
        ('e', 'es', 'ons', 'ez', 'ent'): "présent",
        ('is', 'it', 'issons', 'issez', 'issent'): "présent",
        ('s', 't', 'vons', 'vez', 'vent'): "présent",
        
        # Imparfait
        ('ais', 'ait', 'ions', 'iez', 'aient'): "imparfait",
        ('issais', 'issait', 'issions', 'issiez', 'issaient'): "imparfait",
        
        # Futur
        ('erai', 'eras', 'era', 'erons', 'erez', 'eront'): "futur",
        ('irai', 'iras', 'ira', 'irons', 'irez', 'iront'): "futur",
        
        # Passé simple
        ('ai', 'as', 'a', 'âmes', 'âtes', 'èrent'): "passé simple"
    }
    
    for endings, tense in tense_patterns.items():
        for ending in endings:
            if word_clean.endswith(ending):
                return {"temps": tense, "mode": "indicatif", "personne": None}
    
    return {"temps": None, "mode": None, "personne": None}

class WordRequest(BaseModel):
    word: str

class AnalysisResponse(BaseModel):
    lemme: str
    temps: Optional[str] = None
    mode: Optional[str] = None
    personne: Optional[int] = None

@app.get("/")
async def root():
    status = "avec détection du temps" if VERBE_AVAILABLE else "lemmatisation seulement"
    return {"message": f"API de lemmatisation française ({status})", "status": "active"}

@app.post("/analyser", response_model=AnalysisResponse)
async def analyse_word(request: WordRequest):
    try:
        lemme = lemmatize_french_verb(request.word)
        tense_info = detect_verb_tense(request.word)
        
        return AnalysisResponse(
            lemme=lemme,
            temps=tense_info["temps"],
            mode=tense_info["mode"],
            personne=tense_info["personne"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lemmatize")  # Garde l'ancien endpoint pour compatibilité
async def lemmatize_word(request: WordRequest):
    try:
        lemma = lemmatize_french_verb(request.word)
        return {"lemma": lemma}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "verbe_library": VERBE_AVAILABLE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
