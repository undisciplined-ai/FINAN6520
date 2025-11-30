# Configurable Knowledge Graph Generator for RAG Systems

## First Principles: What You See Is All There Is

### The Problem
Text contains patterns. Extracting them manually doesn't scale. LLMs can extract patterns, but without structure, the patterns aren't reusable.

### What We Actually Have
- PDFs containing source material
- LLMs that can extract and categorize concepts
- A need for structured knowledge that can be queried dynamically

### What We Need
A configurable extraction pipeline that produces structured knowledge graphs from unstructured text, where the schema is user-defined, not hardcoded.

---

## The System (No Abstractions)

### Input
A folder of PDF files. That's it.

### Process
1. **Extract and chunk text** (configurable size and overlap)
2. **Phase 1 - Extract nodes**: LLM identifies concepts matching your defined node types → structured JSON
3. **Phase 2 - Extract local relationships**: LLM identifies connections between concepts using your defined edge types
4. **Phase 3 - Cross-document synthesis**: Embeddings cluster similar concepts, LLM identifies global relationships across documents

### Output
Two JSONL files:
- `nodes.jsonl`: One node per line (id, type, label, description, importance, source provenance)
- `edges.jsonl`: One edge per line (source, target, relation, weight, confidence, provenance)

### What Makes It Useful
For RAG systems:
1. User query triggers semantic search across the knowledge graph
2. System retrieves relevant nodes and their connected concepts
3. Context is injected into LLM prompt
4. LLM responds using the structured knowledge from source material

Works for any domain: persona modeling, technical documentation, domain expertise, conceptual frameworks.

---

## Data Flow & Identifier Lifecycle

### PDF Extraction → Chunking → ID Assignment

The pipeline follows a strict two-stage chunking process to preserve document structure while ensuring LLM-friendly chunk sizes:

**Stage 1: Page-Level Extraction**
- Extract each PDF page independently using `pdfplumber` or `pymupdf`
- Maintain reading order and preserve page boundaries for provenance
- Assign `doc_id` (zero-padded, e.g., `doc003`) and `page_id` (e.g., `p012`)
- Handle tables/figures as placeholder nodes for future enrichment

**Stage 2: Token-Aware Chunking**
- Split each page's text using a token-based splitter (configurable size + overlap)
- Default: 1400 tokens per chunk, 200 token overlap
- Assign `chunk_id` within each page (e.g., `c01`, `c02`)
- All parameters (chunk size, overlap, tokenizer) live in config file

### Node ID Format

Every node receives a deterministic ID immediately after Phase 1 extraction:

```
{doc_id}-{page_id}-{chunk_id}-{type_code}-{seq}
```

**Example**: `doc003-p012-c02-PER-01`
- `doc003`: Third PDF in the batch
- `p012`: Page 12
- `c02`: Second chunk on that page
- `PER`: Node type code (e.g., Persona, Value, Reasoning)
- `01`: First node of this type extracted from this chunk

**Why This Matters**:
- IDs are stable across retries (deterministic)
- Provenance is baked into every identifier
- Later phases (relationships, synthesis) reference these IDs without ambiguity
- Human-readable for debugging and spot-checking

### Provenance Metadata

Every node carries full source tracking:
```json
{
  "id": "doc003-p012-c02-PER-01",
  "type": "Persona",
  "label": "Growth-Oriented Learner",
  "description": "...",
  "provenance": {
    "doc_id": "doc003",
    "doc_name": "cognitive_patterns.pdf",
    "page_num": 12,
    "chunk_id": "c02",
    "extraction_phase": "phase1"
  }
}
```

---

## Configuration Philosophy

Everything is configurable. The pipeline is an execution engine, not a decision-maker.

### Schema Definition

The pipeline is domain-agnostic. Define your ontology in a YAML or JSON configuration file—the same engine adapts to any schema.

**Example 1: Persona Ontology** (`config/schema/persona.yaml`)
```yaml
node_types:
  Persona:
    code: "PER"
    fields:
      worldview: string
      core_values: list[string]
      communication_style: enum[directive, socratic, nurturing, analytical]
      evidence_strength: float  # 0.0 - 1.0
  Value:
    code: "VAL"
    fields:
      polarity: enum[positive, caution, taboo]
      strength: float
      context: string
  ReasoningPattern:
    code: "REA"
    fields:
      trigger: string
      preferred_response: string
      failure_mode: string
  LinguisticStyle:
    code: "LIN"
    fields:
      formality: enum[casual, professional, academic]
      complexity: enum[simple, moderate, technical]
      example_phrases: list[string]

edge_types:
  - persona_has_value
  - persona_uses_reasoning
  - value_conflicts_with
  - reasoning_supports
  - style_manifests_as
```

