# Common Optimization Patterns

## Anti-Patterns and Fixes

### 1. Redundant Tool Calls

**Pattern Description**:
Agent calls the same tool multiple times with identical or near-identical inputs within a short time window.

**Detection Method**:
```python
def detect_redundant_calls(trajectory, similarity_threshold=0.9):
    """Detect redundant tool calls using input similarity."""
    redundant = []
    
    for i, step1 in enumerate(trajectory):
        for j, step2 in enumerate(trajectory[i+1:], i+1):
            if step1['tool_name'] == step2['tool_name']:
                similarity = calculate_input_similarity(step1['input'], step2['input'])
                if similarity > similarity_threshold:
                    redundant.append({
                        'step1': step1['step_id'],
                        'step2': step2['step_id'],
                        'tool': step1['tool_name'],
                        'similarity': similarity
                    })
    
    return redundant
```

**Common Causes**:
- Lack of result caching
- Missing state management
- Redundant validation checks
- Poor task decomposition

**Optimization Fixes**:

1. **Implement Caching**:
```python
class ToolCache:
    def __init__(self):
        self.cache = {}
    
    def call(self, tool_name, input_data):
        cache_key = self._generate_key(tool_name, input_data)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self._execute_tool(tool_name, input_data)
        self.cache[cache_key] = result
        return result
```

2. **Add Conditional Logic**:
```python
# Before: Redundant calls
search_results = web_search("query1")
search_results_again = web_search("query1")  # Redundant

# After: Conditional execution
if not hasattr(self, 'search_cache'):
    self.search_cache = {}
    
if "query1" not in self.search_cache:
    self.search_cache["query1"] = web_search("query1")

search_results = self.search_cache["query1"]
```

3. **Refactor Task Decomposition**:
```python
# Before: Over-decomposed
step1 = read_file("config.json")
step2 = parse_json(step1)
step3 = validate_config(step2)
step4 = read_file("config.json")  # Redundant

# After: Consolidated
config = read_and_validate_config("config.json")
```

---

### 2. Unnecessary Exploration

**Pattern Description**:
Agent explores too many alternatives when a direct path exists, often due to poor heuristics or lack of domain knowledge.

**Detection Method**:
```python
def detect_unnecessary_exploration(trajectory, branching_threshold=3):
    """Detect excessive branching without progress."""
    exploration_sequences = []
    current_sequence = []
    
    for step in trajectory:
        if is_exploratory(step):
            current_sequence.append(step)
        else:
            if len(current_sequence) > branching_threshold:
                exploration_sequences.append(current_sequence)
            current_sequence = []
    
    return exploration_sequences
```

**Common Causes**:
- Weak heuristics
- Missing domain knowledge
- Over-cautious decision making
- Lack of early stopping criteria

**Optimization Fixes**:

1. **Improve Heuristics**:
```python
class ImprovedHeuristic:
    def evaluate_options(self, options, context):
        # Score options based on multiple factors
        scores = []
        for option in options:
            score = (
                self.relevance_score(option, context) * 0.4 +
                self.confidence_score(option) * 0.3 +
                self.cost_score(option) * 0.3
            )
            scores.append((option, score))
        
        # Return top-k options instead of all
        return sorted(scores, key=lambda x: x[1], reverse=True)[:3]
```

2. **Implement Early Stopping**:
```python
def should_continue_exploring(exploration_state, threshold=0.8):
    """Determine if further exploration is worthwhile."""
    if exploration_state.best_score > threshold:
        return False
    
    if exploration_state.iterations > exploration_state.max_iterations:
        return False
    
    if exploration_state.improvement_rate < 0.01:
        return False
    
    return True
```

3. **Add Domain Knowledge**:
```python
class DomainKnowledge:
    def __init__(self):
        self.known_patterns = {}
        self.successful_strategies = []
    
    def suggest_strategy(self, task_type):
        """Suggest strategy based on historical success."""
        if task_type in self.known_patterns:
            return self.known_patterns[task_type]
        
        # Default to most successful general strategy
        return self.successful_strategies[0] if self.successful_strategies else None
```

---

### 3. Context Window Waste

**Pattern Description**:
Agent accumulates irrelevant observations in context, leading to degraded performance and higher token costs.

**Detection Method**:
```python
def detect_context_waste(trajectory, relevance_threshold=0.3):
    """Detect accumulation of irrelevant context."""
    context_growth = []
    useful_output_ratio = []
    
    for i, step in enumerate(trajectory):
        # Calculate context size
        context_size = sum(len(str(s['output'])) for s in trajectory[:i+1])
        
        # Calculate useful output ratio
        useful_output = calculate_usefulness(step['output'], step.get('goal'))
        total_output = len(str(step['output']))
        ratio = useful_output / total_output if total_output > 0 else 0
        
        context_growth.append(context_size)
        useful_output_ratio.append(ratio)
    
    return {
        'context_growth': context_growth,
        'useful_ratio': useful_output_ratio,
        'waste_detected': any(r < relevance_threshold for r in useful_output_ratio)
    }
```

