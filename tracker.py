"""
Main expense tracker class.
"""
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
from pathlib import Path

from models import Expense, TimePeriod


class ExpenseTracker:
    """Main expense tracker class."""
    
    def __init__(self, data_file: str = "expense_data.json"):
        """Initialize the expense tracker.
        
        Args:
            data_file: Path to JSON file for storing expense data
        """
        self.data_file = Path(data_file)
        self.time_periods: List[TimePeriod] = []
        self.load_data()
    
    def create_time_period(self, start_date: datetime, end_date: datetime, 
                          expense_heads: List[str], period_name: Optional[str] = None) -> TimePeriod:
        """Create a new time period.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            expense_heads: List of expense category heads
            period_name: Optional name for the period
            
        Returns:
            Created TimePeriod object
        """
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        period = TimePeriod(
            start_date=start_date,
            end_date=end_date,
            expense_heads=expense_heads,
            period_name=period_name
        )
        self.time_periods.append(period)
        self.save_data()
        return period
    
    def get_time_period(self, period_name: Optional[str] = None, 
                       index: Optional[int] = None) -> Optional[TimePeriod]:
        """Get a time period by name or index.
        
        Args:
            period_name: Name of the period
            index: Index of the period in the list
            
        Returns:
            TimePeriod object or None if not found
        """
        if index is not None:
            if 0 <= index < len(self.time_periods):
                return self.time_periods[index]
        elif period_name:
            for period in self.time_periods:
                if period.period_name == period_name:
                    return period
        return None
    
    def add_expense(self, amount: Decimal, category: str, description: str, 
                   date: datetime, period_name: Optional[str] = None,
                   period_index: Optional[int] = None) -> Expense:
        """Add an expense to a time period.
        
        Args:
            amount: Expense amount
            category: Expense category (must be in period's expense_heads)
            description: Description of the expense
            date: Date of the expense
            period_name: Name of the period to add to
            period_index: Index of the period to add to
            
        Returns:
            Created Expense object
        """
        period = self.get_time_period(period_name, period_index)
        if period is None:
            raise ValueError("Time period not found")
        
        if category not in period.expense_heads:
            raise ValueError(f"Category '{category}' not in expense heads. Available: {period.expense_heads}")
        
        expense = Expense(amount=amount, category=category, description=description, date=date)
        period.add_expense(expense)
        self.save_data()
        return expense
    
    def update_expense_heads(self, period_name: Optional[str] = None,
                            period_index: Optional[int] = None,
                            expense_heads: Optional[List[str]] = None):
        """Update expense heads for a time period.
        
        Args:
            period_name: Name of the period
            period_index: Index of the period
            expense_heads: New list of expense heads
        """
        period = self.get_time_period(period_name, period_index)
        if period is None:
            raise ValueError("Time period not found")
        
        if expense_heads is not None:
            period.expense_heads = expense_heads
            self.save_data()
    
    def list_time_periods(self) -> List[Dict]:
        """List all time periods with summary information.
        
        Returns:
            List of dictionaries with period information
        """
        return [
            {
                'index': i,
                'name': period.period_name,
                'start_date': period.start_date.strftime('%Y-%m-%d'),
                'end_date': period.end_date.strftime('%Y-%m-%d'),
                'expense_heads': period.expense_heads,
                'total_expenses': float(period.get_total_expenses()),
                'expense_count': len(period.expenses)
            }
            for i, period in enumerate(self.time_periods)
        ]
    
    def save_data(self):
        """Save expense data to JSON file."""
        data = {
            'time_periods': [period.to_dict() for period in self.time_periods]
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_data(self):
        """Load expense data from JSON file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.time_periods = [
                        TimePeriod.from_dict(period_data)
                        for period_data in data.get('time_periods', [])
                    ]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading data: {e}. Starting with empty tracker.")
                self.time_periods = []
        else:
            self.time_periods = []
