"""Export utilities for sending tracker data to Google Sheets."""

from __future__ import annotations

from typing import Dict, List, Sequence

from .analytics import summarise_period
from .models import ExpensePeriod


class GoogleSheetsExporter:
    """Push period data + analytics into a Google Sheet."""

    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file

    def _get_client(self):
        try:
            import gspread
        except ImportError as exc:
            raise RuntimeError(
                "gspread is required for Google Sheets export. "
                "Install it with `pip install gspread`."
            ) from exc
        return gspread.service_account(filename=self.credentials_file)

    def export(
        self,
        period: ExpensePeriod,
        *,
        spreadsheet_name: str,
        worksheet_name: str | None = None,
        analytics_override: Dict[str, object] | None = None,
        share_with: Sequence[str] | None = None,
    ) -> str:
        """Write period data into a sheet and return the worksheet URL."""

        client = self._get_client()
        try:
            sheet = client.open(spreadsheet_name)
        except Exception:  # SpreadsheetNotFound
            sheet = client.create(spreadsheet_name)
            for email in share_with or []:
                sheet.share(email, perm_type="user", role="writer")

        if worksheet_name:
            try:
                worksheet = sheet.worksheet(worksheet_name)
                worksheet.clear()
            except Exception:  # WorksheetNotFound
                worksheet = sheet.add_worksheet(title=worksheet_name, rows=200, cols=20)
        else:
            worksheet = sheet.sheet1
            worksheet.clear()

        analytics_payload = analytics_override or summarise_period(period)

        rows: List[List[object]] = []
        rows.append(["Period", period.name])
        rows.append(["Start date", analytics_payload["period"]["start_date"]])
        rows.append(["End date", analytics_payload["period"]["end_date"]])
        rows.append(["Days", analytics_payload["period"]["days"]])
        rows.append(["Total spent", analytics_payload["total_spent"]])
        rows.append(["Daily average", analytics_payload["daily_average"]])
        rows.append([])

        rows.append(["Head", "Total", "Percent"])
        head_totals: Dict[str, float] = analytics_payload.get("head_totals", {})
        head_percentages: Dict[str, float] = analytics_payload.get("head_percentages", {})
        for head in sorted(head_totals):
            rows.append(
                [head, head_totals[head], head_percentages.get(head, 0.0)],
            )

        rows.append([])
        rows.append(["Date", "Head", "Amount", "Note"])
        for expense in sorted(period.expenses, key=lambda exp: exp.date):
            rows.append(
                [
                    expense.date.strftime("%Y-%m-%d"),
                    expense.head,
                    expense.amount,
                    expense.note,
                ]
            )

        worksheet.update("A1", rows)
        return worksheet.url
