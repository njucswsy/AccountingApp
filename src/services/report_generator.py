from typing import Dict, List
from src.models.record import Record
from src.models.statistics import Statistics

class ReportGenerator:
    def generate_monthly_report(self, records: List[Record]) -> Dict[str, Dict[str, float]]:
        stats = Statistics(records)
        return stats.get_trend_analysis()

    def generate_category_chart(self, records: List[Record]) -> Dict[str, float]:
        stats = Statistics(records)
        return stats.generate_category_report()