**Example 2: Research Ontology** (`config/schema/research.yaml`)
```yaml
node_types:
  Concept:
    code: "CON"
    fields:
      definition: string
      domain: string
      novelty: float
  Method:
    code: "MET"
    fields:
      procedure: string
      constraints: list[string]
      validation: string
  Finding:
    code: "FIN"
    fields:
      claim: string
      confidence: float
      limitations: string
  Author:
    code: "AUT"
    fields:
      name: string
      affiliation: string

edge_types:
  - concept_defined_by
  - method_produces_finding
  - finding_supports_concept
  - author_contributes
  - concept_contradicts
```

**Configuration File** (`config/run_config.yaml`)
```yaml
# Point to your chosen ontology
schema_path: "config/schema/persona.yaml"

# Switching domains is a one-line change:
# schema_path: "config/schema/research.yaml"
```

**The schema defines the application**—same pipeline, infinite use cases.

### Prompt Configuration (prompts.py)
```python
# Phase 1: Node Extraction Prompt
# Variables injected: {node_types}, {chunk_text}, {doc_id}, {page_id}, {chunk_id}
PHASE1_PROMPT = """
You are extracting structured concepts from text.

NODE TYPES TO EXTRACT:
{node_types}

INSTRUCTIONS:
- Identify concepts that match the defined node types
- Rate importance from 0.000 (trivial) to 1.000 (foundational)
- Be conservative: extract only clear, distinct concepts
- Include type-specific fields as defined in the schema
- Return valid JSON only

SOURCE CONTEXT:
- Document: {doc_id}
- Page: {page_id}
- Chunk: {chunk_id}

TEXT TO ANALYZE:
{chunk_text}

OUTPUT FORMAT:
{{
  "nodes": [
    {{
      "type": "Persona",
      "label": "Brief concept label",
      "description": "Clear description of the concept",
      "tags": ["tag1", "tag2"],
      "importance": 0.750,
      "fields": {{
        "worldview": "...",
        "core_values": ["value1", "value2"],
        "communication_style": "socratic"
      }}
    }}
  ]
}}

Note: Node IDs will be auto-generated as {doc_id}-{page_id}-{chunk_id}-{type_code}-{seq}
"""

# Phase 2: Relationship Extraction Prompt
# Variables injected: {edge_types}, {nodes}, {chunk_text}
PHASE2_PROMPT = """
You are identifying relationships between concepts.

RELATIONSHIP TYPES AVAILABLE:
{edge_types}

NODES FROM THIS CHUNK:
{nodes}

INSTRUCTIONS:
- Identify relationships between the listed nodes
- Only use the defined relationship types
- Skip relationships if a node has 'duplicate_of' flag pointing to another node
- Rate confidence from 0.000 (uncertain) to 1.000 (explicit)
- Rate weight from 0.000 (weak) to 1.000 (strong)
- Return valid JSON only

TEXT FOR CONTEXT:
{chunk_text}

OUTPUT FORMAT:
{{
  "edges": [
    {{
      "source_id": "doc003-p012-c02-PER-01",
      "target_id": "doc003-p012-c02-VAL-03",
      "relation": "persona_has_value",
      "weight": 0.800,
      "confidence": 0.900,
      "evidence": "Brief quote or reference from text"
    }}
  ]
}}

Note: Use the exact node IDs provided in the NODES list above.
"""

# Phase 3: Cross-Document Synthesis Prompt
# Variables injected: {edge_types}, {cluster_nodes}
PHASE3_PROMPT = """
You are identifying relationships between concepts from different documents or pages.

RELATIONSHIP TYPES AVAILABLE:
{edge_types}

CONCEPTS TO ANALYZE:
{cluster_nodes}

CONTEXT:
- These concepts are semantically similar (cosine similarity ≥ 0.88)
- They come from different documents, pages, or chunks
- Look for how they reinforce, contradict, refine, or elaborate each other

INSTRUCTIONS:
- Identify cross-document/cross-page relationships
- Only create edges when connection is clear from the descriptions
- Rate confidence from 0.000 (inferred) to 1.000 (explicit in text)
- Optionally synthesize bridging concepts if cluster reveals gaps
- Return valid JSON only

OUTPUT FORMAT:
{{
  "edges": [
    {{
      "source_id": "doc001-p003-c01-PER-01",
      "target_id": "doc005-p042-c03-PER-02",
      "relation": "persona_refines",
      "weight": 0.750,
      "confidence": 0.600,
      "rationale": "Both describe growth mindset; doc005 adds failure-tolerance dimension"
    }}
  ],
  "new_nodes": [
    {{
      "type": "Persona",
      "label": "Bridging concept missing from extraction",
      "description": "Why this concept connects the cluster",
      "tags": ["synthesized", "cross-document"],
      "importance": 0.500,
      "fields": {{}}
    }}
  ]
}}

Note: New nodes will receive auto-generated IDs with 'synth' document prefix.
"""
```

