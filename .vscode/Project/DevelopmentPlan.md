# Knowledge Graph Extraction Pipeline — Development Plan

> **Source Template**: MetaDevelopmentPlan.md  
> **Project**: Configurable Knowledge Graph Generator for RAG Systems  
> **Immediate Goal**: Generate `nodes.jsonl`, `edges.jsonl`, and a Mad-Libs style persona sheet from PDFs—no extra tooling.

---

## Phase 0 — Foundations _(Priority: REQUIRED)_

Establish the complete configuration surface and reference materials before writing code. All files created in this phase serve as sources of truth for LLM-assisted development.

### 0.1 Directory Structure

Create the project skeleton:

```
/workspaces/FINAN6520/
├── .env                          # API keys (git-ignored)
├── .gitignore                    # Ignore .env, outputs/, __pycache__
├── config/
│   ├── persona_schema.yaml       # Node types, edge types, field definitions
│   └── run_config.yaml           # Chunk size, models, thresholds, token budget
├── docs/
│   ├── api_reference.md          # Vercel AI Gateway HTTP API specs
│   ├── pdfplumber_quickref.md    # Methods we'll use (extract_text, pages, metadata)
│   └── python_patterns.md        # Module 10 patterns: JSONL, defaultdict, f-strings
├── examples/
│   ├── chunks.jsonl              # 3-5 sample chunks with proper IDs
│   ├── nodes.jsonl               # 10-15 sample nodes (all types)
│   ├── edges.jsonl               # 10 sample edges (all relation types)
│   └── persona_prompt.txt        # Example output format
├── outputs/                      # Pipeline outputs (git-ignored)
├── prompts/
│   ├── phase1_extraction.txt     # Node extraction prompt template
│   └── phase2_relationships.txt  # Edge extraction prompt template
└── scripts/                      # Python pipeline scripts (Phases 1-4)
```

**Deliverables**:
- All directories created
- `.gitignore` configured
- Directory structure matches cognitive ontology spec

### 0.2 Schema Definition

Create `config/persona_schema.yaml` defining the cognitive ontology:

```yaml
node_types:
  Persona:
    code: "PER"
    description: "High-level cognitive identity with worldview and communication style"
    fields:
      worldview: string
      core_values: list[string]
      communication_style: enum[directive, socratic, nurturing, analytical]
      evidence_strength: float
  Value:
    code: "VAL"
    description: "Explicit value judgment or principle"
    fields:
      polarity: enum[positive, caution, taboo]
      strength: float
      context: string
  ReasoningPattern:
    code: "REA"
    description: "Recurring logic pattern or decision framework"
    fields:
      trigger: string
      preferred_response: string
      failure_mode: string
  LinguisticStyle:
    code: "LIN"
    description: "Tone, formality, and phrasing preferences"
    fields:
      formality: enum[casual, professional, academic]
      complexity: enum[simple, moderate, technical]
      example_phrases: list[string]

edge_types:
  - name: "persona_has_value"
    description: "Links persona to explicit value or principle"
  - name: "persona_uses_reasoning"
    description: "Links persona to preferred reasoning pattern"
  - name: "persona_has_style"
    description: "Links persona to linguistic style"
  - name: "value_conflicts_with"
    description: "Two values in tension"
  - name: "reasoning_supports"
    description: "One reasoning pattern builds on another"

# Common fields for all nodes
node_common_fields:
  - id: string           # Auto-generated: doc-page-chunk-type-seq
  - type: string         # One of node_types above
  - label: string        # Brief concept label
  - description: string  # Clear description
  - tags: list[string]   # Categorization
  - importance: float    # 0.0-1.0
  - provenance:
      doc_id: string
      doc_name: string
      page_num: int
      chunk_id: string
      extraction_phase: string

# Common fields for all edges
edge_common_fields:
  - source_id: string
  - target_id: string
  - relation: string     # One of edge_types above
  - weight: float        # 0.0-1.0
  - confidence: float    # 0.0-1.0
  - evidence: string     # Optional quote/reference
```

**Deliverables**:
- Schema YAML matches cognitive ontology doc exactly
- All node types from ontology included
- All edge types documented

### 0.3 Runtime Configuration

Create `config/run_config.yaml` with all processing parameters:

