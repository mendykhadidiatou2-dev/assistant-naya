import logging
from functools import lru_cache
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from src.rag.ingest import DOSSIER_DOCUMENTS, construire_chunks

logger = logging.getLogger(__name__)

DOSSIER_INDEX = Path("data/index")
NOM_MODELE = "intfloat/multilingual-e5-base"


@lru_cache(maxsize=None)
def charger_modele() -> SentenceTransformer:
    """Charge le modèle d'embedding une seule fois."""
    logger.info("Chargement du modèle d'embedding...")
    return SentenceTransformer(NOM_MODELE)


@lru_cache(maxsize=None)
def obtenir_collection():
    """Ouvre (ou crée) la collection ChromaDB, stockée sur le disque."""
    client = chromadb.PersistentClient(path=str(DOSSIER_INDEX))
    return client.get_or_create_collection(name="documents")


def indexer_documents() -> None:
    """Transforme tous les PDF en chunks, les encode et les range dans ChromaDB."""
    modele = charger_modele()
    collection = obtenir_collection()

    for pdf in DOSSIER_DOCUMENTS.glob("*.pdf"):
        chunks = construire_chunks(pdf)
        if not chunks:
            continue

        # Le modèle E5 veut le préfixe "passage:" devant chaque texte à ranger
        textes = [f"passage: {c['texte']}" for c in chunks]
        embeddings = modele.encode(textes).tolist()

        # Un identifiant unique par chunk : hash du doc + numéro de page
        ids = [f"{c['hash']}_{c['page']}" for c in chunks]

        # Les métadonnées, sans le texte (déjà stocké à part)
        metadonnees = [
            {"source": c["source"], "page": c["page"], "type_document": c["type_document"]}
            for c in chunks
        ]

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=[c["texte"] for c in chunks],
            metadatas=metadonnees,
        )
        logger.info("Indexé : %s (%d chunks)", pdf.name, len(chunks))


def chercher(question: str, k: int = 4) -> list[dict]:
    """Cherche les k chunks les plus proches d'une question."""
    modele = charger_modele()
    collection = obtenir_collection()

    # La question veut le préfixe "query:"
    embedding_question = modele.encode(f"query: {question}").tolist()

    resultats = collection.query(query_embeddings=[embedding_question], n_results=k)

    chunks_trouves = []
    for texte, meta, distance in zip(
        resultats["documents"][0],
        resultats["metadatas"][0],
        resultats["distances"][0],
    ):
        chunks_trouves.append({"texte": texte, "meta": meta, "distance": distance})
    return chunks_trouves


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== ÉTAPE 1 : indexation des documents ===")
    indexer_documents()

    print("\n=== ÉTAPE 2 : test de recherche ===")
    question = "quand se termine mon titre de séjour ?"
    print(f"Question : {question}\n")

    for i, r in enumerate(chercher(question), start=1):
        print(f"--- Résultat {i} (distance {r['distance']:.3f}) ---")
        print(f"Source : {r['meta']['source']} p.{r['meta']['page']}")
        print(r["texte"][:200])
        print()