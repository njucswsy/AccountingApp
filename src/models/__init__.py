"""Data model definitions for the accounting application.

This package contains classes that model the core domain
entities for the accounting system, such as records of
financial transactions, categories to group those transactions,
budgets to monitor spending goals, and statistics to analyse
the aggregated data. Each class defined here encapsulates
both state (data) and behaviours (methods) relevant to
the domain concept it represents. By keeping these classes
in a separate package we can clearly separate the domain
model from controllers, services, user interface code and
other infrastructure. This separation helps maintain a clean
architecture and makes the system easier to reason about and
extend.
"""

from .record import Record  # noqa: F401
from .category import Category  # noqa: F401
from .budget import Budget  # noqa: F401
from .statistics import Statistics  # noqa: F401