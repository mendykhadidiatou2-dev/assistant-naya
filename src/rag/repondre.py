import logging
import os
import time
from venv import logger

from groq import Groq
from dotenv import load_dotenv

from src.rag.vectorstore import chercher

load_dotenv()
client_groq = Groq(api_key=os.environ["GROQ_API_KEY"])
NOM_LLM = "openai/gpt-oss-120b"

PROMPT_SYSTEME = """Tu es un assistant personnel qui aide à retrouver des informations \
dans des documents administratifs.

Ta méthode :
- Lis attentivement TOUS les extraits fournis.
- Cherche l'information demandée, même si elle est formulée différemment dans les extraits \
(par exemple "validité" peut répondre à une question sur une date de fin).
- Si tu trouves l'information, réponds clairement et cite le document source (nom et page).
- Si, après avoir bien cherché, l'information n'est vraiment nulle part dans les extraits, \
réponds : "Je ne trouve pas cette information dans tes documents."
- Ne devine jamais une information absente. Réponds en français."""


def construire_prompt_utilisateur(question: str, chunks: list[dict]) -> str:
    """Assemble les extraits trouvés et la question en un seul message."""
    extraits = "\n\n".join(
        f"[Extrait {i} — {c['meta']['source']} p.{c['meta']['page']}]\n{c['texte']}"
        for i, c in enumerate(chunks, start=1)
    )
    return f"EXTRAITS :\n{extraits}\n\nQUESTION : {question}"


def repondre(question: str, k: int = 4) -> str:
    """Cherche les chunks, construit le prompt, interroge le LLM, renvoie la réponse."""
    chunks = chercher(question, k=3)
    for c in chunks:
        print(f"  [reçu] {c['meta']['source']} p.{c['meta']['page']}")
    prompt_utilisateur = construire_prompt_utilisateur(question, chunks)

    debut = time.time()
    reponse = client_groq.chat.completions.create(
        model=NOM_LLM,
        messages=[
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": prompt_utilisateur},
        ],
        temperature=0.1,
    )
    duree = time.time() - debut
    logger.info("Réponse générée en %.1f secondes", duree)
    return reponse.choices[0].message.content


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    questions = [
        "quand se termine mon titre de séjour ?",   # réponse DANS les documents
        "quel est le nom de mon chat ?",            # réponse ABSENTE (test d'abstention)
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"QUESTION : {q}")
        print(f"{'='*60}")
        print(repondre(q))