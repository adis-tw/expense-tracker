"""Analytics routines for expense periods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import ExpenseHead, ExpensePeriod, ExpenseRecord


@dataclass
class HeadAnalytics:
    head: str
    total_amount: float
    transaction_count: int
    avg_transaction: float
    percent_of_total: float
    budget: Optional[float] = None
    budget_delta: Optional[float] = None


@dataclass
class PeriodAnalytics:
    period_label: str
    total_spend: float
    total_transactions: int
    days_in_period: int
    active_days: int
    average_daily_spend: float
    head_summaries: List[HeadAnalytics]
    peak_spend_day: Optional[str]
    peak_spend_total: float
    largest_expense: Optional[ExpenseRecord]
    cumulative_series: List[Dict[str, float]]


def _head_lookup(period: ExpensePeriod) -> Dict[str, ExpenseHead]:
    return {head.name.lower(): head for head in period.heads}


def calculate_period_analytics(period: ExpensePeriod) -> PeriodAnalytics:
    if not period.records:
        return PeriodAnalytics(
            period_label=period.label,
            total_spend=0.0,
            total_transactions=0,
            days_in_period=(period.end_date - period.start_date).days + 1,
            active_days=0,
            average_daily_spend=0.0,
            head_summaries=[
                HeadAnalytics(
                    head=head.name,
                    total_amount=0.0,
                    transaction_count=0,
                    avg_transaction=0.0,
                    percent_of_total=0.0,
                    budget=head.budget,
                    budget_delta=head.budget,
                )
                for head in period.heads
            ],
            peak_spend_day=None,
            peak_spend_total=0.0,
            largest_expense=None,
            cumulative_series=[],
        )

    sorted_records = sorted(period.records, key=lambda rec: rec.date)
    total_spend = sum(record.amount for record in sorted_records)
    total_transactions = len(sorted_records)
    days_in_period = (period.end_date - period.start_date).days + 1
    average_daily_spend = total_spend / days_in_period if days_in_period else 0.0

    totals_by_head: Dict[str, float] = {}
    counts_by_head: Dict[str, int] = {}
    for record in sorted_records:
        key = record.head.lower()
        totals_by_head[key] = totals_by_head.get(key, 0.0) + record.amount
        counts_by_head[key] = counts_by_head.get(key, 0) + 1

    summaries: List[HeadAnalytics] = []
    head_lookup = _head_lookup(period)
    for head_key, amount in totals_by_head.items():
        head = head_lookup.get(head_key)
        percent = (amount / total_spend) * 100 if total_spend else 0.0
        count = counts_by_head[head_key]
        avg_txn = amount / count if count else 0.0
        budget = head.budget if head else None
        budget_delta = None
        if budget is not None:
            budget_delta = budget - amount
        summaries.append(
            HeadAnalytics(
                head=head.name if head else head_key,
                total_amount=amount,
                transaction_count=count,
                avg_transaction=avg_txn,
                percent_of_total=percent,
                budget=budget,
                budget_delta=budget_delta,
            )
        )

    # Include heads that had no spend for better reporting.
    for head in period.heads:
        if head.name.lower() not in totals_by_head:
            summaries.append(
                HeadAnalytics(
                    head=head.name,
                    total_amount=0.0,
                    transaction_count=0,
                    avg_transaction=0.0,
                    percent_of_total=0.0,
                    budget=head.budget,
                    budget_delta=head.budget,
                )
            )

    summaries.sort(key=lambda s: s.total_amount, reverse=True)

    spend_by_day: Dict[str, float] = {}
    for record in sorted_records:
        key = record.date.isoformat()
        spend_by_day[key] = spend_by_day.get(key, 0.0) + record.amount

    peak_day = max(spend_by_day.items(), key=lambda item: item[1]) if spend_by_day else None
    peak_day_label = peak_day[0] if peak_day else None
    peak_day_total = peak_day[1] if peak_day else 0.0

    largest_expense = max(sorted_records, key=lambda record: record.amount)

    cumulative_total = 0.0
    cumulative_series: List[Dict[str, float]] = []
    for record in sorted_records:
        cumulative_total += record.amount
        cumulative_series.append({"date": record.date.isoformat(), "running_total": cumulative_total})

    analytics = PeriodAnalytics(
        period_label=period.label,
        total_spend=total_spend,
        total_transactions=total_transactions,
        days_in_period=days_in_period,
        active_days=len(spend_by_day),
        average_daily_spend=average_daily_spend,
        head_summaries=summaries,
        peak_spend_day=peak_day_label,
        peak_spend_total=peak_day_total,
        largest_expense=largest_expense,
        cumulative_series=cumulative_series,
    )

    return analytics
