"""
Main CLI application for expense tracker.
"""
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from tracker import ExpenseTracker
from analytics import ExpenseAnalytics
from export import GoogleSheetsExporter


def print_menu():
    """Print main menu."""
    print("\n" + "="*50)
    print("Monthly Expense Tracker")
    print("="*50)
    print("1. Create new time period")
    print("2. List all time periods")
    print("3. Add expense to period")
    print("4. View period details")
    print("5. View analytics for period")
    print("6. Update expense heads for period")
    print("7. Compare two periods")
    print("8. Export to Google Sheets")
    print("9. Exit")
    print("="*50)


def get_date_input(prompt: str) -> datetime:
    """Get date input from user."""
    while True:
        date_str = input(f"{prompt} (YYYY-MM-DD): ").strip()
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")


def get_decimal_input(prompt: str) -> Decimal:
    """Get decimal input from user."""
    while True:
        value_str = input(f"{prompt}: ").strip()
        try:
            return Decimal(value_str)
        except (InvalidOperation, ValueError):
            print("Invalid number. Please enter a valid decimal number.")


def create_period(tracker: ExpenseTracker):
    """Create a new time period."""
    print("\n--- Create New Time Period ---")
    start_date = get_date_input("Start date")
    end_date = get_date_input("End date")
    
    if start_date >= end_date:
        print("Error: Start date must be before end date.")
        return
    
    period_name = input("Period name (optional, press Enter for auto-generated): ").strip()
    if not period_name:
        period_name = None
    
    print("\nEnter expense heads (categories). Press Enter on empty line to finish:")
    expense_heads = []
    while True:
        head = input(f"Expense head {len(expense_heads) + 1}: ").strip()
        if not head:
            break
        expense_heads.append(head)
    
    if not expense_heads:
        print("Error: At least one expense head is required.")
        return
    
    try:
        period = tracker.create_time_period(start_date, end_date, expense_heads, period_name)
        print(f"\n✓ Time period '{period.period_name}' created successfully!")
    except Exception as e:
        print(f"Error: {e}")


def list_periods(tracker: ExpenseTracker):
    """List all time periods."""
    periods = tracker.list_time_periods()
    if not periods:
        print("\nNo time periods found.")
        return
    
    print("\n--- All Time Periods ---")
    for period in periods:
        print(f"\n[{period['index']}] {period['name']}")
        print(f"    Dates: {period['start_date']} to {period['end_date']}")
        print(f"    Expense Heads: {', '.join(period['expense_heads'])}")
        print(f"    Total Expenses: ${period['total_expenses']:.2f}")
        print(f"    Expense Count: {period['expense_count']}")


def add_expense(tracker: ExpenseTracker):
    """Add an expense to a period."""
    periods = tracker.list_time_periods()
    if not periods:
        print("\nNo time periods found. Please create one first.")
        return
    
    print("\n--- Add Expense ---")
    list_periods(tracker)
    
    try:
        period_idx = int(input("\nEnter period index: "))
        period = tracker.get_time_period(index=period_idx)
        if period is None:
            print("Invalid period index.")
            return
        
        print(f"\nAvailable categories: {', '.join(period.expense_heads)}")
        category = input("Category: ").strip()
        description = input("Description: ").strip()
        amount = get_decimal_input("Amount")
        date = get_date_input("Date")
        
        expense = tracker.add_expense(amount, category, description, date, period_index=period_idx)
        print(f"\n✓ Expense added successfully!")
        print(f"   ID: {expense.id}")
        print(f"   Amount: ${float(expense.amount):.2f}")
        
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")


def view_period_details(tracker: ExpenseTracker):
    """View details of a time period."""
    periods = tracker.list_time_periods()
    if not periods:
        print("\nNo time periods found.")
        return
    
    print("\n--- View Period Details ---")
    list_periods(tracker)
    
    try:
        period_idx = int(input("\nEnter period index: "))
        period = tracker.get_time_period(index=period_idx)
        if period is None:
            print("Invalid period index.")
            return
        
        print(f"\n{'='*60}")
        print(f"Period: {period.period_name}")
        print(f"Dates: {period.start_date.strftime('%Y-%m-%d')} to {period.end_date.strftime('%Y-%m-%d')}")
        print(f"Expense Heads: {', '.join(period.expense_heads)}")
        print(f"Total Expenses: ${float(period.get_total_expenses()):.2f}")
        print(f"Number of Expenses: {len(period.expenses)}")
        print(f"{'='*60}")
        
        if period.expenses:
            print("\nExpenses:")
            print("-" * 60)
            sorted_expenses = sorted(period.expenses, key=lambda x: x.date)
            for exp in sorted_expenses:
                print(f"{exp.date.strftime('%Y-%m-%d')} | {exp.category:15s} | "
                      f"${float(exp.amount):10.2f} | {exp.description}")
        else:
            print("\nNo expenses recorded yet.")
            
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")


