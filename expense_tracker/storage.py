"""JSON-backed storage for expense tracker periods."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .models import ExpensePeriod


class ExpenseTrackerStore:
    """Handle persistence of tracker data."""

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_periods(self) -> List[ExpensePeriod]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return [ExpensePeriod.from_dict(item) for item in payload.get("periods", [])]

    def save_periods(self, periods: Iterable[ExpensePeriod]) -> None:
        serialised = {"periods": [period.to_dict() for period in periods]}
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(serialised, handle, indent=2)
