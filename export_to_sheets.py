"""
Google Sheets Export Module
Export expense data to Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import sqlite3

# Google Sheets API scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_google_client():
    """Get authenticated Google Sheets client"""
    creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    if not os.path.exists(creds_file):
        raise FileNotFoundError(
            f"Google credentials file not found: {creds_file}\n"
            "Please download your service account credentials from Google Cloud Console\n"
            "and save it as 'credentials.json' in the project root."
        )
    
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPE)
    return gspread.authorize(creds)

def export_expenses_to_sheets(period_id):
    """
    Export expenses for a time period to Google Sheets
    
    Args:
        period_id: ID of the time period to export
        
    Returns:
        dict: Result with success status and sheet URL
    """
    try:
        # Get period and expenses data
        conn = get_db_connection()
        
        period = conn.execute(
            'SELECT * FROM time_periods WHERE id = ?', (period_id,)
        ).fetchone()
        
        if not period:
            return {'success': False, 'message': 'Time period not found'}
        
        expenses = conn.execute('''
            SELECT e.*, eh.head_name, tp.name as period_name
            FROM expenses e
            JOIN expense_heads eh ON e.expense_head_id = eh.id
            JOIN time_periods tp ON e.time_period_id = tp.id
            WHERE e.time_period_id = ?
            ORDER BY e.expense_date, e.created_at
        ''', (period_id,)).fetchall()
        
        conn.close()
        
        # Get Google Sheets client
        client = get_google_client()
        
        # Create a new spreadsheet
        spreadsheet_name = f"Expense Tracker - {period['name']} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        spreadsheet = client.create(spreadsheet_name)
        
        # Get the first worksheet
        worksheet = spreadsheet.sheet1
        
        # Set headers
        headers = ['Date', 'Expense Head', 'Amount', 'Description']
        worksheet.append_row(headers)
        
        # Format header row
        worksheet.format('A1:D1', {
            'backgroundColor': {'red': 0.4, 'green': 0.49, 'blue': 0.92},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
        })
        
        # Add expense data
        total = 0
        for expense in expenses:
            row = [
                expense['expense_date'],
                expense['head_name'],
                float(expense['amount']),
                expense['description'] or ''
            ]
            worksheet.append_row(row)
            total += float(expense['amount'])
        
        # Add summary row
        worksheet.append_row([''])  # Empty row
        worksheet.append_row(['TOTAL', '', total, ''])
        
        # Format summary row
        last_row = len(expenses) + 3
        worksheet.format(f'A{last_row}:D{last_row}', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
        })
        
        # Add period info sheet
        info_sheet = spreadsheet.add_worksheet(title="Period Info", rows=10, cols=2)
        info_sheet.append_row(['Period Name', period['name']])
        info_sheet.append_row(['Start Date', period['start_date']])
        info_sheet.append_row(['End Date', period['end_date']])
        info_sheet.append_row(['Total Expenses', total])
        info_sheet.append_row(['Number of Expenses', len(expenses)])
        
        # Format info sheet
        info_sheet.format('A1:A5', {'textFormat': {'bold': True}})
        
        # Calculate analytics by head
        by_head = {}
        for expense in expenses:
            head = expense['head_name']
            by_head[head] = by_head.get(head, 0) + float(expense['amount'])
        
        # Add analytics sheet
        analytics_sheet = spreadsheet.add_worksheet(title="Analytics", rows=20, cols=2)
        analytics_sheet.append_row(['Expense Head', 'Total Amount'])
        analytics_sheet.format('A1:B1', {
            'backgroundColor': {'red': 0.4, 'green': 0.49, 'blue': 0.92},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
        })
        
        for head, amount in sorted(by_head.items(), key=lambda x: x[1], reverse=True):
            analytics_sheet.append_row([head, amount])
        
        # Make the spreadsheet publicly viewable (optional - comment out if you want it private)
        # spreadsheet.share('', perm_type='anyone', role='reader')
        
        return {
            'success': True,
            'message': 'Successfully exported to Google Sheets',
            'url': spreadsheet.url,
            'spreadsheet_id': spreadsheet.id
        }
        
    except FileNotFoundError as e:
        return {'success': False, 'message': str(e)}
    except Exception as e:
        return {'success': False, 'message': f'Export error: {str(e)}'}
