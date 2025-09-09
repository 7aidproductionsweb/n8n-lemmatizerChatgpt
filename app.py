# app.py (version finale, corrigée pour mlconjug3)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# L'import correct pour la bibliothèque mlconjug3
from mlconjug3 import Conjugator

app = FastAPI()

# Initialiser le conjugueur pour le français
conjugator = Conjugator(language='fr')

# ====================================================================
# VOTRE CODE DE LEMMATISATION EXISTANT (INCHANGÉ)
# ====================================================================
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

# ====================================================================
# NOUVELLE FONCTION POUR DÉTECTER LE TEMPS (avec mlconjug3)
# ====================================================================
def detect_verb_tense(word: str) -> dict:
    """Utilise la bibliothèque 'mlconjug3' pour trouver le temps, le mode, etc."""
    try:
        # La méthode 'conjugate' de mlconjug3 peut aussi trouver l'infinitif
        conjugated_verb = conjugator.conjugate(word.lower().strip())
        if conjugated_verb:
            # On extrait les informations de la conjugaison trouvée
            conjugation_info = conjugated_verb.conjug_info
            return {
                "infinitif_mlconjug": conjugated_verb.name, # L'infinitif trouvé par la lib
                "temps": conjugation_info.get('temps'),
                "mode": conjugation_info.get('mode'),
                "personne": conjugation_info.get('personne')
            }
    except Exception:
        pass
    return {"infinitif_mlconjug": None, "temps": None, "mode": None, "personne": None}

# ====================================================================
# MODÈLES DE DONNÉES ET POINTS DE TERMINAISON MIS À JOUR
# ====================================================================
class WordRequest(BaseModel):
    word: str

class AnalysisResponse(BaseModel):
    lemme_perso: str
    infinitif_lib: str | None
    temps: str | None
    mode: str | None
    personne: str | None

@app.post("/analyser", response_model=AnalysisResponse)
async def analyse_word(request: WordRequest):
    """
    Analyse un mot pour retourner son lemme (votre méthode) 
    et son temps (via la bibliothèque 'mlconjug3').
    """
    try:
        lemme_perso = lemmatize_french_verb(request.word)
        tense_info = detect_verb_tense(request.word)
        
        return AnalysisResponse(
            lemme_perso=lemme_perso,
            infinitif_lib=tense_info["infinitif_mlconjug"],
            temps=tense_info["temps"],
            mode=tense_info["mode"],
            personne=tense_info["personne"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
