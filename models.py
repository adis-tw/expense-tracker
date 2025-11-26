"""
Data models for the expense tracker.
"""
from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass, field
import json


@dataclass
class ExpenseHead:
    """Represents an expense category/head."""
    name: str
    description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExpenseHead':
        return cls(
            name=data['name'],
            description=data.get('description')
        )


@dataclass
class Expense:
    """Represents a single expense entry."""
    amount: float
    expense_head: str
    date: datetime
    description: Optional[str] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.date.strftime('%Y%m%d%H%M%S')}_{hash(self.expense_head)}"
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'amount': self.amount,
            'expense_head': self.expense_head,
            'date': self.date.isoformat(),
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        return cls(
            id=data.get('id'),
            amount=float(data['amount']),
            expense_head=data['expense_head'],
            date=datetime.fromisoformat(data['date']),
            description=data.get('description')
        )


@dataclass
class TimePeriod:
    """Represents a time period with custom dates and expense heads."""
    start_date: datetime
    end_date: datetime
    expense_heads: List[ExpenseHead] = field(default_factory=list)
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.start_date.strftime('%Y%m%d')}_{self.end_date.strftime('%Y%m%d')}"
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'expense_heads': [head.to_dict() for head in self.expense_heads]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TimePeriod':
        return cls(
            id=data.get('id'),
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            expense_heads=[ExpenseHead.from_dict(h) for h in data.get('expense_heads', [])]
        )
    
    def contains_date(self, date: datetime) -> bool:
        """Check if a date falls within this time period."""
        return self.start_date <= date <= self.end_date
