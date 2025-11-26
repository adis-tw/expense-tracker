# Monthly Expense Tracker

Python toolkit + CLI for tracking expenses between custom date ranges, analysing spend per head, and exporting the results to Google Sheets.

## Key Features
- Create named periods with custom start/end dates and editable expense heads.
- Record expenses per head and slice data for arbitrary date ranges.
- Built-in analytics: totals per head, contribution %, running daily totals, spend velocity.
- JSON storage so you can version-control or sync the raw data file.
- One-command export to Google Sheets (period summary + full transaction log).

## Getting Started
1. **Install dependencies**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run the CLI**
   ```bash
   python -m expense_tracker.cli --help
   ```

## Typical Workflow
```bash
# 1. Create a period with custom heads
python -m expense_tracker.cli init-period "Nov-2025" --start 2025-11-01 --end 2025-11-30 \
  --head Rent --head Groceries --head Utilities --head Leisure

# 2. Add more heads later if needed
python -m expense_tracker.cli add-head "Nov-2025" Savings

# 3. Record expenses whenever they happen
python -m expense_tracker.cli record-expense "Nov-2025" Groceries 42.75 --date 2025-11-03 --note "Veg market"

# 4. Generate analytics (optionally with head/date filters)
python -m expense_tracker.cli analytics "Nov-2025" --start 2025-11-01 --end 2025-11-15

# 5. Export to Google Sheets
python -m expense_tracker.cli export "Nov-2025" \
  --spreadsheet "Household Finances" \
  --worksheet "Nov 2025" \
  --credentials path/to/service_account.json
```

- All commands support `--data-file your_file.json` if you want to store data elsewhere (default `./expense_data.json`).
- Analytics output is JSON so it can be piped into other tooling or dashboards.

## Google Sheets Export
1. Create a Google Cloud service account and enable the *Google Sheets API*.
2. Download the JSON credentials file and keep it safe.
3. Share the target spreadsheet with the service account email (or rely on the exporter to create + share automatically by passing `--share you@example.com`).
4. Run the `export` command shown above. The sheet receives a summary table plus the detailed expense ledger.

## Using the ExpenseTracker class directly
```python
from expense_tracker import ExpenseTracker

tracker = ExpenseTracker("./expense_data.json")
tracker.create_period(
    name="Q1",
    start_date="2026-01-01",
    end_date="2026-03-31",
    heads=["Rent", "Travel", "Food"],
)
tracker.record_expense(period_name="Q1", head="Food", amount=18.9, date_="2026-02-10")
print(tracker.analytics(period_name="Q1"))
```

This package is intentionally filesystem-friendly: commit `expense_data.json` to git for a full audit trail or sync it across devices for collaborative tracking.
