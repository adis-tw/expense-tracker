# Monthly Expense Tracker

Python toolkit for tracking expenses within any custom date range, analyzing spend
by category (head), and exporting the results to Google Sheets on demand.

## Features
- Define arbitrary periods (e.g., calendar months, project phases) with their own heads and optional budgets.
- Record expenses with date, head, amount, and notes.
- Built-in analytics: category totals, budget deltas, burn rate, peak spend day, and cumulative trend.
- JSON-based persistence keeps the tool lightweight and portable.
- One-command export to Google Sheets (ideal for sharing reports).

## Getting Started
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Running `main.py` seeds a demo period (`Sample-Nov-2025`) and prints analytics to the console. Data is stored in `data/expenses.json`.

## Using the Library

```python
from datetime import date
from expense_tracker import ExpenseHead, ExpenseTracker, calculate_period_analytics
from expense_tracker.data_store import JSONDataStore

tracker = ExpenseTracker(JSONDataStore("data/expenses.json"))
tracker.create_period(
    label="Jan-2026",
    start_date=date(2026, 1, 1),
    end_date=date(2026, 1, 31),
    heads=[ExpenseHead("Rent", 1200), ExpenseHead("Food", 500), ExpenseHead("Misc")],
)
tracker.record_expense("Jan-2026", expense_date=date(2026, 1, 2), head="Rent", amount=1200)

period = tracker.get_period("Jan-2026")
analytics = calculate_period_analytics(period)
print(analytics.total_spend)
```

### Updating Heads
Heads are editable per period. Use `tracker.update_heads(...)` with the new list of `ExpenseHead`
instances; the tracker prevents removing a head that already has transactions.

## Google Sheets Export
1. Create a service account in Google Cloud and share the destination sheet with the service account email.
2. Download the JSON credentials file and set the path in `GOOGLE_APPLICATION_CREDENTIALS`.
3. Set `EXPENSE_TRACKER_SPREADSHEET_ID` to the sheet ID (the long string in the sheet URL).
4. Run `python main.py` again (or call `GoogleSheetsExporter` yourself) to push the latest period.

The exporter writes:
- Metadata rows (period label, date range, totals)
- Detailed transaction table
- Category analytics table with budgets/variance
- Peak day + largest expense callouts
- Cumulative running total for charting

## Project Layout
```
expense_tracker/
  analytics.py
  data_store.py
  exporters.py
  models.py
  tracker.py
docs/plan.md
main.py
requirements.txt
```

## Next Steps
- Extend analytics with rolling averages or forecasts.
- Hook up a simple CLI or web UI for data entry.
- Swap JSON storage for a database if you need multi-user access.
