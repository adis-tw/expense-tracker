"""Example usage for the monthly expense tracker."""

from __future__ import annotations

import os
from datetime import date

from expense_tracker.analytics import calculate_period_analytics
from expense_tracker.data_store import JSONDataStore
from expense_tracker.exporters import GoogleSheetsExporter
from expense_tracker.models import ExpenseHead
from expense_tracker.tracker import ExpenseTracker


def bootstrap_tracker(storage_path: str = "data/expenses.json") -> ExpenseTracker:
    store = JSONDataStore(storage_path)
    tracker = ExpenseTracker(store)
    return tracker


def seed_sample_data(tracker: ExpenseTracker) -> None:
    label = "Sample-Nov-2025"
    if label not in tracker.list_periods():
        tracker.create_period(
            label=label,
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30),
            heads=[
                ExpenseHead("Housing", budget=1200),
                ExpenseHead("Food", budget=600),
                ExpenseHead("Transport", budget=200),
                ExpenseHead("Entertainment", budget=250),
                ExpenseHead("Misc"),
            ],
        )

    period = tracker.get_period(label)
    if period.records:
        return  # Avoid duplicating demo data.

    tracker.record_expense(label, expense_date=date(2025, 11, 2), head="Housing", amount=900, notes="Rent")
    tracker.record_expense(label, expense_date=date(2025, 11, 3), head="Food", amount=45.5, notes="Groceries")
    tracker.record_expense(
        label, expense_date=date(2025, 11, 5), head="Transport", amount=30.0, notes="Metro top-up"
    )
    tracker.record_expense(label, expense_date=date(2025, 11, 6), head="Food", amount=18.5, notes="Lunch")
    tracker.record_expense(
        label, expense_date=date(2025, 11, 8), head="Entertainment", amount=60.0, notes="Concert tickets"
    )
    tracker.record_expense(label, expense_date=date(2025, 11, 10), head="Misc", amount=25.0, notes="Gifts")


def maybe_export_to_google(period_label: str, tracker: ExpenseTracker) -> None:
    spreadsheet_id = os.getenv("EXPENSE_TRACKER_SPREADSHEET_ID")
    if not spreadsheet_id:
        return

    period = tracker.get_period(period_label)
    analytics = calculate_period_analytics(period)
    exporter = GoogleSheetsExporter()
    url = exporter.export_period(period, analytics, spreadsheet_id=spreadsheet_id)
    print(f"Exported analytics to {url}")


def main() -> None:
    tracker = bootstrap_tracker()
    seed_sample_data(tracker)

    period_label = "Sample-Nov-2025"
    period = tracker.get_period(period_label)
    analytics = calculate_period_analytics(period)

    print(f"Period: {period.label}")
    print(f"Date range: {period.start_date} → {period.end_date}")
    print(f"Total spend: {analytics.total_spend:.2f}")
    print(f"Average daily spend: {analytics.average_daily_spend:.2f}")
    print("\nCategory breakdown:")
    for summary in analytics.head_summaries:
        budget_note = ""
        if summary.budget is not None:
            status = "under" if summary.budget_delta and summary.budget_delta >= 0 else "over"
            budget_note = f" ({status} budget by {abs(summary.budget_delta or 0):.2f})"
        print(
            f" - {summary.head}: {summary.total_amount:.2f} "
            f"({summary.percent_of_total:.1f}% of total, {summary.transaction_count} txns){budget_note}"
        )

    print("\nPeak spend day:", analytics.peak_spend_day or "N/A")
    if analytics.largest_expense:
        record = analytics.largest_expense
        print(f"Largest expense: {record.amount:.2f} on {record.date} for {record.head} ({record.notes})")

    maybe_export_to_google(period_label, tracker)


if __name__ == "__main__":
    main()
