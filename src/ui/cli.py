"""Command line interface for the accounting application."""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List

from src.controllers.record_controller import RecordController
from src.controllers.statistics_controller import StatisticsController
from src.controllers.search_controller import SearchController
from src.services.storage_service import StorageService
from src.services.report_generator import ReportGenerator
from src.services.analysis import Analysis
from src.utils.validators import parse_float, parse_int, parse_date
from src.models.record import Record


class CommandLineUI:
    """Interactive command line interface for the accounting application."""

    def __init__(self) -> None:
        self.storage = StorageService(data_dir="data")
        self.record_controller = RecordController(self.storage)
        self.statistics_controller = StatisticsController(self.record_controller.records)
        self.search_controller = SearchController(self.record_controller.records)
        self.report_generator = ReportGenerator()
        self.analysis = Analysis()

    # ==================================================================
    # 顶层主循环
    # ==================================================================
    def run(self) -> None:
        """Enter the main command loop with five top-level navigations."""
        print("欢迎使用小账精系统！")
        while True:
            self._print_main_menu()
            choice = input("请选择导航：").strip()
            if choice == "1":
                self._nav_home()
            elif choice == "2":
                self._nav_record()
            elif choice == "3":
                self._nav_statistics()
            elif choice == "4":
                self._nav_search()
            elif choice == "5":
                self._nav_profile()
            elif choice == "0":
                print("谢谢使用，再见！")
                break
            else:
                print("无效选项，请重试。")

    # ==================================================================
    # 主导航菜单
    # ==================================================================
    @staticmethod
    def _print_main_menu() -> None:
        """Display the top-level navigation menu."""
        print("\n====== 小账精 · 主导航 ======")
        print("1. 首页（概览 / 预算 / 最近记录）")
        print("2. 记账（新增 / 查看 / 编辑 / 删除 / 分类管理）")
        print("3. 统计（总览 / 分类报表 / 月度趋势 / 数据分析）")
        print("4. 搜索（商家 / 分类 / 日期区间）")
        print("5. 我的（系统信息）")
        print("0. 退出系统")
        print("================================")

    # ------------------------------------------------------------------
    # 导航 1：首页
    # ------------------------------------------------------------------
    def _nav_home(self) -> None:
        """Homepage: summary, budget status, recent records."""
        while True:
            print("\n[首页]")
            print("1. 查看整体收支摘要")
            print("2. 设置预算")
            print("3. 查看当前预算状态")
            print("4. 查看最近 N 条记录")
            print("0. 返回主导航")
            choice = input("请选择：").strip()
            if choice == "1":
                self._handle_summary()
                self._pause()
            elif choice == "2":
                self._handle_set_budget()
                self._pause()
            elif choice == "3":
                self._handle_check_budget()
                self._pause()
            elif choice == "4":
                self._handle_view_recent_records()
                self._pause()
            elif choice == "0":
                break
            else:
                print("无效选项，请重试。")

    # ------------------------------------------------------------------
    # 导航 2：记账（记录 + 分类）
    # ------------------------------------------------------------------
    def _nav_record(self) -> None:
        """Record navigation: CRUD of records and category management."""
        while True:
            print("\n[记账]")
            print("1. 新增收支记录")
            print("2. 查看所有记录")
            print("3. 编辑记录")
            print("4. 删除记录")
            print("5. 新增分类")
            print("6. 查看所有分类")
            print("0. 返回主导航")
            choice = input("请选择：").strip()
            if choice == "1":
                self._handle_add_record()
                self._pause()
            elif choice == "2":
                self._handle_view_records()
                self._pause()
            elif choice == "3":
                self._handle_edit_record()
                self._pause()
            elif choice == "4":
                self._handle_delete_record()
                self._pause()
            elif choice == "5":
                self._handle_add_category()
                self._pause()
            elif choice == "6":
                self._handle_view_categories()
                self._pause()
            elif choice == "0":
                break
            else:
                print("无效选项，请重试。")

    # ------------------------------------------------------------------
    # 导航 3：统计（总览 / 分类 / 趋势 / 分析）
    # ------------------------------------------------------------------
    def _nav_statistics(self) -> None:
        """Statistics navigation: summary, category stats, trends, analysis."""
        while True:
            print("\n[统计]")
            print("1. 查看总收入 / 总支出 / 结余")
            print("2. 查看分类报表")
            print("3. 查看月份趋势")
            print("4. 分析与建议")
            print("0. 返回主导航")
            choice = input("请选择：").strip()
            if choice == "1":
                self._handle_summary()
                self._pause()
            elif choice == "2":
                self._handle_category_report()
                self._pause()
            elif choice == "3":
                self._handle_monthly_trend()
                self._pause()
            elif choice == "4":
                self._handle_analysis()
                self._pause()
            elif choice == "0":
                break
            else:
                print("无效选项，请重试。")

    # ------------------------------------------------------------------
    # 导航 4：搜索
    # ------------------------------------------------------------------
    def _nav_search(self) -> None:
        """Search navigation: by store, category or date range."""
        while True:
            print("\n[搜索]")
            print("1. 按商家查询")
            print("2. 按分类查询")
            print("3. 按日期区间查询")
            print("0. 返回主导航")
            choice = input("请选择：").strip()
            if choice == "1":
                self._handle_search_by_store()
                self._pause()
            elif choice == "2":
                self._handle_search_by_category()
                self._pause()
            elif choice == "3":
                self._handle_search_by_date_range()
                self._pause()
            elif choice == "0":
                break
            else:
                print("无效选项，请重试。")

    # ------------------------------------------------------------------
    # 导航 5：我的（目前作为系统信息占位）
    # ------------------------------------------------------------------
    def _nav_profile(self) -> None:
        """Profile navigation: show basic app info and future extensions."""
        print("\n[我的]")
        print("当前为命令行原型版本。")
        print("· 支持：记账、分类管理、统计分析、预算、搜索、分析建议等核心功能。")
        print("· 数据存储位置：项目根目录下 data/ 目录中的 JSON 文件。")
        print("· 后续图形化 UI 将在此处扩展个人资料、主题设置、数据同步等功能。")
        self._pause()


    def _handle_add_record(self) -> None:
        """Prompt the user to input fields for a new record."""
        print("\n--- 新增收支记录 ---")
        amount = self._ask_float("金额：")
        r_type = self._ask_type()
        category = input("分类：").strip()
        date_str = self._ask_date("日期（YYYY-MM-DD）：")
        note = input("备注（可选）：").strip()
        store = input("商家或来源（可选）：").strip()
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
        if record.r_type == "expense":
            try:
                level, warn_text = self.record_controller.get_budget_status_detail()
            except AttributeError:
                level, warn_text = "unknown", ""
            if level in ("warning", "over"):
                print("\n*** 预算提醒 ***")
                print(warn_text)


    def _handle_view_records(self) -> None:
        """Display all records in a human-readable format."""
        print("\n--- 所有记录 ---")
        records = self.record_controller.get_records()
        if not records:
            print("暂无记录。")
            return
        for rec in records:
            self._print_record(rec)

    def _handle_view_recent_records(self, limit: int = 5) -> None:
        """Display the most recent N records."""
        print(f"\n--- 最近 {limit} 条记录 ---")
        records = self.record_controller.get_records()
        if not records:
            print("暂无记录。")
            return
        # 假设记录列表按时间 / ID 递增，这里取末尾 N 条
        recent = records[-limit:]
        for rec in recent:
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
        type_str = input(
            f"类型(1=收入,2=支出) ({'1' if record.r_type=='income' else '2'}): "
        ).strip()
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
        print("\n--- 按商家查询 ---")
        store = input("请输入商家名称：").strip()
        results = self.search_controller.execute_search(store=store)
        self._display_search_results(results)

    def _handle_search_by_category(self) -> None:
        """Search records by category name."""
        print("\n--- 按分类查询 ---")
        category = input("请输入分类名称：").strip()
        results = self.search_controller.execute_search(category=category)
        self._display_search_results(results)

    def _handle_search_by_date_range(self) -> None:
        """Search records within a date range."""
        print("\n--- 按日期区间查询 ---")
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

    def _handle_analysis(self) -> None:
        """Perform analysis and show suggestions."""
        print("\n--- 分析与建议 ---")
        records = self.record_controller.get_records()
        suggestion = self.analysis.generate_suggestions(records)
        print(suggestion)

    # ==================================================================
    # Helper methods
    # ==================================================================
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

    @staticmethod
    def _pause() -> None:
        """Pause until the user presses Enter."""
        input("\n按回车键继续...")
