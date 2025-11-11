"""Controller for managing record CRUD operations.

The :class:`RecordController` exposes methods to create, read,
update and delete records, and also to manage categories. It
acts as a facade over the :class:`StorageService` and domain
models, providing a simpler API for the user interface layer
to work with. All changes to records or categories are
immediately persisted via the storage service.
"""

from datetime import date
from typing import List, Optional

from src.models.record import Record
from src.models.category import Category
from src.models.budget import Budget
from src.services.storage_service import StorageService


class RecordController:
    """Handle record and category management tasks."""

    def __init__(self, storage: StorageService, budget: Optional[Budget] = None) -> None:
        self.storage = storage
        self.records: List[Record] = storage.load_records()
        self.categories: List[Category] = storage.load_categories()
        # If a budget is provided, use it; otherwise try loading from storage
        self.budget = budget or storage.load_budget() or Budget(monthly_goal=0.0)

    # -- Record operations -------------------------------------------------
    def _get_next_record_id(self) -> int:
        """Compute the next available record ID."""
        if not self.records:
            return 1
        return max(r.record_id for r in self.records) + 1

    def create_record(
        self,
        amount: float,
        r_type: str,
        category: str,
        record_date: date,
        note: str = "",
        store: str = "",
    ) -> Record:
        """Create and persist a new record.

        Parameters
        ----------
        amount : float
            The transaction amount. Use positive values for both
            income and expense; the ``r_type`` determines the sign
            when computing statistics.
        r_type : str
            Either ``income`` or ``expense``. This method does not
            validate the string beyond checking these two values.
        category : str
            The name of the category to which this record belongs.
        record_date : date
            The date of the transaction.
        note : str, optional
            Free-form text description of the transaction.
        store : str, optional
            The store or merchant associated with this record.

        Returns
        -------
        Record
            The newly created record.
        """
        new_id = self._get_next_record_id()
        record = Record(
            record_id=new_id,
            amount=amount,
            r_type=r_type,
            category=category,
            note=note,
            record_date=record_date,
            store=store,
        )
        self.records.append(record)
        self.storage.save_records(self.records)
        # Update budget spending if this is an expense
        if r_type == "expense":
            self.budget.add_spending(amount)
            self.storage.save_budget(self.budget)
        return record

    def update_record(self, record_id: int, **kwargs) -> bool:
        """Update attributes of a record if it exists.

        Accepted keyword arguments correspond to the fields on
        :class:`Record` (amount, r_type, category, note,
        record_date and store). Values not matching the expected
        type may cause a runtime error; the caller is responsible
        for validation.
        """
        record = self.get_record(record_id)
        if not record:
            return False
        for key, value in kwargs.items():
            if hasattr(record, key):
                # Cast date strings to date objects if necessary
                if key == "record_date" and isinstance(value, str):
                    value = Record.parse_date(value)
                setattr(record, key, value)
        self.storage.save_records(self.records)
        return True

    def delete_record(self, record_id: int) -> bool:
        """Remove a record from the list and persist the change."""
        for i, rec in enumerate(self.records):
            if rec.record_id == record_id:
                # Adjust budget if this record is an expense
                if rec.r_type == "expense":
                    self.budget.current_spending = max(
                        0.0, self.budget.current_spending - rec.amount
                    )
                    self.storage.save_budget(self.budget)
                del self.records[i]
                self.storage.save_records(self.records)
                return True
        return False

    def get_record(self, record_id: int) -> Optional[Record]:
        """Return the record with the given ID or None."""
        for rec in self.records:
            if rec.record_id == record_id:
                return rec
        return None

    def get_records(self) -> List[Record]:
        """Return a copy of the current list of records."""
        return list(self.records)

    # -- Category operations -----------------------------------------------
    def _get_next_category_id(self) -> int:
        """Compute the next available category ID."""
        if not self.categories:
            return 1
        return max(c.category_id for c in self.categories) + 1

    def add_category(self, name: str, icon: str, c_type: str) -> Category:
        """Create and persist a new category."""
        new_id = self._get_next_category_id()
        category = Category(category_id=new_id, name=name, icon=icon, c_type=c_type)
        self.categories.append(category)
        self.storage.save_categories(self.categories)
        return category

    def edit_category(self, category_id: int, **kwargs) -> bool:
        """Modify attributes of a category if it exists."""
        for cat in self.categories:
            if cat.category_id == category_id:
                for key, value in kwargs.items():
                    if hasattr(cat, key):
                        setattr(cat, key, value)
                self.storage.save_categories(self.categories)
                return True
        return False

    def get_categories(self) -> List[Category]:
        """Return a copy of the current list of categories."""
        return list(self.categories)

    # -- Budget operations -------------------------------------------------
    def set_budget(self, amount: float) -> None:
        """Set a new monthly budget goal and persist it."""
        self.budget.set_budget(amount)
        self.storage.save_budget(self.budget)

    def check_budget_status(self) -> str:
        """Return a human-friendly budget status message."""
        return self.budget.send_reminder()
