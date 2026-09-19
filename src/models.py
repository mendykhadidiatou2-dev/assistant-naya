from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Evenement:
    titre: str
    debut: datetime
    fin: datetime
    journee_entiere: bool
    lieu: str | None = None

    def resume(self) -> str:
        if self.journee_entiere:
            return f"{self.debut:%a %d/%m} — {self.titre} (journée)"
        return f"{self.debut:%a %d/%m %H:%M} — {self.titre}"