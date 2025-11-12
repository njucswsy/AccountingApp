"""Application settings."""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AppSettings:
    """Application configuration and user preferences."""

    # Display settings
    theme: str = "light"  # light / dark
    font_size: str = "normal"  # small / normal / large
    language: str = "zh-CN"  # zh-CN / en-US
    
    # Notification settings
    budget_notifications: bool = True
    daily_reminders: bool = False
    expense_warnings: bool = True
    
    # Data settings
    auto_backup: bool = True
    backup_frequency: str = "weekly"  # daily / weekly / monthly
    export_format: str = "json"  # json / csv / excel
    
    # Privacy settings
    hide_amounts: bool = False
    require_password: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize settings to dictionary."""
        return {
            "theme": self.theme,
            "font_size": self.font_size,
            "language": self.language,
            "budget_notifications": self.budget_notifications,
            "daily_reminders": self.daily_reminders,
            "expense_warnings": self.expense_warnings,
            "auto_backup": self.auto_backup,
            "backup_frequency": self.backup_frequency,
            "export_format": self.export_format,
            "hide_amounts": self.hide_amounts,
            "require_password": self.require_password,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSettings":
        """Construct settings from dictionary."""
        return cls(
            theme=data.get("theme", "light"),
            font_size=data.get("font_size", "normal"),
            language=data.get("language", "zh-CN"),
            budget_notifications=bool(data.get("budget_notifications", True)),
            daily_reminders=bool(data.get("daily_reminders", False)),
            expense_warnings=bool(data.get("expense_warnings", True)),
            auto_backup=bool(data.get("auto_backup", True)),
            backup_frequency=data.get("backup_frequency", "weekly"),
            export_format=data.get("export_format", "json"),
            hide_amounts=bool(data.get("hide_amounts", False)),
            require_password=bool(data.get("require_password", False)),
        )
