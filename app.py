# app.py (nouvelle approche avec la bibliothèque "verbe")
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from verbe import Verbe

app = FastAPI(title="API d'Analyse de Verbes")

class In(BaseModel):
    text: str

class Out(BaseModel):
    infinitif: str | None
    temps: str | None
    mode: str | None
    personne: str | None
    erreur: str | None

@app.post("/analyser-verbe", response_model=Out)
def analyser_verbe(inp: In):
    """
    Analyse un verbe conjugué pour trouver son infinitif, son temps, son mode et sa personne.
    """
    if not inp.text.strip():
        raise HTTPException(status_code=400, detail="Le champ 'text' ne peut pas être vide.")

    mot = inp.text.strip().split()[0]

    try:
        # On recherche toutes les formes possibles pour le mot donné
        resultats = Verbe.search(mot)

        if not resultats:
            return Out(erreur=f"Le mot '{mot}' n'a pas été reconnu comme une forme de verbe.")

        # On prend le premier résultat (le plus probable)
        premier_resultat = resultats[0]
        
        infinitif = premier_resultat.verbe
        temps = premier_resultat.temps
        mode = premier_resultat.mode
        
        # Formater la personne pour être plus lisible
        personnes = ["1ère pers. sing.", "2ème pers. sing.", "3ème pers. sing.", 
                     "1ère pers. plur.", "2ème pers. plur.", "3ème pers. plur."]
        personne = personnes[premier_resultat.personne]

        return Out(infinitif=infinitif, temps=temps, mode=mode, personne=personne)

    except Exception as e:
        return Out(erreur=f"Une erreur inattendue est survenue: {str(e)}")
