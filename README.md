# Monthly Expense Tracker

A comprehensive Python-based expense tracker that allows you to track monthly expenses between custom dates, with editable expense heads for each time period, and export functionality to Google Sheets. Includes built-in analytics for each time period.

## Features

- **Custom Date Ranges**: Track expenses for any time period (not limited to calendar months)
- **Editable Expense Heads**: Define and manage expense categories (heads) for each time period
- **Expense Management**: Add, view, and manage expense entries
- **Analytics**: Comprehensive analytics including:
  - Total expenses
  - Expenses by category
  - Average daily expenses
  - Top expense heads
  - Monthly/weekly trends
  - Detailed reports
- **Google Sheets Export**: Export expenses and analytics to Google Sheets
- **Time Period Management**: Create and manage multiple time periods with different expense heads

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. For Google Sheets export, set up Google API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Sheets API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download the credentials JSON file
   - Save it as `credentials.json` in the project directory

## Usage

Run the application:
```bash
python main.py
```

Or directly:
```bash
python cli.py
```

### Main Menu Options

1. **Create time period**: Define a new time period with custom start and end dates
2. **Edit expense heads for period**: Add, remove, or modify expense categories for a time period
3. **Add expense**: Record a new expense entry
4. **View expenses**: View expenses with filters (all, by period, or by date range)
5. **View analytics**: See detailed analytics for selected expenses
6. **List time periods**: View all created time periods
7. **Export to Google Sheets**: Export expenses and analytics to Google Sheets
8. **Exit**: Quit the application

### Example Workflow

1. Create a time period (e.g., "2024-01-01" to "2024-01-31")
2. Add expense heads for that period (e.g., "Food", "Transport", "Utilities")
3. Add expenses throughout the period
4. View analytics to see spending patterns
5. Export to Google Sheets for further analysis or sharing

## Data Storage

Expenses and time periods are stored locally in `expenses.json` in JSON format. This file is automatically created and updated as you use the application.

## Google Sheets Export

When exporting to Google Sheets:
- The first time you export, you'll be asked to authenticate via your web browser
- Authentication token is saved in `token.json` for future use
- You can create a new spreadsheet or export to an existing one
- Both expenses and analytics are exported to separate sheets

## Project Structure

- `main.py`: Application entry point
- `cli.py`: Command-line interface
- `expense_tracker.py`: Core expense tracking functionality
- `models.py`: Data models (Expense, ExpenseHead, TimePeriod)
- `analytics.py`: Analytics and reporting engine
- `google_sheets_export.py`: Google Sheets export functionality
- `requirements.txt`: Python dependencies
- `expenses.json`: Local data storage (created automatically)

## Requirements

- Python 3.7+
- See `requirements.txt` for package dependencies

## Notes

- Date formats supported: YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY, DD/MM/YYYY
- Expense amounts are stored as floats
- All dates are stored with time information
- The application automatically saves data after each operation
