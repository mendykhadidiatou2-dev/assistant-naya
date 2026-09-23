from pathlib import Path
from pypdf import PdfReader

DOSSIER = Path("data/documents")

for pdf in DOSSIER.glob("*.pdf"):
    print(f"\n{'='*60}")
    print(f"Fichier : {pdf.name}")
    print(f"Taille  : {pdf.stat().st_size // 1024} Ko")

    reader = PdfReader(pdf)
    print(f"Pages   : {len(reader.pages)}")

    for i, page in enumerate(reader.pages, start=1):
        texte = page.extract_text() or ""
        nb_caracteres = len(texte.strip())
        verdict = "TEXTE" if nb_caracteres > 100 else "SCAN probable (peu/pas de texte)"
        print(f"  Page {i} : {nb_caracteres} caractères extraits  ->  {verdict}")