import json
from pathlib import Path
from typing import List, Optional

from src.models.record import Record
from src.models.category import Category
from src.models.budget import Budget
from src.models.user import User
from src.models.settings import AppSettings


class StorageService:
    """A simple file-based persistence layer."""

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.records_file = self.data_dir / "records.json"
        self.categories_file = self.data_dir / "categories.json"
        self.budget_file = self.data_dir / "budget.json"
        self.user_file = self.data_dir / "user.json"
        self.settings_file = self.data_dir / "settings.json"

    def load_records(self) -> List[Record]:
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

    def load_user(self) -> User:
        """Load user profile or return default."""
        if not self.user_file.exists():
            return User()
        with self.user_file.open("r", encoding="utf-8") as file:
            raw = json.load(file)
        return User.from_dict(raw)

    def save_user(self, user: User) -> None:
        """Persist the given user to disk."""
        with self.user_file.open("w", encoding="utf-8") as file:
            json.dump(user.to_dict(), file, ensure_ascii=False, indent=2)

    def load_settings(self) -> AppSettings:
        """Load app settings or return defaults."""
        if not self.settings_file.exists():
            return AppSettings()
        with self.settings_file.open("r", encoding="utf-8") as file:
            raw = json.load(file)
        return AppSettings.from_dict(raw)

    def save_settings(self, settings: AppSettings) -> None:
        """Persist the given settings to disk."""
        with self.settings_file.open("w", encoding="utf-8") as file:
            json.dump(settings.to_dict(), file, ensure_ascii=False, indent=2)
