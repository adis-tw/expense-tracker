"""Analytics helpers for the expense tracker."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Dict, Iterable, List, Tuple

from .models import Expense, ExpensePeriod, parse_date


def _date_range_days(start: date, end: date) -> int:
    return (end - start).days + 1


def summarise_period(
    period: ExpensePeriod,
    *,
    start: str | date | None = None,
    end: str | date | None = None,
    heads: Iterable[str] | None = None,
) -> Dict[str, object]:
    """Return analytics for a slice of the period."""

    start_date = parse_date(start) if start else period.start_date
    end_date = parse_date(end) if end else period.end_date
    head_filter = set(heads or period.heads)

    filtered: List[Expense] = [
        exp
        for exp in period.expenses
        if start_date <= exp.date <= end_date and exp.head in head_filter
    ]

    totals_by_head: Dict[str, float] = defaultdict(float)
    totals_by_day: Dict[date, float] = defaultdict(float)
    total_spent = 0.0
    for exp in filtered:
        totals_by_head[exp.head] += exp.amount
        totals_by_day[exp.date] += exp.amount
        total_spent += exp.amount

    days = max(_date_range_days(start_date, end_date), 1)
    daily_average = total_spent / days if total_spent else 0.0

    head_percentages = {
        head: (amount / total_spent) * 100 if total_spent else 0.0
        for head, amount in totals_by_head.items()
    }

    peak_head: Tuple[str, float] | None = None
    if totals_by_head:
        peak_head = max(totals_by_head.items(), key=lambda item: item[1])

    cumulative_total = 0.0
    spend_by_day = []
    for day in sorted(totals_by_day):
        cumulative_total += totals_by_day[day]
        spend_by_day.append(
            {
                "date": day.strftime("%Y-%m-%d"),
                "amount": round(totals_by_day[day], 2),
                "cumulative": round(cumulative_total, 2),
            }
        )

    return {
        "period": {
            "name": period.name,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "days": days,
            "heads": sorted(head_filter),
        },
        "total_spent": round(total_spent, 2),
        "daily_average": round(daily_average, 2),
        "head_totals": {head: round(amount, 2) for head, amount in totals_by_head.items()},
        "head_percentages": {
            head: round(percent, 2) for head, percent in head_percentages.items()
        },
        "peak_head": peak_head,
        "spend_by_day": spend_by_day,
        "expense_count": len(filtered),
    }
