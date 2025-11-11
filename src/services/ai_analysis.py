"""AI-assisted analysis for spending patterns.

This module implements a very lightweight and heuristic based
analysis engine that attempts to extract useful insights from
the user's expense data. While not truly 'intelligent', it
demonstrates how more sophisticated machine learning models or
third-party services could be integrated into the system to
provide personalised suggestions and pattern recognition.
"""

from typing import Dict, List

from src.models.record import Record


class AIAnalysis:
    """Provide basic analytical feedback on expense patterns."""

    def analyze_spending_patterns(self, records: List[Record]) -> Dict[str, float]:
        """Compute total expenses per category.

        Only expense records are considered; income records are
        ignored for the purpose of identifying spending habits.

        Returns
        -------
        dict
            A mapping of category name to total expense amount.
        """
        totals: Dict[str, float] = {}
        for r in records:
            if r.r_type != "expense":
                continue
            totals[r.category] = totals.get(r.category, 0.0) + r.amount
        return totals

    def generate_suggestions(self, records: List[Record]) -> str:
        """Produce a textual suggestion based on expense patterns.

        The current implementation identifies the category with the
        highest total expenses and suggests that the user consider
        reducing spending in that category. If there are no
        expenses, a generic message is returned.

        Returns
        -------
        str
            A simple suggestion for the user on how to adjust
            spending habits.
        """
        totals = self.analyze_spending_patterns(records)
        if not totals:
            return "No expense data to analyse."
        # Identify the category with the maximum total expense.
        top_category = max(totals, key=totals.get)
        return (
            f"Consider reducing expenses in the '{top_category}' category. "
            f"You spent {totals[top_category]:.2f} there this period."
        )
