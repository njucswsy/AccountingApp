"""Statistics model for aggregated analysis.

The :class:`Statistics` class provides methods to compute
various summary statistics from a collection of
:class:`Record` instances. This includes total income and
expense values, per-category summaries that account for the
sign of each transaction, and monthly trend analysis to show
how income, expenses and balance evolve over time. The class
does not hold any persistent state of its own beyond a list of
records provided at construction time, which makes it cheap to
instantiate and to use repeatedly on different subsets of
records without side effects.
"""

from collections import defaultdict
from datetime import date
from typing import Dict, List

from .record import Record


class Statistics:
    """Compute summary statistics over a list of records."""

    def __init__(self, records: List[Record]) -> None:
        # It's safe to keep a reference to the list here because
        # the caller controls when records are added or removed. The
        # statistics will always reflect the current state of the
        # list passed in as long as the caller doesn't replace the
        # list entirely.
        self.records = records

    def calculate_totals(self) -> Dict[str, float]:
        """Return total income, total expense and balance.

        The balance is computed as income minus expense. Both
        income and expense values are returned as absolute values
        (i.e. expenses are positive numbers) to avoid confusion.

        Returns
        -------
        dict
            A mapping with keys ``income``, ``expense`` and
            ``balance``.
        """
        income = sum(r.amount for r in self.records if r.r_type == "income")
        expense = sum(r.amount for r in self.records if r.r_type == "expense")
        return {
            "income": income,
            "expense": expense,
            "balance": income - expense,
        }

    def generate_category_report(self) -> Dict[str, float]:
        """Aggregate net amounts per category.

        For income records the amount is added; for expenses the
        amount is subtracted. As a result, categories with only
        expenses will show negative totals. This can be useful for
        quickly identifying where money is being spent.

        Returns
        -------
        dict
            A mapping of category name to net amount.
        """
        totals: Dict[str, float] = defaultdict(float)
        for r in self.records:
            sign = 1.0 if r.r_type == "income" else -1.0
            totals[r.category] += sign * r.amount
        return dict(totals)

    def get_trend_analysis(self) -> Dict[str, Dict[str, float]]:
        """Compute monthly income, expense and balance.

        The keys of the returned dictionary are in ``YYYY-MM``
        format. Each value is itself a dictionary with keys
        ``income``, ``expense`` and ``balance``.

        Returns
        -------
        dict
            A nested mapping of month to aggregated totals.
        """
        result: Dict[str, Dict[str, float]] = {}
        for r in self.records:
            month_key = r.record_date.strftime("%Y-%m")
            if month_key not in result:
                result[month_key] = {"income": 0.0, "expense": 0.0, "balance": 0.0}
            if r.r_type == "income":
                result[month_key]["income"] += r.amount
            else:
                result[month_key]["expense"] += r.amount
            result[month_key]["balance"] = (
                result[month_key]["income"] - result[month_key]["expense"]
            )
        return result
