from datetime import datetime, date
from typing import Optional


def parse_float(input_str: str) -> Optional[float]:
    """Attempt to parse a floating point number from a string.

    Parameters
    ----------
    input_str : str
        The user-provided string to parse.

    Returns
    -------
    float or None
        The parsed floating point number on success, or ``None``
        if parsing fails.
    """
    try:
        value = float(input_str)
        return value
    except ValueError:
        return None


def parse_int(input_str: str) -> Optional[int]:
    """Attempt to parse an integer from a string."""
    try:
        return int(input_str)
    except ValueError:
        return None


def parse_date(input_str: str) -> Optional[date]:
    """Parse a date in ISO format (YYYY-MM-DD)."""
    try:
        return datetime.strptime(input_str, "%Y-%m-%d").date()
    except ValueError:
        return None
