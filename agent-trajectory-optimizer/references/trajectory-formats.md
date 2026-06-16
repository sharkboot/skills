# Supported Trajectory Formats

## JSON Format (Recommended)

The JSON format provides the most flexibility and is easiest to parse.

### Structure
```json
{
  "metadata": {
    "agent_name": "hermes-agent",
    "task_id": "task-123",
    "start_time": "2026-06-16T10:30:00Z",
    "end_time": "2026-06-16T10:35:00Z",
    "total_tokens": 1500,
    "success": true
  },
  "trajectory": [
    {
      "step_id": 1,
      "timestamp": "2026-06-16T10:30:00Z",
      "tool_name": "web_search",
      "input": {
        "query": "agent optimization techniques"
      },
      "output": {
        "results": [
          {"title": "Optimizing Agent Trajectories", "url": "..."}
        ],
        "result_count": 5
      },
      "tokens": 150,
      "latency_ms": 1200,
      "status": "success",
      "parent_step_id": null,
      "context": {
        "reasoning": "Need to find current optimization methods",
        "confidence": 0.9
      }
    }
  ]
}
```

### Required Fields
- `step_id`: Unique identifier for each step
- `tool_name`: Name of the tool/action taken
- `input`: Input parameters (can be any JSON-serializable object)
- `output`: Output/result (can be any JSON-serializable object)

### Optional Fields
- `timestamp`: ISO 8601 timestamp
- `tokens`: Token count for this step
- `latency_ms`: Execution time in milliseconds
- `status`: "success", "error", "timeout"
- `parent_step_id`: For branching workflows
- `context`: Additional metadata (reasoning, confidence, etc.)

---

## CSV Format

Suitable for simple, linear trajectories.

### Structure
```csv
step_id,tool_name,input,output,timestamp,tokens,latency_ms,status
1,web_search,"query: agent optimization","results: [...]",2026-06-16T10:30:00Z,150,1200,success
2,read_file,"path: results.txt","content: ...",2026-06-16T10:30:01Z,50,100,success
```

### Parsing Notes
- Input/output fields may need JSON escaping for complex objects
- Timestamps should be ISO 8601 format
- Tokens and latency are numeric fields

---

## Text Log Format

Common in traditional logging systems.

### Structure
```
[2026-06-16 10:30:00] STEP 1: web_search(input={"query": "agent optimization"}) -> 150 tokens, 1200ms
[2026-06-16 10:30:01] STEP 2: read_file(path="results.txt") -> 50 tokens, 100ms
[2026-06-16 10:30:02] STEP 3: process(content=...) -> 200 tokens, 500ms
```

### Parsing Regex
```python
import re

pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] STEP (\d+): (\w+)\((.*?)\) -> (\d+) tokens, (\d+)ms'
```

---

## Hermes Agent Log Format

Special format for Hermes agent logs.

### Structure
```
2026-06-16 10:30:00 | INFO | Step 1 | web_search | Input: {"query": "agent optimization"}
2026-06-16 10:30:00 | INFO | Step 1 | web_search | Output: {"results": [...]}
2026-06-16 10:30:00 | INFO | Step 1 | web_search | Tokens: 150 | Latency: 1200ms
```

### Parsing Strategy
1. Group log lines by step ID
2. Extract tool name from first line of group
3. Parse input/output from subsequent lines
4. Extract metrics from final line of group

---

## Custom Format Support

To add support for a new format:

1. Create a parser class:
```python
class CustomFormatParser:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def parse(self):
        # Implement parsing logic
        return standardized_trajectory
```

2. Register the parser:
```python
from parsers import register_parser
register_parser('custom', CustomFormatParser)
```

3. Use in analysis:
```bash
python analyze_trajectory.py --format custom --input trajectory.custom
```

---

## Format Conversion

### JSON to CSV
```python
import json
import csv

def json_to_csv(json_file, csv_file):
    with open(json_file) as f:
        data = json.load(f)
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['step_id', 'tool_name', 'input', 'output', 'timestamp', 'tokens', 'latency_ms'])
        writer.writeheader()
        for step in data['trajectory']:
            writer.writerow({
                'step_id': step['step_id'],
                'tool_name': step['tool_name'],
                'input': json.dumps(step['input']),
                'output': json.dumps(step['output']),
                'timestamp': step.get('timestamp', ''),
                'tokens': step.get('tokens', 0),
                'latency_ms': step.get('latency_ms', 0)
            })
```

### Text to JSON
```python
import re
import json
from datetime import datetime

def text_to_json(text_file, json_file):
    pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] STEP (\d+): (\w+)\((.*?)\) -> (\d+) tokens, (\d+)ms'
    
    trajectory = []
    with open(text_file) as f:
        for line in f:
            match = re.match(pattern, line.strip())
            if match:
                timestamp, step_id, tool_name, input_str, tokens, latency = match.groups()
                trajectory.append({
                    'step_id': int(step_id),
                    'timestamp': timestamp,
                    'tool_name': tool_name,
                    'input': parse_input_string(input_str),
                    'output': {},  # May need additional parsing
                    'tokens': int(tokens),
                    'latency_ms': int(latency)
                })
    
    with open(json_file, 'w') as f:
        json.dump({'trajectory': trajectory}, f, indent=2)
```

---

## Validation

### JSON Schema Validation
```python
import jsonschema

schema = {
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "properties": {
                "agent_name": {"type": "string"},
                "task_id": {"type": "string"},
                "start_time": {"type": "string", "format": "date-time"},
                "end_time": {"type": "string", "format": "date-time"},
                "total_tokens": {"type": "number"},
                "success": {"type": "boolean"}
            }
        },
        "trajectory": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_id": {"type": "integer"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "tool_name": {"type": "string"},
                    "input": {"type": "object"},
                    "output": {"type": "object"},
                    "tokens": {"type": "number"},
                    "latency_ms": {"type": "number"},
                    "status": {"type": "string", "enum": ["success", "error", "timeout"]}
                },
                "required": ["step_id", "tool_name", "input", "output"]
            }
        }
    }
}

def validate_trajectory(data):
    jsonschema.validate(instance=data, schema=schema)
```
