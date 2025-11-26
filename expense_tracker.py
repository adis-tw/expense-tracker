"""
Core expense tracking functionality.
"""
from datetime import datetime
from typing import List, Optional, Dict
from models import Expense, ExpenseHead, TimePeriod
import json
import os


class ExpenseTracker:
    """Main expense tracker class."""
    
    def __init__(self, data_file: str = "expenses.json"):
        self.data_file = data_file
        self.expenses: List[Expense] = []
        self.time_periods: List[TimePeriod] = []
        self.load_data()
    
    def load_data(self):
        """Load expenses and time periods from file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.expenses = [Expense.from_dict(e) for e in data.get('expenses', [])]
                    self.time_periods = [TimePeriod.from_dict(tp) for tp in data.get('time_periods', [])]
            except Exception as e:
                print(f"Error loading data: {e}")
                self.expenses = []
                self.time_periods = []
    
    def save_data(self):
        """Save expenses and time periods to file."""
        data = {
            'expenses': [e.to_dict() for e in self.expenses],
            'time_periods': [tp.to_dict() for tp in self.time_periods]
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_time_period(self, start_date: datetime, end_date: datetime, 
                          expense_heads: Optional[List[ExpenseHead]] = None) -> TimePeriod:
        """Create a new time period with custom dates and expense heads."""
        if expense_heads is None:
            expense_heads = []
        
        period = TimePeriod(
            start_date=start_date,
            end_date=end_date,
            expense_heads=expense_heads
        )
        
        # Check if period already exists
        existing = self.get_time_period(period.id)
        if existing:
            return existing
        
        self.time_periods.append(period)
        self.save_data()
        return period
    
    def get_time_period(self, period_id: str) -> Optional[TimePeriod]:
        """Get a time period by ID."""
        for period in self.time_periods:
            if period.id == period_id:
                return period
        return None
    
    def get_time_period_for_date(self, date: datetime) -> Optional[TimePeriod]:
        """Get the time period that contains a given date."""
        for period in self.time_periods:
            if period.contains_date(date):
                return period
        return None
    
    def update_time_period_heads(self, period_id: str, expense_heads: List[ExpenseHead]):
        """Update expense heads for a time period."""
        period = self.get_time_period(period_id)
        if period:
            period.expense_heads = expense_heads
            self.save_data()
            return True
        return False
    
    def add_expense(self, amount: float, expense_head: str, date: datetime, 
                   description: Optional[str] = None) -> Expense:
        """Add a new expense entry."""
        expense = Expense(
            amount=amount,
            expense_head=expense_head,
            date=date,
            description=description
        )
        self.expenses.append(expense)
        self.save_data()
        return expense
    
    def get_expenses(self, start_date: Optional[datetime] = None, 
                    end_date: Optional[datetime] = None,
                    period_id: Optional[str] = None) -> List[Expense]:
        """Get expenses filtered by date range or time period."""
        expenses = self.expenses.copy()
        
        if period_id:
            period = self.get_time_period(period_id)
            if period:
                start_date = period.start_date
                end_date = period.end_date
        
        if start_date:
            expenses = [e for e in expenses if e.date >= start_date]
        
        if end_date:
            expenses = [e for e in expenses if e.date <= end_date]
        
        return sorted(expenses, key=lambda x: x.date)
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense by ID."""
        original_count = len(self.expenses)
        self.expenses = [e for e in self.expenses if e.id != expense_id]
        if len(self.expenses) < original_count:
            self.save_data()
            return True
        return False
    
    def get_all_time_periods(self) -> List[TimePeriod]:
        """Get all time periods."""
        return sorted(self.time_periods, key=lambda x: x.start_date, reverse=True)
    
    def get_expense_heads_for_period(self, period_id: str) -> List[ExpenseHead]:
        """Get expense heads for a specific time period."""
        period = self.get_time_period(period_id)
        if period:
            return period.expense_heads
        return []
