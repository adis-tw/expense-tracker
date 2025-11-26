"""Export helpers for sending tracker data to external systems."""

from __future__ import annotations

import os
from typing import List, Sequence

from .analytics import HeadAnalytics, PeriodAnalytics
from .models import ExpensePeriod


class GoogleSheetsExporter:
    """Exports period details to a Google Sheet using a service account."""

    def __init__(self, credentials_path: str | None = None) -> None:
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    def _get_client(self):
        try:
            import gspread  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "gspread is required for Google Sheets export. Install it via 'pip install gspread'."
            ) from exc

        if self.credentials_path:
            return gspread.service_account(filename=self.credentials_path)
        return gspread.service_account()

    def export_period(
        self,
        period: ExpensePeriod,
        analytics: PeriodAnalytics,
        spreadsheet_id: str,
        worksheet_title: str | None = None,
    ) -> str:
        """Create/update a worksheet with transaction + analytics data."""
        client = self._get_client()
        sheet = client.open_by_key(spreadsheet_id)
        title = worksheet_title or period.label

        try:
            worksheet = sheet.worksheet(title)
            worksheet.clear()
        except Exception as exc:  # WorksheetNotFound (lazy import)
            if exc.__class__.__name__ == "WorksheetNotFound":
                worksheet = sheet.add_worksheet(title=title, rows="200", cols="8")
            else:
                raise

        rows = self._build_rows(period, analytics)
        worksheet.update("A1", rows)
        return worksheet.url

    def _build_rows(self, period: ExpensePeriod, analytics: PeriodAnalytics) -> List[List[str | float]]:
        rows: List[List[str | float]] = [
            ["Period", period.label],
            ["Date Range", f"{period.start_date.isoformat()} → {period.end_date.isoformat()}"],
            ["Total Spend", round(analytics.total_spend, 2)],
            ["Average Daily Spend", round(analytics.average_daily_spend, 2)],
            ["Active Days", analytics.active_days],
            [],
            ["Transactions"],
            ["Date", "Head", "Amount", "Notes"],
        ]

        for record in sorted(period.records, key=lambda r: r.date):
            rows.append([record.date.isoformat(), record.head, round(record.amount, 2), record.notes])

        rows.extend(
            [
                [],
                ["Head Analytics"],
                ["Head", "Total", "% of Total", "# Txns", "Avg Txn", "Budget", "Budget Delta"],
            ]
        )
        rows.extend(self._head_summary_rows(analytics.head_summaries))

        rows.extend(
            [
                [],
                ["Peak Spend Day", analytics.peak_spend_day or "N/A", round(analytics.peak_spend_total, 2)],
            ]
        )

        if analytics.largest_expense:
            rows.append(
                [
                    "Largest Expense",
                    analytics.largest_expense.date.isoformat(),
                    analytics.largest_expense.head,
                    round(analytics.largest_expense.amount, 2),
                    analytics.largest_expense.notes,
                ]
            )

        rows.extend(
            [
                [],
                ["Cumulative Trend"],
                ["Date", "Running Total"],
            ]
        )
        rows.extend([[point["date"], round(point["running_total"], 2)] for point in analytics.cumulative_series])
        return rows

    @staticmethod
    def _head_summary_rows(summaries: Sequence[HeadAnalytics]) -> List[List[str | float]]:
        rows: List[List[str | float]] = []
        for summary in summaries:
            rows.append(
                [
                    summary.head,
                    round(summary.total_amount, 2),
                    round(summary.percent_of_total, 2),
                    summary.transaction_count,
                    round(summary.avg_transaction, 2),
                    summary.budget if summary.budget is not None else "",
                    round(summary.budget_delta, 2)
                    if summary.budget_delta is not None
                    else "",
                ]
            )
        return rows
