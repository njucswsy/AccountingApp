"""Controller layer for the accounting application.

Controllers mediate between the user interface (e.g. CLI,
GUI, web) and the underlying services and domain models.
They orchestrate operations, call into services and models,
and prepare data for presentation. Keeping controllers in
their own module helps maintain a clean separation of
concerns and simplifies the substitution of different UI
frameworks.
"""

from .record_controller import RecordController  # noqa: F401
from .search_controller import SearchController  # noqa: F401
from .statistics_controller import StatisticsController  # noqa: F401