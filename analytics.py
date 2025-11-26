"""
Analytics module for expense analysis.
"""
from datetime import datetime
from typing import List, Dict, Optional
from models import Expense, TimePeriod
import pandas as pd


class ExpenseAnalytics:
    """Analytics engine for expense data."""
    
    def __init__(self, expenses: List[Expense]):
        self.expenses = expenses
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Create a pandas DataFrame from expenses."""
        if not self.expenses:
            return pd.DataFrame(columns=['date', 'amount', 'expense_head', 'description'])
        
        data = []
        for expense in self.expenses:
            data.append({
                'date': expense.date,
                'amount': expense.amount,
                'expense_head': expense.expense_head,
                'description': expense.description or ''
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def total_expenses(self) -> float:
        """Calculate total expenses."""
        return self.df['amount'].sum() if not self.df.empty else 0.0
    
    def expenses_by_head(self) -> Dict[str, float]:
        """Get total expenses grouped by expense head."""
        if self.df.empty:
            return {}
        return self.df.groupby('expense_head')['amount'].sum().to_dict()
    
    def expenses_by_date(self) -> Dict[str, float]:
        """Get total expenses grouped by date."""
        if self.df.empty:
            return {}
        df_copy = self.df.copy()
        df_copy['date_str'] = df_copy['date'].dt.strftime('%Y-%m-%d')
        return df_copy.groupby('date_str')['amount'].sum().to_dict()
    
    def average_daily_expense(self) -> float:
        """Calculate average daily expense."""
        if self.df.empty:
            return 0.0
        
        date_range = (self.df['date'].max() - self.df['date'].min()).days + 1
        if date_range == 0:
            return self.total_expenses()
        return self.total_expenses() / date_range
    
    def top_expense_heads(self, n: int = 5) -> List[tuple]:
        """Get top N expense heads by total amount."""
        if self.df.empty:
            return []
        
        by_head = self.expenses_by_head()
        sorted_heads = sorted(by_head.items(), key=lambda x: x[1], reverse=True)
        return sorted_heads[:n]
    
    def expense_trend(self) -> Dict[str, float]:
        """Get weekly expense trend."""
        if self.df.empty:
            return {}
        
        df_copy = self.df.copy()
        df_copy['week'] = df_copy['date'].dt.to_period('W')
        weekly = df_copy.groupby('week')['amount'].sum()
        return {str(week): float(amount) for week, amount in weekly.items()}
    
    def monthly_summary(self) -> Dict[str, Dict]:
        """Get monthly summary of expenses."""
        if self.df.empty:
            return {}
        
        df_copy = self.df.copy()
        df_copy['year_month'] = df_copy['date'].dt.to_period('M')
        
        summary = {}
        for period, group in df_copy.groupby('year_month'):
            period_str = str(period)
            summary[period_str] = {
                'total': float(group['amount'].sum()),
                'count': len(group),
                'by_head': group.groupby('expense_head')['amount'].sum().to_dict()
            }
        
        return summary
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        return {
            'total_expenses': self.total_expenses(),
            'expense_count': len(self.expenses),
            'average_daily_expense': self.average_daily_expense(),
            'expenses_by_head': self.expenses_by_head(),
            'top_expense_heads': dict(self.top_expense_heads()),
            'date_range': {
                'start': self.df['date'].min().isoformat() if not self.df.empty else None,
                'end': self.df['date'].max().isoformat() if not self.df.empty else None
            }
        }
    
    def generate_report(self) -> str:
        """Generate a text report of analytics."""
        stats = self.get_statistics()
        
        report = []
        report.append("=" * 60)
        report.append("EXPENSE ANALYTICS REPORT")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Total Expenses: ${stats['total_expenses']:.2f}")
        report.append(f"Number of Expenses: {stats['expense_count']}")
        report.append(f"Average Daily Expense: ${stats['average_daily_expense']:.2f}")
        report.append("")
        
        if stats['date_range']['start']:
            report.append(f"Date Range: {stats['date_range']['start']} to {stats['date_range']['end']}")
            report.append("")
        
        report.append("Expenses by Head:")
        report.append("-" * 60)
        for head, amount in sorted(stats['expenses_by_head'].items(), 
                                  key=lambda x: x[1], reverse=True):
            percentage = (amount / stats['total_expenses'] * 100) if stats['total_expenses'] > 0 else 0
            report.append(f"  {head:30s} ${amount:10.2f} ({percentage:5.1f}%)")
        report.append("")
        
        report.append("Top Expense Heads:")
        report.append("-" * 60)
        for head, amount in stats['top_expense_heads'].items():
            report.append(f"  {head:30s} ${amount:10.2f}")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