```yaml
# PDF Processing
pdf_extractor: "pdfplumber"
chunk_size: 1400         # tokens (not words)
chunk_overlap: 200       # tokens
tokenizer: "cl100k_base" # OpenAI tokenizer for token counting

# API Configuration
api_key_env: "AI_GATEWAY_API_KEY"  # Vercel AI Gateway API key
api_provider: "vercel"             # Use Vercel AI SDK

# Phase 1: Node Extraction
phase1:
  model: "openai/gpt-4o-mini"  # Vercel AI SDK format: provider/model
  temperature: 0.1
  max_tokens: 2000
  prompt_template: "prompts/phase1_extraction.txt"

# Phase 2: Relationship Extraction
phase2:
  model: "openai/gpt-4o-mini"
  temperature: 0.1
  max_tokens: 1500
  importance_threshold: 0.5  # Only process nodes above this
  prompt_template: "prompts/phase2_relationships.txt"

# Phase 3: Persona Sheet
phase3:
  max_values: 5
  max_reasoning: 3
  max_styles: 2
```

Create `.env` file (git-ignored) using Vercel AI Gateway authentication:

```bash
AI_GATEWAY_API_KEY=your_api_key_here
```

Create `.env.example` (committed to repo):

```bash
# Vercel AI Gateway API Key
# Get your key from: https://vercel.com/docs/ai-gateway
AI_GATEWAY_API_KEY=
```

Python scripts read `os.environ["AI_GATEWAY_API_KEY"]` directly—no third-party env loaders.

**Deliverables**:
- All config values explicit (no hardcoded defaults in scripts)
- `.env.example` committed; actual `.env` git-ignored
- Config values match cognitive ontology recommendations

### 0.4 Example I/O Files

Create reference examples showing exact structure expected at each phase.

**`examples/chunks.jsonl`** (3 samples):
```jsonl
{"doc_id": "doc001", "page_id": "p001", "chunk_id": "c01", "text": "Sample text showing cognitive pattern...", "doc_name": "example.pdf", "page_num": 1}
{"doc_id": "doc001", "page_id": "p001", "chunk_id": "c02", "text": "Second chunk with overlap from previous...", "doc_name": "example.pdf", "page_num": 1}
{"doc_id": "doc001", "page_id": "p002", "chunk_id": "c01", "text": "First chunk from page 2...", "doc_name": "example.pdf", "page_num": 2}
```

**`examples/nodes.jsonl`** (showing all four node types with complete fields):
```jsonl
{"id": "doc001-p001-c01-PER-01", "type": "Persona", "label": "Growth-Oriented Learner", "description": "Values iterative improvement through failure", "tags": ["learning", "resilience"], "importance": 0.85, "fields": {"worldview": "Challenges reveal capability", "core_values": ["growth", "humility"], "communication_style": "socratic", "evidence_strength": 0.75}, "provenance": {"doc_id": "doc001", "doc_name": "example.pdf", "page_num": 1, "chunk_id": "c01", "extraction_phase": "phase1"}}
{"id": "doc001-p001-c01-VAL-01", "type": "Value", "label": "Embrace Failure", "description": "Failure is feedback, not identity", "tags": ["resilience"], "importance": 0.70, "fields": {"polarity": "positive", "strength": 0.80, "context": "Learning contexts"}, "provenance": {"doc_id": "doc001", "doc_name": "example.pdf", "page_num": 1, "chunk_id": "c01", "extraction_phase": "phase1"}}
{"id": "doc001-p001-c01-REA-01", "type": "ReasoningPattern", "label": "Test-Then-Scale", "description": "Validate assumptions before committing resources", "tags": ["methodology"], "importance": 0.65, "fields": {"trigger": "New opportunity or strategy", "preferred_response": "Small experiment first", "failure_mode": "Premature scaling"}, "provenance": {"doc_id": "doc001", "doc_name": "example.pdf", "page_num": 1, "chunk_id": "c01", "extraction_phase": "phase1"}}
{"id": "doc001-p001-c01-LIN-01", "type": "LinguisticStyle", "label": "Socratic Questioning", "description": "Guides discovery through questions rather than direct answers", "tags": ["communication", "pedagogy"], "importance": 0.60, "fields": {"formality": "professional", "complexity": "moderate", "example_phrases": ["What if we tested...", "Let's break this down", "I'm curious about..."]}, "provenance": {"doc_id": "doc001", "doc_name": "example.pdf", "page_num": 1, "chunk_id": "c01", "extraction_phase": "phase1"}}
```

