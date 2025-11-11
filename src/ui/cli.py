"""Command line interface for the accounting application.

The :class:`CommandLineUI` class provides an interactive text
menu that allows users to manage their financial records,
categories, budgets, perform searches, view statistical
summaries and receive AI-based suggestions. The menu is
structured to be easy to navigate and each option delegates
the work to the appropriate controller or service. Input
validation is performed consistently using helper functions
from the :mod:`utils.validators` module. This interface
could serve as the basis for a more sophisticated UI in the
future; for example, it could be wrapped in a GUI framework or
exposed over a web API.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from src.controllers.record_controller import RecordController
from src.controllers.statistics_controller import StatisticsController
from src.controllers.search_controller import SearchController
from src.services.storage_service import StorageService
from src.services.report_generator import ReportGenerator
from src.services.ai_analysis import AIAnalysis
from src.utils.validators import parse_float, parse_int, parse_date
from src.models.record import Record


class CommandLineUI:
    """Provide an interactive command line menu to the user."""

    def __init__(self) -> None:
        # Initialise storage and controllers. The same storage is
        # shared across controllers so that changes made in one place
        # are visible in others. The record controller also holds
        # the budget.
        self.storage = StorageService(data_dir="data")
        self.record_controller = RecordController(self.storage)
        # Statistics and search controllers operate on the same
        # record list from the record controller to stay in sync.
        self.statistics_controller = StatisticsController(self.record_controller.records)
        self.search_controller = SearchController(self.record_controller.records)
        self.report_generator = ReportGenerator()
        self.ai_analysis = AIAnalysis()

    def run(self) -> None:
        """Enter the main command loop."""
        print("欢迎使用记账本系统！")
        while True:
            self._print_main_menu()
            choice = input("请选择功能：").strip()
            # Route the user's choice to the appropriate handler.
            if choice == "1":
                self._handle_add_record()
            elif choice == "2":
                self._handle_view_records()
            elif choice == "3":
                self._handle_edit_record()
            elif choice == "4":
                self._handle_delete_record()
            elif choice == "5":
                self._handle_add_category()
            elif choice == "6":
                self._handle_view_categories()
            elif choice == "7":
                self._handle_search_by_store()
            elif choice == "8":
                self._handle_search_by_category()
            elif choice == "9":
                self._handle_search_by_date_range()
            elif choice == "10":
                self._handle_summary()
            elif choice == "11":
                self._handle_category_report()
            elif choice == "12":
                self._handle_monthly_trend()
            elif choice == "13":
                self._handle_set_budget()
            elif choice == "14":
                self._handle_check_budget()
            elif choice == "15":
                self._handle_ai_analysis()
            elif choice == "0":
                print("谢谢使用，再见！")
                break
            else:
                print("无效选项，请重试。")

    # -- Menu printing -----------------------------------------------------
    def _print_main_menu(self) -> None:
        """Display the top-level menu options to the user."""
        print("\n====== 记账本系统菜单 ======")
        print("1. 新增收支记录")
        print("2. 查看所有记录")
        print("3. 编辑记录")
        print("4. 删除记录")
        print("5. 新增分类")
        print("6. 查看所有分类")
        print("7. 按商家查询")
        print("8. 按分类查询")
        print("9. 按日期区间查询")
        print("10. 查看汇总统计")
        print("11. 查看分类报表")
        print("12. 查看月份趋势")
        print("13. 设置预算")
        print("14. 检查预算状态")
        print("15. AI 分析与建议")
        print("0. 退出系统")
        print("============================")

    # -- Handler methods ---------------------------------------------------
    def _handle_add_record(self) -> None:
        """Prompt the user to input fields for a new record."""
        print("\n--- 新增收支记录 ---")
        amount = self._ask_float("金额：")
        r_type = self._ask_type()
        category = input("分类：").strip()
        date_str = self._ask_date("日期（YYYY-MM-DD）：")
        note = input("备注（可选）：").strip()
        store = input("商家或来源（可选）：").strip()
        # Convert date string to a date object. _ask_date validates format.
        record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        record = self.record_controller.create_record(
            amount=amount,
            r_type=r_type,
            category=category,
            record_date=record_date,
            note=note,
            store=store,
        )
        print(f"已新增记录，ID = {record.record_id}")

    def _handle_view_records(self) -> None:
        """Display all records in a human-readable format."""
        print("\n--- 所有记录 ---")
        records = self.record_controller.get_records()
        if not records:
            print("暂无记录。")
            return
        for rec in records:
            self._print_record(rec)

    def _handle_edit_record(self) -> None:
        """Allow the user to modify an existing record."""
        print("\n--- 编辑记录 ---")
        id_str = input("请输入要编辑的记录 ID：").strip()
        rec_id = parse_int(id_str)
        if rec_id is None:
            print("ID 必须是整数。")
            return
        record = self.record_controller.get_record(rec_id)
        if not record:
            print("未找到对应 ID 的记录。")
            return
        print("输入新的值，留空则保持不变：")
        amount_str = input(f"金额 ({record.amount}): ").strip()
        new_amount = parse_float(amount_str) if amount_str else None
        type_str = input(f"类型(1=收入,2=支出) ({'1' if record.r_type=='income' else '2'}): ").strip()
        new_type = None
        if type_str == "1":
            new_type = "income"
        elif type_str == "2":
            new_type = "expense"
        category_str = input(f"分类 ({record.category}): ").strip() or None
        date_input = input(f"日期 ({record.record_date.strftime('%Y-%m-%d')}): ").strip()
        new_date = parse_date(date_input) if date_input else None
        note_input = input(f"备注 ({record.note}): ").strip() or None
        store_input = input(f"商家 ({record.store}): ").strip() or None
        updates = {}
        if new_amount is not None:
            updates["amount"] = new_amount
        if new_type is not None:
            updates["r_type"] = new_type
        if category_str is not None:
            updates["category"] = category_str
        if new_date is not None:
            updates["record_date"] = new_date
        if note_input is not None:
            updates["note"] = note_input
        if store_input is not None:
            updates["store"] = store_input
        if not updates:
            print("未做任何修改。")
            return
        success = self.record_controller.update_record(rec_id, **updates)
        if success:
            print("修改成功。")
        else:
            print("修改失败。")

    def _handle_delete_record(self) -> None:
        """Prompt the user for an ID and delete the corresponding record."""
        print("\n--- 删除记录 ---")
        id_str = input("请输入要删除的记录 ID：").strip()
        rec_id = parse_int(id_str)
        if rec_id is None:
            print("ID 必须是整数。")
            return
        success = self.record_controller.delete_record(rec_id)
        if success:
            print("删除成功。")
        else:
            print("未找到对应 ID 的记录。")

    def _handle_add_category(self) -> None:
        """Allow the user to create a new category."""
        print("\n--- 新增分类 ---")
        name = input("分类名称：").strip()
        icon = input("图标（可选，可为空）：").strip()
        c_type = self._ask_type()
        cat = self.record_controller.add_category(name=name, icon=icon, c_type=c_type)
        print(f"已新增分类，ID = {cat.category_id}")

    def _handle_view_categories(self) -> None:
        """List all existing categories."""
        print("\n--- 所有分类 ---")
        categories = self.record_controller.get_categories()
        if not categories:
            print("暂无分类。")
            return
        for cat in categories:
            print(
                f"[ID {cat.category_id}] {cat.name} "
                f"({cat.c_type}) {cat.icon}"
            )

    def _handle_search_by_store(self) -> None:
        """Search records by store name."""
        store = input("请输入商家名称：").strip()
        results = self.search_controller.execute_search(store=store)
        self._display_search_results(results)

    def _handle_search_by_category(self) -> None:
        """Search records by category name."""
        category = input("请输入分类名称：").strip()
        results = self.search_controller.execute_search(category=category)
        self._display_search_results(results)

    def _handle_search_by_date_range(self) -> None:
        """Search records within a date range."""
        start_str = self._ask_date("起始日期（YYYY-MM-DD）：")
        end_str = self._ask_date("结束日期（YYYY-MM-DD）：")
        start = datetime.strptime(start_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_str, "%Y-%m-%d").date()
        results = self.search_controller.execute_search(start=start, end=end)
        self._display_search_results(results)

    def _handle_summary(self) -> None:
        """Display overall income, expense and balance summary."""
        print("\n--- 汇总统计 ---")
        summary = self.statistics_controller.get_summary()
        print(f"总收入：{summary['income']:.2f}")
        print(f"总支出：{summary['expense']:.2f}")
        print(f"结余：  {summary['balance']:.2f}")

    def _handle_category_report(self) -> None:
        """Display net amount per category."""
        print("\n--- 分类报表 ---")
        report = self.statistics_controller.get_category_stats()
        if not report:
            print("暂无数据。")
            return
        for category, total in report.items():
            print(f"{category}: {total:.2f}")

    def _handle_monthly_trend(self) -> None:
        """Show income, expense and balance by month."""
        print("\n--- 月份趋势 ---")
        trend = self.statistics_controller.get_time_based_stats()
        if not trend:
            print("暂无数据。")
            return
        for month, data in sorted(trend.items()):
            print(
                f"{month}: 收入 {data['income']:.2f}, "
                f"支出 {data['expense']:.2f}, "
                f"结余 {data['balance']:.2f}"
            )

    def _handle_set_budget(self) -> None:
        """Prompt the user to set a new monthly budget."""
        print("\n--- 设置预算 ---")
        amount = self._ask_float("请输入本月预算：")
        self.record_controller.set_budget(amount)
        print("预算设置成功。")

    def _handle_check_budget(self) -> None:
        """Display the current budget status message."""
        print("\n--- 预算状态 ---")
        message = self.record_controller.check_budget_status()
        print(message)

    def _handle_ai_analysis(self) -> None:
        """Perform AI analysis and show suggestions."""
        print("\n--- AI 分析与建议 ---")
        records = self.record_controller.get_records()
        suggestion = self.ai_analysis.generate_suggestions(records)
        print(suggestion)

    # -- Helper methods ----------------------------------------------------
    def _display_search_results(self, results) -> None:
        """Pretty-print a list of records returned from a search."""
        if not results:
            print("未找到符合条件的记录。")
            return
        for rec in results:
            self._print_record(rec)

    @staticmethod
    def _print_record(rec: Record) -> None:
        """Render a record as a single formatted line."""
        sign = '+' if rec.r_type == 'income' else '-'
        print(
            f"[ID {rec.record_id}] {rec.record_date.strftime('%Y-%m-%d')} "
            f"{rec.category} {sign}{rec.amount:.2f} "
            f"{rec.note} @ {rec.store}"
        )

    @staticmethod
    def _ask_float(prompt: str) -> float:
        """Repeatedly prompt the user for a valid floating point number."""
        while True:
            text = input(prompt).strip()
            value = parse_float(text)
            if value is None:
                print("请输入合法数字。")
            else:
                return value

    @staticmethod
    def _ask_int(prompt: str) -> int:
        """Repeatedly prompt the user for a valid integer."""
        while True:
            text = input(prompt).strip()
            value = parse_int(text)
            if value is None:
                print("请输入整数。")
            else:
                return value

    @staticmethod
    def _ask_date(prompt: str) -> str:
        """Repeatedly prompt the user for a valid ISO-formatted date."""
        while True:
            text = input(prompt).strip()
            if parse_date(text) is None:
                print("日期格式错误，请使用 YYYY-MM-DD。")
            else:
                return text

    @staticmethod
    def _ask_type() -> str:
        """Prompt for income or expense type."""
        while True:
            t_type = input("类型（1=收入, 2=支出）：").strip()
            if t_type == "1":
                return "income"
            if t_type == "2":
                return "expense"
            print("无效类型，请输入 1 或 2。")
