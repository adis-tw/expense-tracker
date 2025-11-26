# Monthly Expense Tracker

A comprehensive Python-based expense tracker that allows you to track monthly expenses between custom dates, with editable expense heads for each time period, and export functionality to Google Sheets. Includes detailed analytics for each time period.

## Features

- **Custom Date Ranges**: Create time periods with any start and end dates
- **Editable Expense Heads**: Define custom expense categories (heads) for each time period
- **Expense Tracking**: Add, view, and manage expenses within time periods
- **Analytics**: Comprehensive analytics including:
  - Total expenses and daily averages
  - Category breakdowns with percentages
  - Top expenses by amount
  - Daily expense trends
  - Period comparisons
- **Google Sheets Export**: Export expense data and analytics to Google Sheets
- **Data Persistence**: All data is saved to JSON file automatically

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up Google Sheets API for export functionality:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Sheets API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials JSON file
   - Save it as `credentials.json` in the project directory

## Usage

### Running the Application

```bash
python main.py
```

### Basic Workflow

1. **Create a Time Period**
   - Select option 1 from the menu
   - Enter start and end dates (YYYY-MM-DD format)
   - Optionally provide a period name
   - Define expense heads (categories) for this period

2. **Add Expenses**
   - Select option 3 from the menu
   - Choose a time period
   - Enter expense details:
     - Category (must match one of the expense heads)
     - Description
     - Amount
     - Date

3. **View Analytics**
   - Select option 5 from the menu
   - Choose a time period
   - View comprehensive analytics including:
     - Total expenses and daily average
     - Category breakdown with percentages
     - Top 5 expenses

4. **Export to Google Sheets**
   - Select option 8 from the menu
   - Choose to export a single period or all periods
   - The spreadsheet will include:
     - All expense entries
     - Summary statistics
     - Category breakdowns

### Menu Options

1. **Create new time period**: Set up a new tracking period with custom dates and expense heads
2. **List all time periods**: View all created periods with summary information
3. **Add expense to period**: Record a new expense entry
4. **View period details**: See all expenses in a period
5. **View analytics for period**: Get detailed analytics and insights
6. **Update expense heads for period**: Modify the expense categories for a period
7. **Compare two periods**: Compare expenses between two time periods
8. **Export to Google Sheets**: Export data to Google Sheets
9. **Exit**: Quit the application

## Project Structure

```
.
├── main.py              # Main CLI application
├── tracker.py           # Core expense tracking functionality
├── models.py            # Data models (Expense, TimePeriod)
├── analytics.py         # Analytics and reporting functions
├── export.py            # Google Sheets export functionality
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore file
```

## Data Storage

All expense data is automatically saved to `expense_data.json` in the project directory. This file contains:
- All time periods with their date ranges
- Expense heads for each period
- All expense entries

## Google Sheets Export Setup

To enable Google Sheets export:

1. **Create Google Cloud Project**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable Google Sheets API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Create OAuth Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file

4. **Save Credentials**:
   - Rename the downloaded file to `credentials.json`
   - Place it in the project root directory

5. **First Run**:
   - When you first export, a browser window will open
   - Sign in with your Google account
   - Grant permissions
   - A `token.pickle` file will be created for future use

## Example Usage

```
1. Create a time period:
   Start date: 2024-01-01
   End date: 2024-01-31
   Period name: January 2024
   Expense heads: Food, Transportation, Utilities, Entertainment

2. Add expenses:
   - Food: $150.00 - "Groceries" - 2024-01-05
   - Transportation: $50.00 - "Gas" - 2024-01-10
   - Utilities: $100.00 - "Electricity" - 2024-01-15

3. View analytics:
   - Total: $300.00
   - Daily Average: $9.68
   - Category breakdown with percentages

4. Export to Google Sheets:
   - Creates a formatted spreadsheet with all data
```

## Requirements

- Python 3.7+
- pandas >= 2.0.0
- gspread >= 5.12.0
- google-auth >= 2.23.0
- google-auth-oauthlib >= 1.1.0
- google-auth-httplib2 >= 0.1.1
- python-dateutil >= 2.8.2

## Notes

- Expense dates must fall within the time period's date range
- Expense categories must match one of the defined expense heads
- All monetary values are stored using Python's `Decimal` for precision
- The application automatically saves data after each operation
- Google Sheets export requires internet connection and valid credentials

## License

This project is open source and available for personal use.