**`examples/edges.jsonl`**:
```jsonl
{"source_id": "doc001-p001-c01-PER-01", "target_id": "doc001-p001-c01-VAL-01", "relation": "persona_has_value", "weight": 0.85, "confidence": 0.90, "evidence": "Explicitly states failure as learning mechanism"}
{"source_id": "doc001-p001-c01-PER-01", "target_id": "doc001-p001-c01-REA-01", "relation": "persona_uses_reasoning", "weight": 0.75, "confidence": 0.80, "evidence": "Prefers iterative validation"}
```

**`examples/persona_prompt.txt`**:
```
You are Growth-Oriented Learner.

WORLDVIEW:
Challenges reveal capability. Growth comes from iterative improvement through failure.

CORE VALUES:
- Embrace Failure: Failure is feedback, not identity (strength: 0.80)
- Humility: Acknowledge limits; seek input (strength: 0.75)
- Curiosity: Question assumptions (strength: 0.70)

REASONING PATTERNS:
- Test-Then-Scale: Small experiments before big commitments
- First-Principles: Break problems into fundamental truths
- Meta-Cognition: Reflect on thinking process itself

COMMUNICATION STYLE:
- Formality: Professional but approachable
- Complexity: Moderate; explain technical concepts clearly
- Signature Phrases: "Let's break this down", "What if we tested...", "I'm curious about..."

When responding:
1. Stay consistent with these values and patterns
2. Use Socratic questioning to guide discovery
3. Acknowledge uncertainty; model learning process
4. Reference evidence from source material when relevant
```

**Deliverables**:
- Example files validate against schema
- IDs follow `doc-page-chunk-type-seq` format exactly
- Provenance fields complete
- Persona sheet demonstrates traversal logic

### 0.5 Prompt Templates

Create `prompts/phase1_extraction.txt`:

```
You are extracting structured concepts from text.

NODE TYPES TO EXTRACT:
{node_types}

INSTRUCTIONS:
- Identify concepts matching the defined node types
- Rate importance from 0.0 (trivial) to 1.0 (foundational)
- Extract only clear, distinct concepts (be conservative)
- Include all type-specific fields from schema
- Return ONLY valid JSON (no markdown, no code blocks, no explanatory text)

SOURCE CONTEXT:
- Document: {doc_id}
- Page: {page_id}
- Chunk: {chunk_id}

TEXT TO ANALYZE:
{chunk_text}

REQUIRED OUTPUT FORMAT:
Return a single JSON object with a "nodes" array. Each node must match one of these exact schemas:

Persona node:
{{
  "type": "Persona",
  "label": "Brief label",
  "description": "Clear description",
  "tags": ["tag1", "tag2"],
  "importance": 0.75,
  "fields": {{
    "worldview": "Core belief system",
    "core_values": ["value1", "value2"],
    "communication_style": "socratic",
    "evidence_strength": 0.80
  }}
}}

Value node:
{{
  "type": "Value",
  "label": "Value name",
  "description": "What this value means",
  "tags": ["category"],
  "importance": 0.65,
  "fields": {{
    "polarity": "positive",
    "strength": 0.75,
    "context": "When this applies"
  }}
}}

ReasoningPattern node:
{{
  "type": "ReasoningPattern",
  "label": "Pattern name",
  "description": "How this reasoning works",
  "tags": ["logic"],
  "importance": 0.70,
  "fields": {{
    "trigger": "What activates this pattern",
    "preferred_response": "What action follows",
    "failure_mode": "What goes wrong when misapplied"
  }}
}}

LinguisticStyle node:
{{
  "type": "LinguisticStyle",
  "label": "Style name",
  "description": "Communication characteristics",
  "tags": ["tone"],
  "importance": 0.60,
  "fields": {{
    "formality": "professional",
    "complexity": "moderate",
    "example_phrases": ["phrase1", "phrase2"]
  }}
}}

Your complete response (example):
{{
  "nodes": [
    {{
      "type": "Persona",
      "label": "Growth-Oriented Learner",
      "description": "Values iterative improvement through failure",
      "tags": ["learning"],
      "importance": 0.85,
      "fields": {{
        "worldview": "Challenges reveal capability",
        "core_values": ["growth", "humility"],
        "communication_style": "socratic",
        "evidence_strength": 0.75
      }}
    }}
  ]
}}

Note: IDs will be auto-generated as {doc_id}-{page_id}-{chunk_id}-{type_code}-{seq}
```

