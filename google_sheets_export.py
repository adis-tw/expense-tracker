"""
Google Sheets export functionality.
"""
from typing import List, Optional
from models import Expense, TimePeriod
from analytics import ExpenseAnalytics
import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsExporter:
    """Export expenses to Google Sheets."""
    
    def __init__(self, credentials_file: str = "credentials.json", 
                 token_file: str = "token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.client = gspread.authorize(creds)
    
    def create_spreadsheet(self, title: str) -> gspread.Spreadsheet:
        """Create a new Google Spreadsheet."""
        spreadsheet = self.client.create(title)
        return spreadsheet
    
    def export_expenses(self, expenses: List[Expense], spreadsheet_id: str,
                       sheet_name: str = "Expenses", clear_existing: bool = True):
        """Export expenses to a Google Sheet."""
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            if clear_existing:
                worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
        
        # Prepare data
        headers = ['ID', 'Date', 'Expense Head', 'Amount', 'Description']
        data = [headers]
        
        for expense in expenses:
            data.append([
                expense.id,
                expense.date.strftime('%Y-%m-%d %H:%M:%S'),
                expense.expense_head,
                expense.amount,
                expense.description or ''
            ])
        
        # Write to sheet
        worksheet.update('A1', data)
        
        # Format header row
        worksheet.format('A1:E1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        
        return worksheet.url
    
    def export_analytics(self, analytics: ExpenseAnalytics, spreadsheet_id: str,
                        sheet_name: str = "Analytics", clear_existing: bool = True):
        """Export analytics to a Google Sheet."""
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            if clear_existing:
                worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
        
        stats = analytics.get_statistics()
        
        # Summary section
        summary_data = [
            ['SUMMARY', ''],
            ['Total Expenses', f"${stats['total_expenses']:.2f}"],
            ['Number of Expenses', stats['expense_count']],
            ['Average Daily Expense', f"${stats['average_daily_expense']:.2f}"],
            ['', ''],
            ['Date Range', ''],
            ['Start Date', stats['date_range']['start'] or ''],
            ['End Date', stats['date_range']['end'] or ''],
            ['', ''],
            ['EXPENSES BY HEAD', 'Amount', 'Percentage'],
        ]
        
        total = stats['total_expenses']
        for head, amount in sorted(stats['expenses_by_head'].items(), 
                                  key=lambda x: x[1], reverse=True):
            percentage = (amount / total * 100) if total > 0 else 0
            summary_data.append([head, f"${amount:.2f}", f"{percentage:.1f}%"])
        
        summary_data.append(['', '', ''])
        summary_data.append(['TOP EXPENSE HEADS', 'Amount', ''])
        
        for head, amount in stats['top_expense_heads'].items():
            summary_data.append([head, f"${amount:.2f}", ''])
        
        worksheet.update('A1', summary_data)
        
        # Format headers
        worksheet.format('A1:C1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        worksheet.format('A10:C10', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        
        return worksheet.url
    
    def export_time_period(self, period: TimePeriod, expenses: List[Expense],
                          spreadsheet_id: str, sheet_name: Optional[str] = None,
                          include_analytics: bool = True):
        """Export a complete time period with expenses and analytics."""
        if sheet_name is None:
            sheet_name = f"Period_{period.id}"
        
        # Export expenses
        expenses_url = self.export_expenses(expenses, spreadsheet_id, 
                                           f"{sheet_name}_Expenses")
        
        # Export analytics if requested
        analytics_url = None
        if include_analytics and expenses:
            analytics_obj = ExpenseAnalytics(expenses)
            analytics_url = self.export_analytics(analytics_obj, spreadsheet_id,
                                                 f"{sheet_name}_Analytics")
        
        return {
            'expenses_sheet': expenses_url,
            'analytics_sheet': analytics_url
        }
