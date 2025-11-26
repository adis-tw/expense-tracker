"""
Command-line interface for the expense tracker.
"""
from datetime import datetime
from typing import Optional
from expense_tracker import ExpenseTracker
from models import ExpenseHead
from analytics import ExpenseAnalytics
from google_sheets_export import GoogleSheetsExporter
from tabulate import tabulate
import sys
import os


class ExpenseTrackerCLI:
    """Command-line interface for expense tracking."""
    
    def __init__(self):
        self.tracker = ExpenseTracker()
        self.sheets_exporter = None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in various formats."""
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _print_expenses(self, expenses, title="Expenses"):
        """Print expenses in a formatted table."""
        if not expenses:
            print(f"\nNo {title.lower()} found.")
            return
        
        data = []
        for expense in expenses:
            data.append([
                expense.id[:8] + '...',
                expense.date.strftime('%Y-%m-%d'),
                expense.expense_head,
                f"${expense.amount:.2f}",
                expense.description or ''
            ])
        
        print(f"\n{title}:")
        print(tabulate(data, headers=['ID', 'Date', 'Head', 'Amount', 'Description'], 
                      tablefmt='grid'))
        print(f"\nTotal: ${sum(e.amount for e in expenses):.2f}")
    
    def create_period(self):
        """Create a new time period."""
        print("\n=== Create Time Period ===")
        
        start_str = input("Start date (YYYY-MM-DD): ").strip()
        end_str = input("End date (YYYY-MM-DD): ").strip()
        
        try:
            start_date = self._parse_date(start_str)
            end_date = self._parse_date(end_str)
            
            if start_date > end_date:
                print("Error: Start date must be before end date.")
                return
            
            period = self.tracker.create_time_period(start_date, end_date)
            print(f"\nTime period created: {period.id}")
            print(f"  Start: {start_date.strftime('%Y-%m-%d')}")
            print(f"  End: {end_date.strftime('%Y-%m-%d')}")
            
            # Ask if user wants to add expense heads
            add_heads = input("\nAdd expense heads now? (y/n): ").strip().lower()
            if add_heads == 'y':
                self.edit_period_heads(period.id)
        
        except ValueError as e:
            print(f"Error: {e}")
    
    def edit_period_heads(self, period_id: Optional[str] = None):
        """Edit expense heads for a time period."""
        if period_id is None:
            print("\n=== Edit Expense Heads ===")
            periods = self.tracker.get_all_time_periods()
            if not periods:
                print("No time periods found. Create one first.")
                return
            
            print("\nAvailable time periods:")
            for i, period in enumerate(periods, 1):
                print(f"{i}. {period.id} ({period.start_date.strftime('%Y-%m-%d')} to "
                      f"{period.end_date.strftime('%Y-%m-%d')})")
            
            choice = input("\nSelect period number: ").strip()
            try:
                period_id = periods[int(choice) - 1].id
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
        
        period = self.tracker.get_time_period(period_id)
        if not period:
            print("Period not found.")
            return
        
        print(f"\nEditing expense heads for period: {period.id}")
        print("Current expense heads:")
        for i, head in enumerate(period.expense_heads, 1):
            print(f"{i}. {head.name}")
        
        print("\nOptions:")
        print("1. Add new head")
        print("2. Remove head")
        print("3. Clear all")
        print("4. Done")
        
        new_heads = period.expense_heads.copy()
        
        while True:
            option = input("\nSelect option: ").strip()
            
            if option == '1':
                name = input("Expense head name: ").strip()
                desc = input("Description (optional): ").strip() or None
                new_heads.append(ExpenseHead(name=name, description=desc))
                print(f"Added: {name}")
            
            elif option == '2':
                if not new_heads:
                    print("No heads to remove.")
                    continue
                for i, head in enumerate(new_heads, 1):
                    print(f"{i}. {head.name}")
                try:
                    idx = int(input("Select number to remove: ").strip()) - 1
                    removed = new_heads.pop(idx)
                    print(f"Removed: {removed.name}")
                except (ValueError, IndexError):
                    print("Invalid selection.")
            
            elif option == '3':
                new_heads = []
                print("All heads cleared.")
            
            elif option == '4':
                break
            
            else:
                print("Invalid option.")
        
        self.tracker.update_time_period_heads(period_id, new_heads)
        print(f"\nUpdated expense heads for period {period_id}")
    
    def add_expense(self):
        """Add a new expense."""
        print("\n=== Add Expense ===")
        
        amount_str = input("Amount: ").strip()
        try:
            amount = float(amount_str)
        except ValueError:
            print("Error: Invalid amount.")
            return
        
        expense_head = input("Expense head: ").strip()
        if not expense_head:
            print("Error: Expense head is required.")
            return
        
        date_str = input("Date (YYYY-MM-DD, or press Enter for today): ").strip()
        if date_str:
            try:
                date = self._parse_date(date_str)
            except ValueError as e:
                print(f"Error: {e}")
                return
        else:
            date = datetime.now()
        
        description = input("Description (optional): ").strip() or None
        
        expense = self.tracker.add_expense(amount, expense_head, date, description)
        print(f"\nExpense added successfully!")
        print(f"  ID: {expense.id}")
        print(f"  Amount: ${expense.amount:.2f}")
        print(f"  Head: {expense.expense_head}")
        print(f"  Date: {expense.date.strftime('%Y-%m-%d')}")
    
    def view_expenses(self):
        """View expenses with filters."""
        print("\n=== View Expenses ===")
        print("1. All expenses")
        print("2. By time period")
        print("3. By date range")
        
        choice = input("\nSelect option: ").strip()
        expenses = []
        
        if choice == '1':
            expenses = self.tracker.get_expenses()
        
        elif choice == '2':
            periods = self.tracker.get_all_time_periods()
            if not periods:
                print("No time periods found.")
                return
            
            print("\nAvailable time periods:")
            for i, period in enumerate(periods, 1):
                print(f"{i}. {period.id} ({period.start_date.strftime('%Y-%m-%d')} to "
                      f"{period.end_date.strftime('%Y-%m-%d')})")
            
            try:
                period_idx = int(input("\nSelect period number: ").strip()) - 1
                period_id = periods[period_idx].id
                expenses = self.tracker.get_expenses(period_id=period_id)
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
        
        elif choice == '3':
            start_str = input("Start date (YYYY-MM-DD): ").strip()
            end_str = input("End date (YYYY-MM-DD): ").strip()
            
            try:
                start_date = self._parse_date(start_str)
                end_date = self._parse_date(end_str)
                expenses = self.tracker.get_expenses(start_date=start_date, end_date=end_date)
            except ValueError as e:
                print(f"Error: {e}")
                return
        
        else:
            print("Invalid option.")
            return
        
        self._print_expenses(expenses)
    
    def view_analytics(self):
        """View analytics for expenses."""
        print("\n=== View Analytics ===")
        print("1. All expenses")
        print("2. By time period")
        print("3. By date range")
        
        choice = input("\nSelect option: ").strip()
        expenses = []
        
        if choice == '1':
            expenses = self.tracker.get_expenses()
        
        elif choice == '2':
            periods = self.tracker.get_all_time_periods()
            if not periods:
                print("No time periods found.")
                return
            
            print("\nAvailable time periods:")
            for i, period in enumerate(periods, 1):
                print(f"{i}. {period.id} ({period.start_date.strftime('%Y-%m-%d')} to "
                      f"{period.end_date.strftime('%Y-%m-%d')})")
            
            try:
                period_idx = int(input("\nSelect period number: ").strip()) - 1
                period_id = periods[period_idx].id
                expenses = self.tracker.get_expenses(period_id=period_id)
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
        
        elif choice == '3':
            start_str = input("Start date (YYYY-MM-DD): ").strip()
            end_str = input("End date (YYYY-MM-DD): ").strip()
            
            try:
                start_date = self._parse_date(start_str)
                end_date = self._parse_date(end_str)
                expenses = self.tracker.get_expenses(start_date=start_date, end_date=end_date)
            except ValueError as e:
                print(f"Error: {e}")
                return
        
        else:
            print("Invalid option.")
            return
        
        if not expenses:
            print("\nNo expenses found for the selected criteria.")
            return
        
        analytics = ExpenseAnalytics(expenses)
        print(analytics.generate_report())
    
    def export_to_sheets(self):
        """Export expenses to Google Sheets."""
        print("\n=== Export to Google Sheets ===")
        
        if not os.path.exists("credentials.json"):
            print("\nError: credentials.json not found.")
            print("Please download it from Google Cloud Console:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Create a new project or select existing")
            print("3. Enable Google Sheets API")
            print("4. Create OAuth 2.0 credentials")
            print("5. Download credentials.json to this directory")
            return
        
        try:
            if self.sheets_exporter is None:
                self.sheets_exporter = GoogleSheetsExporter()
        except Exception as e:
            print(f"Error initializing Google Sheets exporter: {e}")
            return
        
        print("\nExport options:")
        print("1. Create new spreadsheet")
        print("2. Export to existing spreadsheet")
        
        option = input("\nSelect option: ").strip()
        
        if option == '1':
            title = input("Spreadsheet title: ").strip() or "Expense Tracker"
            spreadsheet = self.sheets_exporter.create_spreadsheet(title)
            spreadsheet_id = spreadsheet.id
            print(f"\nCreated spreadsheet: {spreadsheet.url}")
        
        elif option == '2':
            spreadsheet_id = input("Spreadsheet ID (from URL): ").strip()
        
        else:
            print("Invalid option.")
            return
        
        print("\nWhat to export:")
        print("1. All expenses")
        print("2. By time period")
        print("3. By date range")
        
        choice = input("\nSelect option: ").strip()
        expenses = []
        period = None
        
        if choice == '1':
            expenses = self.tracker.get_expenses()
        
        elif choice == '2':
            periods = self.tracker.get_all_time_periods()
            if not periods:
                print("No time periods found.")
                return
            
            print("\nAvailable time periods:")
            for i, p in enumerate(periods, 1):
                print(f"{i}. {p.id} ({p.start_date.strftime('%Y-%m-%d')} to "
                      f"{p.end_date.strftime('%Y-%m-%d')})")
            
            try:
                period_idx = int(input("\nSelect period number: ").strip()) - 1
                period = periods[period_idx]
                expenses = self.tracker.get_expenses(period_id=period.id)
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
        
        elif choice == '3':
            start_str = input("Start date (YYYY-MM-DD): ").strip()
            end_str = input("End date (YYYY-MM-DD): ").strip()
            
            try:
                start_date = self._parse_date(start_str)
                end_date = self._parse_date(end_str)
                expenses = self.tracker.get_expenses(start_date=start_date, end_date=end_date)
            except ValueError as e:
                print(f"Error: {e}")
                return
        
        else:
            print("Invalid option.")
            return
        
        if not expenses:
            print("\nNo expenses to export.")
            return
        
        try:
            if period:
                result = self.sheets_exporter.export_time_period(
                    period, expenses, spreadsheet_id
                )
                print(f"\nExported successfully!")
                print(f"Expenses sheet: {result['expenses_sheet']}")
                if result['analytics_sheet']:
                    print(f"Analytics sheet: {result['analytics_sheet']}")
            else:
                expenses_url = self.sheets_exporter.export_expenses(
                    expenses, spreadsheet_id, "Expenses"
                )
                analytics = ExpenseAnalytics(expenses)
                analytics_url = self.sheets_exporter.export_analytics(
                    analytics, spreadsheet_id, "Analytics"
                )
                print(f"\nExported successfully!")
                print(f"Expenses sheet: {expenses_url}")
                print(f"Analytics sheet: {analytics_url}")
        
        except Exception as e:
            print(f"\nError exporting: {e}")
    
    def list_periods(self):
        """List all time periods."""
        periods = self.tracker.get_all_time_periods()
        
        if not periods:
            print("\nNo time periods found.")
            return
        
        print("\n=== Time Periods ===")
        data = []
        for period in periods:
            expense_count = len(self.tracker.get_expenses(period_id=period.id))
            data.append([
                period.id,
                period.start_date.strftime('%Y-%m-%d'),
                period.end_date.strftime('%Y-%m-%d'),
                len(period.expense_heads),
                expense_count
            ])
        
        print(tabulate(data, headers=['ID', 'Start Date', 'End Date', 
                                     'Expense Heads', 'Expenses'], 
                      tablefmt='grid'))
    
    def run(self):
        """Run the CLI main loop."""
        print("\n" + "=" * 60)
        print("MONTHLY EXPENSE TRACKER")
        print("=" * 60)
        
        while True:
            print("\nMain Menu:")
            print("1. Create time period")
            print("2. Edit expense heads for period")
            print("3. Add expense")
            print("4. View expenses")
            print("5. View analytics")
            print("6. List time periods")
            print("7. Export to Google Sheets")
            print("8. Exit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.create_period()
            elif choice == '2':
                self.edit_period_heads()
            elif choice == '3':
                self.add_expense()
            elif choice == '4':
                self.view_expenses()
            elif choice == '5':
                self.view_analytics()
            elif choice == '6':
                self.list_periods()
            elif choice == '7':
                self.export_to_sheets()
            elif choice == '8':
                print("\nGoodbye!")
                break
            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    cli = ExpenseTrackerCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
