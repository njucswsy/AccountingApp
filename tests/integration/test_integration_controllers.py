import json
import pytest
from datetime import date

from src.controllers.record_controller import RecordController
from src.models.budget import Budget
from src.services.search_engine import SearchEngine
from src.services.storage_service import StorageService

# 固定 today()，避免预算联动受真实日期影响
class _FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2025, 12, 23)

@pytest.fixture()
def storage(tmp_path):
    return StorageService(data_dir=str(tmp_path))

@pytest.fixture()
def rc(storage, monkeypatch):
    import src.controllers.record_controller as rc_mod
    monkeypatch.setattr(rc_mod, "date", _FixedDate)
    return RecordController(storage=storage, budget=Budget(monthly_goal=1000.0, month="2025-12"))

def test_integration_flow_record_to_search_and_persist(rc, storage):
    """
    集成测试组1（流程型）：
    RecordController -> 预算联动 -> SearchEngine -> StorageService落盘
    """
    # 1) 新增两条记录（其中一条用于搜索）
    rc.create_record(100.0, "expense", "food", _FixedDate(2025, 12, 1), store="Starbucks")
    rc.create_record(200.0, "income", "salary", _FixedDate(2025, 12, 2), store="Company")

    # 2) 当月支出应计入预算
    assert rc.budget.current_spending == 100.0

    # 3) 搜索模块集成：高级搜索
    se = SearchEngine(rc.get_records())
    res = se.advanced_search(store="STARBUCKS", category="food")
    assert len(res) == 1
    assert res[0].amount == 100.0

    # 4) 持久化集成：records.json 应写入两条
    raw = json.loads(storage.records_file.read_text(encoding="utf-8"))
    assert len(raw) == 2
