import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.config import config
from src.infra.google_clients import client_calendar
from src.models import Evenement

logger = logging.getLogger(__name__)
FUSEAU = ZoneInfo(config.timezone)


def _parser_evenement(brut: dict) -> Evenement:
    debut_brut = brut["start"]
    fin_brut = brut["end"]
    journee_entiere = "date" in debut_brut

    if journee_entiere:
        debut = datetime.fromisoformat(debut_brut["date"]).replace(tzinfo=FUSEAU)
        fin = datetime.fromisoformat(fin_brut["date"]).replace(tzinfo=FUSEAU)
    else:
        debut = datetime.fromisoformat(debut_brut["dateTime"]).astimezone(FUSEAU)
        fin = datetime.fromisoformat(fin_brut["dateTime"]).astimezone(FUSEAU)

    return Evenement(
        titre=brut.get("summary", "(sans titre)"),
        debut=debut,
        fin=fin,
        journee_entiere=journee_entiere,
        lieu=brut.get("location"),
    )


def lire_agenda(jours: int = 7, limite: int = 20) -> list[Evenement]:
    maintenant = datetime.now(FUSEAU)
    reponse = (
        client_calendar()
        .events()
        .list(
            calendarId="primary",
            timeMin=maintenant.isoformat(),
            timeMax=(maintenant + timedelta(days=jours)).isoformat(),
            maxResults=limite,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    bruts = reponse.get("items", [])
    logger.info("Agenda : %d evenements recuperes sur %d jours", len(bruts), jours)
    return [_parser_evenement(e) for e in bruts]


if __name__ == "__main__":
    logging.basicConfig(level=config.log_level)
    for evenement in lire_agenda():
        print(evenement.resume())
#cette partie donne à notre programme ll'autorisation d'acceder au projet assistant qu'on a du crer pourqu'il puisse lire 
#notre calendrier 
#calendar veut l'agenda → il appelle google_clients → qui demande l'autorisation à google_auth → qui lit les réglages dans config → la page Google s'ouvre, tu autorises → Google renvoie les événements → calendar les range dans le moule models → ils s'affichent dans ton terminal.