### Processing Configuration

**All configuration lives in YAML** (`config/run_config.yaml`)—no hardcoded values.

```yaml
# PDF & Chunking
pdf_extractor: "pdfplumber"  # or "pymupdf"
chunk_size: 1400  # tokens
chunk_overlap: 200
tokenizer: "cl100k_base"  # OpenAI tokenizer; adjust per your models

# LLM Provider: Vercel AI Gateway (day-one integration)
api_gateway: "vercel"
api_key_env: "VERCEL_AI_GATEWAY_KEY"  # Read from environment

# Phase 1: Node extraction
phase1:
  model: "vercel:openai/gpt-4o-mini"  # Fast & cheap for extraction
  prompt_template: "prompts/phase1_extraction.txt"
  parallel: true
  max_workers: 10
  
# Phase 2: Local relationships
phase2:
  model: "vercel:anthropic/claude-3-5-sonnet"  # Precise for relationships
  prompt_template: "prompts/phase2_relationships.txt"
  importance_threshold: 0.500  # Only process high-value nodes
  parallel: true
  max_workers: 10
  
# Phase 3: Global synthesis
phase3:
  model: "vercel:anthropic/claude-3-5-sonnet"
  prompt_template: "prompts/phase3_synthesis.txt"
  embedding_model: "vercel:openai/text-embedding-3-large"
  embedding_cache: "outputs/embeddings.db"  # SQLite cache for reuse
  importance_threshold: 0.600
  similarity_threshold: 0.88  # Cosine similarity for clustering

# Token Budget & Cost Control
token_budget:
  max_tokens_per_run: 150000  # Hard ceiling
  warn_at_percentage: 80  # Alert at 120k tokens
  pause_before_phase: true  # Prompt user before each phase starts
  
# Execution Control
run_mode: "full"  # Options: "full", "phase1", "phase2", "phase3"
resume_from: null  # Options: null, "phase2", "phase3"
run_state_file: "outputs/run_state.json"  # Tracks progress for resume

# Duplicate Handling
duplicates:
  enable_intra_chunk_collapse: false  # Set true for large corpuses
  track_frequency: true  # Always count duplicate observations
```

### How Prompts Work
The pipeline injects configuration variables into prompts at runtime:

```python
# Example: Phase 1 execution
formatted_prompt = PHASE1_PROMPT.format(
    node_types=schema['node_types'],  # From YAML schema
    chunk_text=current_chunk,
    doc_id=document_id,
    page_id=page_identifier,
    chunk_id=chunk_identifier
)
# Send formatted_prompt to LLM via Vercel AI Gateway
```

**Variables automatically injected**:
- `{node_types}`: Node categories from your schema YAML
- `{edge_types}`: Relationship types from your schema YAML
- `{chunk_text}`: Current text being processed
- `{nodes}`: Previously extracted nodes (Phase 2/3)
- `{doc_id}`, `{page_id}`, `{chunk_id}`: Full provenance tracking
- `{cluster_nodes}`: Semantically similar nodes (Phase 3 only)

### Why This Matters
- **Schema changes**: Edit config, prompts update automatically
- **Prompt iteration**: Tweak instructions without touching code
- **Model experimentation**: Try GPT vs Claude without refactoring
- **Cost optimization**: Adjust thresholds to control token usage
- **Domain adaptation**: Same codebase works for any extraction task
- **Testing workflow**: Run phase-by-phase, review outputs, continue
- **Performance**: Parallel processing for large document sets

