#!/usr/bin/env python3
"""
Agent Trajectory Analyzer

Analyzes AI agent execution trajectories to identify redundancy,
inefficiency, and optimization opportunities.

Usage:
    python analyze_trajectory.py --input trajectory.json --output report.md
    python analyze_trajectory.py --input-dir ./trajectories/ --aggregate
"""

import argparse
import json
import csv
import re
import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

# ============================================================================
# PARSING FUNCTIONS
# ============================================================================

def parse_json_trajectory(file_path: str) -> Dict[str, Any]:
    """Parse JSON trajectory file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if 'trajectory' in data:
        return data
    elif isinstance(data, list):
        return {'trajectory': data}
    else:
        return {'trajectory': [data]}


def parse_csv_trajectory(file_path: str) -> Dict[str, Any]:
    """Parse CSV trajectory file."""
    trajectory = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            step = {
                'step_id': int(row.get('step_id', i + 1)),
                'tool_name': row.get('tool_name', 'unknown'),
                'input': parse_json_field(row.get('input', '{}')),
                'output': parse_json_field(row.get('output', '{}')),
                'timestamp': row.get('timestamp', ''),
                'tokens': int(row.get('tokens', 0)),
                'latency_ms': int(row.get('latency_ms', 0)),
                'status': row.get('status', 'success')
            }
            trajectory.append(step)
    
    return {'trajectory': trajectory}


def parse_text_trajectory(file_path: str) -> Dict[str, Any]:
    """Parse text log trajectory file."""
    pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] STEP (\d+): (\w+)\((.*?)\) -> (\d+) tokens, (\d+)ms'
    trajectory = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(pattern, line.strip())
            if match:
                timestamp, step_id, tool_name, input_str, tokens, latency = match.groups()
                trajectory.append({
                    'step_id': int(step_id),
                    'timestamp': timestamp,
                    'tool_name': tool_name,
                    'input': parse_input_string(input_str),
                    'output': {},
                    'tokens': int(tokens),
                    'latency_ms': int(latency),
                    'status': 'success'
                })
    
    return {'trajectory': trajectory}


def parse_json_field(field: str) -> Any:
    """Parse JSON field from CSV."""
    try:
        return json.loads(field)
    except:
        return field


def parse_input_string(input_str: str) -> Dict[str, Any]:
    """Parse input string from text log."""
    result = {}
    pairs = input_str.split(', ')
    
    for pair in pairs:
        if ':' in pair:
            key, value = pair.split(':', 1)
            result[key.strip()] = value.strip()
    
    return result


def parse_trajectory(file_path: str, file_format: str = 'auto') -> Dict[str, Any]:
    """Parse trajectory file in any supported format."""
    if file_format == 'auto':
        file_format = detect_format(file_path)
    
    parsers = {
        'json': parse_json_trajectory,
        'csv': parse_csv_trajectory,
        'text': parse_text_trajectory
    }
    
    if file_format not in parsers:
        raise ValueError(f"Unsupported format: {file_format}")
    
    return parsers[file_format](file_path)


def detect_format(file_path: str) -> str:
    """Detect file format from extension and content."""
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == '.json':
        return 'json'
    elif ext == '.csv':
        return 'csv'
    elif ext in ['.log', '.txt']:
        return 'text'
    else:
        # Try to detect from content
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('{') or first_line.startswith('['):
                return 'json'
            elif ',' in first_line and 'step_id' in first_line.lower():
                return 'csv'
            else:
                return 'text'


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def calculate_state_hash(step: Dict[str, Any]) -> str:
    """Calculate hash of agent state at a step."""
    state_data = {
        'tool': step['tool_name'],
        'input_hash': hashlib.md5(json.dumps(step['input'], sort_keys=True).encode()).hexdigest(),
        'output_hash': hashlib.md5(json.dumps(step['output'], sort_keys=True).encode()).hexdigest()
    }
    return hashlib.md5(json.dumps(state_data, sort_keys=True).encode()).hexdigest()


def detect_cycles(trajectory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect cycles in trajectory using state hashing."""
    visited_states = {}
    cycles = []
    
    for step in trajectory:
        state_hash = calculate_state_hash(step)
        
        if state_hash in visited_states:
            cycle_start = visited_states[state_hash]
            cycles.append({
                'start_step': cycle_start,
                'end_step': step['step_id'],
                'length': step['step_id'] - cycle_start,
                'state_hash': state_hash,
                'tool_name': step['tool_name']
            })
        else:
            visited_states[state_hash] = step['step_id']
    
    return cycles


