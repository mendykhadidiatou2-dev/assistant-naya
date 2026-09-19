import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from src.config import config

logger = logging.getLogger(__name__)


def obtenir_credentials() -> Credentials:
    """Retourne des credentials valides, en renouvelant ou consentant si nécessaire."""
    creds: Credentials | None = None

    if config.token_absolu.exists():
        creds = Credentials.from_authorized_user_file(
            str(config.token_absolu), list(config.SCOPES)
        )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        logger.info("Access token expiré, renouvellement via le refresh token")
        creds.refresh(Request())
    else:
        logger.info("Aucun token exploitable, ouverture du consentement navigateur")
        if not config.credentials_absolu.exists():
            raise FileNotFoundError(
                f"credentials.json introuvable : {config.credentials_absolu}"
            )
        flow = InstalledAppFlow.from_client_secrets_file(
            str(config.credentials_absolu), list(config.SCOPES)
        )
        creds = flow.run_local_server(port=0)

    config.token_absolu.parent.mkdir(parents=True, exist_ok=True)
    config.token_absolu.write_text(creds.to_json(), encoding="utf-8")
    return creds