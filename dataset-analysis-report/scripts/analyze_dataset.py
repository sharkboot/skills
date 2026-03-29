#!/usr/bin/env python
"""
通用数据集分析脚本
支持JSONL格式的问答数据集自动分析

功能：
- 自动读取JSONL文件
- 解析字段结构
- 统计数据量
- 分类分布统计
- 问题/答案长度统计
- 输出格式化的分析报告
"""

import os
import json
import argparse
from collections import Counter
from pathlib import Path

def analyze_jsonl_dataset(file_path: str, output_file: str = None, top_n: int = 20):
    """
    分析JSONL格式的问答数据集

    Args:
        file_path: JSONL文件路径
        output_file: 输出报告文件路径（可选）
        top_n: 显示前N个最常见的分类
    """
    print(f"🔍 开始分析数据集: {file_path}")

    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None

    print(f"📊 总数据量: {len(lines)} 条")

    # 解析数据
    data = []
    invalid_lines = 0
    for i, line in enumerate(lines):
        try:
            data.append(json.loads(line.strip()))
        except Exception as e:
            invalid_lines += 1
            if invalid_lines < 5:  # 只显示前5个错误
                print(f"⚠️  第{i+1}行解析失败: {e}")

    if invalid_lines > 0:
        print(f"⚠️  共 {invalid_lines} 行解析失败")

    if not data:
        print("❌ 没有有效的数据")
        return None

    # 分析字段结构
    print("\n📋 字段结构分析:")
    first_sample = data[0]
    all_fields = list(first_sample.keys())
    print(f"所有字段: {', '.join(all_fields)}")

    # 检查常见字段
    common_fields = {
        'id': '唯一标识',
        'question': '问题',
        'answer': '参考答案',
        'primary_category': '一级分类',
        'secondary_category': '二级分类',
        'category': '分类',
        'label': '标签',
        'urls': '参考来源',
        'context': '上下文'
    }

    for field, desc in common_fields.items():
        if field in first_sample:
            print(f"  ✅ {field}: {desc} (示例: {repr(first_sample[field])[:50]})")
        else:
            print(f"  ❌ {field}: 不存在")

    # 字段类型检查
    print("\n🔍 字段类型检查:")
    for field in all_fields:
        sample_val = first_sample[field]
        field_type = type(sample_val).__name__
        print(f"  {field}: {field_type}")

    # 分类分布统计
    print("\n🏷️  分类分布统计:")

    # 统计一级分类
    if 'primary_category' in all_fields:
        primary_cats = Counter([d['primary_category'] for d in data if 'primary_category' in d])
        print(f"\n一级分类分布（共{len(primary_cats)}类）:")
        for cat, count in primary_cats.most_common():
            print(f"  {cat}: {count} 条 ({count/len(data)*100:.1f}%)")

    # 统计二级分类
    if 'secondary_category' in all_fields:
        secondary_cats = Counter([d['secondary_category'] for d in data if 'secondary_category' in d])
        print(f"\n二级分类分布（共{len(secondary_cats)}类，显示前{top_n}个）:")
        for cat, count in secondary_cats.most_common(top_n):
            print(f"  {cat}: {count} 条")

    # 普通分类
    if 'category' in all_fields and 'primary_category' not in all_fields:
        cats = Counter([d['category'] for d in data if 'category' in d])
        print(f"\n分类分布（共{len(cats)}类）:")
        for cat, count in cats.most_common():
            print(f"  {cat}: {count} 条")

    # 长度统计
    print("\n📏 长度统计:")

    if 'question' in all_fields:
        question_lens = [len(str(d.get('question', ''))) for d in data]
        avg_q = sum(question_lens) / len(question_lens)
        max_q = max(question_lens)
        min_q = min(question_lens)
        print(f"问题长度:")
        print(f"  平均: {avg_q:.1f} 字符")
        print(f"  最长: {max_q} 字符")
        print(f"  最短: {min_q} 字符")

    if 'answer' in all_fields:
        answer_lens = [len(str(d.get('answer', ''))) for d in data]
        avg_a = sum(answer_lens) / len(answer_lens)
        max_a = max(answer_lens)
        min_a = min(answer_lens)
        print(f"答案长度:")
        print(f"  平均: {avg_a:.1f} 字符")
        print(f"  最长: {max_a} 字符")
        print(f"  最短: {min_a} 字符")

    # 示例数据展示
    print("\n📝 示例数据（前3条）:")
    for i, sample in enumerate(data[:3]):
        print(f"\n--- 第{i+1}条 ---")
        for field in all_fields:
            value = sample.get(field, '')
            if isinstance(value, list) and len(value) > 2:
                value = f"[列表，共{len(value)}项]"
            elif isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"  {field}: {repr(value)}")

    # 生成报告
    report = f"""# 数据集分析报告
## 基本信息
- 文件路径: {os.path.abspath(file_path)}
- 总数据量: {len(lines)} 条
- 有效数据: {len(data)} 条
- 无效数据: {invalid_lines} 条

## 字段结构
| 字段名 | 类型 | 存在 | 示例 |
|--------|------|------|------|
"""

    for field in all_fields:
        sample_val = first_sample[field]
        field_type = type(sample_val).__name__
        sample_str = repr(sample_val)[:50]
        report += f"| {field} | {field_type} | ✅ | {sample_str} |\n"

    # 分类统计
    report += "\n## 分类统计\n"

    if 'primary_category' in all_fields:
        report += f"\n### 一级分类（共{len(primary_cats)}类）\n"
        report += "| 分类 | 数量 | 占比 |\n"
        report += "|------|------|------|\n"
        for cat, count in primary_cats.most_common():
            pct = count / len(data) * 100
            report += f"| {cat} | {count} | {pct:.1f}% |\n"

    if 'secondary_category' in all_fields:
        report += f"\n### 二级分类（共{len(secondary_cats)}类，前{top_n}个）\n"
        report += "| 子分类 | 数量 |\n"
        report += "|--------|------|\n"
        for cat, count in secondary_cats.most_common(top_n):
            report += f"| {cat} | {count} |\n"

    # 长度统计
    report += "\n## 长度统计\n"
    if 'question' in all_fields:
        report += f"- 问题长度: 平均{avg_q:.1f}字符, 最长{max_q}字符, 最短{min_q}字符\n"
    if 'answer' in all_fields:
        report += f"- 答案长度: 平均{avg_a:.1f}字符, 最长{max_a}字符, 最短{min_a}字符\n"

    # 示例数据
    report += "\n## 示例数据\n"
    for i, sample in enumerate(data[:3]):
        report += f"\n### 第{i+1}条\n"
        report += "```json\n"
        report += json.dumps(sample, ensure_ascii=False, indent=2)
        report += "\n```\n"

    # 保存报告
    if output_file is None:
        # 自动生成输出文件名
        base_name = Path(file_path).stem
        output_file = f"{base_name}_analysis_report.md"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ 分析报告已保存到: {output_file}")
    except Exception as e:
        print(f"\n❌ 保存报告失败: {e}")

    return report

def main():
    parser = argparse.ArgumentParser(description='通用JSONL数据集分析工具')
    parser.add_argument('file', help='JSONL数据集文件路径')
    parser.add_argument('-o', '--output', help='输出报告文件路径（可选）')
    parser.add_argument('-n', '--top-n', type=int, default=20, help='显示前N个最常见的二级分类')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        return

    analyze_jsonl_dataset(args.file, args.output, args.top_n)

if __name__ == "__main__":
    main()
