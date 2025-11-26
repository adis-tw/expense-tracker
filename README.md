# Monthly Expense Tracker

A comprehensive expense tracking application that allows you to:
- Track expenses between custom date ranges
- Manage editable expense heads for each time period
- View detailed analytics with charts and statistics
- Export data to Google Sheets

## Features

### 📅 Custom Time Periods
- Create time periods with custom start and end dates
- Each period is independent with its own expense heads and expenses

### 💰 Expense Management
- Add, edit, and delete expenses
- Categorize expenses by custom expense heads
- Track amount, date, and description for each expense

### 📊 Analytics Dashboard
- Total expenses for each period
- Average daily expenses
- Visual charts showing:
  - Expenses breakdown by head (doughnut chart)
  - Daily expenses trend (line chart)

### 📤 Google Sheets Export
- Export complete expense data to Google Sheets
- Includes summary, analytics, and period information
- Automatically formatted with headers and styling

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Google Sheets Export Setup

To enable Google Sheets export functionality:

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable APIs:**
   - Enable "Google Sheets API"
   - Enable "Google Drive API"

3. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Create a service account and download the JSON key file

4. **Save Credentials:**
   - Rename the downloaded JSON file to `credentials.json`
   - Place it in the project root directory
   - **Important:** Add `credentials.json` to `.gitignore` to keep it secure

5. **Alternative: Set Environment Variable:**
   ```bash
   export GOOGLE_CREDENTIALS_FILE=/path/to/your/credentials.json
   ```

## Usage

### Creating a Time Period
1. Click "New Period" button
2. Enter a name for the period (e.g., "January 2024")
3. Select start and end dates
4. Click "Create Period"

### Managing Expense Heads
1. Select a time period
2. Click "Add Head" to create expense categories
3. Edit or delete heads as needed
4. Each time period has its own set of expense heads

### Adding Expenses
1. Select a time period
2. Choose an expense head from the dropdown
3. Enter amount, description (optional), and date
4. Click "Add Expense"

### Viewing Analytics
1. Select a time period
2. Click "Analytics" button
3. View charts and statistics for the selected period

### Exporting to Google Sheets
1. Select a time period
2. Click "Export to Google Sheets"
3. The exported spreadsheet will be created in your Google Drive
4. You'll receive a link to access the spreadsheet

## Database

The application uses SQLite database (`expenses.db`) to store:
- Time periods
- Expense heads (per period)
- Expenses

The database is automatically created when you first run the application.

## Project Structure

```
expense-tracker/
├── app.py                 # Flask application and API routes
├── export_to_sheets.py    # Google Sheets export functionality
├── requirements.txt       # Python dependencies
├── expenses.db           # SQLite database (created automatically)
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Stylesheet
    └── js/
        └── app.js        # Frontend JavaScript
```

## Technologies Used

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Charts:** Chart.js
- **Google Sheets:** gspread, Google API Client

## License

This project is open source and available for personal use.

## Notes

- The application runs on `http://localhost:5000` by default
- All data is stored locally in SQLite database
- Google Sheets export requires valid credentials
- Each time period maintains its own expense heads and expenses independently