---

## Design Decisions (Why Not Something Else)

**Why multiple passes?**
- Can't identify relationships without first knowing what concepts exist
- Can't find cross-document patterns without first extracting local relationships
- Each pass operates on different data: chunks → nodes → clusters

**Why filter by importance?**
- Not all concepts matter equally
- Processing low-value nodes wastes tokens
- Quality over quantity

**Why JSONL not a database?**
- Append-only files are simple
- No setup overhead
- Easy for downstream systems to consume
- Incremental processing (add PDFs without reprocessing)

**Why embeddings for Phase 3?**
- Semantic similarity is cheap compared to LLM comparisons
- Enables efficient clustering without exhaustive pairwise analysis
- Pay only when needed for cross-document synthesis

**When are embeddings generated?**
- Immediately after Phase 1 completes (or incrementally as nodes are extracted)
- Input: `"{label}. {description}. tags: {tags}"` (~150 tokens per node)
- Cached to SQLite (`outputs/embeddings.db`) keyed by node ID
- Phase 2 doesn't need embeddings, so skipping them saves cost
- Phase 3 reads from cache—no re-embedding unless nodes are modified
- If you later enrich a node (e.g., via LLM curation), re-embed only that subset

**Why parallel processing?**
- Phase 1 and 2 are bottlenecks for large document sets (1000+ chunks)
- Each chunk/cluster is independent (no shared state)
- 5-10x speedup with simple threading
- Rate limiting prevents API throttling

**Why phase control?**
- Test and validate outputs incrementally
- Review extractions before committing to expensive synthesis
- Resume from checkpoints without reprocessing
- Essential for iteration and debugging

**How we handle duplicates?**

LLMs sometimes extract the same concept multiple times, especially across overlapping chunks. We maximize signal while mitigating noise:

**Tracking Without Skipping**
1. Every extracted node gets written to `nodes.jsonl` (no silent filtering)
2. Compute deterministic hash: `SHA1(node_type | lowercase(label) | lowercase(description[:200]))`
3. When hash repeats:
   - New node gets `duplicate_of: <canonical_id>` field
   - Canonical node's `frequency_count` increments
   - Both nodes remain in the graph for maximum interconnectedness

**Optional: Intra-Chunk Collapse**

For large document sets (500+ chunks), enable a lightweight mid-phase script:
- Runs after Phase 1 completes
- Collapses nodes with identical hashes **from the same chunk only**
  (These are almost always accidental duplicates from prompt repetition)
- Cross-chunk duplicates are preserved—they may represent legitimate concept reinforcement
- No LLM calls; purely deterministic

**When Phase 2 Sees Duplicates**

The relationship extraction prompt can check the `duplicate_of` flag:
- Skip creating edges between a node and its canonical twin
- Preserves edges from different chunks that reinforce the same concept

**Post-Pipeline LLM Curation**

After Phase 3, run a separate analysis step:
1. Sample high-frequency duplicates (e.g., `frequency_count > 5`)
2. Ask LLM: "Are these distinct concepts or should they merge?"
3. Generate merge recommendations without reprocessing PDFs
4. Apply rewiring script to update `edges.jsonl`

**Decision Guide**
- **Enable intra-chunk collapse**: Large corpuses (>500 chunks), need speed
- **Defer to post-pipeline curation**: Smaller sets, want manual control, research use cases
- **Hybrid approach**: Collapse obvious duplicates, curate edge cases later

---

## Use Cases

**Persona Modeling**
- Extract cognitive patterns (worldview, style, reasoning, values)
- Build behavioral ontology for AI persona systems
- Enable consistent voice and perspective in RAG responses

**Domain Knowledge Extraction**
- Technical documentation → concept graphs
- Research papers → methodology relationships
- Policy documents → requirement dependencies

**Conceptual Frameworks**
- Philosophical texts → belief systems
- Strategic documents → goal hierarchies
- Educational content → learning pathways

**The schema defines the application.**

---

## Success Criteria

The pipeline succeeds if:

