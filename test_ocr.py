from pathlib import Path

import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER = r"C:\Users\USER\Projet_Agent_Ia\Release-26.09.0-0\poppler-26.09.0\Library\bin"

PDF = Path("data/documents/carte d'assurance maladie.pdf")

print("Conversion de la page PDF en image...")
images = convert_from_path(PDF, poppler_path=POPPLER,dpi=400)
print(f"{len(images)} page(s) convertie(s) en image.")

print("\nLecture du texte par l'OCR (francais)...")
for i, image in enumerate(images, start=1):
    texte = pytesseract.image_to_string(image, lang="fra")
    print(f"\n{'='*60}")
    print(f"PAGE {i} - texte extrait par OCR :")
    print(f"{'='*60}")
    print(texte)