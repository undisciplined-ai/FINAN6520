# Phase 1: PDF Ingestion & Chunking

## Status: ✅ COMPLETE

Successfully implemented PDF text extraction and token-aware chunking with provenance metadata.

## Implementation Summary

### Script Created
- **`scripts/phase1_chunk_pdfs.py`**: Main chunking script
  - Uses `pdfplumber` for PDF text extraction
  - Token-aware chunking with `tiktoken` (OpenAI tokenizer)
  - Configurable chunk size and overlap from `run_config.yaml`
  - Generates deterministic IDs: `doc###-p###-c##`
  - Preserves provenance (doc_name, page_num)
  - Logging with configurable levels

### Key Features Implemented

**ID Generation**:
```python
doc_id = f"doc{doc_num:03d}"    # doc001, doc002, ...
page_id = f"p{page_num:03d}"    # p001, p002, ...
chunk_id = f"c{chunk_num:02d}"  # c01, c02, ...
```

**Token-Aware Chunking**:
- Target: 1400 tokens per chunk
- Overlap: 200 tokens between chunks
- Uses tiktoken with `cl100k_base` encoding
- Splits on word boundaries for readability

**Provenance Metadata**:
Each chunk includes:
- `doc_id`: Numeric document identifier
- `page_id`: Zero-padded page number
- `chunk_id`: Zero-padded chunk sequence
- `text`: Extracted text content
- `doc_name`: Original PDF filename
- `page_num`: Integer page number

### Test Results

**Test PDF**: `test_pdfs/sample_persona.pdf` (3-page teaching philosophy)

**Output**: `outputs/chunks.jsonl`
- 2 chunks created
- Chunk 1: doc001-p001-c01 (2614 chars, ~400 tokens)
- Chunk 2: doc001-p002-c01 (241 chars, ~40 tokens)

**Validation**:
```json
{
    "doc_id": "doc001",
    "page_id": "p001",
    "chunk_id": "c01",
    "text": "My Teaching Philosophy I am an educator...",
    "doc_name": "sample_persona.pdf",
    "page_num": 1
}
```

### Usage

```bash
# Single PDF
python scripts/phase1_chunk_pdfs.py test_pdfs/sample_persona.pdf

# Multiple PDFs
python scripts/phase1_chunk_pdfs.py pdfs/*.pdf

# With custom config (edit config/run_config.yaml first)
python scripts/phase1_chunk_pdfs.py input.pdf
```

### Configuration

From `config/run_config.yaml`:
```yaml
chunk_size: 1400         # tokens (not words)
chunk_overlap: 200       # tokens
tokenizer: "cl100k_base" # OpenAI tokenizer
```

### Logging Output

```
============================================================
Phase 1: PDF Ingestion & Chunking
============================================================
PDFs to process: 1
Chunk size: 1400 tokens
Overlap: 200 tokens
Output: outputs/chunks.jsonl

Processing sample_persona.pdf as doc001
  ✓ sample_persona.pdf: 2 chunks

============================================================
✅ Phase 1 Complete
Total chunks created: 2
Output written to: outputs/chunks.jsonl
============================================================
```

## Design Decisions

1. **Word-boundary chunking**: Splits on spaces rather than mid-word to preserve readability
2. **Token counting**: Uses tiktoken to match OpenAI's tokenization for accurate LLM input sizing
3. **Overlap handling**: Approximately maintains token overlap by calculating word-to-token ratios
4. **Empty page handling**: Skips pages with no extractable text
5. **Error handling**: Logs errors but continues processing remaining PDFs

## Next Phase

Phase 2 will:
- Load `outputs/chunks.jsonl`
- Send each chunk to Vercel AI Gateway with `prompts/phase1_extraction.txt`
- Extract 6 node types (Persona, Constraint, Value, Drive, ReasoningPattern, LinguisticStyle)
- Write `outputs/nodes.jsonl` with minted IDs

**Date Completed**: December 1, 2025
