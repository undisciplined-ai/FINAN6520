## 1. Objective

Design and implement a **Python-based ingestion and extraction pipeline** that:

1. Takes **PDF documents (anywhere from a few pages to a few hundred)** as input.
2. Extracts **persona-related cognitive patterns** (worldview, style, reasoning, values) using LLM calls.
3. Outputs a **knowledge graph in JSONL** format, conforming to a predefined minimal schema (nodes + edges) optimized for use in an AI persona system.

This is **not** a generic knowledge graph of facts. It is a **cognitive / stylistic ontology** for driving an AI’s persona.

---

## 2. In Scope

### 2.1 Data Ingestion

* Read multiple PDF files from a specified directory or manifest.
* Extract raw text per page using a robust Python PDF library (e.g. `pypdf`, `pdfplumber`).
* Preserve basic provenance:

  * `doc_id` (document-level identifier)
  * `page_number` or `chunk_id`

### 2.2 Text Chunking

* Implement a configurable chunking strategy:

  * Chunk by character or token count (target: ~500–1000 tokens per chunk).
  * Avoid splitting mid-sentence where reasonably possible.
* Associate each chunk with:

  * `doc_id`
  * `chunk_id`
  * optional page references

### 2.3 LLM-Based Extraction

* Integrate with a specified LLM API (OpenAI or similar) via a **single, well-encapsulated client module**.
* For each chunk, send a **strict extraction prompt** that instructs the model to:

  * Identify candidate nodes of types:

    * `WORLDVIEW`
    * `STYLE`
    * `REASONING`
    * `VALUE`
  * Optionally identify relations between nodes in the same chunk using the limited relation types:

    * `influences`
    * `refines`
    * `contradicts`
    * `modulates`
    * `example_of`
  * Return **valid JSON** with:

    * `nodes: [...]`
    * `edges: [...]`
* Implement basic validation:

  * JSON parse check
  * Schema sanity checks (required fields present, known types only)

### 2.4 Knowledge Graph Schema Implementation

Implement the agreed JSONL schema:

**Nodes (`nodes.jsonl`):**

Each line:

```json
{
  "id": "worldview:humans_cling_to_stories",
  "type": "WORLDVIEW",
  "label": "Humans cling to stories",
  "description": "People prefer stories over uncomfortable facts, interpreting reality through narrative.",
  "tags": ["humans", "stories", "irrationality"],
  "importance": 1,
  "sources": [
    { "doc_id": "book_01", "chunk_id": "ch_032", "note": "LLM-extracted" }
  ]
}
```

**Edges (`edges.jsonl`):**

Each line:

```json
{
  "source": "worldview:humans_cling_to_stories",
  "target": "style:narrative_observer_voice",
  "relation": "influences",
  "weight": 0.8,
  "sources": [
    { "doc_id": "book_01", "chunk_id": "ch_040", "note": "LLM-extracted" }
  ]
}
```

Required behavior:

* Append-only writes to `nodes.jsonl` and `edges.jsonl`.
* Ability to run on the same corpus multiple times with:

  * a basic deduplication strategy (e.g. hashing `type+label`), or
  * a separate “post-processing” script to dedupe nodes/edges.

### 2.5 Configuration & Extensibility

Provide configuration for:

* Chunk size and overlap.
* LLM model name / API key via environment variables.
* Output directories for nodes and edges.
* Toggle for:

  * “nodes only” vs. “nodes + edges” extraction mode.

Expose configuration as:

* `config.py` or `.env` based settings, not hard-coded values.

### 2.6 Basic Operational Tooling

Provide:

* A single CLI entry point, e.g.:

  ```bash
  python ingest_pdfs.py --input-dir ./pdfs --out-dir ./kg_output
  ```

* Logging at INFO level for:

  * number of PDFs processed
  * number of chunks generated
  * number of nodes/edges extracted
  * error chunks (LLM or parsing failures)

* Error handling:

  * Skip failed chunks, log them, do not crash the entire run.

---

## 3. Out of Scope (for this initial phase)

* No UI, dashboards, or visual graph browser.
* No vector database integration.
* No advanced graph algorithms (community detection, centrality, etc.).
* No complex ontology reasoning (inference, rule engines).
* No guarantee of *perfect* node/edge quality; this is **LLM-assisted extraction**, not a curated ontology.

The expectation is a **usable draft graph**, not a philosophically perfect one.

---

## 4. Quality & Non-Functional Expectations

### 4.1 Code Quality

* Python 3.10+ compatible.
* Clear module boundaries:

  * `pdf_ingest.py`
  * `chunking.py`
  * `llm_client.py`
  * `extraction.py`
  * `kg_writer.py`
* Type hints where reasonable.
* Minimal but clear docstrings on public functions.

### 4.2 Performance

* Target: comfortably handle **100–300 pages** (say up to ~1000+ chunks) in a single run.
* CPU-only local execution for PDF + chunking; LLM latency limits overall throughput.
* No hard in-memory scaling constraints: streaming write to JSONL.

### 4.3 Determinism / Reproducibility

* Same input PDFs + same config should produce structurally similar output, subject to LLM stochasticity.
* Extraction prompt and schema definitions must be versioned in code so changes are trackable.

---

## 5. Deliverables

1. **Python Codebase**

   * Ingest, chunk, LLM extraction, JSONL writing.
   * Minimal deduplication or a placeholder for it.

2. **Example Config & Run Instructions**

   * README with:

     * setup steps
     * environment variables
     * sample run command

3. **Sample Output**

   * `nodes.jsonl` and `edges.jsonl` produced from:

     * 1–2 example PDFs (provided by client or public domain).

4. **Prompt Specification**

   * The exact prompt used for LLM extraction, documented and checked into the repo.

---

## 6. Success Criteria

The work is considered successful if:

* Given ~100 pages of irreverent, public-domain-style text:

  * The pipeline runs end-to-end without manual intervention.
  * `nodes.jsonl` contains:

    * dozens to hundreds of nodes classified as `WORLDVIEW`, `STYLE`, `REASONING`, `VALUE`.
  * `edges.jsonl` contains:

    * a meaningful subset of `influences`, `refines`, `contradicts`, `modulates`, `example_of` relations.
* The resulting JSONL files:

  * conform to the schema
  * are easily consumable by downstream TypeScript / Next.js services
  * can be inspected by the developer to see which cognitive patterns were extracted and from where.