**Common Causes**:
- No context pruning strategy
- Missing summarization
- Over-inclusive observation storage
- Poor relevance filtering

**Optimization Fixes**:

1. **Implement Context Pruning**:
```python
class ContextManager:
    def __init__(self, max_tokens=4000):
        self.context = []
        self.max_tokens = max_tokens
    
    def add_observation(self, observation):
        self.context.append(observation)
        self._prune_if_needed()
    
    def _prune_if_needed(self):
        current_tokens = sum(self._count_tokens(obs) for obs in self.context)
        
        while current_tokens > self.max_tokens and len(self.context) > 1:
            # Remove least relevant observation
            least_relevant = min(self.context, key=lambda x: self._relevance_score(x))
            self.context.remove(least_relevant)
            current_tokens -= self._count_tokens(least_relevant)
```

2. **Add Summarization**:
```python
def summarize_context(context, max_length=500):
    """Summarize context to reduce token usage."""
    if len(str(context)) <= max_length:
        return context
    
    # Extract key points
    key_points = []
    for observation in context:
        if is_key_observation(observation):
            key_points.append(extract_key_point(observation))
    
    # Create summary
    summary = {
        'key_points': key_points,
        'total_observations': len(context),
        'time_range': get_time_range(context)
    }
    
    return summary
```

3. **Relevance Filtering**:
```python
def filter_relevant_context(context, current_task, threshold=0.5):
    """Filter context based on relevance to current task."""
    relevant = []
    
    for observation in context:
        relevance = calculate_relevance(observation, current_task)
        if relevance > threshold:
            relevant.append(observation)
    
    return relevant
```

---

### 4. Tool Misuse

**Pattern Description**:
Agent uses complex/expensive tools when simpler ones suffice, leading to unnecessary cost and latency.

**Detection Method**:
```python
def detect_tool_misuse(trajectory, cost_threshold=10.0):
    """Detect use of expensive tools for simple tasks."""
    misuse_instances = []
    
    for step in trajectory:
        tool_cost = get_tool_cost(step['tool_name'])
        task_complexity = estimate_task_complexity(step['input'])
        
        if tool_cost > cost_threshold and task_complexity < 0.3:
            misuse_instances.append({
                'step': step['step_id'],
                'tool': step['tool_name'],
                'cost': tool_cost,
                'complexity': task_complexity,
                'suggested_tool': suggest_cheaper_tool(step['input'])
            })
    
    return misuse_instances
```

**Common Causes**:
- Lack of tool selection guidelines
- Over-reliance on familiar tools
- Missing cost awareness
- Poor task-tool matching

**Optimization Fixes**:

1. **Tool Selection Guidelines**:
```python
class ToolSelector:
    def __init__(self):
        self.tool_capabilities = {
            'web_search': {'cost': 1, 'latency': 1000, 'capabilities': ['search', 'browse']},
            'read_file': {'cost': 0.1, 'latency': 10, 'capabilities': ['file_access']},
            'execute_code': {'cost': 5, 'latency': 5000, 'capabilities': ['computation', 'analysis']}
        }
    
    def select_tool(self, task_requirements):
        """Select most appropriate tool based on requirements."""
        suitable_tools = []
        
        for tool, specs in self.tool_capabilities.items():
            if self._meets_requirements(specs, task_requirements):
                suitable_tools.append((tool, specs))
        
        # Select cheapest suitable tool
        return min(suitable_tools, key=lambda x: x[1]['cost'])[0]
```

2. **Cost-Based Routing**:
```python
def route_by_cost(task, budget_constraint):
    """Route tasks to tools based on cost constraints."""
    if budget_constraint == 'low':
        return select_low_cost_tool(task)
    elif budget_constraint == 'medium':
        return select_balanced_tool(task)
    else:
        return select_high_quality_tool(task)
```

3. **Task-Tool Matching**:
```python
def match_task_to_tool(task_description):
    """Match task description to appropriate tool."""
    task_lower = task_description.lower()
    
    if 'search' in task_lower or 'find' in task_lower:
        return 'web_search'
    elif 'read' in task_lower or 'file' in task_lower:
        return 'read_file'
    elif 'calculate' in task_lower or 'compute' in task_lower:
        return 'execute_code'
    else:
        return 'default_tool'
```

---

### 5. Failed Path Proliferation

