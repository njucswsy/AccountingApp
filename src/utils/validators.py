"""Input parsing helpers.

This module defines functions to safely parse strings into
numerical and date types. They are used primarily by the
command line interface to validate user input before passing
values to the business logic layer. Each function returns
``None`` on failure rather than raising an exception, which
allows the caller to implement custom error handling logic.
"""

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
