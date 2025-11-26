"""
Google Sheets export functionality.
"""
import os
from typing import Optional, List, Dict
from datetime import datetime

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

from models import TimePeriod
from analytics import ExpenseAnalytics


# Google Sheets API scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsExporter:
    """Export expense data to Google Sheets."""
    
    def __init__(self, credentials_file: str = "credentials.json",
                 token_file: str = "token.pickle"):
        """Initialize Google Sheets exporter.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
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
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.client = gspread.authorize(creds)
    
    def export_period(self, period: TimePeriod, spreadsheet_id: Optional[str] = None,
                     sheet_name: Optional[str] = None, create_new: bool = True) -> str:
        """Export a time period to Google Sheets.
        
        Args:
            period: TimePeriod to export
            spreadsheet_id: ID of existing spreadsheet (if None, creates new)
            sheet_name: Name of the sheet (defaults to period name)
            create_new: Whether to create a new spreadsheet if ID not provided
            
        Returns:
            URL of the created/updated spreadsheet
        """
        if self.client is None:
            raise RuntimeError("Not authenticated with Google Sheets")
        
        # Get or create spreadsheet
        if spreadsheet_id:
            try:
                spreadsheet = self.client.open_by_key(spreadsheet_id)
            except Exception as e:
                raise ValueError(f"Could not open spreadsheet with ID {spreadsheet_id}: {e}")
        else:
            if create_new:
                spreadsheet = self.client.create(f"Expense Tracker - {period.period_name}")
            else:
                raise ValueError("spreadsheet_id required when create_new=False")
        
        # Get or create sheet
        sheet_name = sheet_name or period.period_name
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            # Clear existing data
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
        
        # Prepare data
        data = self._prepare_export_data(period)
        
        # Write data to sheet
        worksheet.update('A1', data, value_input_option='USER_ENTERED')
        
        # Format header row
        worksheet.format('A1:F1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
        })
        
        return spreadsheet.url
    
    def _prepare_export_data(self, period: TimePeriod) -> List[List]:
        """Prepare data for export.
        
        Args:
            period: TimePeriod to export
            
        Returns:
            List of lists representing rows for Google Sheets
        """
        # Header
        data = [['Date', 'Category', 'Description', 'Amount', 'Period Total', 'Daily Average']]
        
        # Summary row
        total = period.get_total_expenses()
        days = (period.end_date - period.start_date).days + 1
        daily_avg = float(total / days) if days > 0 else 0
        
        data.append([
            f"Period: {period.period_name}",
            f"Total: ${float(total):.2f}",
            f"Daily Avg: ${daily_avg:.2f}",
            f"Expenses: {len(period.expenses)}",
            '',
            ''
        ])
        
        data.append([])  # Empty row
        
        # Expense rows
        sorted_expenses = sorted(period.expenses, key=lambda x: x.date)
        for exp in sorted_expenses:
            data.append([
                exp.date.strftime('%Y-%m-%d'),
                exp.category,
                exp.description,
                float(exp.amount),
                '',
                ''
            ])
        
        data.append([])  # Empty row
        
        # Category breakdown
        data.append(['Category Breakdown', '', '', '', '', ''])
        category_breakdown = ExpenseAnalytics.get_category_breakdown(period)
        for category, info in sorted(category_breakdown.items(), 
                                     key=lambda x: x[1]['total'], reverse=True):
            data.append([
                category,
                f"${info['total']:.2f}",
                f"{info['percentage']:.1f}%",
                f"{info['count']} expenses",
                '',
                ''
            ])
        
        return data
    
    def export_multiple_periods(self, periods: List[TimePeriod],
                                spreadsheet_id: Optional[str] = None,
                                create_new: bool = True) -> str:
        """Export multiple time periods to a single spreadsheet.
        
        Args:
            periods: List of TimePeriods to export
            spreadsheet_id: ID of existing spreadsheet
            create_new: Whether to create a new spreadsheet
            
        Returns:
            URL of the spreadsheet
        """
        if self.client is None:
            raise RuntimeError("Not authenticated with Google Sheets")
        
        # Get or create spreadsheet
        if spreadsheet_id:
            try:
                spreadsheet = self.client.open_by_key(spreadsheet_id)
            except Exception:
                if create_new:
                    spreadsheet = self.client.create("Expense Tracker - Multiple Periods")
                else:
                    raise
        else:
            if create_new:
                spreadsheet = self.client.create("Expense Tracker - Multiple Periods")
            else:
                raise ValueError("spreadsheet_id required when create_new=False")
        
        # Export each period to its own sheet
        for period in periods:
            try:
                worksheet = spreadsheet.worksheet(period.period_name)
                worksheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=period.period_name, rows=1000, cols=10
                )
            
            data = self._prepare_export_data(period)
            worksheet.update('A1', data, value_input_option='USER_ENTERED')
            
            # Format header
            worksheet.format('A1:F1', {
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
            })
        
        return spreadsheet.url