1. **It runs**: End-to-end execution on your PDFs without manual intervention (with optional user checkpoints)
2. **Output is valid**: JSONL conforms to your defined schema with proper provenance
3. **Results are useful**: Downstream RAG system produces better responses using the graph
4. **It's tunable**: Changing config YAML produces predictable changes in output
5. **It scales**: Adding new PDFs doesn't require reprocessing existing ones
6. **It's cost-controlled**: Token budgets prevent surprise bills; resume from any checkpoint
7. **It's versatile**: Switching ontologies (persona → research → policy) requires only config changes

**Quality is measurable**:
- Precision: Are extracted nodes actually relevant?
- Coverage: Did it capture the important concepts?
- Coherence: Do relationships make sense?
- Provenance: Can every node be traced back to source?
- Deduplication: Are obvious duplicates flagged without losing signal?
- Utility: Does the RAG system perform better with this graph?

---

## Operational Features

### Schema Validation & Logging Guardrails

- **Validation script** (`scripts/validate_outputs.py`) is standard-library only. It loads `persona_schema.yaml`, streams JSONL lines, and rejects any record missing required keys, mis-typed fields, or dangling edge references. The pipeline must pass this check before every phase transition.
- **Logging configuration** originates in `config/run_config.yaml` and feeds Python's built-in `logging` module. Each phase logs start/end, token counts, and validation failures to either stdout or `outputs/run.log` depending on config.
- **Token reporting** mirrors the development plan’s `token_reporting` settings so human operators see usage before approving the next phase—no hidden state.

These guardrails keep the system deterministic and debuggable without introducing new dependencies.

### Phase Control
```bash
# Run entire pipeline
python ingest_pdfs.py --run-mode full

# Stop after Phase 1 (review node extractions)
python ingest_pdfs.py --run-mode phase1

# Run Phase 1+2, stop before synthesis
python ingest_pdfs.py --run-mode phase2

# Resume from Phase 2 (skip completed Phase 1)
python ingest_pdfs.py --resume-from phase2
```

**How it works**:
- Each phase writes output to disk
- Pipeline checks for existing outputs before running
- Review intermediate results, adjust config, continue
- Zero complexity—just file existence checks

### Parallel Processing

**Phase 1 & 2**: Process chunks concurrently
- Configurable worker count (respects API rate limits)
- 5-10x speedup on large document sets
- Simple `ThreadPoolExecutor` implementation

**Phase 3**: Serial processing (fewer calls, less benefit from parallelism)

**Rate limiting**: Built-in to prevent API throttling

### Token Budget & Cost Control

The pipeline prevents runaway costs through proactive estimation and user checkpoints.

**Before Each Phase Starts**
1. **Estimate tokens**: Count chunks × avg tokens per prompt
2. **Check budget**: Compare against `max_tokens_per_run` from config
3. **Warn user** if threshold exceeded:
   ```
   Phase 2 estimated: 45,000 tokens
   Current usage: 82,000 / 150,000 (55%)
   Proceeding will reach: 127,000 tokens (85%)
   
   Continue? [y/N]: _
   ```
4. **On 'N'**: Write `run_state.json` with exact resume point
5. **On 'y'**: Proceed and update token counter

**Resume Workflow**
```bash
# Pipeline paused after Phase 1
python ingest_pdfs.py --resume

# Reads run_state.json:
# {"last_completed": "phase1", "next_chunk": 0, "tokens_used": 82000}
# Skips Phase 1, continues from Phase 2 chunk 0
```

**State File Format** (`outputs/run_state.json`)
```json
{
  "run_id": "20251129_143052",
  "last_completed_phase": "phase1",
  "next_phase": "phase2",
  "next_chunk_index": 0,
  "tokens_used": 82000,
  "tokens_budget": 150000,
  "timestamp": "2025-11-29T14:45:23Z"
}
```

**Benefits**
- No wasted work: resume from exact stopping point
- No surprise bills: user controls when to proceed
- No complexity: simple file-based checkpointing

**Vercel AI Gateway Integration**

All LLM calls route through a single API key:
```python
# .env file
VERCEL_AI_GATEWAY_KEY=your_key_here
```

The gateway provides:
- Access to 100+ models (OpenAI, Anthropic, Mistral, Llama, etc.)
- Built-in rate limiting and retry logic
- Usage tracking across providers
- Cost optimization (automatic model selection by price/quality)

