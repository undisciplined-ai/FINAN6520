# Knowledge Graph Pipeline

> Extract persona knowledge graphs from PDFs using LLM-powered concept extraction.

## Overview

This pipeline transforms **PDFs or audio files** (M4B audiobooks) into structured knowledge graphs containing 5 node types (CharacterTrait, Value, Drive, ReasoningPattern, LinguisticStyle) and 4 relationship types designed for downstream RAG consumers.

For audio files, the pipeline first transcribes them using OpenAI Whisper API with parallel processing, then extracts knowledge graphs from the transcripts.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**For audio transcription (M4B files):**
- Install ffmpeg: `sudo apt install ffmpeg` (Linux) or `brew install ffmpeg` (macOS)
- Get OpenAI API key from https://platform.openai.com/api-keys

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add:
#   - OPENAI_API_KEY (for audio transcription)
#   - AI_GATEWAY_API_KEY (for KG extraction)
```

### 3. Validate Setup

```bash
python scripts/validate_outputs.py examples/nodes.jsonl examples/edges.jsonl
```

Expected output: `✅ VALIDATION PASSED`

## Directory Structure

```
kg_pipeline/
├── config/
│   ├── persona_schema.yaml    # Node/edge type definitions
│   ├── kg_graph_export_schema.yaml # GraphRAG export + archetype query spec
│   └── run_config.yaml         # Processing parameters
├── docs/
│   ├── api_reference.md        # Vercel AI Gateway API docs
│   ├── pdfplumber_quickref.md  # PDF extraction reference
│   └── python_patterns.md      # Code patterns from Module 10
├── examples/
│   ├── chunks.jsonl            # Example chunked text
│   ├── nodes.jsonl             # Example extracted nodes
│   └── edges.jsonl             # Example relationships
├── outputs/                    # Generated files (git-ignored)
├── prompts/
│   ├── phase1_extraction.txt   # Node extraction template
│   └── phase2_relationships.txt # Edge extraction template
└── scripts/
    └── validate_outputs.py     # Schema validation tool
```

## Usage

### Process PDFs

```bash
python scripts/run_pipeline.py \
  --input pdfs/document1.pdf pdfs/document2.pdf \
  --message "Extract persona knowledge graph" \
  --clean
```

### Process Audio (M4B Audiobooks)

```bash
python scripts/run_pipeline.py \
  --input audiobooks/book.m4b \
  --message "Extract persona knowledge graph from audiobook" \
  --clean
```

You can also point `--input` at a directory. The runner will recursively gather every supported file type (`.pdf`, `.m4b`, `.txt`) from that folder, so you can drop mixed media into a single `inputs/` directory and process everything in one command.

**Audio Processing Details:**
- Automatically splits M4B into 20-minute chunks (stays under Whisper API 25 MB limit)
- Transcribes chunks in parallel (8 workers by default)
- **Cost**: ~$0.36/hour of audio ($4.32 for 12-hour audiobook)
- **Speed**: ~14 minutes for 12-hour audiobook (vs. 54 minutes sequential)
- Output: `outputs/transcripts/<audiobook>.txt` → chunked → KG extraction

## Pipeline Phases

**Phase 0: Audio Transcription** (for M4B files)  
Split audio into chunks, transcribe in parallel using OpenAI Whisper API, reassemble transcript.

**Phase 1: Text Ingestion & Chunking**  
Extract text from PDFs/transcripts, split into token-aware chunks with provenance.

**Phase 2: Node Extraction**  
Send chunks to LLM to extract 5 node types with complete fields. Includes entity resolution (Phase 2.5).

**Phase 3: Relationship Extraction**  
Two-pass extraction: local relationships within chunks (parallel), then global cross-chunk relationships (sequential).

**Graph Export** (after Phase 3)  
Convert `nodes_canonical.jsonl` and `edges.jsonl` into GraphRAG-compatible format:

```bash
# Export to entities.jsonl & relationships.jsonl
python scripts/export_knowledge_graph.py

# Query by Jungian archetype
python scripts/query_by_archetype.py --archetype Sage --top-k 20 --output outputs/sage_subgraph.json
python scripts/query_by_archetype.py --archetype Hero --threshold 0.7
```

See `config/kg_graph_export_schema.yaml` for entity/relationship schema and archetype query workflow.

## Configuration

### Schema (`config/persona_schema.yaml`)

Defines 5 node types:
- **CharacterTrait**: Observable personality patterns and behaviors
- **Value**: Prescriptive principles with behavioral directives
- **Drive**: Goals, motivations, conflicts, stakes
- **ReasoningPattern**: Decision templates with triggers
- **LinguisticStyle**: Communication preferences and affect

Defines 4 edge types:
- **causes**: Source directly produces target
- **conflicts_with**: Source contradicts or undermines target
- **evidences**: Source provides concrete support for target
- **reinforces**: Source strengthens or amplifies target

### Runtime (`config/run_config.yaml`)

Processing parameters:
- Token-based chunking (1400 tokens, 200 overlap)
- Model selection (openai/gpt-4o-mini)
- Temperature, max_tokens, thresholds
- Logging and token reporting

### Graph Export (`config/kg_graph_export_schema.yaml`)

Describes how to convert canonical nodes/edges into GraphRAG-compatible format:

**Entity Schema** (`outputs/entities.jsonl`):
- id, title, type, description, source_id
- attributes.importance (0-1 score for sampling)
- attributes.jungian_traits (desires, fears, strategies, talents, weaknesses, themes)
- attributes.provenance (chunk_id, page_num)

**Relationship Schema** (`outputs/relationships.jsonl`):
- source, target, relationship, description
- weight, confidence (0-1 scores)
- source_id (document provenance)

**Archetype Query Workflow**:
1. Load archetype signature from `config/jungian_archetype_mapping.yaml`
2. Score entities by weighted trait overlap (desires/fears: 3.0, strategies/talents: 2.0, weaknesses: 1.5, themes: 1.0)
3. Filter entities with score ≥ 0.6 (or top-k)
4. Return induced subgraph (entities + connecting relationships)

Use `scripts/query_by_archetype.py` to filter the knowledge graph by any of the 12 Jungian archetypes (Innocent, Hero, Magician, Caregiver, Ruler, Creator, Everyman, Lover, Jester, Explorer, Sage, Rebel).

## Validation

The validation script ensures outputs conform to schema:

```bash
# Validate nodes only
python scripts/validate_outputs.py outputs/nodes.jsonl

# Validate nodes and edges together
python scripts/validate_outputs.py outputs/nodes.jsonl outputs/edges.jsonl
```

Checks performed:
- ID format: `doc###-p###-c##-XXX-##`
- Type codes match node types (PER, VAL, DRV, REA, LIN)
- Required fields present for each type
- Enum values within allowed sets
- Edge references point to existing nodes
- Numeric ranges (importance, weight, confidence: 0.0-1.0)

## Development

Phase 0 establishes the complete specification. Subsequent phases will reference these files as source-of-truth when implementing extraction scripts.

See `.vscode/Project/DevelopmentPlan.md` for detailed implementation guidance.