def detect_redundant_calls(trajectory: List[Dict[str, Any]], similarity_threshold: float = 0.9) -> List[Dict[str, Any]]:
    """Detect redundant tool calls."""
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


def calculate_input_similarity(input1: Any, input2: Any) -> float:
    """Calculate similarity between two inputs."""
    str1 = json.dumps(input1, sort_keys=True)
    str2 = json.dumps(input2, sort_keys=True)
    
    if str1 == str2:
        return 1.0
    
    # Simple Jaccard similarity on words
    words1 = set(str1.split())
    words2 = set(str2.split())
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def calculate_metrics(trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate comprehensive metrics for trajectory."""
    if not trajectory:
        return {}
    
    # Basic counts
    total_steps = len(trajectory)
    unique_tools = len(set(step['tool_name'] for step in trajectory))
    
    # Token metrics
    total_tokens = sum(step.get('tokens', 0) for step in trajectory)
    avg_tokens_per_step = total_tokens / total_steps if total_steps > 0 else 0
    
    # Time metrics
    total_latency = sum(step.get('latency_ms', 0) for step in trajectory)
    avg_latency_per_step = total_latency / total_steps if total_steps > 0 else 0
    
    # Error metrics
    errors = sum(1 for step in trajectory if step.get('status') == 'error')
    error_rate = errors / total_steps if total_steps > 0 else 0
    
    # Redundancy metrics
    cycles = detect_cycles(trajectory)
    redundant_calls = detect_redundant_calls(trajectory)
    
    unique_hashes = set()
    for step in trajectory:
        step_hash = hash((step['tool_name'], json.dumps(step['input'], sort_keys=True)))
        unique_hashes.add(step_hash)
    
    redundancy_rate = (total_steps - len(unique_hashes)) / total_steps if total_steps > 0 else 0
    
    # Progress metrics (simplified)
    tool_sequence = [step['tool_name'] for step in trajectory]
    tool_changes = sum(1 for i in range(1, len(tool_sequence)) if tool_sequence[i] != tool_sequence[i-1])
    
    return {
        'total_steps': total_steps,
        'unique_tools': unique_tools,
        'total_tokens': total_tokens,
        'avg_tokens_per_step': avg_tokens_per_step,
        'total_latency_ms': total_latency,
        'avg_latency_per_step_ms': avg_latency_per_step,
        'error_count': errors,
        'error_rate': error_rate,
        'cycle_count': len(cycles),
        'redundant_call_count': len(redundant_calls),
        'redundancy_rate': redundancy_rate,
        'tool_changes': tool_changes,
        'unique_step_count': len(unique_hashes)
    }


def generate_optimization_suggestions(metrics: Dict[str, Any], cycles: List[Dict[str, Any]], 
                                      redundant_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate optimization suggestions based on analysis."""
    suggestions = []
    
    # Cycle-based suggestions
    if cycles:
        suggestions.append({
            'priority': 'high',
            'category': 'cycle_detection',
            'title': 'Detected execution cycles',
            'description': f'Found {len(cycles)} cycles in trajectory',
            'impact': 'Reduces wasted tokens and time',
            'recommendation': 'Implement cycle detection and breaking logic'
        })
    
    # Redundancy-based suggestions
    if redundant_calls:
        suggestions.append({
            'priority': 'high',
            'category': 'redundant_calls',
            'title': 'Detected redundant tool calls',
            'description': f'Found {len(redundant_calls)} redundant calls',
            'impact': 'Reduces token waste and improves speed',
            'recommendation': 'Implement caching or conditional execution'
        })
    
    # Token efficiency suggestions
    if metrics.get('avg_tokens_per_step', 0) > 1000:
        suggestions.append({
            'priority': 'medium',
            'category': 'token_efficiency',
            'title': 'High token usage per step',
            'description': f'Average {metrics["avg_tokens_per_step"]:.0f} tokens per step',
            'impact': 'Reduces cost and improves speed',
            'recommendation': 'Optimize prompts and reduce context size'
        })
    
    # Error rate suggestions
    if metrics.get('error_rate', 0) > 0.1:
        suggestions.append({
            'priority': 'medium',
            'category': 'error_handling',
            'title': 'High error rate',
            'description': f'Error rate: {metrics["error_rate"]:.1%}',
            'impact': 'Improves reliability and reduces waste',
            'recommendation': 'Add validation and error recovery'
        })
    
    # Redundancy rate suggestions
    if metrics.get('redundancy_rate', 0) > 0.2:
        suggestions.append({
            'priority': 'medium',
            'category': 'redundancy',
            'title': 'High redundancy rate',
            'description': f'Redundancy rate: {metrics["redundancy_rate"]:.1%}',
            'impact': 'Reduces wasted effort',
            'recommendation': 'Refactor task decomposition and add state management'
        })
    
    # Tool diversity suggestions
    if metrics.get('unique_tools', 0) == 1 and metrics.get('total_steps', 0) > 5:
        suggestions.append({
            'priority': 'low',
            'category': 'tool_diversity',
            'title': 'Low tool diversity',
            'description': 'Using single tool for all steps',
            'impact': 'May miss optimization opportunities',
            'recommendation': 'Consider tool specialization'
        })
    
    return suggestions


def generate_compressed_trajectory(trajectory: List[Dict[str, Any]], cycles: List[Dict[str, Any]], 
                                  redundant_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate compressed trajectory by removing redundant steps."""
    # Mark steps to remove
    steps_to_remove = set()
    
    # Remove cycles (keep first occurrence)
    for cycle in cycles:
        for step_id in range(cycle['start_step'] + 1, cycle['end_step'] + 1):
            steps_to_remove.add(step_id)
    
    # Remove redundant calls (keep first occurrence)
    for call in redundant_calls:
        steps_to_remove.add(call['step2'])
    
    # Filter trajectory
    compressed = [step for step in trajectory if step['step_id'] not in steps_to_remove]
    
    return compressed


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_report(trajectory_data: Dict[str, Any], metrics: Dict[str, Any], 
                   cycles: List[Dict[str, Any]], redundant_calls: List[Dict[str, Any]],
                   suggestions: List[Dict[str, Any]], compressed_trajectory: List[Dict[str, Any]]) -> str:
    """Generate comprehensive optimization report."""
    report = []
    
    # Header
    report.append("# Agent Trajectory Optimization Report\n")
    report.append(f"**Generated**: {datetime.now().isoformat()}\n")
    
    # Executive Summary
    report.append("## Executive Summary\n")
    report.append(f"- **Total Steps**: {metrics.get('total_steps', 0)}")
    report.append(f"- **Unique Steps**: {metrics.get('unique_step_count', 0)}")
    report.append(f"- **Redundancy Rate**: {metrics.get('redundancy_rate', 0):.1%}")
    report.append(f"- **Cycles Detected**: {metrics.get('cycle_count', 0)}")
    report.append(f"- **Token Usage**: {metrics.get('total_tokens', 0):,}")
    report.append(f"- **Estimated Savings**: {len(compressed_trajectory)} steps (compressed from {metrics.get('total_steps', 0)})\n")
    
    # Detailed Metrics
    report.append("## Detailed Metrics\n")
    report.append("### Step Metrics")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Steps | {metrics.get('total_steps', 0)} |")
    report.append(f"| Unique Steps | {metrics.get('unique_step_count', 0)} |")
    report.append(f"| Tool Changes | {metrics.get('tool_changes', 0)} |")
    report.append(f"| Redundancy Rate | {metrics.get('redundancy_rate', 0):.1%} |\n")
    
    report.append("### Token Metrics")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Tokens | {metrics.get('total_tokens', 0):,} |")
    report.append(f"| Avg per Step | {metrics.get('avg_tokens_per_step', 0):.0f} |\n")
    
    report.append("### Time Metrics")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Latency | {metrics.get('total_latency_ms', 0):,}ms |")
    report.append(f"| Avg per Step | {metrics.get('avg_latency_per_step_ms', 0):.0f}ms |\n")
    
    report.append("### Error Metrics")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Error Count | {metrics.get('error_count', 0)} |")
    report.append(f"| Error Rate | {metrics.get('error_rate', 0):.1%} |\n")
    
    # Redundancy Analysis
    report.append("## Redundancy Analysis\n")
    
    if cycles:
        report.append("### Detected Cycles\n")
        report.append("| Cycle | Steps | Length | Tool |")
        report.append("|-------|-------|--------|------|")
        for i, cycle in enumerate(cycles[:5], 1):
            report.append(f"| {i} | {cycle['start_step']}-{cycle['end_step']} | {cycle['length']} | {cycle['tool_name']} |")
        report.append("")
    
    if redundant_calls:
        report.append("### Redundant Tool Calls\n")
        report.append("| Call | Steps | Tool | Similarity |")
        report.append("|------|-------|------|------------|")
        for i, call in enumerate(redundant_calls[:5], 1):
            report.append(f"| {i} | {call['step1']}-{call['step2']} | {call['tool']} | {call['similarity']:.1%} |")
        report.append("")
    
    # Optimization Suggestions
    report.append("## Optimization Recommendations\n")
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            report.append(f"### {i}. {suggestion['title']}")
            report.append(f"**Priority**: {suggestion['priority'].title()}")
            report.append(f"**Category**: {suggestion['category']}")
            report.append(f"**Description**: {suggestion['description']}")
            report.append(f"**Impact**: {suggestion['impact']}")
            report.append(f"**Recommendation**: {suggestion['recommendation']}\n")
    else:
        report.append("No significant optimization opportunities detected.\n")
    
    # Compressed Trajectory
    report.append("## Compressed Trajectory\n")
    report.append(f"- **Original Steps**: {metrics.get('total_steps', 0)}")
    report.append(f"- **Compressed Steps**: {len(compressed_trajectory)}")
    report.append(f"- **Reduction**: {metrics.get('total_steps', 0) - len(compressed_trajectory)} steps ({(metrics.get('total_steps', 0) - len(compressed_trajectory)) / metrics.get('total_steps', 1):.1%})\n")
    
    if compressed_trajectory:
        report.append("### Optimized Step Sequence\n")
        report.append("```")
        for step in compressed_trajectory[:20]:
            report.append(f"Step {step['step_id']}: {step['tool_name']}")
        if len(compressed_trajectory) > 20:
            report.append(f"... and {len(compressed_trajectory) - 20} more steps")
        report.append("```\n")
    
    # Appendix
    report.append("## Appendix\n")
    report.append("### Tool Usage Distribution\n")
    tool_counts = defaultdict(int)
    for step in trajectory_data.get('trajectory', []):
        tool_counts[step['tool_name']] += 1
    
    report.append("| Tool | Count | Percentage |")
    report.append("|------|-------|------------|")
    for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / metrics.get('total_steps', 1) * 100
        report.append(f"| {tool} | {count} | {percentage:.1f}% |")
    
    return "\n".join(report)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Analyze agent trajectories for optimization')
    parser.add_argument('--input', '-i', required=True, help='Input trajectory file')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--format', '-f', choices=['json', 'csv', 'text', 'auto'], default='auto',
                       help='Input file format')
    parser.add_argument('--aggregate', action='store_true', help='Aggregate multiple trajectories')
    parser.add_argument('--input-dir', help='Directory containing trajectory files')
    parser.add_argument('--similarity-threshold', type=float, default=0.9,
                       help='Similarity threshold for redundancy detection')
    
    args = parser.parse_args()
    
    # Parse trajectory
    print(f"Parsing trajectory from {args.input}...")
    trajectory_data = parse_trajectory(args.input, args.format)
    trajectory = trajectory_data.get('trajectory', [])
    
    if not trajectory:
        print("Error: No trajectory data found")
        sys.exit(1)
    
    print(f"Loaded {len(trajectory)} steps")
    
    # Run analysis
    print("Analyzing trajectory...")
    metrics = calculate_metrics(trajectory)
    cycles = detect_cycles(trajectory)
    redundant_calls = detect_redundant_calls(trajectory, args.similarity_threshold)
    suggestions = generate_optimization_suggestions(metrics, cycles, redundant_calls)
    compressed_trajectory = generate_compressed_trajectory(trajectory, cycles, redundant_calls)
    
    # Generate report
    print("Generating report...")
    report = generate_report(trajectory_data, metrics, cycles, redundant_calls, suggestions, compressed_trajectory)
    
    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print("\n" + "="*80)
        print(report)
    
    # Print summary
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    print(f"Total Steps: {metrics.get('total_steps', 0)}")
    print(f"Redundancy Rate: {metrics.get('redundancy_rate', 0):.1%}")
    print(f"Cycles Detected: {metrics.get('cycle_count', 0)}")
    print(f"Redundant Calls: {metrics.get('redundant_call_count', 0)}")
    print(f"Token Usage: {metrics.get('total_tokens', 0):,}")
    print(f"Compressed Steps: {len(compressed_trajectory)}")
    print(f"Potential Savings: {metrics.get('total_steps', 0) - len(compressed_trajectory)} steps")
    print("="*80)


if __name__ == '__main__':
    main()
