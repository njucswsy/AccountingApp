import json
import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Tuple

from PyQt5.QtCore import QObject, pyqtSlot, QUrl
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

from src.controllers.record_controller import RecordController
from src.controllers.statistics_controller import StatisticsController
from src.controllers.search_controller import SearchController
from src.models.record import Record
from src.models.user import User
from src.models.settings import AppSettings
from src.services.storage_service import StorageService
from src.services.analysis import Analysis


def _parse_date(d: Any) -> date:
    if isinstance(d, date):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str) and d:
        # 允许 'YYYY-MM-DD'
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except Exception:
            pass
    return date.today()


def record_to_dict(r: Record) -> Dict[str, Any]:
    return {
        "record_id": r.record_id,
        "amount": r.amount,
        "r_type": r.r_type,
        "category": r.category,
        "note": r.note,
        "store": r.store,
        "date": r.record_date.isoformat() if hasattr(r.record_date, "isoformat") else str(r.record_date),
    }


def _month_range(today: date) -> Tuple[date, date]:
    start = today.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1, day=1)
    else:
        end = start.replace(month=start.month + 1, day=1)
    return start, end


class Backend(QObject):
    """暴露给前端 JS 的后端接口。"""

    def __init__(self, storage: StorageService):
        super().__init__()
        self.storage = storage
        self.record_controller = RecordController(storage)
        self.stats_controller = StatisticsController(self.record_controller.get_records())
        self.search_controller = SearchController(self.record_controller.get_records())
        self.analysis = Analysis()
        self.user = storage.load_user()
        self.settings = storage.load_settings()

    # ========================= 首页 / 总览 =========================

    @pyqtSlot(result=str)
    def get_home_overview(self) -> str:
        """返回首页需要的汇总信息：收入、支出、结余、预算使用、最近记录（当月）。"""
        records = self.record_controller.get_records()
        self.stats_controller.records = records

        totals_all = self.stats_controller.get_summary()
        income_all = float(totals_all.get("income", 0.0))
        expense_all = float(totals_all.get("expense", 0.0))
        balance_all = float(totals_all.get("balance", income_all - expense_all))

        budget_total = 0.0
        try:
            b = self.storage.load_budget()
            for f in ("monthly_goal", "total_budget", "budget", "limit"):
                if hasattr(b, f):
                    budget_total = float(getattr(b, f) or 0.0)
                    if budget_total:
                        break
        except Exception:
            pass

        today = date.today()
        m_start, m_end = _month_range(today)
        month_records = [r for r in records if m_start <= _parse_date(getattr(r, "record_date", today)) < m_end]
        month_expense = sum(float(r.amount) for r in month_records if getattr(r, "r_type", "expense") == "expense")

        budget_percent = 0
        if budget_total > 0:
            budget_percent = max(0, min(100, round((month_expense * 100.0) / budget_total)))

        recent = sorted(month_records or records, key=lambda r: r.record_id, reverse=True)[:10]

        payload = {
            "income": round(income_all, 2),
            "expense": round(expense_all, 2),
            "balance": round(balance_all, 2),
            "budget_percent": budget_percent,
            "budget_used": round(month_expense, 2),
            "budget_total": round(budget_total, 2),
            "recent": [record_to_dict(r) for r in recent],
        }
        return json.dumps(payload, ensure_ascii=False)

    # ========================= 记账 =========================

    @pyqtSlot(str, result=str)
    def add_record(self, json_str: str) -> str:
        """
        新增一条收支记录。
        json_str: {"amount": 12.3, "r_type": "income"/"expense", "category": "...",
                   "note": "...", "store": "...", "record_date": "YYYY-MM-DD"}
        """
        try:
            data = json.loads(json_str)
            amount = float(data.get("amount", 0))
            r_type = data.get("r_type", "expense")
            category = data.get("category", "其他")
            note = data.get("note") or ""
            store = data.get("store") or ""
            r_date = _parse_date(data.get("record_date"))  # ✅ 支持手动选择日期
            rec = self.record_controller.create_record(amount, r_type, category, r_date, note=note, store=store)
            res = {"ok": True, "record": record_to_dict(rec)}
        except Exception as e:
            res = {"ok": False, "error": str(e)}
        return json.dumps(res, ensure_ascii=False)

    @pyqtSlot(str, result=str)
    def edit_record(self, json_str: str) -> str:
        """编辑一条收支记录
        json_str: {"record_id": 1, "amount": 12.3, "r_type": "income"/"expense", 
                   "category": "...", "note": "...", "store": "...", "record_date": "YYYY-MM-DD"}
        """
        try:
            data = json.loads(json_str)
            record_id = int(data.get("record_id", 0))
            if not record_id:
                return json.dumps({"ok": False, "error": "记录ID不能为空"}, ensure_ascii=False)
            
            updates = {}
            if "amount" in data:
                updates["amount"] = float(data["amount"])
            if "r_type" in data:
                updates["r_type"] = data["r_type"]
            if "category" in data:
                updates["category"] = data["category"]
            if "note" in data:
                updates["note"] = data["note"]
            if "store" in data:
                updates["store"] = data["store"]
            if "record_date" in data:
                updates["record_date"] = _parse_date(data["record_date"])
            
            if not updates:
                return json.dumps({"ok": False, "error": "没有提供要修改的字段"}, ensure_ascii=False)
            
            ok = self.record_controller.update_record(record_id, **updates)
            if ok:
                # 返回更新后的记录
                record = self.record_controller.get_record(record_id)
                res = {"ok": True, "record": record_to_dict(record)}
            else:
                res = {"ok": False, "error": "未找到对应的记录"}
        except Exception as e:
            res = {"ok": False, "error": str(e)}
        return json.dumps(res, ensure_ascii=False)

    @pyqtSlot(int, result=str)
    def delete_record(self, record_id: int) -> str:
        """删除一条收支记录"""
        try:
            ok = self.record_controller.delete_record(record_id)
            return json.dumps({"ok": bool(ok)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    @pyqtSlot(result=str)
    def get_all_records(self) -> str:
        """获取所有账单记录"""
        try:
            records = self.record_controller.get_records()
            # 按记录ID倒序排列（最新的在前）
            records = sorted(records, key=lambda r: r.record_id, reverse=True)
            payload = {"records": [record_to_dict(r) for r in records]}
            return json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ========================= 分类 =========================

    @pyqtSlot(result=str)
    def get_categories(self) -> str:
        cats = self.record_controller.get_categories()
        payload = []
        for c in cats:
            payload.append({
                "category_id": getattr(c, "category_id", 0),
                "name": getattr(c, "name", ""),
                "icon": getattr(c, "icon", "fas fa-circle"),
                "c_type": getattr(c, "c_type", "expense"),  # ✅ 用于前端过滤 收入/支出
            })
        return json.dumps(payload, ensure_ascii=False)

    @pyqtSlot(str, result=str)
    def add_category(self, json_str: str) -> str:
        """添加分类，支持指定类型（收入/支出）
        json_str: {"name": "分类名称", "c_type": "income"/"expense"}
        """
        try:
            data = json.loads(json_str)
            name = data.get("name", "").strip()
            c_type = data.get("c_type", "expense")  # 默认为支出
            if not name:
                return json.dumps({"ok": False, "error": "分类名称不能为空"}, ensure_ascii=False)
            c = self.record_controller.add_category(name=name, icon="fas fa-circle", c_type=c_type)
            res = {"ok": True, "category": {"category_id": c.category_id, "name": c.name, "c_type": c.c_type}}
        except Exception as e:
            res = {"ok": False, "error": str(e)}
        return json.dumps(res, ensure_ascii=False)

    @pyqtSlot(str, result=str)
    def edit_category(self, json_str: str) -> str:
        """编辑分类，支持修改名称和类型
        json_str: {"category_id": 1, "name": "新名称", "c_type": "income"/"expense"}
        """
        try:
            data = json.loads(json_str)
            category_id = int(data.get("category_id", 0))
            updates = {}
            if "name" in data:
                updates["name"] = data["name"].strip()
            if "c_type" in data:
                updates["c_type"] = data["c_type"]
            if not updates:
                return json.dumps({"ok": False, "error": "没有提供要修改的字段"}, ensure_ascii=False)
            ok = self.record_controller.edit_category(category_id, **updates)
            return json.dumps({"ok": bool(ok)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    @pyqtSlot(int, result=str)
    def delete_category(self, category_id: int) -> str:
        """删除分类"""
        try:
            ok = self.record_controller.delete_category(category_id)
            return json.dumps({"ok": bool(ok)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    # ========================= 搜索 =========================

    @pyqtSlot(str, result=str)
    def search(self, json_str: str) -> str:
        """高级搜索，支持多条件筛选"""
        try:
            data = json.loads(json_str)
            keyword = (data.get("keyword") or "").strip()
            category = data.get("category", "").strip()
            amount_min = data.get("amount_min")
            amount_max = data.get("amount_max")
            start_date_str = data.get("start_date")
            end_date_str = data.get("end_date")
            
            records = self.record_controller.get_records()
            result = list(records)
            
            # 关键字搜索（分类、商家、备注）
            if keyword:
                keyword_lower = keyword.lower()
                result = [r for r in result if 
                         keyword_lower in (getattr(r, "category", "") or "").lower() or
                         keyword_lower in (getattr(r, "store", "") or "").lower() or
                         keyword_lower in (getattr(r, "note", "") or "").lower()]
            
            # 分类筛选
            if category:
                result = [r for r in result if (getattr(r, "category", "") or "").lower() == category.lower()]
            
            # 金额范围筛选
            if amount_min is not None:
                try:
                    min_val = float(amount_min)
                    result = [r for r in result if float(getattr(r, "amount", 0) or 0) >= min_val]
                except:
                    pass
            if amount_max is not None:
                try:
                    max_val = float(amount_max)
                    result = [r for r in result if float(getattr(r, "amount", 0) or 0) <= max_val]
                except:
                    pass
            
            # 日期范围筛选
            if start_date_str:
                start_date = _parse_date(start_date_str)
                result = [r for r in result if _parse_date(getattr(r, "record_date", date.today())) >= start_date]
            if end_date_str:
                end_date = _parse_date(end_date_str)
                result = [r for r in result if _parse_date(getattr(r, "record_date", date.today())) <= end_date]

            payload = {"records": [record_to_dict(r) for r in result]}
            return json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @pyqtSlot(result=str)
    def get_search_categories(self) -> str:
        """获取所有分类列表，用于搜索筛选"""
        try:
            categories = self.record_controller.get_categories()
            cat_list = [{"name": c.name, "c_type": getattr(c, "c_type", "expense")} for c in categories if c.name]
            return json.dumps(cat_list, ensure_ascii=False)
        except Exception as e:
            return json.dumps([], ensure_ascii=False)

    # ========================= 统计 + 消费分析 =========================

    @pyqtSlot(str, result=str)
    def get_statistics(self, json_str: str) -> str:
        """
        支持自定义时间范围的统计
        json_str: {"period": "day/week/month/year/custom", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
        """
        try:
            data = json.loads(json_str)
            period = data.get("period", "month")
            start_date_str = data.get("start_date")
            end_date_str = data.get("end_date")
        except:
            period = "month"
            start_date_str = None
            end_date_str = None

        recs = self.record_controller.get_records()
        today = date.today()

        # 根据period计算时间范围
        if period == "day":
            start = today
            end = today
        elif period == "week":
            # 本周一
            days_since_monday = today.weekday()
            start = today - timedelta(days=days_since_monday)
            end = today
        elif period == "month":
            start, end = _month_range(today)
            end = end - timedelta(days=1)  # 月末最后一天
        elif period == "year":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        elif period == "custom" and start_date_str and end_date_str:
            start = _parse_date(start_date_str)
            end = _parse_date(end_date_str)
        else:
            # 默认本月
            start, end = _month_range(today)
            end = end - timedelta(days=1)

        # 筛选记录
        recs = [r for r in recs if start <= _parse_date(getattr(r, "record_date", today)) <= end]

        # 总览
        stats = StatisticsController(recs)
        totals = stats.get_summary()

        # 分类聚合：支出 & 收入分开
        expense_map: Dict[str, float] = {}
        income_map: Dict[str, float] = {}
        for r in recs:
            cat = getattr(r, "category", "") or "未分类"
            amt = float(getattr(r, "amount", 0.0) or 0.0)
            if getattr(r, "r_type", "expense") == "expense":
                expense_map[cat] = expense_map.get(cat, 0.0) + amt
            else:
                income_map[cat] = income_map.get(cat, 0.0) + amt

        expense_series = [{"name": k, "value": round(v, 2)} for k, v in expense_map.items() if v > 0]
        income_series = [{"name": k, "value": round(v, 2)} for k, v in income_map.items() if v > 0]

        # 趋势数据：按日期分组统计
        trend_map: Dict[str, Dict[str, float]] = {}  # {date: {income: x, expense: y}}
        for r in recs:
            r_date = _parse_date(getattr(r, "record_date", today))
            date_str = r_date.isoformat()
            if date_str not in trend_map:
                trend_map[date_str] = {"income": 0.0, "expense": 0.0}
            amt = float(getattr(r, "amount", 0.0) or 0.0)
            r_type = getattr(r, "r_type", "expense")
            if r_type == "income":
                trend_map[date_str]["income"] += amt
            else:
                trend_map[date_str]["expense"] += amt

        # 按日期排序
        sorted_dates = sorted(trend_map.keys())
        trend_data = {
            "dates": sorted_dates,
            "income": [round(trend_map[d]["income"], 2) for d in sorted_dates],
            "expense": [round(trend_map[d]["expense"], 2) for d in sorted_dates]
        }

        payload = {
            "totals": totals,
            "expenseSeries": expense_series,
            "incomeSeries": income_series,
            "trendData": trend_data
        }
        return json.dumps(payload, ensure_ascii=False)

    @pyqtSlot(str, result=str)
    def get_ai_analysis(self, period: str) -> str:
        """生成消费分析"""
        try:
            txt = self.analysis.generate_suggestions(self.record_controller.get_records())
        except Exception:
            txt = "数据较少，暂无法生成有效消费分析。"
        return txt

    # ========================= 预算 =========================

    @pyqtSlot(str, result=str)
    def save_budget(self, total_budget: str) -> str:
        try:
            value = float(str(total_budget).replace(",", "").strip())
        except Exception:
            value = 0.0
        self.record_controller.set_budget(value)
        return json.dumps({"ok": True, "budget": value}, ensure_ascii=False)

    @pyqtSlot(result=str)
    def get_budget_status(self) -> str:
        """获取预算状态，返回level和message"""
        try:
            today = date.today()
            m_start, m_end = _month_range(today)
            records = self.record_controller.get_records()
            month_records = [r for r in records if m_start <= _parse_date(getattr(r, "record_date", today)) < m_end]
            month_expense = sum(float(r.amount) for r in month_records if getattr(r, "r_type", "expense") == "expense")
            
            budget_total = 0.0
            try:
                b = self.storage.load_budget()
                for f in ("monthly_goal", "total_budget", "budget", "limit"):
                    if hasattr(b, f):
                        budget_total = float(getattr(b, f) or 0.0)
                        if budget_total:
                            break
            except Exception:
                pass
            
            budget_percent = 0
            if budget_total > 0:
                budget_percent = max(0, min(100, round((month_expense * 100.0) / budget_total)))
            
            level, msg = self.record_controller.get_budget_status_detail()
            payload = {
                "level": level,
                "message": msg,
                "used": round(month_expense, 2),
                "total": round(budget_total, 2),
                "percent": budget_percent
            }
            return json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"level": "unknown", "message": str(e), "used": 0, "total": 0, "percent": 0}, ensure_ascii=False)

    # ========================= 用户 & 设置 =========================

    @pyqtSlot(result=str)
    def get_user_profile(self) -> str:
        """获取用户个人信息"""
        try:
            payload = {
                "user_id": self.user.user_id,
                "username": self.user.username,
                "nickname": self.user.nickname,
                "email": self.user.email,
                "avatar_emoji": self.user.avatar_emoji,
                "is_logged_in": self.user.is_logged_in,
            }
            return json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @pyqtSlot(str, result=str)
    def update_user_profile(self, json_str: str) -> str:
        """更新用户个人信息"""
        try:
            data = json.loads(json_str)
            if "username" in data:
                self.user.username = data["username"].strip()
            if "nickname" in data:
                self.user.nickname = data["nickname"].strip()
            if "email" in data:
                self.user.email = data["email"].strip()
            if "avatar_emoji" in data:
                self.user.avatar_emoji = data["avatar_emoji"].strip()
            self.storage.save_user(self.user)
            return json.dumps({"ok": True, "user": self.user.to_dict()}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    @pyqtSlot(str, result=str)
    def user_login(self, json_str: str) -> str:
        """用户登录"""
        try:
            data = json.loads(json_str)
            username = data.get("username", "").strip()
            if not username:
                return json.dumps({"ok": False, "error": "用户名不能为空"}, ensure_ascii=False)
            self.user.username = username
            self.user.is_logged_in = True
            if not self.user.nickname:
                self.user.nickname = username
            self.storage.save_user(self.user)
            return json.dumps({"ok": True, "user": self.user.to_dict()}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    @pyqtSlot(result=str)
    def user_logout(self) -> str:
        """用户登出"""
        try:
            self.user.is_logged_in = False
            self.storage.save_user(self.user)
            return json.dumps({"ok": True}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    @pyqtSlot(result=str)
    def get_settings(self) -> str:
        """获取应用设置"""
        try:
            return json.dumps(self.settings.to_dict(), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @pyqtSlot(str, result=str)
    def update_settings(self, json_str: str) -> str:
        """更新应用设置"""
        try:
            data = json.loads(json_str)
            if "theme" in data:
                self.settings.theme = data["theme"]
            if "font_size" in data:
                self.settings.font_size = data["font_size"]
            if "budget_notifications" in data:
                self.settings.budget_notifications = bool(data["budget_notifications"])
            if "daily_reminders" in data:
                self.settings.daily_reminders = bool(data["daily_reminders"])
            if "expense_warnings" in data:
                self.settings.expense_warnings = bool(data["expense_warnings"])
            if "auto_backup" in data:
                self.settings.auto_backup = bool(data["auto_backup"])
            if "backup_frequency" in data:
                self.settings.backup_frequency = data["backup_frequency"]
            if "hide_amounts" in data:
                self.settings.hide_amounts = bool(data["hide_amounts"])
            if "require_password" in data:
                self.settings.require_password = bool(data["require_password"])
            self.storage.save_settings(self.settings)
            return json.dumps({"ok": True, "settings": self.settings.to_dict()}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)


class MoneyManagerApp(QMainWindow):
    """主窗口：加载 ui.html，并向其注入 backend 对象。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("小账精")
        # 放大一点默认窗口（你提了字体和整体偏小）
        self.resize(460, 900)

        # 计算 data 目录路径 & 初始化存储
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../src
        project_dir = os.path.dirname(src_dir)  # 上一级：包含 data 和 src
        data_dir = os.path.join(project_dir, "data")

        storage = StorageService(data_dir=data_dir)
        self.backend = Backend(storage)

        # WebEngine 视图
        self.web = QWebEngineView(self)

        # WebChannel，将 backend 暴露给 JS
        self.channel = QWebChannel(self.web.page())
        self.channel.registerObject("backend", self.backend)
        self.web.page().setWebChannel(self.channel)

        # 加载 HTML
        html_path = os.path.join(src_dir, "ui", "assets", "ui.html")
        self.web.setUrl(QUrl.fromLocalFile(html_path))

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web)
        self.setCentralWidget(container)
