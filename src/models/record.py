from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Dict


@dataclass
class Record:
    record_id: int
    amount: float
    r_type: str
    category: str
    note: str
    record_date: date
    store: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Record":
        return cls(
            record_id=int(data["record_id"]),
            amount=float(data["amount"]),
            r_type=data["r_type"],
            category=data["category"],
            note=data.get("note", ""),
            record_date=cls.parse_date(data["record_date"]),
            store=data.get("store", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "amount": self.amount,
            "r_type": self.r_type,
            "category": self.category,
            "note": self.note,
            "record_date": self.record_date.strftime("%Y-%m-%d"),
            "store": self.store,
        }

    @staticmethod
    def parse_date(date_str: str) -> date:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
