from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

RACINE = Path(__file__).resolve().parent.parent


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_credentials_path: Path = Path("secrets/credentials.json")
    google_token_path: Path = Path("secrets/token.json")
    timezone: str = "Europe/Paris"
    log_level: str = "INFO"

    SCOPES: tuple[str, ...] = (
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/gmail.readonly",
    )

    @property
    def credentials_absolu(self) -> Path:
        return RACINE / self.google_credentials_path

    @property
    def token_absolu(self) -> Path:
        return RACINE / self.google_token_path


config = Config()