Create `prompts/phase2_relationships.txt`:

```
You are identifying relationships between concepts.

RELATIONSHIP TYPES:
{edge_types}

NODES FROM THIS CHUNK:
{nodes}

INSTRUCTIONS:
- Identify relationships between listed nodes only
- Use only the defined relationship types
- Rate confidence from 0.0 (uncertain) to 1.0 (explicit)
- Rate weight from 0.0 (weak) to 1.0 (strong)
- Provide brief evidence from text
- Return ONLY valid JSON (no markdown, no code blocks, no explanatory text)

TEXT FOR CONTEXT:
{chunk_text}

REQUIRED OUTPUT FORMAT:
Return a single JSON object with an "edges" array. Each edge must have this exact structure:

{{
  "source_id": "doc001-p001-c01-PER-01",
  "target_id": "doc001-p001-c01-VAL-01",
  "relation": "persona_has_value",
  "weight": 0.80,
  "confidence": 0.90,
  "evidence": "Direct quote or paraphrase from text"
}}

Example complete response:
{{
  "edges": [
    {{
      "source_id": "doc001-p001-c01-PER-01",
      "target_id": "doc001-p001-c01-VAL-01",
      "relation": "persona_has_value",
      "weight": 0.85,
      "confidence": 0.90,
      "evidence": "Explicitly states failure as learning mechanism"
    }},
    {{
      "source_id": "doc001-p001-c01-PER-01",
      "target_id": "doc001-p001-c01-REA-01",
      "relation": "persona_uses_reasoning",
      "weight": 0.75,
      "confidence": 0.80,
      "evidence": "Prefers iterative validation before scaling"
    }}
  ]
}}

IMPORTANT: Use exact node IDs from the NODES list above.
```

**Deliverables**:
- Prompts use `{variable}` placeholders for runtime injection
- Instructions clear and minimal (no over-specification)
- Output format shows exact JSON structure expected

### 0.6 API Reference Documentation

Create `docs/api_reference.md`:

```markdown
# Vercel AI Gateway API Reference

## Authentication
```python
import os

# Read API key from environment
api_key = os.environ["AI_GATEWAY_API_KEY"]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

## Endpoint
```
POST https://gateway.vercel.com/v1/chat/completions
```

## Request Format
```python
import requests
import json

payload = {
    "model": "openai/gpt-4o-mini",  # Format: provider/model
    "messages": [
        {"role": "system", "content": "System prompt here"},
        {"role": "user", "content": "User message here"}
    ],
    "temperature": 0.1,
    "max_tokens": 2000
}

url = "https://gateway.vercel.com/v1/chat/completions"
response = requests.post(url, headers=headers, json=payload)
result = response.json()
```

## Response Format
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "{\"nodes\": [...]}"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 450,
    "completion_tokens": 320,
    "total_tokens": 770
  }
}
```

## Parsing with Error Handling
```python
import json
import re

def parse_llm_response(response_text):
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Strip markdown code blocks if present
    text = response_text.strip()
    if text.startswith("```"):
        # Remove ```json or ``` wrapper
        text = re.sub(r'^```(?:json)?\n', '', text)
        text = re.sub(r'\n```$', '', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nResponse: {text[:200]}...")

# Usage
assistant_message = result["choices"][0]["message"]["content"]
extracted_data = parse_llm_response(assistant_message)
nodes = extracted_data["nodes"]
```

## Token Counting
```python
import tiktoken

def count_tokens(text, model="cl100k_base"):
    """Count tokens using tiktoken (OpenAI tokenizer)."""
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))
```
```

Create `docs/pdfplumber_quickref.md`:

```markdown
# pdfplumber Quick Reference

## Open PDF
```python
import pdfplumber

with pdfplumber.open('path/to/file.pdf') as pdf:
    # Work with pdf object
```

## Iterate Pages
```python
for page_num, page in enumerate(pdf.pages, start=1):
    text = page.extract_text()
    # Process text
```

## Page Metadata
```python
page.width
page.height
page.page_number
```

## Text Extraction
```python
text = page.extract_text()  # Returns string
```

## Error Handling
```python
text = page.extract_text()
if text is None:
    text = ""  # Handle empty pages
```
```

Create `docs/python_patterns.md`:

