# Monthly Expense Tracker

A comprehensive monthly expense tracker application with custom date ranges, editable expense heads, and analytics.

## Features

- **Custom Date Ranges**: Track expenses for any custom date range, not just calendar months
- **Editable Expense Heads**: Create and manage custom expense categories (heads) for each time period
- **Expense Management**: Add, view, and delete expenses with date, category, amount, and description
- **Analytics Dashboard**: 
  - Total expenses, count, and average
  - Pie chart showing expenses by category
  - Bar chart for visual comparison
  - Detailed breakdown table with percentages
- **Multiple Time Periods**: Save and switch between different time periods
- **Export to Google Sheets**: Export expenses and analytics as CSV (can be imported to Google Sheets)

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. **Set Date Range**: Select your custom start and end dates
2. **Configure Expense Heads**: Add or remove expense categories as needed
3. **Add Expenses**: Fill in the expense form with date, head, amount, and optional description
4. **View Analytics**: Check the analytics panel for insights and visualizations
5. **Save Period**: Click "Save Period" to save your current time period
6. **Export**: Click "Export to Google Sheets" to download a CSV file that can be imported into Google Sheets

## Technology Stack

- React 18
- Recharts for analytics visualizations
- date-fns for date handling
- Local Storage for data persistence

## Future Enhancements

- Direct Google Sheets API integration (currently exports CSV)
- Edit expense functionality
- Data filtering and search
- Budget tracking and alerts
- Multi-currency support
