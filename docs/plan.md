## Monthly Expense Tracker – Implementation Plan

### Goals
- Track expenses within user-defined periods (any start/end date, not just calendar months).
- Allow each period to define its own set of expense heads/categories and optional budgets.
- Record individual transactions with metadata (date, head, amount, notes).
- Generate analytics per period (totals, category breakdown, burn rate, outliers, trends).
- Export any period’s data + analytics to Google Sheets on demand.

### Domain Model
- `ExpenseHead`: category metadata, optional budget.
- `ExpenseRecord`: single transaction (date, head, amount, notes).
- `ExpensePeriod`: label, date range, ordered heads, optional metadata, and the list of records.
- `ExpenseTracker`: orchestrates multiple periods, enforces date/category constraints, persists data.

### Persistence Strategy
- Lightweight JSON storage (one file) via `JSONDataStore`.
  - Reads all periods (including records, heads, analytics cache metadata if needed).
  - Keeps implementation simple and portable; no external DB requirement.
  - Structure keeps periods keyed by label for easy lookup.

### Analytics (per period)
- Category summary: sum, share of total, average transaction size, count, optional budget delta.
- Burn rate: average spend per day and extrapolated monthly total.
- Extremes: peak spend day and largest transaction.
- Cumulative trend: running total ordered by date for plotting/export.
- Budget health: highlight categories exceeding budget.

Analytics will live in `analytics.py`, returning plain `dict`/`dataclass` objects so they can be reused by CLI, tests, or exporters.

### Google Sheets Export
- `GoogleSheetsExporter` uses `gspread` with service-account credentials.
- Creates/updates a worksheet per period:
  - Header rows for metadata (date range, total spend, burn rate).
  - Table of transactions.
  - Table of analytics summary.
- Exporter accepts spreadsheet ID (from URL) and optional worksheet title.
- Credentials path pulled from env (`GOOGLE_APPLICATION_CREDENTIALS`) or passed explicitly.

### CLI / Usage Script
- `main.py` demonstrates how to:
  1. Instantiate tracker with JSON datastore.
  2. Create a period with custom heads.
  3. Record sample expenses.
  4. Print analytics.
  5. Trigger Google Sheets export (guarded to avoid accidental network calls during demos/tests).

### Project Layout
```
expense_tracker/
  __init__.py
  models.py
  data_store.py
  tracker.py
  analytics.py
  exporters.py
main.py
requirements.txt
docs/plan.md
README.md (expanded with usage instructions)
```

### Testing & Validation
- Focused unit tests for analytics and tracker logic (time permitting).
- Manual run: execute `python main.py` to ensure sample flow works.
- Optional: add linter/formatter later if scope expands.

### Open Items
- Users must supply Google credentials + spreadsheet ID.
- For larger deployments, swap JSON store with DB (implemented via interface later).
- Future enhancements: budgets per period, alerts, CLI prompts, dashboard UI.
