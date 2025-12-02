# Knowledge Graph Export Guide

## Overview

After running the pipeline through Phase 3, you have:
- `outputs/nodes_canonical.jsonl` – 123 deduplicated entities
- `outputs/edges.jsonl` – 137 relationships

These can be exported to **GraphRAG-compatible format** for downstream retrieval and querying.

---

## Export to GraphRAG Format

### Basic Export

```bash
python scripts/export_knowledge_graph.py
```

**Output:**
- `outputs/entities.jsonl` – All nodes in standardized entity format
- `outputs/relationships.jsonl` – All edges in standardized relationship format

### Custom Paths

```bash
python scripts/export_knowledge_graph.py \
  --nodes outputs/nodes_canonical.jsonl \
  --edges outputs/edges.jsonl \
  --output-dir exports/
```

---

## Entity Schema

Each line in `entities.jsonl` is a JSON object:

```json
{
  "id": "doc001-p006-c06-CDT-01",
  "title": "Intellectual Resilience",
  "type": "CharacterTrait",
  "description": "Maintaining analytical perspective during extreme trauma",
  "source_id": "doc001",
  "attributes": {
    "importance": 0.95,
    "tags": ["psychological"],
    "jungian_traits": {
      "desires": ["find_truth"],
      "fears": ["powerlessness"],
      "strategies": ["seek_information_knowledge"],
      "talents": ["wisdom_intelligence", "realism_empathy"],
      "weaknesses": [],
      "themes": ["knowledge"]
    },
    "provenance": {
      "chunk_id": "c06",
      "page_num": 6
    }
  }
}
```

