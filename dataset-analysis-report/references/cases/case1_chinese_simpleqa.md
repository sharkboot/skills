# 案例一：Chinese SimpleQA 数据集分析报告

## 数据集信息

- **名称**: Chinese SimpleQA
- **类型**: 大语言模型事实性评测基准
- **数据量**: 3000条
- **语言**: 中文
- **发布时间**: 2024年11月

## 分析过程

### Step 1: 探索数据集结构

通过Glob工具发现目录结构：
```
ChineseSimpleQA-master/
├── README.md / README_zh.md
├── 2411.07140v2.pdf (论文)
├── data/chinese_simpleqa.jsonl (数据文件)
├── judge/chinese_simpleqa_easy.py (评测脚本)
├── simpleqa_eval.py (评测框架)
└── sampler/ (采样器)
```

### Step 2: 分析数据内容

读取jsonl文件，解析JSON结构：
```json
{
  "id": "97e7f58a3b154facaa3a5c64d678c7bf",
  "primary_category": "中华文化",
  "secondary_category": "中医",
  "question": "伏兔穴所属的经脉是什么？",
  "answer": "足阳明胃经",
  "urls": ["https://...", "https://..."]
}
```

统计结果：
- 总数据量: 3000条
- 一级分类: 6个（中华文化、人文与社会科学、自然科学、工程技术与应用科学、生活艺术与文化、社会）
- 子主题: 99个
- 问题平均长度: 24.4字符
- 答案平均长度: 6.8字符

### Step 3: 提取论文关键信息

从README和PDF论文中提取：

**来源**: 阿里巴巴淘天集团算法技术-未来生活实验室团队，2024年11月发布于HuggingFace和arXiv

**目标**: 解决大语言模型幻觉问题，填补中文事实性评测空白

**数据集能力**:
- 事实性问答能力
- 中文知识理解与推理能力
- 知识边界识别能力

**评测指标** (论文Section 2.5):
- Correct (CO): 预测答案完全包含参考答案
- Not attempted (NA): 未包含参考答案但也不矛盾
- Incorrect (IN): 与参考答案相矛盾
- Correct given attempted (CGA): 尝试回答中的正确率
- F-score: CO与CGA的调和平均数

### Step 4: 分析评测代码

**模型调用**: 直接发送问题给模型获取回答

**评判提示词模板** (来自chinese_simpleqa_easy.py):
```
请根据给定问题、标准答案和模型预测的答案来评估模型的回答是否正确。
您的任务是将结果评定为：【正确】、【错误】或【未尝试】。

问题: {question}
正确答案: {target}
预测答案: {predicted_answer}

评定为以下之一：
A:【正确】
B:【错误】
C:【未尝试】
```

### Step 5: 撰写报告

按结构撰写报告，标注来源：
- 数据集描述 → 论文Table 2
- 能力体系 → 论文Section 2.5
- 场景体系 → 论文Figure 1
- 提示词模板 → 论文 + 项目代码

## 关键文件

| 文件 | 用途 |
|------|------|
| README.md | 基本信息介绍 |
| 2411.07140v2.pdf | 论文全文 |
| data/chinese_simpleqa.jsonl | 数据集 |
| judge/chinese_simpleqa_easy.py | 评测脚本+提示词模板 |
| simpleqa_eval.py | 评测框架+GRADER_TEMPLATE |

## 提取的关键信息

1. **来源**: 淘天集团未来生活实验室，arXiv:2411.07140
2. **目标**: 评估LLM中文事实性问答能力
3. **数据量**: 3000条，6大类99子主题
4. **能力**: 事实性问答、中文知识理解、知识边界探测
5. **场景**: 中华文化、人文社科、自然科学等6大领域
6. **评测**: LLM-as-a-Judge，使用GPT-4o评判
7. **指标**: CO/NA/IN/CGA/F-score