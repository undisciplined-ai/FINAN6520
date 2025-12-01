# Python Patterns (Module 10 Reference)

## JSONL Read/Write

**Write**:
```python
import json

with open('output.jsonl', 'w') as f:
    for item in items:
        f.write(json.dumps(item) + '\n')
```

**Read**:
```python
items = []
with open('input.jsonl', 'r') as f:
    for line in f:
        items.append(json.loads(line))

# Or list comprehension:
items = [json.loads(line) for line in open('input.jsonl')]
```

## Grouping with defaultdict

```python
from collections import defaultdict

nodes_by_chunk = defaultdict(list)
for node in nodes:
    chunk_id = node['provenance']['chunk_id']
    nodes_by_chunk[chunk_id].append(node)
```

## ID Generation

```python
doc_id = f"doc{doc_num:03d}"      # doc001, doc002
page_id = f"p{page_num:03d}"      # p001, p042
chunk_id = f"c{chunk_num:02d}"    # c01, c15
node_id = f"{doc_id}-{page_id}-{chunk_id}-{type_code}-{seq:02d}"
# Result: doc001-p003-c02-PER-01
```

## YAML Config Loading

```python
import yaml

with open('config/run_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

chunk_size = config['chunk_size']
model = config['phase1']['model']
```

## Environment Variables (No Third-Party Helpers)

```python
import os

# Ensure AI_GATEWAY_API_KEY is set in environment
api_key = os.environ["AI_GATEWAY_API_KEY"]  # Raises KeyError if missing
```
