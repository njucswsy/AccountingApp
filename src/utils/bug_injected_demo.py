# 这是“故意写坏的代码”，用于测试分析工具的真阳性/误报情况

def fake_memory_leak(path: str, data: str):
    """
    模拟 CWE-401 Memory Leak / 资源泄漏：
    打开文件后某些分支直接 return，没关闭文件。
    """
    f = open(path, "w", encoding="utf-8")
    if len(data) > 10:
        # 这里直接返回，f 没有 close，属于资源泄漏
        return
    f.write(data)
    f.close()


def fake_double_free(path: str) -> str:
    """
    模拟 CWE-415 Double Free：
    同一个资源被关闭两次。
    在 Python 里是 double close 文件句柄。
    """
    f = open(path, "r", encoding="utf-8")
    try:
        content = f.read()
    finally:
        f.close()
    # 第二次多余的关闭，属于 double free 类问题
    f.close()
    return content


def fake_null_deref(flag: bool) -> int:
    """
    模拟 CWE-476 NULL Pointer Dereference：
    None 当成有效对象来用。
    """
    record = None
    if flag:
        record = {"amount": 100}
    # 没有检查 record 是否为 None 就直接用
    return record["amount"]
