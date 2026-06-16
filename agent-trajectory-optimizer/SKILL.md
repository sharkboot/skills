---
name: agent-trajectory-optimizer
description: "Analyze AI agent execution trajectories to identify redundancy, inefficiency, and optimization opportunities. Supports multiple log formats (JSON, CSV, text), detects cycles, duplicate tool calls, semantic redundancy, and generates actionable optimization reports."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agent, trajectory, optimization, analysis, redundancy, efficiency, debugging]
    related_skills: [research, systematic-debugging, coding-agents]
---

# Agent Trajectory Optimizer

Analyze AI agent execution trajectories to identify redundancy, inefficiency, and optimization opportunities.

## Quick Decision Guide

| Need | Use |
|------|-----|
| Analyze agent logs for redundancy | **Trajectory Analysis** (Section 1) |
| Detect cycles and repeated actions | **Cycle Detection** (Section 2) |
| Calculate efficiency metrics | **Metrics Computation** (Section 3) |
| Generate optimization recommendations | **Optimization Report** (Section 4) |

## Reference Files

- `references/trajectory-formats.md` — supported log formats and parsing
- `references/optimization-patterns.md` — common anti-patterns and fixes
- `references/efficiency-metrics.md` — detailed metric definitions
- `scripts/analyze_trajectory.py` — main analysis script
- `scripts/detect_cycles.py` — cycle detection algorithm
- `scripts/generate_report.py` — report generation

---

## Section 1: Trajectory Analysis Workflow

### Supported Formats

1. **JSON Logs** (preferred):
   ```json
   [
     {
       "step_id": 1,
       "tool_name": "web_search",
       "input": {"query": "agent optimization"},
       "output": {"results": [...]},
       "timestamp": "2026-06-16T10:30:00Z",
       "tokens": 150,
       "latency_ms": 1200
     }
   ]
   ```

2. **CSV Format**:
   ```csv
   step_id,tool_name,input,output,timestamp,tokens,latency_ms
   1,web_search,"query: agent optimization","results: [...]",2026-06-16T10:30:00Z,150,1200
   ```

3. **Text Logs** (structured):
   ```
   [2026-06-16 10:30:00] STEP 1: web_search(input="agent optimization") -> 150 tokens, 1200ms
   ```

### Analysis Steps

1. **Parse Trajectory**: Convert to standardized internal format
2. **Extract Features**: Tool calls, inputs, outputs, timing, tokens
3. **Build Dependency Graph**: Map causal relationships between steps
4. **Detect Patterns**: Identify redundancy, cycles, inefficiencies
5. **Generate Report**: Actionable optimization recommendations

---

## Section 2: Cycle Detection

### Algorithm: State Hashing

```python
import hashlib
import json

def detect_cycles(trajectory):
    """Detect cycles by hashing agent state at each step."""
    visited_states = {}
    cycles = []
    
    for step in trajectory:
        # Create state hash from context + last observation
        state_data = {
            'tool': step['tool_name'],
            'input_hash': hashlib.md5(json.dumps(step['input'], sort_keys=True).encode()).hexdigest(),
            'output_hash': hashlib.md5(json.dumps(step['output'], sort_keys=True).encode()).hexdigest()
        }
        state_hash = hashlib.md5(json.dumps(state_data, sort_keys=True).encode()).hexdigest()
        
        if state_hash in visited_states:
            cycle_start = visited_states[state_hash]
            cycles.append({
                'start_step': cycle_start,
                'end_step': step['step_id'],
                'length': step['step_id'] - cycle_start,
                'state_hash': state_hash
            })
        else:
            visited_states[state_hash] = step['step_id']
    
    return cycles
```

### Detection Patterns

1. **Exact Cycles**: Same tool + identical input/output
2. **Near-Duplicate Calls**: Similar inputs with minor variations
3. **Semantic Loops**: Different tools but same logical outcome
4. **Progress-Free Sequences**: Multiple steps without meaningful advancement

---

## Section 3: Efficiency Metrics

### Per-Trajectory Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Step Count** | `len(trajectory)` | Total actions taken |
| **Unique Tool Ratio** | `unique_tools / total_steps` | Tool diversity |
| **Redundancy Rate** | `duplicate_calls / total_steps` | Wasted effort |
| **Cycle Count** | `len(detected_cycles)` | Loop occurrences |
| **Token Efficiency** | `useful_output_tokens / total_tokens` | Cost effectiveness |
| **Time Efficiency** | `useful_time / total_time` | Speed optimization |
| **Error Rate** | `failed_steps / total_steps` | Reliability |

