# Knowledge Graph Pipeline

> Extract persona knowledge graphs from PDFs using LLM-powered concept extraction.

## Overview

This pipeline transforms PDF documents into structured knowledge graphs containing 6 node types (Persona, Constraint, Value, Drive, ReasoningPattern, LinguisticStyle) and 8 relationship types, then assembles them into actionable persona prompts.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Vercel AI Gateway API key
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
│   └── run_config.yaml         # Processing parameters
├── docs/
│   ├── api_reference.md        # Vercel AI Gateway API docs
│   ├── pdfplumber_quickref.md  # PDF extraction reference
│   └── python_patterns.md      # Code patterns from Module 10
├── examples/
│   ├── chunks.jsonl            # Example chunked text
│   ├── nodes.jsonl             # Example extracted nodes
│   ├── edges.jsonl             # Example relationships
│   └── persona_prompt.txt      # Example assembled prompt
├── outputs/                    # Generated files (git-ignored)
├── prompts/
│   ├── phase1_extraction.txt   # Node extraction template
│   └── phase2_relationships.txt # Edge extraction template
└── scripts/
    └── validate_outputs.py     # Schema validation tool
```

## Pipeline Phases

**Phase 0: Foundations** ✅ COMPLETE  
Configuration files, schemas, examples, and validation tooling.

**Phase 1: PDF Ingestion & Chunking** (Next)  
Extract text from PDFs, split into token-aware chunks with provenance.

**Phase 2: Node Extraction**  
Send chunks to LLM to extract 6 node types with complete fields.

**Phase 3: Relationship Extraction**  
Identify 8 relationship types between nodes within each chunk.

**Phase 4: Persona Sheet Generation**  
Traverse graph to assemble deterministic Mad-Libs persona prompts.

## Configuration

### Schema (`config/persona_schema.yaml`)

Defines 6 node types:
- **Persona**: Identity, worldview, communication style
- **Constraint**: Operational boundaries and role limits
- **Value**: Prescriptive principles with behavioral directives
- **Drive**: Goals, motivations, conflicts, stakes
- **ReasoningPattern**: Decision templates with triggers
- **LinguisticStyle**: Communication preferences and affect

Defines 8 edge types:
- persona_has_value, persona_has_drive, persona_uses_reasoning
- persona_has_style, persona_constrained_by
- value_conflicts_with, drive_blocked_by, reasoning_supports

### Runtime (`config/run_config.yaml`)

Processing parameters:
- Token-based chunking (1400 tokens, 200 overlap)
- Model selection (openai/gpt-4o-mini)
- Temperature, max_tokens, thresholds
- Logging and token reporting

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
- Type codes match node types (PER, CON, VAL, DRV, REA, LIN)
- Required fields present for each type
- Enum values within allowed sets
- Edge references point to existing nodes
- Numeric ranges (importance, weight, confidence: 0.0-1.0)

## Development

Phase 0 establishes the complete specification. Subsequent phases will reference these files as source-of-truth when implementing extraction scripts.

See `.vscode/Project/DevelopmentPlan.md` for detailed implementation guidance.
