from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Category:
    category_id: int
    name: str
    icon: str
    c_type: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        return cls(
            category_id=int(data["category_id"]),
            name=data["name"],
            icon=data.get("icon", ""),
            c_type=data["c_type"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category_id": self.category_id,
            "name": self.name,
            "icon": self.icon,
            "c_type": self.c_type,
        }
