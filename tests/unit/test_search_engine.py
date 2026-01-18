from datetime import date
from src.models.record import Record
from src.services.search_engine import SearchEngine

def _r(i, amt, t, cat, d, store="", note=""):
    return Record(record_id=i, amount=amt, r_type=t, category=cat, note=note, record_date=d, store=store)

def test_search_by_store_case_insensitive():
    records = [_r(1, 10, "expense", "food", date(2025,12,1), store="Starbucks"),
               _r(2, 20, "expense", "food", date(2025,12,2), store="starbucks")]
    se = SearchEngine(records)
    res = se.search_by_store("STARBUCKS")
    assert len(res) == 2
    assert se.get_search_history()[-1].startswith("store:")

def test_search_by_category_case_insensitive():
    records = [_r(1, 10, "expense", "Food", date(2025,12,1)),
               _r(2, 20, "expense", "food", date(2025,12,2))]
    se = SearchEngine(records)
    assert len(se.search_by_category("FOOD")) == 2

def test_search_by_date_range_inclusive():
    records = [_r(1, 10, "expense", "food", date(2025,12,1)),
               _r(2, 20, "expense", "food", date(2025,12,3))]
    se = SearchEngine(records)
    res = se.search_by_date_range(date(2025,12,1), date(2025,12,1))
    assert [r.record_id for r in res] == [1]

def test_advanced_search_store_only():
    records = [_r(1, 10, "expense", "food", date(2025,12,1), store="A"),
               _r(2, 20, "expense", "food", date(2025,12,2), store="B")]
    se = SearchEngine(records)
    res = se.advanced_search(store="A")
    assert [r.record_id for r in res] == [1]

def test_advanced_search_category_only():
    records = [_r(1, 10, "expense", "food", date(2025,12,1)),
               _r(2, 20, "expense", "rent", date(2025,12,2))]
    se = SearchEngine(records)
    res = se.advanced_search(category="rent")
    assert [r.record_id for r in res] == [2]

def test_advanced_search_date_range():
    records = [_r(1, 10, "expense", "food", date(2025,12,1)),
               _r(2, 20, "expense", "food", date(2025,12,10))]
    se = SearchEngine(records)
    res = se.advanced_search(start=date(2025,12,2), end=date(2025,12,31))
    assert [r.record_id for r in res] == [2]

def test_advanced_search_combined_filters():
    records = [
        _r(1, 10, "expense", "food", date(2025,12,1), store="A"),
        _r(2, 20, "expense", "food", date(2025,12,3), store="B"),
        _r(3, 30, "expense", "rent", date(2025,12,3), store="B"),
    ]
    se = SearchEngine(records)
    res = se.advanced_search(store="B", category="rent", start=date(2025,12,1), end=date(2025,12,31))
    assert [r.record_id for r in res] == [3]

def test_history_is_copy():
    se = SearchEngine([])
    h = se.get_search_history()
    h.append("x")
    assert se.get_search_history() == []
