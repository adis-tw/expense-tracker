"""High-level API for managing expense periods and transactions."""

from __future__ import annotations

from datetime import date
from typing import Iterable, List

from .data_store import JSONDataStore
from .models import ExpenseHead, ExpenseModelError, ExpensePeriod, ExpenseRecord


class ExpenseTracker:
    """Facade that coordinates persistence, validation, and analytics."""

    def __init__(self, data_store: JSONDataStore) -> None:
        self._store = data_store
        self._periods = self._store.load_periods()

    # CRUD helpers ---------------------------------------------------------
    def list_periods(self) -> List[str]:
        return list(self._periods)

    def get_period(self, label: str) -> ExpensePeriod:
        try:
            return self._periods[label]
        except KeyError as exc:
            raise ExpenseModelError(f"Unknown period '{label}'.") from exc

    def create_period(
        self,
        label: str,
        start_date: date,
        end_date: date,
        heads: Iterable[ExpenseHead],
    ) -> ExpensePeriod:
        if label in self._periods:
            raise ExpenseModelError(f"Period '{label}' already exists.")
        period = ExpensePeriod(
            label=label, start_date=start_date, end_date=end_date, heads=list(heads)
        )
        self._periods[label] = period
        self._persist()
        return period

    def update_heads(
        self,
        label: str,
        heads: Iterable[ExpenseHead],
        allow_existing_records: bool = True,
    ) -> ExpensePeriod:
        period = self.get_period(label)
        period.set_heads(heads, allow_existing_records=allow_existing_records)
        self._persist()
        return period

    def record_expense(
        self,
        label: str,
        *,
        expense_date: date,
        head: str,
        amount: float,
        notes: str = "",
    ) -> ExpenseRecord:
        period = self.get_period(label)
        record = ExpenseRecord(date=expense_date, head=head, amount=amount, notes=notes)
        period.record_expense(record)
        self._persist()
        return record

    def remove_expense(self, label: str, index: int) -> ExpenseRecord:
        period = self.get_period(label)
        record = period.remove_expense(index)
        self._persist()
        return record

    def _persist(self) -> None:
        self._store.save_periods(self._periods)
