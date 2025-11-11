"""Search engine for querying records.

The :class:`SearchEngine` provides a set of methods for
filtering a collection of records based on different criteria
such as store, category or date range. It also keeps an
internal history of search queries that have been executed to
enable features like displaying recent searches to the user.
"""

from datetime import date
from typing import List, Optional

from src.models.record import Record


class SearchEngine:
    """Implements various search strategies over a list of records."""

    def __init__(self, records: List[Record]) -> None:
        self.records = records
        self.history: List[str] = []

    def search_by_store(self, store: str) -> List[Record]:
        """Return all records associated with a particular store."""
        result = [r for r in self.records if r.store.lower() == store.lower()]
        self.history.append(f"store:{store}")
        return result

    def search_by_category(self, category: str) -> List[Record]:
        """Return all records belonging to a given category."""
        result = [r for r in self.records if r.category.lower() == category.lower()]
        self.history.append(f"category:{category}")
        return result

    def search_by_date_range(self, start: date, end: date) -> List[Record]:
        """Return records whose date falls within the inclusive range."""
        result = [r for r in self.records if start <= r.record_date <= end]
        self.history.append(f"date:{start.isoformat()}->{end.isoformat()}")
        return result

    def advanced_search(
        self,
        *,
        store: Optional[str] = None,
        category: Optional[str] = None,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> List[Record]:
        """Perform an advanced search combining multiple filters.

        Parameters
        ----------
        store : str, optional
            If provided, only records matching this store are returned.
        category : str, optional
            If provided, only records belonging to this category are
            returned.
        start : date, optional
            The start date for the date range filter. Must be used
            together with ``end``.
        end : date, optional
            The end date for the date range filter. Must be used
            together with ``start``.

        Returns
        -------
        list of Record
            A list of records satisfying all specified filters. If no
            filters are provided, the entire record list is returned.
        """
        result: List[Record] = list(self.records)
        if store:
            result = [r for r in result if r.store.lower() == store.lower()]
        if category:
            result = [r for r in result if r.category.lower() == category.lower()]
        if start and end:
            result = [r for r in result if start <= r.record_date <= end]
        self.history.append(
            f"advanced:{store or '-'}:{category or '-'}:{start.isoformat() if start else '-'}:{end.isoformat() if end else '-'}"
        )
        return result

    def get_search_history(self) -> List[str]:
        """Return a copy of the executed search history."""
        return list(self.history)
