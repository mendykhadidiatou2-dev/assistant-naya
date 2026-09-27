import logging

import ollama

from src.rag.vectorstore import chercher

logger = logging.getLogger(__name__)

NOM_LLM = "llama3.1:8b"

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
    chunks = chercher(question, k=k)
    for c in chunks:
        print(f"  [reçu] {c['meta']['source']} p.{c['meta']['page']}")
    prompt_utilisateur = construire_prompt_utilisateur(question, chunks)

    reponse = ollama.chat(
        model=NOM_LLM,
        messages=[
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": prompt_utilisateur},
        ],
        options={"temperature": 0.1},   # basse : factuel, pas de créativité
    )
    return reponse["message"]["content"]


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