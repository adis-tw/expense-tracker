"""Core data models for the expense tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional


class ExpenseModelError(ValueError):
    """Raised when invalid data is supplied to a model."""


def _to_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    raise ExpenseModelError(f"Cannot convert {value!r} to date.")


@dataclass
class ExpenseHead:
    name: str
    budget: Optional[float] = None

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ExpenseModelError("Head name cannot be empty.")
        if self.budget is not None and self.budget < 0:
            raise ExpenseModelError("Budget cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "budget": self.budget}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpenseHead":
        return cls(name=data["name"], budget=data.get("budget"))


@dataclass
class ExpenseRecord:
    date: date
    head: str
    amount: float
    notes: str = ""

    def __post_init__(self) -> None:
        self.date = _to_date(self.date)
        self.head = self.head.strip()
        self.notes = self.notes.strip()
        if not self.head:
            raise ExpenseModelError("Expense head is required.")
        if self.amount <= 0:
            raise ExpenseModelError("Expense amount must be positive.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "head": self.head,
            "amount": self.amount,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpenseRecord":
        return cls(
            date=data["date"],
            head=data["head"],
            amount=float(data["amount"]),
            notes=data.get("notes", ""),
        )


@dataclass
class ExpensePeriod:
    label: str
    start_date: date
    end_date: date
    heads: List[ExpenseHead] = field(default_factory=list)
    records: List[ExpenseRecord] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.label = self.label.strip()
        if not self.label:
            raise ExpenseModelError("Period label cannot be empty.")
        self.start_date = _to_date(self.start_date)
        self.end_date = _to_date(self.end_date)
        if self.start_date > self.end_date:
            raise ExpenseModelError("Start date cannot be after end date.")
        self._refresh_head_lookup()
        for record in self.records:
            self._validate_record(record)

    def _refresh_head_lookup(self) -> None:
        self._heads_by_name = {head.name.lower(): head for head in self.heads}
        if len(self._heads_by_name) != len(self.heads):
            raise ExpenseModelError("Duplicate head names detected.")

    def _validate_record(self, record: ExpenseRecord) -> None:
        if not (self.start_date <= record.date <= self.end_date):
            raise ExpenseModelError(
                f"Record date {record.date} is outside period range {self.start_date} - {self.end_date}."
            )
        if record.head.lower() not in self._heads_by_name:
            raise ExpenseModelError(
                f"Record head '{record.head}' not defined for period '{self.label}'."
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "heads": [head.to_dict() for head in self.heads],
            "records": [record.to_dict() for record in self.records],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpensePeriod":
        return cls(
            label=data["label"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            heads=[ExpenseHead.from_dict(item) for item in data.get("heads", [])],
            records=[ExpenseRecord.from_dict(item) for item in data.get("records", [])],
        )

    def add_head(self, head: ExpenseHead) -> None:
        if head.name.lower() in self._heads_by_name:
            raise ExpenseModelError(f"Head '{head.name}' already exists.")
        self.heads.append(head)
        self._refresh_head_lookup()

    def set_heads(self, heads: Iterable[ExpenseHead], allow_existing_records: bool = True) -> None:
        head_list = list(heads)
        new_lookup = {head.name.lower(): head for head in head_list}
        if len(new_lookup) != len(head_list):
            raise ExpenseModelError("Duplicate head names supplied.")
        if not allow_existing_records:
            removed = set(self._heads_by_name) - set(new_lookup)
            if removed:
                raise ExpenseModelError(
                    f"Cannot remove heads {removed} while existing records reference them."
                )
        else:
            missing = {
                record.head.lower()
                for record in self.records
                if record.head.lower() not in new_lookup
            }
            if missing:
                raise ExpenseModelError(
                    f"New head list is missing categories referenced by expenses: {missing}."
                )
        self.heads = head_list
        self._refresh_head_lookup()

    def record_expense(self, record: ExpenseRecord) -> None:
        self._validate_record(record)
        self.records.append(record)

    def remove_expense(self, index: int) -> ExpenseRecord:
        record = self.records.pop(index)
        return record

    @property
    def head_names(self) -> List[str]:
        return [head.name for head in self.heads]