### Comparative Metrics

- **Optimal Step Ratio**: `actual_steps / estimated_optimal_steps`
- **Trajectory Similarity**: Jaccard/Levenshtein distance across runs
- **Consistency Score**: Variance in step count for same task types

---

## Section 4: Optimization Recommendations

### Common Anti-Patterns & Fixes

#### 1. Redundant Tool Calls
**Pattern**: Same tool called multiple times with identical/similar inputs
**Detection**: Hash tool inputs, flag duplicates
**Fix**: Cache results, use conditional logic

#### 2. Unnecessary Exploration
**Pattern**: Agent explores too many alternatives when direct path exists
**Detection**: High branching factor without progress
**Fix**: Add early stopping, improve heuristics

#### 3. Context Window Waste
**Pattern**: Accumulating irrelevant observations
**Detection**: Growing context without useful output
**Fix**: Implement context pruning, summarization

#### 4. Tool Misuse
**Pattern**: Using complex tools when simpler ones suffice
**Detection**: High-cost tools for simple tasks
**Fix**: Tool selection guidelines, cost-based routing

#### 5. Failed Path Proliferation
**Pattern**: Many steps on failing approach before backtracking
**Detection**: Long sequences ending in failure
**Fix**: Early validation, checkpointing

### Report Structure

```markdown
# Agent Trajectory Optimization Report

## Executive Summary
- Total trajectories analyzed: X
- Average efficiency score: Y%
- Top optimization opportunities: Z

## Detailed Findings

### 1. Redundancy Analysis
- Duplicate tool calls: N instances
- Cycle detection: M cycles found
- Estimated token waste: T tokens

### 2. Efficiency Metrics
- Step count distribution
- Token usage breakdown
- Time distribution per tool

### 3. Optimization Recommendations
1. **High Priority**: [Specific fix]
2. **Medium Priority**: [Specific fix]
3. **Low Priority**: [Specific fix]

### 4. Compressed Trajectory
- Original: X steps
- Optimized: Y steps
- Reduction: Z%

## Appendix
- Detailed metric tables
- Visualization links
- Raw data references
```

---

## Usage Examples

### Basic Analysis
```bash
python scripts/analyze_trajectory.py --input trajectory.json --output report.md
```

### Cycle Detection Only
```bash
python scripts/detect_cycles.py --input trajectory.json --threshold 0.8
```

### Generate Optimization Plan
```bash
python scripts/generate_report.py --input trajectory.json --format markdown
```

### Batch Analysis
```bash
python scripts/analyze_trajectory.py --input-dir ./trajectories/ --aggregate
```

---

## Integration with Hermes

### Loading Trajectories from Hermes Logs
```python
from hermes_tools import read_file
import json

# Read Hermes agent log
log_content = read_file("~/.hermes/logs/agent.log")

# Parse into trajectory format
trajectory = parse_hermes_log(log_content)
```

### Generating Optimization Skills
After analysis, use findings to create targeted optimization skills:
```bash
# Generate skill based on common patterns
hermes skill create --name "optimized-web-search" --based-on analysis_report.md
```

---

## Pitfalls

1. **Large Trajectories**: Files >100MB may cause memory issues; use streaming analysis
2. **Noisy Logs**: Ensure proper log formatting before analysis
3. **False Positives**: Semantic similarity thresholds need tuning per domain
4. **Missing Context**: Some "redundant" calls may be necessary for state validation
5. **Platform Differences**: Log formats vary between agent frameworks; normalize first

---

## Advanced Topics

### Custom Metrics
Extend the analysis with domain-specific metrics:
```python
def custom_efficiency_score(trajectory, domain_weights):
    """Calculate domain-weighted efficiency score."""
    # Implement custom logic
    return score
```

### Machine Learning Integration
Train models to predict optimal trajectories:
- Use historical successful trajectories as training data
- Implement reinforcement learning for trajectory optimization
- Apply sequence-to-sequence models for trajectory compression

### Real-time Monitoring
Integrate with live agent execution:
- Stream trajectory data to analysis pipeline
- Provide real-time optimization suggestions
- Implement adaptive thresholds based on task complexity
