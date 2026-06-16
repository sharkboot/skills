# Agent Trajectory Optimizer 使用指南

## 快速开始

### 1. 基本分析

```bash
python scripts/analyze_trajectory.py --input your_trajectory.json --output report.md
```

### 2. 使用示例轨迹测试

```bash
python scripts/analyze_trajectory.py --input references/sample_trajectory.json --output test_report.md
```

### 3. 在Hermes中使用

```python
# 加载skill
hermes skill load agent-trajectory-optimizer

# 分析轨迹
hermes analyze trajectory --input your_trajectory.json
```

## 支持的轨迹格式

### JSON格式 (推荐)
```json
{
  "trajectory": [
    {
      "step_id": 1,
      "tool_name": "web_search",
      "input": {"query": "search term"},
      "output": {"results": [...]},
      "tokens": 150,
      "latency_ms": 1200,
      "status": "success"
    }
  ]
}
```

### CSV格式
```csv
step_id,tool_name,input,output,timestamp,tokens,latency_ms,status
1,web_search,"query: search","results: [...]",2026-06-16T10:30:00Z,150,1200,success
```

### 文本日志格式
```
[2026-06-16 10:30:00] STEP 1: web_search(input={"query": "search"}) -> 150 tokens, 1200ms
```

## 分析指标

### 核心指标
- **总步骤数**: 轨迹中的总操作数
- **冗余率**: 冗余步骤占总步骤的比例
- **循环数**: 检测到的执行循环数量
- **重复调用**: 相同工具相同输入的重复调用

### Token指标
- **总token使用**: 整个轨迹的token消耗
- **平均每步骤token**: 每个步骤的平均token使用

### 时间指标
- **总延迟**: 所有步骤的累计延迟
- **平均每步骤延迟**: 每个步骤的平均执行时间

## 优化建议类型

### 高优先级
1. **循环检测**: 发现执行循环，建议实现循环打破逻辑
2. **重复调用**: 发现重复工具调用，建议实现缓存或条件执行

### 中优先级
3. **冗余率高**: 建议重构任务分解和添加状态管理
4. **token效率低**: 建议优化提示词和减少上下文大小
5. **错误率高**: 建议添加验证和错误恢复

### 低优先级
6. **工具多样性低**: 考虑工具专业化

## 输出报告

分析完成后会生成包含以下部分的报告：

1. **执行摘要**: 关键指标概览
2. **详细指标**: 步骤、token、时间、错误指标
3. **冗余分析**: 检测到的循环和重复调用
4. **优化建议**: 按优先级排序的具体建议
5. **压缩轨迹**: 去除冗余后的优化轨迹
6. **附录**: 工具使用分布等详细信息

## 示例分析结果

```
分析完成!
总步骤: 20
冗余率: 40.0%
检测到循环: 8
重复调用: 12
Token使用: 4,220
压缩后步骤: 2
潜在节省: 18步骤
```

## 高级用法

### 批量分析
```bash
python scripts/analyze_trajectory.py --input-dir ./trajectories/ --aggregate
```

### 自定义相似度阈值
```bash
python scripts/analyze_trajectory.py --input trajectory.json --similarity-threshold 0.8
```

### 集成到CI/CD
```yaml
# GitHub Actions示例
- name: Analyze Agent Trajectory
  run: |
    python scripts/analyze_trajectory.py \
      --input trajectory.json \
      --output report.md
```

## 集成Hermes Agent

### 从Hermes日志分析
```python
from hermes_tools import read_file
import json

# 读取Hermes agent日志
log_content = read_file("~/.hermes/logs/agent.log")

# 解析为轨迹格式
trajectory = parse_hermes_log(log_content)

# 运行分析
analyze_trajectory(trajectory)
```

### 生成优化skill
基于分析结果创建针对性的优化skill：
```bash
hermes skill create --name "optimized-web-search" --based-on analysis_report.md
```

## 常见问题

### Q: 支持哪些agent框架?
A: 支持任何输出结构化日志的agent框架，包括Hermes、LangChain、AutoGPT等。

### Q: 如何处理大型轨迹文件?
A: 对于>100MB的文件，建议使用流式分析或分块处理。

### Q: 如何自定义分析指标?
A: 参考`references/efficiency-metrics.md`中的指标定义，可以扩展自定义指标。

### Q: 如何集成到现有工作流?
A: 可以作为CI/CD管道的一部分，或集成到agent监控系统中。

## 文件结构

```
agent-trajectory-optimizer/
├── SKILL.md                    # 主文档
├── references/
│   ├── trajectory-formats.md   # 支持的轨迹格式
│   ├── optimization-patterns.md # 优化模式参考
│   ├── efficiency-metrics.md   # 效率指标定义
│   ├── usage-guide.md          # 本使用指南
│   └── sample_trajectory.json  # 示例轨迹
└── scripts/
    └── analyze_trajectory.py   # 主分析脚本
```

## 贡献指南

欢迎提交issue和pull request来改进这个skill。

## 许可证

MIT License
