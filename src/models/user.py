"""User profile and authentication."""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class User:
    """Represents a user account."""

    user_id: int = 1
    username: str = ""
    nickname: str = ""
    email: str = ""
    avatar_emoji: str = "👤"
    is_logged_in: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize user to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "nickname": self.nickname,
            "email": self.email,
            "avatar_emoji": self.avatar_emoji,
            "is_logged_in": self.is_logged_in,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Construct user from dictionary."""
        return cls(
            user_id=int(data.get("user_id", 1)),
            username=data.get("username", ""),
            nickname=data.get("nickname", ""),
            email=data.get("email", ""),
            avatar_emoji=data.get("avatar_emoji", "👤"),
            is_logged_in=bool(data.get("is_logged_in", False)),
        )
