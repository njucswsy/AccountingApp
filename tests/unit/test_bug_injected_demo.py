# tests/unit/test_bug_injected_demo.py
import builtins
import pytest

from src.utils import bug_injected_demo as demo


class DummyFile:
    def __init__(self, content: str):
        self.content = content
        self.close_count = 0

    def read(self):
        return self.content

    def close(self):
        self.close_count += 1

    # 支持 with open(...) as f
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def test_fake_memory_leak_closes_file(monkeypatch):
    f = DummyFile("0123456789ABCDEF")  # len > 10，触发“提前 return”路径
    monkeypatch.setattr(builtins, "open", lambda *a, **k: f)

    demo.fake_memory_leak("whatever.txt")
    assert f.close_count == 1


def test_fake_double_free_close_only_once(monkeypatch):
    f = DummyFile("hello")
    monkeypatch.setattr(builtins, "open", lambda *a, **k: f)

    demo.fake_double_free("whatever.txt")
    assert f.close_count == 1


def test_fake_null_deref_flag_false_is_safe():
    # 你修复后建议：flag=False 时返回 0（或抛 ValueError，但要和这里一致）
    assert demo.fake_null_deref(False) == 0
