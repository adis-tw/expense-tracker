"""Typer-powered CLI for the expense tracker."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import typer

from .exporters import GoogleSheetsExporter
from .tracker import ExpenseTracker

app = typer.Typer(help="Monthly expense tracker with analytics and sheet export.")


def _tracker(data_file: Path) -> ExpenseTracker:
    return ExpenseTracker(data_file)


@app.command("init-period")
def init_period(
    name: str = typer.Argument(..., help="Friendly period name"),
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    heads: List[str] = typer.Option(
        ...,
        "--head",
        "-h",
        help="Repeat for each expense head you want to add.",
    ),
    data_file: Path = typer.Option(
        "./expense_data.json", "--data-file", help="JSON file to store tracker data"
    ),
) -> None:
    tracker = _tracker(data_file)
    tracker.create_period(name=name, start_date=start, end_date=end, heads=heads)
    typer.echo(f"Created period '{name}' with heads: {', '.join(heads)}")


@app.command("list-periods")
def list_periods(
    data_file: Path = typer.Option(
        "./expense_data.json", "--data-file", help="JSON file to store tracker data"
    ),
) -> None:
    tracker = _tracker(data_file)
    periods = tracker.list_periods()
    if not periods:
        typer.echo("No periods found.")
        raise typer.Exit(code=0)
    for period in periods:
        typer.echo(period)


@app.command("add-head")
def add_head(
    period: str = typer.Argument(..., help="Period name"),
    head: str = typer.Argument(..., help="New head to add"),
    data_file: Path = typer.Option("./expense_data.json", "--data-file"),
) -> None:
    tracker = _tracker(data_file)
    tracker.add_head(period, head)
    typer.echo(f"Added head '{head}' to period '{period}'.")


@app.command("record-expense")
def record_expense(
    period: str = typer.Argument(..., help="Period name"),
    head: str = typer.Argument(..., help="Expense head"),
    amount: float = typer.Argument(..., help="Expense amount"),
    date_: str = typer.Option(..., "--date", "-d", help="Expense date YYYY-MM-DD"),
    note: str = typer.Option("", "--note", "-n", help="Optional note"),
    data_file: Path = typer.Option("./expense_data.json", "--data-file"),
) -> None:
    tracker = _tracker(data_file)
    expense = tracker.record_expense(
        period_name=period,
        head=head,
        amount=amount,
        date_=date_,
        note=note,
    )
    typer.echo(
        f"Recorded {expense.amount} to '{expense.head}' on "
        f"{expense.date.strftime('%Y-%m-%d')}"
    )


@app.command("analytics")
def analytics_command(
    period: str = typer.Argument(..., help="Period name"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Optional start"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="Optional end"),
    heads: Optional[List[str]] = typer.Option(
        None, "--head", "-h", help="Optional head filters. Omit to use all heads."
    ),
    data_file: Path = typer.Option("./expense_data.json", "--data-file"),
) -> None:
    tracker = _tracker(data_file)
    head_filters = heads or None
    payload = tracker.analytics(
        period_name=period,
        start=start,
        end=end,
        heads=head_filters,
    )
    typer.echo(json.dumps(payload, indent=2))


@app.command("export")
def export_command(
    period: str = typer.Argument(..., help="Period name"),
    spreadsheet: str = typer.Option(..., "--spreadsheet", "-s", help="Sheet name"),
    credentials: Path = typer.Option(
        ..., "--credentials", "-c", help="Path to Google service account JSON"
    ),
    worksheet: Optional[str] = typer.Option(
        None, "--worksheet", "-w", help="Optional worksheet name"
    ),
    share: Optional[List[str]] = typer.Option(
        None,
        "--share",
        help="Repeat for emails that should get edit access when sheet is created.",
    ),
    data_file: Path = typer.Option("./expense_data.json", "--data-file"),
) -> None:
    tracker = _tracker(data_file)
    period_obj = tracker.get_period(period)
    exporter = GoogleSheetsExporter(str(credentials))
    url = exporter.export(
        period_obj,
        spreadsheet_name=spreadsheet,
        worksheet_name=worksheet,
        share_with=share or [],
    )
    typer.echo(f"Exported analytics + expenses to {url}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
