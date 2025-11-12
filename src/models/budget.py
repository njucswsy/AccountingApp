from dataclasses import dataclass
from datetime import date
from typing import Any, Dict


@dataclass
class Budget:
    monthly_goal: float
    current_spending: float = 0.0
    month: str = date.today().strftime("%Y-%m")

    def set_budget(self, amount: float) -> None:
        self.monthly_goal = amount
        self.current_spending = 0.0  # Reset spending for the new budget period
        self.month = date.today().strftime("%Y-%m")

    def add_spending(self, amount: float) -> None:
        self.current_spending += amount

    def check_budget_status(self) -> bool:
        return self.current_spending > self.monthly_goal

    def send_reminder(self) -> str:
        if self.check_budget_status():
            return (
                f"Warning: spending {self.current_spending:.2f} exceeds "
                f"budget {self.monthly_goal:.2f} for {self.month}. "
                "Consider reducing expenses."
            )
        return (
            f"Current spending {self.current_spending:.2f} is within "
            f"budget {self.monthly_goal:.2f} for {self.month}. Keep up the good work!"
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
