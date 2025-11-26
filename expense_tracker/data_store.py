"""Persistence helpers for the expense tracker."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .models import ExpensePeriod


class JSONDataStore:
    """Simple JSON-backed storage for expense periods."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if self.path.suffix != ".json":
            raise ValueError("JSONDataStore path must point to a .json file.")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_periods(self) -> Dict[str, ExpensePeriod]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        periods = {
            label: ExpensePeriod.from_dict(raw_period)
            for label, raw_period in payload.get("periods", {}).items()
        }
        return periods

    def save_periods(self, periods: Dict[str, ExpensePeriod]) -> None:
        data = {"periods": {label: period.to_dict() for label, period in periods.items()}}
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
