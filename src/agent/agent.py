import json
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from openai import OpenAI

from src.rag.vectorstore import chercher
from src.tools.calendar import lire_agenda
from src.tools.gmail import lister_mails

load_dotenv()

logger = logging.getLogger(__name__)

client_llm = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
NOM_LLM = "gemini-2.5-flash"   # recopie le nom exact de ta liste
FUSEAU = ZoneInfo("Europe/Paris")
# ---------- Les 3 outils, décrits pour le LLM ----------
OUTILS = [
    {
        "type": "function",
        "function": {
            "name": "chercher_documents",
            "description": (
                "Recherche dans les documents administratifs personnels archivés "
                "(attestations, contrats, titre de séjour, assurance). "
                "À utiliser pour toute question sur un papier officiel. "
                "NE PAS utiliser pour les mails ni pour l'agenda."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "La question à chercher dans les documents"}
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lire_agenda",
            "description": (
                "Lit les événements de l'agenda (cours, rendez-vous) sur les prochains jours. "
                "À utiliser pour toute question sur le planning, l'emploi du temps, les cours à venir. "
                "NE PAS utiliser pour les mails ni les documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "jours": {"type": "integer", "description": "Nombre de jours à regarder (défaut 7)"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lister_mails",
            "description": (
                "Liste les e-mails selon une requête Gmail (ex: 'is:unread newer_than:7d'). "
                "À utiliser pour toute question sur les mails, messages non lus, courriers reçus. "
                "NE PAS utiliser pour l'agenda ni les documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "requete": {"type": "string", "description": "Requête Gmail, ex: 'is:unread'"}
                },
            },
        },
    },
]


# ---------- Exécuter réellement un outil ----------
def executer_outil(nom: str, arguments: dict) -> str:
    """TON CODE exécute l'outil que le LLM a demandé, et renvoie le résultat en texte."""
    logger.info("Outil appelé : %s(%s)", nom, arguments)

    if nom == "chercher_documents":
        chunks = chercher(arguments["question"], k=3)
        return "\n\n".join(c["texte"] for c in chunks)

    if nom == "lire_agenda":
        jours = arguments.get("jours", 7)
        evenements = lire_agenda(jours=jours)
        if not evenements:
            return "Aucun événement dans cette période."
        return "\n".join(e.resume() for e in evenements)

    if nom == "lister_mails":
        requete = arguments.get("requete", "is:unread newer_than:7d")
        mails = lister_mails(requete, limite=5)
        if not mails:
            return "Aucun mail trouvé."
        return "\n".join(
            f"De {m['expediteur']} — {m['objet']} : {m['apercu']}" for m in mails
        )

    return "Outil inconnu."


PROMPT_SYSTEME = """Tu es Naya, une assistante personnelle en français.
Tu as accès à trois outils : les documents administratifs, l'agenda, et les mails.
Choisis le bon outil selon la question, puis réponds clairement à partir du résultat.
Si l'information n'est pas disponible, dis-le honnêtement. Ne devine jamais.
La date du jour est {date}."""
#Les informations que recoivent le modele a chaque fois qu'on lui pose une question, il recoit le prompt systeme 
#l'historique pour continuer une question de suivie et la question posée
def repondre_agent(question: str, historique: list | None = None, max_iterations: int = 5) -> str:   # ← NOUVEAU (paramètre)
    """La boucle agent : le LLM choisit ses outils jusqu'à pouvoir répondre."""
    historique = historique or []                                                                      # ← NOUVEAU (carnet vide par défaut)
    messages = [
        {"role": "system", "content": PROMPT_SYSTEME.format(date=datetime.now(FUSEAU).strftime("%A %d %B %Y"))},
        *historique,                                                                                   # ← NOUVEAU (on glisse le carnet ici)
        {"role": "user", "content": question},
    ]

    for tour in range(max_iterations):
        reponse = client_llm.chat.completions.create(
            model=NOM_LLM,
            messages=messages,
            tools=OUTILS,
            temperature=0.1,
        )
        message = reponse.choices[0].message

        # Si le LLM ne demande aucun outil, c'est qu'il a sa réponse finale
        if not message.tool_calls:
            return message.content

        # Sinon, on exécute les outils demandés
        messages.append(message)
        for appel in message.tool_calls:
            nom = appel.function.name
            arguments = json.loads(appel.function.arguments or "{}")                                   # ← petite sécurité (voir plus bas)
            resultat = executer_outil(nom, arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": appel.id,
                "content": resultat,
            })

    return "Je n'ai pas réussi à répondre après plusieurs tentatives."