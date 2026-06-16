# Efficiency Metrics Definitions

## Core Metrics

### 1. Step Count Metrics

**Total Steps**
```python
def total_steps(trajectory):
    """Count total number of steps in trajectory."""
    return len(trajectory)
```

**Unique Steps**
```python
def unique_steps(trajectory):
    """Count unique tool calls (by tool name + input hash)."""
    unique_hashes = set()
    for step in trajectory:
        step_hash = hash((step['tool_name'], json.dumps(step['input'], sort_keys=True)))
        unique_hashes.add(step_hash)
    return len(unique_hashes)
```

**Redundancy Rate**
```python
def redundancy_rate(trajectory):
    """Calculate ratio of redundant steps to total steps."""
    total = total_steps(trajectory)
    unique = unique_steps(trajectory)
    return (total - unique) / total if total > 0 else 0
```

### 2. Token Metrics

**Total Tokens**
```python
def total_tokens(trajectory):
    """Sum tokens across all steps."""
    return sum(step.get('tokens', 0) for step in trajectory)
```

**Token Efficiency**
```python
def token_efficiency(trajectory, useful_output_tokens):
    """Calculate ratio of useful output tokens to total tokens."""
    total = total_tokens(trajectory)
    return useful_output_tokens / total if total > 0 else 0
```

**Tokens per Step**
```python
def tokens_per_step(trajectory):
    """Average tokens per step."""
    total = total_tokens(trajectory)
    steps = total_steps(trajectory)
    return total / steps if steps > 0 else 0
```

### 3. Time Metrics

**Total Latency**
```python
def total_latency(trajectory):
    """Sum latency across all steps (in milliseconds)."""
    return sum(step.get('latency_ms', 0) for step in trajectory)
```

**Time per Step**
```python
def time_per_step(trajectory):
    """Average latency per step."""
    total = total_latency(trajectory)
    steps = total_steps(trajectory)
    return total / steps if steps > 0 else 0
```

**Wall Clock Time**
```python
def wall_clock_time(trajectory):
    """Calculate total wall clock time from first to last step."""
    if not trajectory:
        return 0
    
    timestamps = [step['timestamp'] for step in trajectory if 'timestamp' in step]
    if len(timestamps) < 2:
        return 0
    
    start = min(timestamps)
    end = max(timestamps)
    
    if isinstance(start, str):
        start = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end.replace('Z', '+00:00'))
    
    return (end - start).total_seconds() * 1000  # Convert to milliseconds
```

### 4. Error Metrics

**Error Rate**
```python
def error_rate(trajectory):
    """Calculate ratio of failed steps to total steps."""
    errors = sum(1 for step in trajectory if step.get('status') == 'error')
    total = total_steps(trajectory)
    return errors / total if total > 0 else 0
```

**Error Types**
```python
def error_types(trajectory):
    """Categorize errors by type."""
    error_counts = {}
    for step in trajectory:
        if step.get('status') == 'error':
            error_type = step.get('error_type', 'unknown')
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
    return error_counts
```

---

## Advanced Metrics

### 5. Cycle Metrics

**Cycle Count**
```python
def cycle_count(trajectory, state_hash_func):
    """Count number of cycles in trajectory."""
    visited = {}
    cycles = 0
    
    for step in trajectory:
        state_hash = state_hash_func(step)
        if state_hash in visited:
            cycles += 1
        else:
            visited[state_hash] = step['step_id']
    
    return cycles
```

**Cycle Length**
```python
def cycle_lengths(trajectory, state_hash_func):
    """Calculate lengths of detected cycles."""
    visited = {}
    cycle_lengths = []
    
    for step in trajectory:
        state_hash = state_hash_func(step)
        if state_hash in visited:
            cycle_length = step['step_id'] - visited[state_hash]
            cycle_lengths.append(cycle_length)
        else:
            visited[state_hash] = step['step_id']
    
    return cycle_lengths
```

**Cycle Cost**
```python
def cycle_cost(trajectory, state_hash_func):
    """Calculate token cost wasted in cycles."""
    visited = {}
    cycle_tokens = 0
    
    for step in trajectory:
        state_hash = state_hash_func(step)
        if state_hash in visited:
            cycle_tokens += step.get('tokens', 0)
        else:
            visited[state_hash] = step['step_id']
    
    return cycle_tokens
```