**Pattern Description**:
Agent spends many steps on an approach that fails, then backtracks, when early validation could have short-circuited.

**Detection Method**:
```python
def detect_failed_paths(trajectory, failure_threshold=5):
    """Detect long sequences ending in failure."""
    failed_paths = []
    current_path = []
    
    for step in trajectory:
        current_path.append(step)
        
        if step['status'] == 'error':
            if len(current_path) > failure_threshold:
                failed_paths.append({
                    'steps': current_path,
                    'length': len(current_path),
                    'failure_point': step['step_id'],
                    'error': step.get('error_message')
                })
            current_path = []
        elif is_backtrack(step):
            if len(current_path) > failure_threshold:
                failed_paths.append({
                    'steps': current_path,
                    'length': len(current_path),
                    'backtrack_point': step['step_id'],
                    'reason': 'backtrack'
                })
            current_path = []
    
    return failed_paths
```

**Common Causes**:
- Missing early validation
- No checkpointing strategy
- Over-commitment to failing approaches
- Lack of rollback mechanisms

**Optimization Fixes**:

1. **Early Validation**:
```python
def validate_approach_early(approach, validation_criteria):
    """Validate approach before full execution."""
    # Quick validation checks
    if not passes_basic_checks(approach):
        return False, "Failed basic checks"
    
    # Lightweight execution test
    test_result = execute_lightweight_test(approach)
    if not test_result.success:
        return False, test_result.error
    
    return True, "Validation passed"
```

2. **Checkpointing Strategy**:
```python
class CheckpointManager:
    def __init__(self):
        self.checkpoints = {}
    
    def save_checkpoint(self, step_id, state):
        """Save state at important steps."""
        self.checkpoints[step_id] = {
            'state': state.copy(),
            'timestamp': datetime.now(),
            'metrics': self._calculate_metrics(state)
        }
    
    def rollback_to_checkpoint(self, step_id):
        """Rollback to a previous checkpoint."""
        if step_id in self.checkpoints:
            return self.checkpoints[step_id]['state']
        return None
```

3. **Adaptive Backtracking**:
```python
def adaptive_backtrack(current_state, failure_history):
    """Implement adaptive backtracking strategy."""
    # Analyze failure patterns
    failure_patterns = analyze_failure_patterns(failure_history)
    
    # Choose backtracking strategy
    if failure_patterns.is_systematic:
        return rollback_to_last_stable_checkpoint()
    elif failure_patterns.is_random:
        return retry_with_variation(current_state)
    else:
        return try_alternative_approach(current_state)
```

---

## Optimization Strategies

### 1. Trajectory Compression

**Goal**: Reduce trajectory length while maintaining outcome quality.

**Algorithm**:
```python
def compress_trajectory(trajectory, quality_threshold=0.9):
    """Compress trajectory by removing redundant steps."""
    compressed = []
    essential_steps = identify_essential_steps(trajectory)
    
    for step in trajectory:
        if step in essential_steps:
            compressed.append(step)
        elif not is_redundant(step, compressed):
            compressed.append(step)
    
    # Verify quality maintained
    if calculate_quality_score(compressed) >= quality_threshold:
        return compressed
    else:
        return trajectory  # Return original if compression hurts quality
```

### 2. Parallelization Opportunities

**Identify**: Steps that can be executed in parallel.

**Implementation**:
```python
def parallelize_trajectory(trajectory):
    """Identify and implement parallelization opportunities."""
    dependency_graph = build_dependency_graph(trajectory)
    parallel_groups = topological_sort_with_parallelism(dependency_graph)
    
    return parallel_groups
```

### 3. Tool Substitution

**Goal**: Replace expensive tools with cheaper alternatives when possible.

**Strategy**:
```python
def substitute_tools(trajectory, cost_budget):
    """Substitute tools to meet cost constraints."""
    optimized = []
    
    for step in trajectory:
        if get_tool_cost(step['tool_name']) > cost_budget:
            cheaper_alternative = find_cheaper_alternative(step)
            if cheaper_alternative:
                step = cheaper_alternative
        
        optimized.append(step)
    
    return optimized
```

---

## Implementation Checklist

When implementing optimizations:

- [ ] **Baseline Measurement**: Establish current performance metrics
- [ ] **Pattern Detection**: Identify which anti-patterns are present
- [ ] **Root Cause Analysis**: Understand why patterns occur
- [ ] **Solution Design**: Design targeted fixes for each pattern
- [ ] **Incremental Testing**: Test optimizations incrementally
- [ ] **Quality Verification**: Ensure optimizations don't hurt outcome quality
- [ ] **Monitoring**: Implement monitoring to catch regressions
- [ ] **Documentation**: Document changes and their impact
