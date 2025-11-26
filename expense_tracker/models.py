"""Core data models for the expense tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, Iterable, List

DATE_FMT = "%Y-%m-%d"


def parse_date(value: str | date) -> date:
    """Normalise incoming dates from strings or date objects."""
    if isinstance(value, date):
        return value
    return datetime.strptime(value, DATE_FMT).date()


@dataclass
class Expense:
    """Single expense entry."""

    date: date
    head: str
    amount: float
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.strftime(DATE_FMT),
            "head": self.head,
            "amount": self.amount,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Expense":
        return cls(
            date=parse_date(payload["date"]),
            head=payload["head"],
            amount=float(payload["amount"]),
            note=payload.get("note", ""),
        )


@dataclass
class ExpensePeriod:
    """Collection of expenses between two custom dates."""

    name: str
    start_date: date
    end_date: date
    heads: List[str] = field(default_factory=list)
    expenses: List[Expense] = field(default_factory=list)

    def add_head(self, head: str) -> None:
        head = head.strip()
        if not head:
            raise ValueError("Head name cannot be empty")
        if head not in self.heads:
            self.heads.append(head)

    def remove_head(self, head: str) -> None:
        if head in self.heads:
            self.heads.remove(head)

    def record_expense(
        self,
        *,
        head: str,
        amount: float,
        date_: str | date,
        note: str = "",
    ) -> Expense:
        if head not in self.heads:
            raise ValueError(f"Head '{head}' not in configured heads: {self.heads}")
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        expense_date = parse_date(date_)
        if not (self.start_date <= expense_date <= self.end_date):
            raise ValueError(
                f"Expense date {expense_date} outside of period "
                f"{self.start_date} - {self.end_date}"
            )
        expense = Expense(
            date=expense_date,
            head=head,
            amount=amount,
            note=note,
        )
        self.expenses.append(expense)
        return expense

    def expenses_between(
        self,
        start: str | date,
        end: str | date,
        heads: Iterable[str] | None = None,
    ) -> List[Expense]:
        start_date = parse_date(start)
        end_date = parse_date(end)
        head_set = set(heads or self.heads)
        return [
            exp
            for exp in self.expenses
            if start_date <= exp.date <= end_date and exp.head in head_set
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "start_date": self.start_date.strftime(DATE_FMT),
            "end_date": self.end_date.strftime(DATE_FMT),
            "heads": self.heads,
            "expenses": [expense.to_dict() for expense in self.expenses],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ExpensePeriod":
        return cls(
            name=payload["name"],
            start_date=parse_date(payload["start_date"]),
            end_date=parse_date(payload["end_date"]),
            heads=list(payload.get("heads", [])),
            expenses=[Expense.from_dict(item) for item in payload.get("expenses", [])],
        )
