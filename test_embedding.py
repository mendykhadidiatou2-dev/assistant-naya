from sentence_transformers import SentenceTransformer, util

print("Chargement du modèle (peut prendre 1-2 min au premier lancement)...")
modele = SentenceTransformer("intfloat/multilingual-e5-base")
print("Modèle chargé.\n")

# Note : ce modèle veut un préfixe "query:" ou "passage:" devant chaque texte
phrases = [
    "query: quand finit mon titre de séjour ?",
    "passage: Validité : du 29/08/2026 au 28/11/2026",   # devrait être PROCHE
    "passage: Montant de la cotisation annuelle : 12,00 €",  # sans rapport
]

# 1. Le modèle transforme chaque phrase en embedding (liste de nombres)
embeddings = modele.encode(phrases)

# Regardons à quoi ressemble un embedding
print(f"Un embedding = une liste de {len(embeddings[0])} nombres.")
print(f"Les 8 premiers du 1er : {embeddings[0][:8]}\n")

# 2. On calcule la similarité entre la question et chaque passage
question = embeddings[0]
for i in range(1, len(phrases)):
    score = util.cos_sim(question, embeddings[i]).item()
    print(f"Similarité avec « {phrases[i][:50]}... »")
    print(f"   → {score:.3f}\n")