from __future__ import annotations

from collections import Counter
from datetime import date
from typing import List

from src.models.record import Record

class Analysis:
    """Provide heuristic analysis and suggestions based on records."""
    def generate_suggestions(self, records: List[Record]) -> str:
        if not records:
            return (
                "当前还没有任何收支记录，无法进行分析。\n"
                "建议先记几笔日常收支，再使用「分析与建议」功能。"
            )

        expenses = [r for r in records if r.r_type == "expense"]
        incomes = [r for r in records if r.r_type == "income"]

        if not expenses:
            return (
                "当前还没有支出记录，暂时无法分析消费习惯。\n"
                "可以先记录一些日常开销，比如餐饮、出行等，"
                "然后再回来查看消费分析。"
            )

        # 基本统计
        total_expense = sum(r.amount for r in expenses)
        total_income = sum(r.amount for r in incomes) if incomes else 0.0
        balance = total_income - total_expense

        # 时间区间
        all_dates = [r.record_date for r in records if isinstance(r.record_date, date)]
        all_dates = sorted(set(all_dates))
        if all_dates:
            start_date = all_dates[0]
            end_date = all_dates[-1]
            days_span = (end_date - start_date).days + 1
        else:
            start_date = end_date = None
            days_span = 1

        avg_daily_expense = total_expense / days_span if days_span > 0 else total_expense

        # 分类分布
        category_counter = Counter(r.category for r in expenses if r.category)
        top_categories = category_counter.most_common(3)

        # 商家分布
        store_counter = Counter(r.store for r in expenses if r.store)
        top_stores = store_counter.most_common(3)

        # 单笔最大支出
        max_expense_record = max(expenses, key=lambda r: r.amount)

        lines: List[str] = []

        # 一、总体收支概况
        lines.append("一、总体收支概况")
        lines.append(f"- 统计支出共计：{total_expense:.2f} 元")
        if total_income:
            lines.append(f"- 统计收入共计：{total_income:.2f} 元")
            lines.append(f"- 期间净结余：{balance:.2f} 元")
        else:
            lines.append("- 暂未记录收入，仅统计支出。")

        if start_date and end_date:
            lines.append(
                f"- 统计区间：{start_date.isoformat()} 至 {end_date.isoformat()} "
                f"（约 {days_span} 天）"
            )
        lines.append(f"- 日均支出约：{avg_daily_expense:.2f} 元")

        # 二、支出结构分析
        lines.append("\n二、支出结构分析")
        if top_categories:
            lines.append("按支出金额排序的主要消费类别：")
            for name, amount in top_categories:
                ratio = amount / total_expense * 100 if total_expense > 0 else 0.0
                lines.append(
                    f"- {name or '未命名分类'}：{amount:.2f} 元 "
                    f"（约占总支出的 {ratio:.1f}%）"
                )
        else:
            lines.append(
                "暂未能统计出有效的分类信息，请检查记账时是否填写了「分类」字段。"
            )

        if top_stores:
            lines.append("消费较为集中的商家 / 场所：")
            for name, amount in top_stores:
                lines.append(f"- {name}: {amount:.2f} 元")
        else:
            lines.append(
                "尚未记录商家信息，如需更精细的分析建议在记账时填写「商家」字段。"
            )

        # 三、消费习惯与风险提示
        lines.append("\n三、消费习惯与风险提示")

        # 1）某一类消费是否过于集中
        if top_categories:
            top_name, top_amount = top_categories[0]
            top_ratio = top_amount / total_expense if total_expense > 0 else 0.0
            if top_ratio >= 0.5:
                lines.append(
                    f"- 当前消费高度集中在「{top_name}」类别，占比超过总支出的 50%。\n"
                    "  建议回顾这类支出的必要性，考虑设置更严格的预算上限，"
                    "避免非刚需消费持续挤压其他开销。"
                )
            elif top_ratio >= 0.3:
                lines.append(
                    f"- 「{top_name}」类别是目前最大的支出来源，占比约为 "
                    f"{top_ratio * 100:.0f}%。\n"
                    "  可以优先从这一类目入手做优化，例如寻找更划算的替代方案，"
                    "或减少冲动型消费。"
                )
            else:
                lines.append(
                    "- 各消费类别相对均衡，目前未出现某一类目支出极端集中的情况。"
                )

        # 2）整体收支是否平衡
        if total_income and balance < 0:
            lines.append(
                "- 在当前统计区间内，支出大于收入，收支为负。\n"
                "  建议适当减少可选消费（如娱乐、外出就餐），"
                "并考虑增加稳定收入来源，避免长期透支。"
            )
        elif total_income and balance > 0:
            lines.append(
                "- 当前整体处于结余状态，收支结构健康。\n"
                "  可以在保障储蓄的前提下，合理安排提升生活质量的支出，"
                "例如学习投资、健康管理等。"
            )
        else:
            lines.append(
                "- 尚未记录收入，暂无法判断整体收支是否平衡。\n"
                "  建议同时记录收入与支出，以便更全面地评估财务状况。"
            )

        # 3）单笔大额消费提示
        if max_expense_record.amount >= total_expense * 0.3:
            lines.append(
                f"- 单笔大额支出：{max_expense_record.record_date.isoformat()} "
                f"在「{max_expense_record.category}」消费了 "
                f"{max_expense_record.amount:.2f} 元，"
                "占总支出的比例较高。\n"
                "  建议回顾这笔支出的必要性，并在未来遇到类似金额的消费时，"
                "提前做预算和比价。"
            )

        # 4）碎片化消费提示：条数多、平均单笔金额低
        if len(expenses) >= 10:
            avg_per_expense = total_expense / len(expenses)
            if avg_per_expense < avg_daily_expense:
                lines.append(
                    "- 记录中存在较多小额消费，单笔金额偏低但次数较多。\n"
                    "  这类「碎片化消费」容易被忽视，建议定期回顾，"
                    "识别是否存在不必要的频繁小额支出。"
                )

        # 收尾
        lines.append(
            "\n以上分析基于当前已记录的数据以及简单的规则推断，"
            "仅作为理财参考建议。如需更精细的规划，可以结合真实预算、"
            "储蓄目标和投资计划进行综合考虑。"
        )

        return "\n".join(lines)