def view_analytics(tracker: ExpenseTracker):
    """View analytics for a period."""
    periods = tracker.list_time_periods()
    if not periods:
        print("\nNo time periods found.")
        return
    
    print("\n--- View Analytics ---")
    list_periods(tracker)
    
    try:
        period_idx = int(input("\nEnter period index: "))
        period = tracker.get_time_period(index=period_idx)
        if period is None:
            print("Invalid period index.")
            return
        
        summary = ExpenseAnalytics.get_summary(period)
        
        print(f"\n{'='*60}")
        print(f"Analytics for: {summary['period_name']}")
        print(f"{'='*60}")
        print(f"\nTotal Expenses: ${summary['total_expenses']:.2f}")
        print(f"Daily Average: ${summary['daily_average']:.2f}")
        print(f"Total Expense Count: {summary['total_expense_count']}")
        
        print(f"\n--- Category Breakdown ---")
        for category, info in sorted(summary['category_breakdown'].items(),
                                     key=lambda x: x[1]['total'], reverse=True):
            print(f"{category:20s}: ${info['total']:10.2f} ({info['percentage']:5.1f}%) "
                  f"- {info['count']} expenses")
        
        if summary['top_expenses']:
            print(f"\n--- Top 5 Expenses ---")
            for i, exp in enumerate(summary['top_expenses'], 1):
                print(f"{i}. {exp['date']} | {exp['category']:15s} | "
                      f"${exp['amount']:10.2f} | {exp['description']}")
        
        print(f"\n{'='*60}")
        
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")


def update_expense_heads(tracker: ExpenseTracker):
    """Update expense heads for a period."""
    periods = tracker.list_time_periods()
    if not periods:
        print("\nNo time periods found.")
        return
    
    print("\n--- Update Expense Heads ---")
    list_periods(tracker)
    
    try:
        period_idx = int(input("\nEnter period index: "))
        period = tracker.get_time_period(index=period_idx)
        if period is None:
            print("Invalid period index.")
            return
        
        print(f"\nCurrent expense heads: {', '.join(period.expense_heads)}")
        print("\nEnter new expense heads (press Enter on empty line to finish):")
        expense_heads = []
        while True:
            head = input(f"Expense head {len(expense_heads) + 1}: ").strip()
            if not head:
                break
            expense_heads.append(head)
        
        if not expense_heads:
            print("Error: At least one expense head is required.")
            return
        
        tracker.update_expense_heads(period_index=period_idx, expense_heads=expense_heads)
        print(f"\n✓ Expense heads updated successfully!")
        
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")


def compare_periods(tracker: ExpenseTracker):
    """Compare two periods."""
    periods = tracker.list_time_periods()
    if len(periods) < 2:
        print("\nNeed at least 2 time periods to compare.")
        return
    
    print("\n--- Compare Periods ---")
    list_periods(tracker)
    
    try:
        idx1 = int(input("\nEnter first period index: "))
        idx2 = int(input("Enter second period index: "))
        
        period1 = tracker.get_time_period(index=idx1)
        period2 = tracker.get_time_period(index=idx2)
        
        if period1 is None or period2 is None:
            print("Invalid period index.")
            return
        
        comparison = ExpenseAnalytics.compare_periods(period1, period2)
        
        print(f"\n{'='*60}")
        print("Period Comparison")
        print(f"{'='*60}")
        print(f"\nPeriod 1: {comparison['period1']['name']}")
        print(f"  Total: ${comparison['period1']['total']:.2f}")
        print(f"  Daily Avg: ${comparison['period1']['daily_avg']:.2f}")
        print(f"  Count: {comparison['period1']['count']}")
        
        print(f"\nPeriod 2: {comparison['period2']['name']}")
        print(f"  Total: ${comparison['period2']['total']:.2f}")
        print(f"  Daily Avg: ${comparison['period2']['daily_avg']:.2f}")
        print(f"  Count: {comparison['period2']['count']}")
        
        print(f"\nDifference:")
        print(f"  Amount: ${comparison['difference']['amount']:.2f}")
        print(f"  Percent Change: {comparison['difference']['percent_change']:.1f}%")
        print(f"{'='*60}")
        
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")


def export_to_sheets(tracker: ExpenseTracker):
    """Export to Google Sheets."""
    periods = tracker.list_time_periods()
    if not periods:
        print("\nNo time periods found.")
        return
    
    print("\n--- Export to Google Sheets ---")
    print("Note: You need to set up Google Sheets API credentials first.")
    print("See README.md for instructions.")
    
    try:
        exporter = GoogleSheetsExporter()
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nTo set up Google Sheets export:")
        print("1. Go to Google Cloud Console")
        print("2. Create a project and enable Google Sheets API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download credentials.json to the project directory")
        return
    except Exception as e:
        print(f"Error authenticating: {e}")
        return
    
    list_periods(tracker)
    
    choice = input("\nExport (1) single period or (2) all periods? [1/2]: ").strip()
    
    try:
        if choice == '1':
            period_idx = int(input("Enter period index: "))
            period = tracker.get_time_period(index=period_idx)
            if period is None:
                print("Invalid period index.")
                return
            
            url = exporter.export_period(period)
            print(f"\n✓ Exported successfully!")
            print(f"Spreadsheet URL: {url}")
        elif choice == '2':
            all_periods = [tracker.get_time_period(index=i) for i in range(len(periods))]
            url = exporter.export_multiple_periods(all_periods)
            print(f"\n✓ Exported successfully!")
            print(f"Spreadsheet URL: {url}")
        else:
            print("Invalid choice.")
    except Exception as e:
        print(f"Error exporting: {e}")


def main():
    """Main application loop."""
    tracker = ExpenseTracker()
    
    print("Welcome to Monthly Expense Tracker!")
    
    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            create_period(tracker)
        elif choice == '2':
            list_periods(tracker)
        elif choice == '3':
            add_expense(tracker)
        elif choice == '4':
            view_period_details(tracker)
        elif choice == '5':
            view_analytics(tracker)
        elif choice == '6':
            update_expense_heads(tracker)
        elif choice == '7':
            compare_periods(tracker)
        elif choice == '8':
            export_to_sheets(tracker)
        elif choice == '9':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
