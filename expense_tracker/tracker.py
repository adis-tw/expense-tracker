"""High level tracker orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from . import analytics
from .models import Expense, ExpensePeriod, parse_date
from .storage import ExpenseTrackerStore


class ExpenseTracker:
    """Manage multiple expense periods and analytics."""

    def __init__(self, data_file: str | Path = "./expense_data.json"):
        self.store = ExpenseTrackerStore(data_file)
        self._periods: Dict[str, ExpensePeriod] = {
            period.name: period for period in self.store.load_periods()
        }

    def create_period(
        self,
        *,
        name: str,
        start_date: str,
        end_date: str,
        heads: Sequence[str],
    ) -> ExpensePeriod:
        if name in self._periods:
            raise ValueError(f"Period '{name}' already exists")
        start = parse_date(start_date)
        end = parse_date(end_date)
        if start > end:
            raise ValueError("start_date must not be later than end_date")
        period = ExpensePeriod(name=name, start_date=start, end_date=end)
        for head in heads:
            period.add_head(head)
        self._periods[name] = period
        self._persist()
        return period

    def list_periods(self) -> List[str]:
        return sorted(self._periods)

    def get_period(self, name: str) -> ExpensePeriod:
        try:
            return self._periods[name]
        except KeyError as exc:
            raise ValueError(f"Unknown period '{name}'") from exc

    def add_head(self, period_name: str, head: str) -> None:
        period = self.get_period(period_name)
        period.add_head(head)
        self._persist()

    def remove_head(self, period_name: str, head: str) -> None:
        period = self.get_period(period_name)
        period.remove_head(head)
        self._persist()

    def record_expense(
        self,
        *,
        period_name: str,
        date_: str,
        head: str,
        amount: float,
        note: str = "",
    ) -> Expense:
        period = self.get_period(period_name)
        expense = period.record_expense(
            head=head,
            amount=amount,
            date_=date_,
            note=note,
        )
        self._persist()
        return expense

    def expenses_between(
        self,
        *,
        period_name: str,
        start: str,
        end: str,
        heads: Iterable[str] | None = None,
    ) -> List[Expense]:
        period = self.get_period(period_name)
        return period.expenses_between(start, end, heads)

    def analytics(
        self,
        *,
        period_name: str,
        start: str | None = None,
        end: str | None = None,
        heads: Iterable[str] | None = None,
    ) -> Dict[str, object]:
        period = self.get_period(period_name)
        return analytics.summarise_period(period, start=start, end=end, heads=heads)

    def _persist(self) -> None:
        self.store.save_periods(self._periods.values())