### 6. Progress Metrics

**Progress Rate**
```python
def progress_rate(trajectory, goal_progress_func):
    """Calculate rate of progress toward goal."""
    if len(trajectory) < 2:
        return 0
    
    initial_progress = goal_progress_func(trajectory[0])
    final_progress = goal_progress_func(trajectory[-1])
    total_steps = len(trajectory)
    
    return (final_progress - initial_progress) / total_steps
```

**Stagnation Detection**
```python
def detect_stagnation(trajectory, window_size=5, threshold=0.01):
    """Detect periods of no progress."""
    stagnation_periods = []
    current_stagnation = []
    
    for i in range(window_size, len(trajectory)):
        window = trajectory[i-window_size:i]
        progress = calculate_window_progress(window)
        
        if progress < threshold:
            current_stagnation.append(i)
        else:
            if len(current_stagnation) > window_size:
                stagnation_periods.append(current_stagnation)
            current_stagnation = []
    
    return stagnation_periods
```

### 7. Cost Metrics

**Total Cost**
```python
def total_cost(trajectory, token_price=0.00003):
    """Calculate total monetary cost."""
    tokens = total_tokens(trajectory)
    return tokens * token_price
```

**Cost per Useful Output**
```python
def cost_per_useful_output(trajectory, useful_outputs, token_price=0.00003):
    """Calculate cost per useful output unit."""
    total = total_cost(trajectory, token_price)
    return total / useful_outputs if useful_outputs > 0 else float('inf')
```

**Cost Efficiency**
```python
def cost_efficiency(trajectory, value_generated, token_price=0.00003):
    """Calculate value generated per dollar spent."""
    cost = total_cost(trajectory, token_price)
    return value_generated / cost if cost > 0 else 0
```

---

## Comparative Metrics

### 8. Trajectory Comparison

**Trajectory Similarity (Jaccard)**
```python
def trajectory_similarity_jaccard(traj1, traj2):
    """Calculate Jaccard similarity between trajectories."""
    set1 = set((s['tool_name'], json.dumps(s['input'], sort_keys=True)) for s in traj1)
    set2 = set((s['tool_name'], json.dumps(s['input'], sort_keys=True)) for s in traj2)
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0
```

**Trajectory Similarity (Levenshtein)**
```python
def trajectory_similarity_levenshtein(traj1, traj2):
    """Calculate normalized Levenshtein similarity."""
    seq1 = [s['tool_name'] for s in traj1]
    seq2 = [s['tool_name'] for s in traj2]
    
    distance = levenshtein_distance(seq1, seq2)
    max_len = max(len(seq1), len(seq2))
    
    return 1 - (distance / max_len) if max_len > 0 else 1
```

### 9. Optimal Step Ratio

**Optimal Steps Estimation**
```python
def estimate_optimal_steps(trajectory, successful_trajectories):
    """Estimate optimal steps based on successful trajectories."""
    similar_trajectories = find_similar_trajectories(trajectory, successful_trajectories)
    
    if similar_trajectories:
        return min(len(t) for t in similar_trajectories)
    else:
        # Fallback: use percentile of all trajectories
        all_lengths = [len(t) for t in successful_trajectories]
        return percentile(all_lengths, 25)  # 25th percentile
```

**Optimal Step Ratio**
```python
def optimal_step_ratio(trajectory, successful_trajectories):
    """Calculate ratio of actual steps to estimated optimal steps."""
    actual = len(trajectory)
    optimal = estimate_optimal_steps(trajectory, successful_trajectories)
    return actual / optimal if optimal > 0 else float('inf')
```

### 10. Consistency Score

**Consistency Across Runs**
```python
def consistency_score(trajectory_set):
    """Calculate consistency of step counts across similar tasks."""
    if len(trajectory_set) < 2:
        return 1.0
    
    step_counts = [len(t) for t in trajectory_set]
    mean_steps = sum(step_counts) / len(step_counts)
    variance = sum((x - mean_steps) ** 2 for x in step_counts) / len(step_counts)
    std_dev = variance ** 0.5
    
    # Coefficient of variation (lower is more consistent)
    cv = std_dev / mean_steps if mean_steps > 0 else 0
    
    # Convert to 0-1 score (1 is most consistent)
    return 1 / (1 + cv)
```

