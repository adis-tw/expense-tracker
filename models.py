"""
Data models for the expense tracker.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal


@dataclass
class Expense:
    """Represents a single expense entry."""
    amount: Decimal
    category: str
    description: str
    date: datetime
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.date.strftime('%Y%m%d%H%M%S')}_{hash(self.description)}"
    
    def to_dict(self) -> Dict:
        """Convert expense to dictionary."""
        return {
            'id': self.id,
            'amount': float(self.amount),
            'category': self.category,
            'description': self.description,
            'date': self.date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        """Create expense from dictionary."""
        return cls(
            id=data.get('id'),
            amount=Decimal(str(data['amount'])),
            category=data['category'],
            description=data['description'],
            date=datetime.fromisoformat(data['date'])
        )


@dataclass
class TimePeriod:
    """Represents a time period with custom date range and expense heads."""
    start_date: datetime
    end_date: datetime
    expense_heads: List[str] = field(default_factory=list)
    expenses: List[Expense] = field(default_factory=list)
    period_name: Optional[str] = None
    
    def __post_init__(self):
        if self.period_name is None:
            self.period_name = f"{self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}"
    
    def add_expense(self, expense: Expense):
        """Add an expense to this period."""
        if self.start_date <= expense.date <= self.end_date:
            self.expenses.append(expense)
        else:
            raise ValueError(f"Expense date {expense.date} is outside period range")
    
    def get_total_expenses(self) -> Decimal:
        """Get total expenses for this period."""
        return sum(exp.amount for exp in self.expenses)
    
    def get_expenses_by_category(self) -> Dict[str, Decimal]:
        """Get expenses grouped by category."""
        category_totals = {}
        for exp in self.expenses:
            category_totals[exp.category] = category_totals.get(exp.category, Decimal('0')) + exp.amount
        return category_totals
    
    def to_dict(self) -> Dict:
        """Convert time period to dictionary."""
        return {
            'period_name': self.period_name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'expense_heads': self.expense_heads,
            'expenses': [exp.to_dict() for exp in self.expenses]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TimePeriod':
        """Create time period from dictionary."""
        period = cls(
            period_name=data.get('period_name'),
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            expense_heads=data.get('expense_heads', [])
        )
        period.expenses = [Expense.from_dict(exp) for exp in data.get('expenses', [])]
        return period
