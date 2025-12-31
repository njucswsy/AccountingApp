from datetime import date
from typing import List, Optional
from typing import Tuple


from src.models.record import Record
from src.models.category import Category
from src.models.budget import Budget
from src.services.storage_service import StorageService


class RecordController:
    """Handle record and category management tasks."""

    def __init__(self, storage: StorageService, budget: Optional[Budget] = None) -> None:
        self.storage = storage
        self.records: List[Record] = storage.load_records()
        self.categories: List[Category] = storage.load_categories()
        # If a budget is provided, use it; otherwise try loading from storage
        self.budget = budget or storage.load_budget() or Budget(monthly_goal=0.0)

    # -- Record operations -------------------------------------------------
    def _get_next_record_id(self) -> int:
        """Compute the next available record ID."""
        if not self.records:
            return 1
        return max(r.record_id for r in self.records) + 1

    def create_record(
        self,
        amount: float,
        r_type: str,
        category: str,
        record_date: date,
        note: str = "",
        store: str = "",
    ) -> Record:
        new_id = self._get_next_record_id()
        record = Record(
            record_id=new_id,
            amount=amount,
            r_type=r_type,
            category=category,
            note=note,
            record_date=record_date,
            store=store,
        )
        self.records.append(record)
        self.storage.save_records(self.records)
        # Update budget spending if this is an expense and for the current month
        current_month = date.today().strftime("%Y-%m")
        if r_type == "expense" and record_date.strftime("%Y-%m") == current_month:
            self.budget.add_spending(amount)
            self.storage.save_budget(self.budget)
        return record

    def update_record(self, record_id: int, **kwargs) -> bool:
        record = self.get_record(record_id)
        if not record:
            return False
        for key, value in kwargs.items():
            if hasattr(record, key):
                # Cast date strings to date objects if necessary
                #if key == "record_date" and isinstance(value, str):
                #    value = Record.parse_date(value)
                if key == "record_date" and isinstance(value, str):
                    try:
                        value = Record.parse_date(value)
                    except ValueError:
                        # 非法日期字符串：不修改记录，返回失败
                        return False
                setattr(record, key, value)
        self.storage.save_records(self.records)
        return True

    def delete_record(self, record_id: int) -> bool:
        """Remove a record from the list and persist the change."""
        for i, rec in enumerate(self.records):
            if rec.record_id == record_id:
                # Adjust budget if this record is an expense
                if rec.r_type == "expense":
                    self.budget.current_spending = max(
                        0.0, self.budget.current_spending - rec.amount
                    )
                    self.storage.save_budget(self.budget)
                del self.records[i]
                self.storage.save_records(self.records)
                return True
        return False

    def get_record(self, record_id: int) -> Optional[Record]:
        """Return the record with the given ID or None."""
        for rec in self.records:
            if rec.record_id == record_id:
                return rec
        return None

    def get_records(self) -> List[Record]:
        """Return a copy of the current list of records."""
        return list(self.records)

    # -- Category operations -----------------------------------------------
    def _get_next_category_id(self) -> int:
        """Compute the next available category ID."""
        if not self.categories:
            return 1
        return max(c.category_id for c in self.categories) + 1

    def add_category(self, name: str, icon: str, c_type: str) -> Category:
        """Create and persist a new category."""
        new_id = self._get_next_category_id()
        category = Category(category_id=new_id, name=name, icon=icon, c_type=c_type)
        self.categories.append(category)
        self.storage.save_categories(self.categories)
        return category

    def edit_category(self, category_id: int, **kwargs) -> bool:
        """Modify attributes of a category if it exists."""
        for cat in self.categories:
            if cat.category_id == category_id:
                for key, value in kwargs.items():
                    if hasattr(cat, key):
                        setattr(cat, key, value)
                self.storage.save_categories(self.categories)
                return True
        return False

    def delete_category(self, category_id: int) -> bool:
        """Remove a category from the list and persist the change."""
        for i, cat in enumerate(self.categories):
            if cat.category_id == category_id:
                del self.categories[i]
                self.storage.save_categories(self.categories)
                return True
        return False

    def get_categories(self) -> List[Category]:
        """Return a copy of the current list of categories."""
        return list(self.categories)

    # -- Budget operations -------------------------------------------------
    def set_budget(self, amount: float) -> None:
        """Set a new monthly budget goal for the current month."""
        current_month = date.today().strftime("%Y-%m")
        if self.budget.month != current_month:
            # If the budget is for a different month, reset it
            self.budget = Budget(monthly_goal=amount, month=current_month)
        else:
            # Update the budget for the current month
            self.budget.set_budget(amount)
        self.storage.save_budget(self.budget)

    def get_budget_status_detail(self) -> Tuple[str, str]:
        """返回当前月份预算状态的等级和中文说明。

        level 取值：
        - "no_budget": 未设置预算
        - "normal": 预算宽裕（<50%）
        - "tight": 预算使用过半（50%~80%）
        - "warning": 接近上限（80%~100%）
        - "over": 已超出预算
        """
        budget = getattr(self, "budget", None)
        if budget is None:
            msg = (
                "当前尚未设置本月预算。\n"
                "你可以在「首页 → 设置 / 修改本月预算」中设置，例如 2000 元，"
                "用于控制本月整体支出。"
            )
            return "no_budget", msg

        limit = getattr(budget, "monthly_goal", None)
        if not limit or limit <= 0:
            msg = (
                "当前预算数值无效，请重新设置一个大于 0 的本月预算。\n"
                "例如设置为 2000 或 3000 元。"
            )
            return "no_budget", msg

        today = date.today()
        expenses_this_month = [
            r for r in self.records
            if r.r_type == "expense"
            and hasattr(r, "record_date")
            and isinstance(r.record_date, date)
            and r.record_date.year == today.year
            and r.record_date.month == today.month
        ]

        spent = sum(r.amount for r in expenses_this_month)
        ratio = spent / limit if limit > 0 else 0.0
        remaining = limit - spent

        if ratio < 0.5:
            level = "normal"
            msg = (
                f"本月预算：{limit:.2f} 元，目前已支出：{spent:.2f} 元，"
                f"约占预算的 {ratio * 100:.1f}%。\n"
                "整体比较宽裕，可以按计划正常消费，但仍建议预留一部分结余。"
            )
        elif ratio < 0.8:
            level = "tight"
            msg = (
                f"本月预算：{limit:.2f} 元，目前已支出：{spent:.2f} 元，"
                f"约占预算的 {ratio * 100:.1f}%。\n"
                "预算使用已经过半，建议适当关注后续支出节奏，"
                "将大额非刚需消费往后排一排。"
            )
        elif ratio < 1.0:
            level = "warning"
            msg = (
                f"本月预算：{limit:.2f} 元，目前已支出：{spent:.2f} 元，"
                f"约占预算的 {ratio * 100:.1f}%，剩余约 {remaining:.2f} 元。\n"
                "已经接近本月预算上限，建议暂停不必要的消费，"
                "避免轻易超过预算。"
            )
        else:
            level = "over"
            over_amount = spent - limit
            msg = (
                f"本月预算：{limit:.2f} 元，目前已支出：{spent:.2f} 元，"
                f"已经超出预算 {over_amount:.2f} 元。\n"
                "主人主人！！！再乱花钱月底要吃土啦！！！"
                "建议尽快复盘本月的大额支出，暂停非刚需消费，"
                "并在下个月重新评估一个更合理的预算。"
            )

        return level, msg

    def check_budget_status(self) -> str:
        """返回中文预算提示文本。"""
        _, msg = self.get_budget_status_detail()
        return msg