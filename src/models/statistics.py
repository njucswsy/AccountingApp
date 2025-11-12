from collections import defaultdict
from datetime import date
from typing import Dict, List
from .record import Record

class Statistics:
    """Compute summary statistics over a list of records."""

    def __init__(self, records: List[Record]) -> None:
        self.records = records

    def calculate_totals(self) -> Dict[str, float]:
        income = sum(r.amount for r in self.records if r.r_type == "income")
        expense = sum(r.amount for r in self.records if r.r_type == "expense")
        return {
            "income": income,
            "expense": expense,
            "balance": income - expense,
        }

    def generate_category_report(self) -> Dict[str, float]:
        totals: Dict[str, float] = defaultdict(float)
        for r in self.records:
            sign = 1.0 if r.r_type == "income" else -1.0
            totals[r.category] += sign * r.amount
        return dict(totals)

    def get_trend_analysis(self) -> Dict[str, Dict[str, float]]:
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