---

## Composite Metrics

### 11. Overall Efficiency Score

**Weighted Efficiency Score**
```python
def overall_efficiency_score(trajectory, weights=None):
    """Calculate weighted efficiency score."""
    if weights is None:
        weights = {
            'step_efficiency': 0.25,
            'token_efficiency': 0.25,
            'time_efficiency': 0.25,
            'error_rate': 0.25
        }
    
    scores = {
        'step_efficiency': 1 - redundancy_rate(trajectory),
        'token_efficiency': token_efficiency(trajectory, estimate_useful_tokens(trajectory)),
        'time_efficiency': 1 - (total_latency(trajectory) / max_possible_latency(trajectory)),
        'error_rate': 1 - error_rate(trajectory)
    }
    
    weighted_score = sum(scores[metric] * weights[metric] for metric in weights)
    return weighted_score
```

### 12. Quality-Adjusted Efficiency

**Quality-Adjusted Score**
```python
def quality_adjusted_efficiency(trajectory, quality_score):
    """Adjust efficiency by quality of outcome."""
    efficiency = overall_efficiency_score(trajectory)
    return efficiency * quality_score
```

---

## Metric Interpretation Guidelines

### Step Count Metrics
- **< 10 steps**: Excellent (simple tasks)
- **10-50 steps**: Good (medium complexity)
- **50-100 steps**: Fair (complex tasks)
- **> 100 steps**: Poor (may indicate inefficiency)

### Token Efficiency
- **> 0.7**: Excellent (most tokens are useful)
- **0.5-0.7**: Good (moderate waste)
- **0.3-0.5**: Fair (significant waste)
- **< 0.3**: Poor (major optimization needed)

### Error Rate
- **< 5%**: Excellent (highly reliable)
- **5-15%**: Good (acceptable)
- **15-30%**: Fair (needs improvement)
- **> 30%**: Poor (major reliability issues)

### Cycle Metrics
- **0 cycles**: Excellent (no wasted effort)
- **1-3 cycles**: Fair (some redundancy)
- **> 3 cycles**: Poor (significant loops)

### Cost Efficiency
- **High value/$**: Excellent (cost-effective)
- **Medium value/$**: Good (acceptable)
- **Low value/$**: Fair (expensive)
- **Negative value/$**: Poor (losing money)

---

## Metric Visualization

### Time Series Plot
```python
def plot_metric_over_time(trajectory, metric_func, metric_name):
    """Plot metric value over trajectory steps."""
    import matplotlib.pyplot as plt
    
    steps = range(len(trajectory))
    values = [metric_func(trajectory[:i+1]) for i in steps]
    
    plt.figure(figsize=(10, 6))
    plt.plot(steps, values)
    plt.xlabel('Step Number')
    plt.ylabel(metric_name)
    plt.title(f'{metric_name} Over Trajectory')
    plt.grid(True)
    plt.show()
```

### Distribution Plot
```python
def plot_metric_distribution(trajectories, metric_func, metric_name):
    """Plot distribution of metric across multiple trajectories."""
    import matplotlib.pyplot as plt
    
    values = [metric_func(t) for t in trajectories]
    
    plt.figure(figsize=(10, 6))
    plt.hist(values, bins=20, edgecolor='black')
    plt.xlabel(metric_name)
    plt.ylabel('Frequency')
    plt.title(f'Distribution of {metric_name}')
    plt.grid(True)
    plt.show()
```

### Comparison Plot
```python
def plot_trajectory_comparison(trajectories, metric_funcs, metric_names):
    """Compare multiple metrics across trajectories."""
    import matplotlib.pyplot as plt
    import numpy as np
    
    x = np.arange(len(trajectories))
    width = 0.8 / len(metric_funcs)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for i, (metric_func, metric_name) in enumerate(zip(metric_funcs, metric_names)):
        values = [metric_func(t) for t in trajectories]
        ax.bar(x + i * width, values, width, label=metric_name)
    
    ax.set_xlabel('Trajectory')
    ax.set_ylabel('Score')
    ax.set_title('Trajectory Comparison')
    ax.legend()
    plt.grid(True)
    plt.show()
```