Configure models using `vercel:provider/model` syntax:
- `vercel:openai/gpt-4o-mini` — Fast extraction
- `vercel:anthropic/claude-3-5-sonnet` — Precise synthesis
- `vercel:mistral/mistral-large-latest` — Cost-optimized alternative

---

## From Graph to RAG: Deployment Workflow

The extraction pipeline produces `nodes.jsonl` and `edges.jsonl`. Here's how to use them in a Next.js chatbot with AI persona.
### Step 1: Build Persona Sheet (One-Time)

After extraction completes, generate a structured system prompt using only standard-library data structures:

```python
# scripts/build_persona_sheet.py
import json
from collections import defaultdict

def load_jsonl(path):
  with open(path, "r", encoding="utf-8") as fh:
    for line in fh:
      yield json.loads(line)

nodes = list(load_jsonl("outputs/nodes.jsonl"))
edges = list(load_jsonl("outputs/edges.jsonl"))

nodes_by_id = {node["id"]: node for node in nodes}
edges_from = defaultdict(list)
for edge in edges:
  edges_from[edge["source_id"]].append(edge)

persona_ids = [node_id for node_id, node in nodes_by_id.items() if node.get("type") == "Persona"]
primary_id = max(persona_ids, key=lambda node_id: nodes_by_id[node_id].get("importance", 0))

def collect_targets(source_id, target_type, limit):
  collected = []
  for edge in edges_from.get(source_id, []):
    target = nodes_by_id.get(edge["target_id"])
    if target and target.get("type") == target_type:
      collected.append(target)
  return collected[:limit]

primary = nodes_by_id[primary_id]
values = collect_targets(primary_id, "Value", 5)
reasoning = collect_targets(primary_id, "ReasoningPattern", 3)
styles = collect_targets(primary_id, "LinguisticStyle", 2)

def format_value(value_node):
  return f"- {value_node['label']}: {value_node['description']} (strength: {value_node['fields'].get('strength', 'n/a')})"

def format_reasoning(reason_node):
  fields = reason_node["fields"]
  return f"- {fields.get('trigger', 'Trigger')} → {fields.get('preferred_response', 'Response')}"

style_desc = styles[0]["fields"] if styles else {}

persona_prompt = f"""
You are {primary['label']}.

WORLDVIEW:
{primary['fields'].get('worldview', 'Not specified')}

CORE VALUES:
{chr(10).join(format_value(v) for v in values) or '- None captured -'}

REASONING PATTERNS:
{chr(10).join(format_reasoning(r) for r in reasoning) or '- None captured -'}

COMMUNICATION STYLE:
- Formality: {style_desc.get('formality', 'adaptive')}
- Complexity: {style_desc.get('complexity', 'moderate')}
- Signature Phrases: {', '.join(style_desc.get('example_phrases', [])[:3]) or 'Not recorded'}

When responding:
1. Stay consistent with these values and patterns
2. Use the reasoning approaches described above
3. Match the communication style
4. Reference source material when relevant
"""

with open("outputs/persona_prompt.txt", "w", encoding="utf-8") as fh:
  fh.write(persona_prompt.strip() + "\n")
```

### Step 2 & 3: Future RAG Integration (Optional)

- **Vector indexing** and **chat surface integration** require third-party services (Pinecone, Next.js, etc.). Those remain intentionally out of scope for the current build to honor the “no extra software” constraint.
- When the core pipeline proves its value, revisit the original Step 2/3 sketches (stored in version control history) or design a bespoke retrieval layer that still respects the minimal-dependency philosophy.

### Why This Works

1. **Persona sheet** = Static snapshot of core identity (worldview, values, style)
2. **Vector index** = Dynamic retrieval of relevant evidence and concepts
3. **Graph structure** = Traversal ensures connected concepts stay coherent
4. **No reprocessing** = PDFs processed once; persona can be remixed via different traversals

**Alternative Formatters**
- Policy compliance checker: traverse from Policy → Requirement → Constraint
- Research assistant: Concept → Method → Finding pathways
- Learning guide: Concept → Prerequisite → Example chains

Same graph, infinite applications.

---

## What This Is Not

- Not a black box (every parameter is exposed)
- Not prescriptive (you define the ontology)
- Not perfect (LLMs hallucinate; we surface confidence scores)
- Not exhaustive (filtering is intentional for efficiency)
- Not static (designed for incremental updates)
- Not complex (standard library tools, simple patterns)