**Fields:**
- `id` – Unique node identifier
- `title` – Human-readable label
- `type` – CharacterTrait | Value | Drive | ReasoningPattern | LinguisticStyle
- `description` – Conceptual synthesis
- `source_id` – Document provenance (doc###)
- `attributes.importance` – Extraction confidence (0-1)
- `attributes.jungian_traits` – Trait tags for archetype filtering
- `attributes.provenance` – Chunk and page metadata

---

## Relationship Schema

Each line in `relationships.jsonl` is a JSON object:

```json
{
  "source": "doc001-p003-c03-REA-01",
  "target": "doc001-p003-c03-CDT-01",
  "relationship": "causes",
  "description": "Prisoners systematically evaluated survival strategies, directly generating a pragmatic approach focused solely on immediate self-preservation.",
  "weight": 0.95,
  "confidence": 0.95,
  "source_id": "doc001"
}
```

**Fields:**
- `source` / `target` – Entity IDs
- `relationship` – causes | conflicts_with | evidences | reinforces
- `description` – Conceptual rationale (no narrative quotes)
- `weight` – Relationship strength (0-1)
- `confidence` – Extraction confidence (0-1)
- `source_id` – Document provenance

---

## Query by Archetype

### List Archetypes

12 Jungian archetypes available (defined in `config/jungian_archetype_mapping.yaml`):

**Ego** (Leave a Mark on the World):
- Innocent, Hero, Magician

**Order** (Provide Structure):
- Caregiver, Ruler, Creator

**Social** (Connect to Others):
- Everyman, Lover, Jester

**Freedom** (Yearn for Paradise):
- Explorer, Sage, Rebel

### Query by Archetype

```bash
# Get top 20 "Sage" entities
python scripts/query_by_archetype.py --archetype Sage --top-k 20

# Filter by threshold (≥0.6 score)
python scripts/query_by_archetype.py --archetype Hero --threshold 0.7

# Save to file
python scripts/query_by_archetype.py --archetype Ruler --output outputs/ruler_subgraph.json
```

**Output Format:**
```json
{
  "archetype": "Sage",
  "cardinal_orientation": "freedom",
  "entity_count": 20,
  "relationship_count": 15,
  "entities": [
    {
      "id": "doc001-p006-c06-REA-01",
      "title": "Survival Curiosity",
      "type": "ReasoningPattern",
      "description": "Emotional distancing through analytical observation",
      "importance": 0.85,
      "archetype_score": 1.0,
      "traits": {...}
    }
  ],
  "relationships": [...]
}
```

---

## Archetype Scoring Algorithm

Entities are scored by **weighted trait overlap** with archetype signature:

### Weights (from `config/kg_graph_export_schema.yaml`)
- `desires`: 3.0
- `fears`: 3.0
- `strategies`: 2.0
- `talents`: 2.0
- `weaknesses`: 1.5
- `themes`: 1.0

### Formula

For each trait category:
1. Find overlap between entity traits and archetype signature
2. Compute ratio: `overlap_count / signature_count`
3. Multiply by category weight
4. Sum across all categories and normalize by total possible weight

### Example: Sage Archetype

**Signature** (from `jungian_archetype_mapping.yaml`):
```yaml
Sage:
  trait_signature:
    desires: ["find_truth"]
    fears: ["being_duped_ignorance"]
    strategies: ["seek_information_knowledge"]
    talents: ["wisdom_intelligence"]
```

**Entity** (ReasoningPattern):
```json
{
  "desires": ["find_truth"],
  "fears": ["being_duped_ignorance"],
  "strategies": ["seek_information_knowledge"],
  "talents": ["wisdom_intelligence"]
}
```

**Score Calculation:**
- desires: (1/1) × 3.0 = 3.0
- fears: (1/1) × 3.0 = 3.0
- strategies: (1/1) × 2.0 = 2.0
- talents: (1/1) × 2.0 = 2.0
- **Total**: 10.0 / 10.0 = **1.0** (perfect match)

---

## Integration with GraphRAG Systems

### Neo4j Import

```cypher
// Import entities
LOAD CSV WITH HEADERS FROM 'file:///entities.jsonl' AS row
CREATE (e:Entity {
  id: row.id,
  title: row.title,
  type: row.type,
  description: row.description
});

// Import relationships
LOAD CSV WITH HEADERS FROM 'file:///relationships.jsonl' AS row
MATCH (source:Entity {id: row.source})
MATCH (target:Entity {id: row.target})
CREATE (source)-[r:RELATES {
  type: row.relationship,
  description: row.description,
  weight: toFloat(row.weight)
}]->(target);
```

### LangChain GraphRAG

```python
from langchain.graphs import Neo4jGraph

graph = Neo4jGraph(url="bolt://localhost:7687")

# Load entities
with open("outputs/entities.jsonl") as f:
    for line in f:
        entity = json.loads(line)
        graph.query(
            "CREATE (e:Entity {id: $id, title: $title, type: $type})",
            params=entity
        )

# Load relationships
with open("outputs/relationships.jsonl") as f:
    for line in f:
        rel = json.loads(line)
        graph.query(
            "MATCH (s:Entity {id: $source}), (t:Entity {id: $target}) "
            "CREATE (s)-[r:RELATES {type: $relationship}]->(t)",
            params=rel
        )
```

### Vector Store Integration

Combine entity descriptions with vector embeddings:

```python
import openai

# Generate embeddings for entity titles + descriptions
with open("outputs/entities.jsonl") as f:
    for line in f:
        entity = json.loads(line)
        text = f"{entity['title']}: {entity['description']}"
        embedding = openai.Embedding.create(
            input=text,
            model="text-embedding-3-small"
        )
        # Store embedding + entity in Pinecone/Weaviate/Qdrant
```

---

## Next Steps

1. **Import into GraphRAG system** – Use entities.jsonl & relationships.jsonl
2. **Query by archetype** – Filter subgraphs for persona-specific retrieval
3. **Combine with vector search** – Hybrid retrieval (semantic + graph structure)
4. **Iterate on extraction** – Re-run pipeline with refined prompts/importance thresholds

See `config/kg_graph_export_schema.yaml` for full technical specification.
