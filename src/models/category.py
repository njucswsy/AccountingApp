"""Category entity definition.

The :class:`Category` class represents a classification under which
financial records can be grouped. Categories help organise
transactions and make it easier to analyse spending and
income patterns. Each category has a unique identifier, a
human-readable name, a visual icon (which could be a text
symbol or an emoji), and a type indicating whether it is
meant for income or expense records.

Users are able to create and edit their own categories at
runtime. Categories persist alongside the records so that
existing records continue to reference the correct category
even if the user edits the name or icon later.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Category:
    """Represents a category for grouping records.

    Attributes
    ----------
    category_id : int
        A unique identifier assigned to each category. IDs are
        allocated incrementally when new categories are created.
    name : str
        The display name of the category (e.g. ``Food``, ``Salary``).
    icon : str
        An optional visual representation such as an emoji or
        single-character string. Icons are purely cosmetic.
    c_type : str
        Specifies whether this category is used with ``income`` or
        ``expense`` records. This helps validate record data and
        ensures that income records are not mistakenly placed in
        expense categories and vice versa.
    """

    category_id: int
    name: str
    icon: str
    c_type: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        """Create a new :class:`Category` from a dictionary.

        Parameters
        ----------
        data : dict
            A mapping of keys to values. Missing optional keys are
            given sensible defaults.

        Returns
        -------
        Category
            A new category instance populated with the provided
            data. Unknown keys are ignored.
        """
        return cls(
            category_id=int(data["category_id"]),
            name=data["name"],
            icon=data.get("icon", ""),
            c_type=data["c_type"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise this category into a dictionary.

        The resulting mapping can be persisted to a JSON file or
        transmitted over a network. Only known attributes are
        included; additional computed properties would need to be
        added manually if desired.

        Returns
        -------
        dict
            A dictionary representation of the category.
        """
        return {
            "category_id": self.category_id,
            "name": self.name,
            "icon": self.icon,
            "c_type": self.c_type,
        }
