"""
Analytics module for expense tracking.
"""
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime

from models import TimePeriod


class ExpenseAnalytics:
    """Analytics for expense tracking."""
    
    @staticmethod
    def get_category_breakdown(period: TimePeriod) -> Dict[str, Dict]:
        """Get detailed breakdown by category.
        
        Args:
            period: TimePeriod to analyze
            
        Returns:
            Dictionary with category breakdown including total, percentage, and count
        """
        category_totals = period.get_expenses_by_category()
        total = period.get_total_expenses()
        
        breakdown = {}
        for category, amount in category_totals.items():
            percentage = (amount / total * 100) if total > 0 else Decimal('0')
            count = sum(1 for exp in period.expenses if exp.category == category)
            breakdown[category] = {
                'total': float(amount),
                'percentage': float(percentage),
                'count': count
            }
        
        return breakdown
    
    @staticmethod
    def get_daily_average(period: TimePeriod) -> float:
        """Calculate daily average expense.
        
        Args:
            period: TimePeriod to analyze
            
        Returns:
            Daily average expense amount
        """
        days = (period.end_date - period.start_date).days + 1
        if days == 0:
            return 0.0
        return float(period.get_total_expenses() / Decimal(str(days)))
    
    @staticmethod
    def get_top_expenses(period: TimePeriod, limit: int = 10) -> List[Dict]:
        """Get top expenses by amount.
        
        Args:
            period: TimePeriod to analyze
            limit: Number of top expenses to return
            
        Returns:
            List of expense dictionaries sorted by amount (descending)
        """
        sorted_expenses = sorted(
            period.expenses,
            key=lambda x: x.amount,
            reverse=True
        )
        return [
            {
                'date': exp.date.strftime('%Y-%m-%d'),
                'category': exp.category,
                'description': exp.description,
                'amount': float(exp.amount)
            }
            for exp in sorted_expenses[:limit]
        ]
    
    @staticmethod
    def get_expense_trend(period: TimePeriod) -> Dict[str, float]:
        """Get expense trend by date (daily totals).
        
        Args:
            period: TimePeriod to analyze
            
        Returns:
            Dictionary with date strings as keys and daily totals as values
        """
        daily_totals = {}
        for exp in period.expenses:
            date_str = exp.date.strftime('%Y-%m-%d')
            daily_totals[date_str] = daily_totals.get(date_str, Decimal('0')) + exp.amount
        
        return {date: float(amount) for date, amount in sorted(daily_totals.items())}
    
    @staticmethod
    def get_summary(period: TimePeriod) -> Dict:
        """Get comprehensive summary analytics for a period.
        
        Args:
            period: TimePeriod to analyze
            
        Returns:
            Dictionary with all analytics
        """
        total = period.get_total_expenses()
        category_breakdown = ExpenseAnalytics.get_category_breakdown(period)
        daily_avg = ExpenseAnalytics.get_daily_average(period)
        top_expenses = ExpenseAnalytics.get_top_expenses(period, 5)
        trend = ExpenseAnalytics.get_expense_trend(period)
        
        return {
            'period_name': period.period_name,
            'start_date': period.start_date.strftime('%Y-%m-%d'),
            'end_date': period.end_date.strftime('%Y-%m-%d'),
            'total_expenses': float(total),
            'daily_average': daily_avg,
            'total_expense_count': len(period.expenses),
            'category_breakdown': category_breakdown,
            'top_expenses': top_expenses,
            'daily_trend': trend
        }
    
    @staticmethod
    def compare_periods(period1: TimePeriod, period2: TimePeriod) -> Dict:
        """Compare two time periods.
        
        Args:
            period1: First TimePeriod
            period2: Second TimePeriod
            
        Returns:
            Dictionary with comparison metrics
        """
        total1 = period1.get_total_expenses()
        total2 = period2.get_total_expenses()
        diff = total2 - total1
        percent_change = (diff / total1 * 100) if total1 > 0 else Decimal('0')
        
        days1 = (period1.end_date - period1.start_date).days + 1
        days2 = (period2.end_date - period2.start_date).days + 1
        
        avg1 = float(total1 / Decimal(str(days1))) if days1 > 0 else 0
        avg2 = float(total2 / Decimal(str(days2))) if days2 > 0 else 0
        
        return {
            'period1': {
                'name': period1.period_name,
                'total': float(total1),
                'daily_avg': avg1,
                'count': len(period1.expenses)
            },
            'period2': {
                'name': period2.period_name,
                'total': float(total2),
                'daily_avg': avg2,
                'count': len(period2.expenses)
            },
            'difference': {
                'amount': float(diff),
                'percent_change': float(percent_change)
            }
        }
