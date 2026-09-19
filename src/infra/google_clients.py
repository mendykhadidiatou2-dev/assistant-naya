from functools import lru_cache

from googleapiclient.discovery import build

from src.infra.google_auth import obtenir_credentials


@lru_cache(maxsize=None)
def client_calendar():
    return build(
        "calendar", "v3",
        credentials=obtenir_credentials(),
        cache_discovery=False,
    )