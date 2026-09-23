import logging
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)

import re
import hashlib

DOSSIER_DOCUMENTS = Path("data/documents")

#ca commence ici 
def extraire_texte(chemin_pdf: Path) -> list[str]:
    """Extrait le texte d'un PDF, page par page.

    Retourne une liste : un element de texte par page.
    """
    pages_texte: list[str] = []
    with pdfplumber.open(chemin_pdf) as pdf:
        for page in pdf.pages:
            texte = page.extract_text() or ""
            pages_texte.append(texte)
    return pages_texte




def nettoyer_texte(texte: str) -> str:
    """Nettoie le texte : espaces multiples, lignes vides en trop."""
    # Remplace les suites d'espaces/tabulations par un seul espace
    texte = re.sub(r"[ \t]+", " ", texte)
    # Remplace 3+ sauts de ligne par 2 (garde la separation des paragraphes)
    texte = re.sub(r"\n{3,}", "\n\n", texte)
    return texte.strip()


def deviner_type(nom_fichier: str) -> str:
    """Devine le type de document a partir de son nom."""
    nom = nom_fichier.lower()
    if "responsabilite" in nom or "responsabilité" in nom:
        return "assurance"
    if "prolongation" in nom or "sejour" in nom or "séjour" in nom:
        return "titre_de_sejour"
    return "autre"

def calculer_hash(chemin_pdf: Path) -> str:
    """Calcule l'empreinte unique (SHA-256) d'un fichier, d'apres son contenu."""
    sha = hashlib.sha256()
    with open(chemin_pdf, "rb") as f:          # "rb" = lecture en binaire (octets bruts)
        for bloc in iter(lambda: f.read(8192), b""):
            sha.update(bloc)                   # on nourrit le calcul, bloc par bloc
    return sha.hexdigest()   

def construire_chunks(chemin_pdf: Path) -> list[dict]:
    """Transforme un PDF en une liste de chunks, un par page.

    Chaque chunk est un dict : texte (avec prefixe contextuel) + metadonnees.
    """
    pages = extraire_texte(chemin_pdf)
    type_doc = deviner_type(chemin_pdf.name)
    empreinte = calculer_hash(chemin_pdf) 
    chunks: list[dict] = []

    for numero_page, texte_brut in enumerate(pages, start=1):
        texte_propre = nettoyer_texte(texte_brut)
        if not texte_propre:
            continue  # on saute une page vide

        # Prefixe contextuel : colle l'origine DANS le texte du chunk
        prefixe = f"[{chemin_pdf.stem} — page {numero_page}]\n"
        texte_final = prefixe + texte_propre
#ici le decoupage par page 
        chunks.append({
            "texte": texte_final,
            "source": chemin_pdf.name,
            "page": numero_page,
            "type_document": type_doc,
            "hash": empreinte,
        })

    return chunks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    for pdf in DOSSIER_DOCUMENTS.glob("*.pdf"):
        chunks = construire_chunks(pdf)
        print(f"\n{'#'*60}")
        print(f"# {pdf.name} → {len(chunks)} chunk(s)")
        print(f"{'#'*60}")

        for c in chunks:
            print(f"\n--- CHUNK : {c['source']} p.{c['page']} "
                  f"[type: {c['type_document']}] ({len(c['texte'])} car.) ---")
            print(c["texte"])