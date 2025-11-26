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

The application provides two interfaces:
- **CLI Interface**: Command-line interface for terminal use
- **Web Dashboard**: Browser-based interface with visualizations

### Running the CLI Application

```bash
python main.py
```

### Running the Web Dashboard

```bash
python app.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

The web dashboard provides:
- Visual overview of all time periods
- Interactive charts for category breakdowns and daily trends
- Easy expense entry through forms
- Period comparison tools
- Real-time analytics visualization

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
├── app.py               # Flask web application (dashboard)
├── tracker.py           # Core expense tracking functionality
├── models.py            # Data models (Expense, TimePeriod)
├── analytics.py         # Analytics and reporting functions
├── export.py            # Google Sheets export functionality
├── templates/           # HTML templates for web dashboard
│   ├── base.html        # Base template
│   ├── dashboard.html   # Main dashboard page
│   └── period_detail.html  # Period detail page
├── static/              # Static files (CSS, JS)
│   └── css/
│       └── style.css    # Dashboard styles
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
- flask >= 2.3.0

## Web Dashboard Features

The web dashboard provides a user-friendly interface with:

- **Dashboard Overview**: View all time periods at a glance with summary statistics
- **Period Details**: Detailed view of each period with:
  - Summary cards (total expenses, daily average, expense count)
  - Interactive charts (category breakdown pie chart, daily trend line chart)
  - Expense list with sorting
  - Category breakdown details
  - Top 5 expenses
- **Period Comparison**: Compare two periods side-by-side
- **Easy Data Entry**: Modal forms for creating periods and adding expenses
- **Responsive Design**: Works on desktop and mobile devices

Both the CLI and web dashboard share the same data file (`expense_data.json`), so you can use either interface interchangeably.

## Notes

- Expense dates must fall within the time period's date range
- Expense categories must match one of the defined expense heads
- All monetary values are stored using Python's `Decimal` for precision
- The application automatically saves data after each operation
- Google Sheets export requires internet connection and valid credentials
- The web dashboard runs on `http://localhost:5000` by default
- Both CLI and web dashboard can be used simultaneously with the same data

## License

This project is open source and available for personal use.
