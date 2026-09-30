import logging

from src.infra.google_clients import client_gmail

logger = logging.getLogger(__name__)


def _extraire_entete(message: dict, nom: str) -> str:
    """Fonction PURE : récupère un en-tête (From, Subject...) d'un message."""
    entetes = message.get("payload", {}).get("headers", [])
    for e in entetes:
        if e.get("name", "").lower() == nom.lower():
            return e.get("value", "")
    return ""


def lister_mails(requete: str = "is:unread", limite: int = 10) -> list[dict]:
    """Partie IMPURE : liste les mails correspondant à une requête Gmail.

    'requete' utilise la syntaxe Gmail (ex: 'is:unread', 'newer_than:7d').
    """
    service = client_gmail()
    reponse = (
        service.users().messages()
        .list(userId="me", q=requete, maxResults=limite)
        .execute()
    )
    ids = reponse.get("messages", [])
    logger.info("Gmail : %d mails trouvés pour '%s'", len(ids), requete)

    mails = []
    for item in ids:
        msg = (
            service.users().messages()
            .get(userId="me", id=item["id"], format="metadata",
                 metadataHeaders=["From", "Subject", "Date"])
            .execute()
        )
        mails.append({
            "expediteur": _extraire_entete(msg, "From"),
            "objet": _extraire_entete(msg, "Subject"),
            "date": _extraire_entete(msg, "Date"),
            "apercu": msg.get("snippet", "")[:200],
        })
    return mails


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for mail in lister_mails("is:unread newer_than:7d", limite=5):
        print(f"\nDe : {mail['expediteur']}")
        print(f"Objet : {mail['objet']}")
        print(f"Aperçu : {mail['apercu']}")