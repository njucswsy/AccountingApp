from datetime import date
from typing import List, Optional

from src.models.record import Record
from src.services.search_engine import SearchEngine


class SearchController:
    """Coordinate search operations across a record list."""

    def __init__(self, records: List[Record]) -> None:
        # Note: we copy the reference to the records list; if the
        # caller appends new records this controller will see them.
        self.search_engine = SearchEngine(records)

    def execute_search(
        self,
        *,
        store: Optional[str] = None,
        category: Optional[str] = None,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> List[Record]:
        """Execute a search with arbitrary combination of filters."""
        # Use the advanced search method to handle all filters in one place.
        return self.search_engine.advanced_search(
            store=store,
            category=category,
            start=start,
            end=end,
        )

    def get_search_history(self) -> List[str]:
        """Return the list of past search queries."""
        return self.search_engine.get_search_history()
