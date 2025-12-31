import json
import pytest
from datetime import date

from src.controllers.record_controller import RecordController
from src.models.budget import Budget
from src.services.storage_service import StorageService

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

def test_integration_restart_reload_then_update(rc, storage):
    """
    集成测试组2（重启/重载型）：
    写盘 -> 新建Controller模拟重启 -> 从JSON重载 -> 更新 -> 再次写盘
    """
    r = rc.create_record(50.0, "expense", "food", _FixedDate(2025, 12, 3), store="A")

    # 模拟“重启”：重新创建一个 controller（同一 data_dir）
    rc2 = RecordController(storage=storage, budget=Budget(monthly_goal=1000.0, month="2025-12"))

    # 1) 重载后能读到刚才写入的记录
    got = rc2.get_record(r.record_id)
    assert got is not None
    assert got.amount == 50.0

    # 2) 更新记录金额并落盘
    ok = rc2.update_record(r.record_id, amount=80.0)
    assert ok is True

    raw = json.loads(storage.records_file.read_text(encoding="utf-8"))
    updated = [x for x in raw if x["record_id"] == r.record_id][0]
    assert updated["amount"] == 80.0
