"""Budget entity definition.

The :class:`Budget` class encapsulates the concept of a
monthly spending goal. It tracks both the user's intended
spending limit (``monthly_goal``) and the amount they have
already spent in the current period (``current_spending``).
Methods are provided to set a new budget, to add to the
running total of spending as expense records are created,
to check whether the budget has been exceeded, and to
generate a textual reminder message when appropriate. The
class can also serialise to and from a dictionary for
persistence.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Budget:
    """Represents a simple monthly budget.

    Attributes
    ----------
    monthly_goal : float
        The total amount the user plans or aims to spend within
        the current calendar month.
    current_spending : float
        The running total of all expenses recorded in the current
        month. This value is updated whenever a new expense
        record is added. It should be reset at the start of a
        new period.
    """

    monthly_goal: float
    current_spending: float = 0.0

    def set_budget(self, amount: float) -> None:
        """Update the monthly spending goal.

        Parameters
        ----------
        amount : float
            The new budget target for the month. Negative values
            are allowed but will likely trigger immediate warnings.
        """
        self.monthly_goal = amount

    def add_spending(self, amount: float) -> None:
        """Increase the current spending total.

        Parameters
        ----------
        amount : float
            The amount to add to the existing ``current_spending``.
            Typically this should correspond to the amount of a new
            expense record.
        """
        self.current_spending += amount

    def check_budget_status(self) -> bool:
        """Determine whether spending has exceeded the goal.

        Returns
        -------
        bool
            True if the current spending is greater than the monthly
            goal, False otherwise.
        """
        return self.current_spending > self.monthly_goal

    def send_reminder(self) -> str:
        """Generate a human-readable reminder message.

        If the spending has exceeded the goal, the message warns
        the user; otherwise it reassures them that they remain
        within budget.

        Returns
        -------
        str
            A message describing the current budget status and
            optionally prompting the user to adjust their spending.
        """
        if self.check_budget_status():
            return (
                f"Warning: spending {self.current_spending:.2f} exceeds "
                f"budget {self.monthly_goal:.2f}. Consider reducing expenses."
            )
        return (
            f"Current spending {self.current_spending:.2f} is within "
            f"budget {self.monthly_goal:.2f}. Keep up the good work!"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise this budget to a dictionary."""
        return {
            "monthly_goal": self.monthly_goal,
            "current_spending": self.current_spending,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Budget":
        """Construct a :class:`Budget` from a dictionary."""
        return cls(
            monthly_goal=float(data.get("monthly_goal", 0.0)),
            current_spending=float(data.get("current_spending", 0.0)),
        )
