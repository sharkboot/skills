---
name: dataset-analysis-report
description: 撰写数据集分析报告。用于分析论文、代码和数据，撰写结构化的数据集评测报告，包括数据集来源、目标、应用场景、数据描述、能力体系、场景体系、测评方法等章节。适用于评测集、基准测试数据集的分析场景。
---

# 数据集分析报告撰写 Skill

> **使用建议**：在进行新数据集分析前，建议先阅读 [references/cases/](references/cases/) 中的案例，了解分析报告的结构和内容格式。

本skill提供撰写数据集分析报告的完整工作流程，适用于分析评测集、基准测试数据集等。

## 适用场景

- 分析大语言模型评测数据集（如SimpleQA、C-Eval、CMMLU等）
- 撰写技术报告或论文背景章节
- 评估数据集的质量和适用性

## 工作流程

### Step 0: 阅读案例参考（推荐）

在开始分析新数据集前，建议先阅读已有的案例了解分析报告的结构和格式：
- [case1_dataset_analysis_report.md](references/cases/case1_dataset_analysis_report.md) - Chinese SimpleQA分析报告
- [case2_alignbench_analysis_report.md](references/cases/case2_alignbench_analysis_report.md) - AlignBench分析报告

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
   1.1 来源
   1.2 目标
   1.3 应用场景
   1.4 数据集描述（数据量、字段结构、长度统计）

2. 数据集能力体系
   - 评估模型的哪些通用能力
   - 评测指标及说明

3. 数据集场景体系
   - 数据分类体系
   - 来源（论文/数据集）

4. 测评
   4.1 测评数据介绍（字段说明、提示词模板）
   4.2 测评方法介绍（评判逻辑、评分方法）
```

## 工具清单

| 工具 | 位置 | 用途 |
|------|------|------|
| analyze_dataset.py | scripts/ | 通用JSONL数据集分析脚本 |
| cases/case1_chinese_simpleqa.md | references/ | 案例一：Chinese SimpleQA分析过程参考 |
| cases/case1_dataset_analysis_report.md | references/ | 案例一：Chinese SimpleQA完整分析报告 |
| cases/case2_alignbench_analysis_report.md | references/ | 案例二：AlignBench完整分析报告 |
| cases/case2_alignbench_analysis_process.md | references/ | 案例二：AlignBench分析过程参考 |

## 输出格式

报告应包含：
- 清晰的章节结构
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