"""Record entity definition.

The :class:`Record` class models a single financial transaction
within the accounting system. Each record contains the basic
information necessary to describe an income or expense event,
such as the unique identifier, the amount of money involved,
its type (income or expense), the associated category, an
optional note for additional context, the date on which the
record occurred, and the store or merchant at which the
transaction took place. The class provides helper methods
for serialising to and from dictionaries, which is useful
when persisting records to storage (e.g. JSON files).

Example usage::

    from datetime import date
    record = Record(
        record_id=1,
        amount=100.0,
        r_type="income",
        category="Salary",
        note="Monthly salary",
        record_date=date(2025, 1, 15),
        store="Company"
    )
    as_dict = record.to_dict()
    restored = Record.from_dict(as_dict)

"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Dict


@dataclass
class Record:
    """Represents a single income or expense record.

    Attributes
    ----------
    record_id : int
        A unique identifier for the record. IDs are assigned
        incrementally when new records are created.
    amount : float
        The magnitude of the transaction. Positive values are used
        for both income and expense and the sign is determined by
        the ``r_type`` attribute.
    r_type : str
        Indicates whether the record is an ``income`` or an ``expense``.
    category : str
        The user-defined category that groups this record with other
        related transactions (e.g. ``Food``, ``Salary``).
    note : str
        An optional free-form text field that allows the user to
        attach additional information about the transaction.
    record_date : date
        The calendar date on which the transaction occurred.
    store : str
        An optional field denoting the merchant or store at which the
        transaction took place. For income records this may be
        empty or used to record the payer.

    """

    record_id: int
    amount: float
    r_type: str
    category: str
    note: str
    record_date: date
    store: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Record":
        """Create a :class:`Record` instance from a dictionary.

        Parameters
        ----------
        data : dict
            A mapping with keys corresponding to the fields of
            :class:`Record`. Unknown keys are ignored.

        Returns
        -------
        Record
            A new :class:`Record` populated with values from the
            provided dictionary. The ``record_date`` field is parsed
            from a ``YYYY-MM-DD`` string.
        """
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
        """Serialise this record into a dictionary.

        Returns
        -------
        dict
            A JSON-serialisable representation of the record. The
            ``record_date`` attribute is formatted as ``YYYY-MM-DD``.
        """
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
        """Parse a ``YYYY-MM-DD`` formatted string into a :class:`date`.

        Parameters
        ----------
        date_str : str
            A string in ISO-8601 date format (``YYYY-MM-DD``).

        Returns
        -------
        date
            A :class:`datetime.date` object representing the parsed
            date. This helper ensures that date parsing is consistent
            across the codebase.
        """
        return datetime.strptime(date_str, "%Y-%m-%d").date()
