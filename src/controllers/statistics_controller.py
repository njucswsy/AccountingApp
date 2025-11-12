from typing import Dict, List

from src.models.record import Record
from src.models.statistics import Statistics


class StatisticsController:
    """Provide access to summary statistics over records."""

    def __init__(self, records: List[Record]) -> None:
        # Keep a reference to the list to reflect updates made by the
        # record controller.
        self.records = records

    def get_summary(self) -> Dict[str, float]:
        """Return total income, expense and balance."""
        stats = Statistics(self.records)
        return stats.calculate_totals()

    def get_category_stats(self) -> Dict[str, float]:
        """Return net amounts per category."""
        stats = Statistics(self.records)
        return stats.generate_category_report()

    def get_time_based_stats(self) -> Dict[str, Dict[str, float]]:
        """Return monthly income, expense and balance."""
        stats = Statistics(self.records)
        return stats.get_trend_analysis()
