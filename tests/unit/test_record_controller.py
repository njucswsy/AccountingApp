from datetime import date
import json
import pytest

from src.controllers.record_controller import RecordController
from src.services.storage_service import StorageService
from src.models.budget import Budget

# --- 工具：把 RecordController 里用到的 date.today() 固定住 ---
class _FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2025, 12, 23)  # 固定成你当前实验日期也行

@pytest.fixture()
def tmp_storage(tmp_path):
    return StorageService(data_dir=str(tmp_path))

@pytest.fixture()
def rc(tmp_storage, monkeypatch):
    # 固定 record_controller 模块里的 date
    import src.controllers.record_controller as rc_mod
    monkeypatch.setattr(rc_mod, "date", _FixedDate)
    return RecordController(storage=tmp_storage, budget=Budget(monthly_goal=1000.0, month="2025-12"))

def test_create_record_id_starts_from_1(rc):
    r = rc.create_record(10.0, "income", "salary", _FixedDate(2025,12,1))
    assert r.record_id == 1

def test_create_record_persists_records_json(rc, tmp_storage):
    rc.create_record(10.0, "income", "salary", _FixedDate(2025,12,1))
    raw = json.loads(tmp_storage.records_file.read_text(encoding="utf-8"))
    assert len(raw) == 1
    assert raw[0]["amount"] == 10.0

def test_create_expense_current_month_updates_budget(rc, tmp_storage):
    rc.create_record(200.0, "expense", "food", _FixedDate(2025,12,2))
    assert rc.budget.current_spending == 200.0
    raw = json.loads(tmp_storage.budget_file.read_text(encoding="utf-8"))
    assert raw["current_spending"] == 200.0

def test_create_expense_not_current_month_does_not_update_budget(rc):
    rc.create_record(200.0, "expense", "food", _FixedDate(2025,11,30))
    assert rc.budget.current_spending == 0.0

def test_delete_record_removes_and_persists(rc, tmp_storage):
    r = rc.create_record(50.0, "income", "salary", _FixedDate(2025,12,3))
    assert rc.delete_record(r.record_id) is True
    raw = json.loads(tmp_storage.records_file.read_text(encoding="utf-8"))
    assert raw == []

def test_update_record_casts_date_string(rc):
    r = rc.create_record(10.0, "income", "salary", _FixedDate(2025,12,1))
    ok = rc.update_record(r.record_id, record_date="2025-12-05")
    assert ok is True
    assert rc.get_record(r.record_id).record_date == _FixedDate(2025,12,5)

def test_set_budget_saves(rc, tmp_storage):
    rc.set_budget(3000.0)
    raw = json.loads(tmp_storage.budget_file.read_text(encoding="utf-8"))
    assert raw["monthly_goal"] == 3000.0

@pytest.mark.parametrize("spent, expected_level", [
    (100.0, "normal"),     # <50%
    (600.0, "tight"),      # 50%-80%
    (900.0, "warning"),    # 80%-100%
    (1200.0, "over"),      # >100%
])
def test_budget_status_levels(rc, spent, expected_level):
    # 用当月支出来堆 spent
    rc.records.clear()
    # monthly_goal=1000
    rc.create_record(spent, "expense", "food", _FixedDate(2025,12,2))
    level, msg = rc.get_budget_status_detail()
    assert level == expected_level
    assert isinstance(msg, str) and len(msg) > 0

def test_get_record_not_found_returns_none(rc):
    assert rc.get_record(9999) is None

def test_delete_record_not_found_returns_false(rc):
    assert rc.delete_record(9999) is False

def test_update_record_not_found_returns_false(rc):
    assert rc.update_record(9999, amount=123.0) is False

def test_update_record_invalid_date_string_returns_false(rc):
    r = rc.create_record(10.0, "income", "salary", _FixedDate(2025,12,1))
    ok = rc.update_record(r.record_id, record_date="2025-99-99")
    assert ok is False

def test_delete_record_twice_second_false(rc):
    r = rc.create_record(10.0, "income", "salary", _FixedDate(2025,12,1))
    assert rc.delete_record(r.record_id) is True
    assert rc.delete_record(r.record_id) is False

def test_get_records_returns_list(rc):
    rc.create_record(10.0, "income", "salary", _FixedDate(2025,12,1))
    lst = rc.get_records()
    assert isinstance(lst, list)
    assert len(lst) == 1

def test_get_record_not_found_is_none(rc):
    assert rc.get_record(99999) is None

def test_create_record_id_increments(rc):
    r1 = rc.create_record(10.0, "income", "salary", _FixedDate(2025, 12, 1))
    r2 = rc.create_record(20.0, "income", "salary", _FixedDate(2025, 12, 2))
    assert r1.record_id == 1
    assert r2.record_id == 2

def test_delete_expense_updates_budget(rc):
    r = rc.create_record(200.0, "expense", "food", _FixedDate(2025, 12, 2))
    assert rc.budget.current_spending >= 200.0
    assert rc.delete_record(r.record_id) is True
    assert rc.budget.current_spending == 0.0


def test_add_category_persists(rc):
    c = rc.add_category(name="餐饮", icon="🍔", c_type="expense")
    assert c.category_id == 1
    raw = json.loads(rc.storage.categories_file.read_text(encoding="utf-8"))
    assert len(raw) == 1
    assert raw[0]["name"] == "餐饮"

def test_edit_category_success_and_fail(rc):
    c = rc.add_category(name="餐饮", icon="🍔", c_type="expense")
    ok = rc.edit_category(c.category_id, name="外卖")
    assert ok is True
    assert rc.get_categories()[0].name == "外卖"

    ok2 = rc.edit_category(9999, name="不会存在")
    assert ok2 is False

def test_delete_category_success_and_fail(rc):
    c = rc.add_category(name="餐饮", icon="🍔", c_type="expense")
    assert rc.delete_category(c.category_id) is True
    assert rc.get_categories() == []

    assert rc.delete_category(9999) is False

def test_set_budget_resets_when_month_mismatch(rc):
    # rc 里的 today 被固定为 2025-12，所以 current_month 是 2025-12
    rc.budget.month = "2025-11"
    rc.set_budget(3000.0)
    assert rc.budget.month == "2025-12"
    assert rc.budget.monthly_goal == 3000.0

def test_check_budget_status_returns_string(rc):
    msg = rc.check_budget_status()
    assert isinstance(msg, str)
    assert len(msg) > 0