```markdown
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

# Ensure `VERCEL_AI_GATEWAY_KEY` is exported in the shell first
api_key = os.environ["VERCEL_AI_GATEWAY_KEY"]  # Raises KeyError if missing
```
```

**Deliverables**:
- API docs show exact request/response structure
- pdfplumber docs cover only methods we use
- Python patterns match Module 10 learnings

### 0.7 Python Environment

pdfplumber>=0.11.0
Install dependencies:

```bash
pip install pdfplumber PyYAML requests tiktoken
```

Create `requirements.txt`:
```
pdfplumber>=0.11.0
PyYAML>=6.0
requests>=2.31.0
tiktoken>=0.5.0
```

**Deliverables**:
- All dependencies installed
- `requirements.txt` committed
- Test imports work: `python -c "import pdfplumber, yaml, requests"`

### 0.8 Validation & Logging Contracts

Add a guardrail layer before any LLM calls:

- **`scripts/validate_outputs.py`** (pure stdlib) reads `persona_schema.yaml`, then streams `examples/*.jsonl` or real outputs to ensure:
  - Required keys exist and match primitive types (string/float/list)
  - IDs follow `doc-page-chunk-type-seq` format
  - Edge references exist in `nodes.jsonl`
  - Type-specific fields match schema requirements (e.g., Persona has worldview, Value has polarity)
- **Validation behavior**: Report ALL errors found, then exit with `sys.exit(1)` if any errors exist
- Output format: Line-by-line error reporting with node/edge IDs and specific validation failures
- Extend `config/run_config.yaml` with lightweight logging settings:

```yaml
logging:
  level: "INFO"        # INFO for normal runs, DEBUG for troubleshooting
  destination: "stdout" # or "outputs/run.log" using `logging.FileHandler`
token_reporting:
  enabled: true
  warn_at_tokens: 120000  # matches token_budget warn threshold
```

- Each script imports `logging`, calls `logging.basicConfig` using the config values, and records:
  - Start/finish per phase
  - Token usage per chunk/response
  - Validation failures (with offending IDs)

**Deliverables**:
- Validation script checked in and runnable via `python scripts/validate_outputs.py nodes.jsonl`
- `run_config.yaml` contains `logging` + `token_reporting` sections used by every phase
- README note explaining that validation is Step 0.9 before Phase 1 execution

### Phase 0 Completion Checklist

Before proceeding to Phase 1:

- [ ] Directory structure matches spec
- [ ] Schema YAML validates against cognitive ontology
- [ ] Run config includes all parameters (no hardcoded values, token-based chunking)
- [ ] Example JSONL files show all four node types with complete fields
- [ ] Prompt templates use `{variables}` for injection and include schema examples
- [ ] API reference shows Vercel AI Gateway with error handling
- [ ] Python patterns doc references Module 10 learnings
- [ ] Dependencies installed (`requirements.txt` includes tiktoken)
- [ ] `.env` file exists with `AI_GATEWAY_API_KEY`
- [ ] `.env.example` committed to repo
- [ ] `.gitignore` prevents committing secrets/outputs
- [ ] `python scripts/validate_outputs.py examples/nodes.jsonl` succeeds (reports all errors)

**Why This Matters**: Every file created in Phase 0 serves as a source of truth during implementation. LLMs can reference exact schemas, see example outputs, and follow proven patterns—eliminating hallucination and ensuring consistency.

---

## Phase 1 — PDF Ingestion & Chunking _(Priority: REQUIRED)_

Extract text from PDFs and create provenance-rich chunks.

**What to do**
- Use `pdfplumber` (or `PyMuPDF`) to iterate pages and capture text.
- Apply a simple token-aware chunker (word-count slice with overlap) per page.
- Emit `chunks.jsonl` containing `doc_id`, `page_id`, `chunk_id`, `text`, and provenance metadata.

**Python Implementation Approach**
1. Iterate PDFs with `enumerate(pdf.pages)`; generate zero-padded `doc_id`/`page_id` (Module 3 loops + f-strings).
2. Chunk text using a sliding window over `text.split()`; join back to strings; assign `chunk_id` sequentially.
3. Write each chunk as a dict via `json.dumps` to `outputs/chunks.jsonl`.
4. Log sample chunk metadata with `print` for quick verification.

**Checks**
- Chunks preserve page order and include deterministic IDs.
- Sample run on 1–2 PDFs shows readable text and provenance.

---

## Phase 2 — Node Extraction _(Priority: REQUIRED)_

Send each chunk to the LLM to extract schema-compliant nodes; no embeddings or duplicate merges yet.

**What to do**
- Load `chunks.jsonl` and schema YAML to know allowed node types/fields.
- Format Phase‑1 prompt with chunk text + schema, call Vercel AI Gateway, parse JSON response.
- Mint IDs (`doc-page-chunk-type-seq`) and append to `nodes.jsonl`.

**Python Implementation Approach**
1. Read chunks via list comprehension `[json.loads(line) for line in open('outputs/chunks.jsonl')]`.
2. Format prompt strings with basic f-strings; no template engine required.
3. Use `requests.post` (or `urllib.request`) to call Vercel Gateway; parse with `response.json()`.
4. For each returned node, build ID with `f"{doc}-{page}-{chunk}-{code}-{idx:02d}"` and write to JSONL.
5. Collect minimal stats (node counts per type) for console feedback.

**Checks**
- `nodes.jsonl` entries validate against schema (required fields present, IDs deterministic).
- No references to embeddings or duplicate hashes yet—pure extraction.

---

## Phase 3 — Relationship Extraction _(Priority: REQUIRED)_

Identify intra-chunk relationships using the extracted nodes.

**What to do**
- Group nodes by chunk, filter by importance threshold from config.
- Format Phase‑2 prompt with the node list + available edge types.
- Call LLM, parse edges, and append to `edges.jsonl`.

**Python Implementation Approach**
1. Build `nodes_by_chunk = defaultdict(list)` from `nodes.jsonl`.
2. Filter out nodes below threshold via list comprehension.
3. Serialize node subset to JSON when filling the prompt; reuse the same HTTP helper from Phase 2.
4. Validate each returned edge references existing node IDs; log and skip invalid ones.
5. Append edges to `outputs/edges.jsonl` (one JSON object per line).

**Checks**
- `edges.jsonl` populated with source/target IDs, relation names, confidence/weight values.
- Input node files left untouched.

---

## Phase 4 — Persona Sheet Generation _(Priority: REQUIRED)_

Traverse the graph to build a simple Mad-Libs persona sheet for validation/testing.

**What to do**
- Load `nodes.jsonl` and `edges.jsonl` into in-memory dicts/lists.
- Locate the highest-importance Persona node, gather connected Values/Reasoning/Styles.
- Produce `persona_prompt.txt` summarizing worldview, values, reasoning patterns, and tone.

**Python Implementation Approach**
1. Create `nodes_by_id = {node['id']: node for node in nodes}` and `edges_from = defaultdict(list)`.
2. Identify Persona nodes via `[n for n in nodes if n['type'] == 'Persona']` and select by `max(..., key=lambda n: n.get('importance', 0))`.
3. Traverse outgoing edges and collect target nodes by type using simple loops; keep everything in standard-library lists/dicts (no NetworkX or other graph libs).
4. Render multiline f-string to produce the persona sheet; cap list lengths for readability.
5. Save to `outputs/persona_prompt.txt` and print a preview snippet.

**Checks**
- Persona sheet exists and matches ontology fields.
- Manual spot-check confirms content ties back to source nodes.

---

## Optional Extensions (Parked for Later)

These are intentionally deferred until the core KG + persona workflow proves valuable:

1. **Cross-Document Synthesis** — add embeddings + cosine clustering before asking the LLM for cross-PDF edges.
2. **Token Budget & Resume Controls** — introduce run-state checkpoints and budget prompts for large corpora.
3. **Duplicate Management & Collapse** — hash-based duplicate tracking plus intra-chunk merge scripts.
4. **Post-Pipeline LLM Curation** — sample high-frequency duplicates and have the LLM suggest merges.

Each extension can be plugged in without rewriting the foundational phases because the I/O contracts are file-based.

> Detailed specs for these extensions live in `Cognitive Ontology Extraction for RAG Persona.md`; this plan simply records when to tackle them.

---

## Out of Scope for Repository Initialization

Documented for completeness but **not** part of the initial build:

- Vector index population (Pinecone/pgvector) and semantic retrieval.
- Next.js / Vercel chatbot integration.
- Advanced CLI packaging, token dashboards, or production hardening (security, observability, lifecycle automation).

These items stay in the backlog until we prove the KG produces useful persona answers.
