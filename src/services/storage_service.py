"""Persistence service for accounting data.

The :class:`StorageService` class abstracts away the details of
reading from and writing to the filesystem. It handles
serialising and deserialising lists of records and categories
to JSON files and also provides support for persisting a
single budget object. The paths to the data files are
determined relative to a root data directory, which defaults
to ``data`` in the project directory. By centralising all file
I/O here we make it easier to later swap in a different
persistence mechanism (e.g. a database) without changing
other parts of the application.
"""

import json
from pathlib import Path
from typing import List, Optional

from src.models.record import Record
from src.models.category import Category
from src.models.budget import Budget


class StorageService:
    """A simple file-based persistence layer."""

    def __init__(self, data_dir: str = "data") -> None:
        # Resolve the path relative to the package root. If the
        # caller passes an absolute path, Path will handle it.
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.records_file = self.data_dir / "records.json"
        self.categories_file = self.data_dir / "categories.json"
        self.budget_file = self.data_dir / "budget.json"

    def load_records(self) -> List[Record]:
        """Load all records from the JSON file.

        If the file does not exist, an empty list is returned.
        This method never raises an exception on missing files or
        empty contents; any JSON decoding errors will propagate
        naturally and should be handled by the caller.
        """
        if not self.records_file.exists():
            return []
        with self.records_file.open("r", encoding="utf-8") as file:
            raw_list = json.load(file)
        return [Record.from_dict(item) for item in raw_list]

    def save_records(self, records: List[Record]) -> None:
        """Persist the given list of records to disk."""
        with self.records_file.open("w", encoding="utf-8") as file:
            json.dump([r.to_dict() for r in records], file, ensure_ascii=False, indent=2)

    def load_categories(self) -> List[Category]:
        """Load all categories from the JSON file or return an empty list."""
        if not self.categories_file.exists():
            return []
        with self.categories_file.open("r", encoding="utf-8") as file:
            raw_list = json.load(file)
        return [Category.from_dict(item) for item in raw_list]

    def save_categories(self, categories: List[Category]) -> None:
        """Persist the given list of categories to disk."""
        with self.categories_file.open("w", encoding="utf-8") as file:
            json.dump([c.to_dict() for c in categories], file, ensure_ascii=False, indent=2)

    def load_budget(self) -> Optional[Budget]:
        """Load the persisted budget if it exists."""
        if not self.budget_file.exists():
            return None
        with self.budget_file.open("r", encoding="utf-8") as file:
            raw = json.load(file)
        return Budget.from_dict(raw)

    def save_budget(self, budget: Budget) -> None:
        """Persist the given budget to disk."""
        with self.budget_file.open("w", encoding="utf-8") as file:
            json.dump(budget.to_dict(), file, ensure_ascii=False, indent=2)
