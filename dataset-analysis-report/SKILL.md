---
name: dataset-analysis-report
description: 撰写数据集分析报告。用于分析论文、代码和数据，撰写结构化的数据集评测报告，包括数据集来源、目标、应用场景、数据描述、能力体系、场景体系、测评方法等章节。适用于评测集、基准测试数据集的分析场景。
---

# 数据集分析报告撰写 Skill

本skill提供撰写数据集分析报告的完整工作流程，适用于分析评测集、基准测试数据集等。

## 适用场景

- 分析大语言模型评测数据集（如SimpleQA、C-Eval、CMMLU等）
- 撰写技术报告或论文背景章节
- 评估数据集的质量和适用性

## 工作流程

### Step 1: 探索数据集结构

1. 查找目录中的README文件（README.md, README_zh.md）
2. 定位数据文件（.jsonl, .csv, .json等）
3. 查找论文PDF文件
4. 分析代码文件结构

**关键工具**: Glob, Read, Bash

### Step 2: 分析数据内容

使用通用脚本自动分析JSONL数据集：

```bash
python scripts/analyze_dataset.py /path/to/dataset.jsonl [-o output_report.md] [-n top_n_categories]
```

脚本会自动完成：
1. 读取数据文件，解析JSON结构
2. 统计字段分布、类别数量、数据量
3. 分析数据长度特征（问题/答案长度）
4. 生成结构化的Markdown分析报告

**脚本功能**:
- 自动检测字段结构
- 分类分布统计（一级/二级分类）
- 问题/答案长度统计
- 示例数据展示
- 自动输出Markdown格式报告

### Step 3: 提取论文关键信息

1. 从README和论文中提取数据集基本信息
   - 来源（发布机构、时间、平台）
   - 目标（解决什么问题）
   - 应用场景
   - 数据量与分类
2. 提取评测方法（评测指标、提示词模板）

**关键工具**: Read (PDF), Python PDF解析

### Step 4: 分析评测代码

1. 查看评测脚本中的提示词模板
2. 分析评判逻辑和评分方法
3. 理解模型调用流程

**关键工具**: Read (代码文件), Grep

### Step 5: 撰写报告

按照以下结构撰写：

```
1. 简介
   1.1 来源（前置文字描述 + 表格信息）
   1.2 目标（前置文字描述 + 列表）
   1.3 应用场景（前置文字描述 + 列表）
   1.4 数据集描述（前置文字描述 + 表格 + 代码块示例）

2. 数据集能力体系
   - 评估模型的哪些通用能力
   - 评测指标及说明

3. 数据集场景体系
   - 数据分类体系
   - 来源（论文/数据集）

4. 测评
   4.1 获取模型回复（提示词模板，如果没有则为空）
   4.2 测评方法（方法类型、评测指标、评分规则、提示词模板）
```

> **提示**：可参考 [templates/dataset_report_template.md](templates/dataset_report_template.md) 模板文件，确保报告结构完整。

## 工具清单

| 工具 | 位置 | 用途 |
|------|------|------|
| analyze_dataset.py | scripts/ | 通用JSONL数据集分析脚本 |
| dataset_report_template.md | templates/ | 数据集分析报告模板 |
| case1_chinese_simpleqa.md | references/cases/ | 案例一：Chinese SimpleQA分析过程 |
| case1_dataset_analysis_report.md | references/cases/ | 案例一：Chinese SimpleQA完整报告 |
| case2_alignbench_analysis_process.md | references/cases/ | 案例二：AlignBench分析过程 |
| case2_alignbench_analysis_report.md | references/cases/ | 案例二：AlignBench完整报告 |

## 输出格式

报告应包含：
- 清晰的章节结构
- 每章节有前置文字描述，再跟表格/列表
- 数据统计信息（数据量、分布、长度等）
- 字段说明
- 提示词模板（标注来源）
- 评测方法说明

## 注意事项

- 提示词模板优先参考论文，其次参考项目代码
- 数据统计放在1.4数据集描述中
- 场景体系只列分类，不含具体数量
- 能力体系指模型的通用能力，不是数据分类
- 引用来源时标注清楚（论文/代码/数据集）
- 撰写报告时可参考templates/中的模板文件
- 4.1获取模型回复：如果没有专门提示词模板，填写"（无专门的提示词模板，直接将question发送给模型获取回答）"
- 4.2测评方法：说明方法类型（评估器/提示词评估），并附上提示词模板

---

### 1.4 数据集描述 - 案例参考

> 以下为案例数据格式，供参考：

**Chinese SimpleQA 单条数据示例：**

```json
{
  "id": "simpleqa_0001",
  "primary_category": "科技",
  "secondary_category": "互联网",
  "question": "微信是在哪一年发布的？",
  "answer": "2011年",
  "urls": ["https://zh.wikipedia.org/wiki/微信"]
}
```

**AlignBench 单条数据示例：**

```json
{
  "question_id": "align_001",
  "category": "基本任务",
  "subcategory": "常识知识",
  "question": "如果明天下雨，我将不带伞。如果后天晴天，我将去跑步。后天会跑步吗？",
  "reference": "后天会跑步。因为后天是晴天，而晴天对应去跑步的条件。",
  "evidences": []
}
```

> 更多案例详情见 [references/cases/](references/cases/) 目录