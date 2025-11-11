"""Reporting utilities for the accounting application.

This module defines a simple :class:`ReportGenerator` class
capable of producing aggregated summaries suitable for display
in reports or charts. It leverages the :class:`Statistics`
model to perform the heavy lifting and returns plain Python
data structures (dictionaries) that can easily be consumed
by the user interface layer or by external reporting tools.
"""

from typing import Dict, List

from src.models.record import Record
from src.models.statistics import Statistics


class ReportGenerator:
    """Generate summary reports from a collection of records."""

    def generate_monthly_report(self, records: List[Record]) -> Dict[str, Dict[str, float]]:
        """Produce a mapping of month to income, expense and balance.

        Parameters
        ----------
        records : list of Record
            The records to summarise.

        Returns
        -------
        dict
            A nested dictionary where each key is a ``YYYY-MM`` string
            and the corresponding value is itself a mapping with
            keys ``income``, ``expense`` and ``balance``. The
            ``balance`` value is always equal to ``income`` minus
            ``expense``.
        """
        stats = Statistics(records)
        return stats.get_trend_analysis()

    def generate_category_chart(self, records: List[Record]) -> Dict[str, float]:
        """Aggregate net amounts by category.

        This method returns the same data structure as
        :meth:`Statistics.generate_category_report` to avoid
        duplicating logic. It is provided here for symmetry with
        :meth:`generate_monthly_report` and to serve as a
        convenient one-stop shop for report data.
        """
        stats = Statistics(records)
        return stats.generate_category_report()
