#!/usr/bin/env python3
"""
Export Knowledge Graph to GraphRAG-Compatible Format
----------------------------------------------------
Converts canonical nodes and edges into standardized entities.jsonl and
relationships.jsonl files for downstream GraphRAG retrieval.

Reads:
  - outputs/nodes_canonical.jsonl (deduplicated nodes)
  - outputs/edges.jsonl (relationships)
  - config/kg_graph_export_schema.yaml (schema definition)

Writes:
  - outputs/entities.jsonl
  - outputs/relationships.jsonl

Usage:
  python scripts/export_knowledge_graph.py [--nodes outputs/nodes_canonical.jsonl] [--edges outputs/edges.jsonl]
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse
import yaml


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load the export schema configuration."""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_source_id(node_id: str) -> str:
    """Extract document ID from node ID (e.g., doc001-p006-c06-CDT-01 → doc001)."""
    parts = node_id.split('-')
    if parts and parts[0].startswith('doc'):
        return parts[0]
    return "unknown"


def extract_chunk_id(node_id: str) -> str:
    """Extract chunk ID from node ID (e.g., doc001-p006-c06-CDT-01 → c06)."""
    parts = node_id.split('-')
    for part in parts:
        if part.startswith('c') and part[1:].isdigit():
            return part
    return "unknown"


def extract_page_num(provenance: List[Dict]) -> int:
    """Extract page number from provenance list."""
    if provenance and len(provenance) > 0:
        return provenance[0].get('page_num', 0)
    return 0


def convert_node_to_entity(node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a canonical node into a GraphRAG entity record.
    
    Maps node structure:
      - label → title
      - description → description
      - type → type
      - importance → attributes.importance
      - jungian_traits → attributes.jungian_traits
      - provenance → attributes.provenance
    """
    node_id = node.get('id', 'unknown')
    
    # Build core entity
    entity = {
        'id': node_id,
        'title': node.get('label', ''),
        'type': node.get('type', 'Unknown'),
        'description': node.get('description', ''),
        'source_id': extract_source_id(node_id),
        'attributes': {
            'importance': node.get('importance', 0.5),
            'tags': node.get('tags', []),
            'jungian_traits': node.get('jungian_traits', {
                'desires': [],
                'fears': [],
                'strategies': [],
                'talents': [],
                'weaknesses': [],
                'themes': []
            }),
            'provenance': {
                'chunk_id': extract_chunk_id(node_id),
                'page_num': extract_page_num(node.get('provenance', []))
            }
        }
    }
    
    # Preserve type-specific fields if present
    if 'fields' in node:
        entity['attributes']['fields'] = node['fields']
    
    return entity


def convert_edge_to_relationship(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform an edge into a GraphRAG relationship record.
    
    Maps edge structure:
      - source_id → source
      - target_id → target
      - relation → relationship
      - evidence → description
      - weight → weight
      - confidence → confidence
    """
    source_id = edge.get('source_id', '')
    
    relationship = {
        'source': source_id,
        'target': edge.get('target_id', ''),
        'relationship': edge.get('relation', 'related_to'),
        'description': edge.get('evidence', ''),
        'weight': edge.get('weight', 0.5),
        'confidence': edge.get('confidence', 0.5),
        'source_id': extract_source_id(source_id)
    }
    
    return relationship


def export_entities(
    nodes_file: Path,
    output_file: Path
) -> int:
    """
    Export canonical nodes as entities.jsonl.
    
    Returns:
        Number of entities written
    """
    count = 0
    
    with open(nodes_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            line = line.strip()
            if not line:
                continue
                
            node = json.loads(line)
            entity = convert_node_to_entity(node)
            outfile.write(json.dumps(entity, ensure_ascii=False) + '\n')
            count += 1
    
    return count


def export_relationships(
    edges_file: Path,
    output_file: Path
) -> int:
    """
    Export edges as relationships.jsonl.
    
    Returns:
        Number of relationships written
    """
    count = 0
    
    with open(edges_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            line = line.strip()
            if not line:
                continue
                
            edge = json.loads(line)
            relationship = convert_edge_to_relationship(edge)
            outfile.write(json.dumps(relationship, ensure_ascii=False) + '\n')
            count += 1
    
    return count


def main():
    parser = argparse.ArgumentParser(
        description='Export knowledge graph to GraphRAG-compatible format'
    )
    parser.add_argument(
        '--nodes',
        type=Path,
        default=Path('outputs/nodes_canonical.jsonl'),
        help='Path to canonical nodes file (default: outputs/nodes_canonical.jsonl)'
    )
    parser.add_argument(
        '--edges',
        type=Path,
        default=Path('outputs/edges.jsonl'),
        help='Path to edges file (default: outputs/edges.jsonl)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('outputs/graphrag_export'),
        help='Output directory (default: outputs/graphrag_export)'
    )
    
    args = parser.parse_args()
    
    # Check input files
    if not args.nodes.exists():
        print(f"❌ Nodes file not found: {args.nodes}", file=sys.stderr)
        sys.exit(1)
    
    if not args.edges.exists():
        print(f"❌ Edges file not found: {args.edges}", file=sys.stderr)
        sys.exit(1)
    
    # Ensure output directory exists (clean slate)
    import shutil
    if args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define output files
    entities_file = args.output_dir / 'entities.jsonl'
    relationships_file = args.output_dir / 'relationships.jsonl'
    
    print("=" * 60)
    print("KNOWLEDGE GRAPH EXPORT")
    print("=" * 60)
    print(f"Source nodes:       {args.nodes}")
    print(f"Source edges:       {args.edges}")
    print(f"Output entities:    {entities_file}")
    print(f"Output relationships: {relationships_file}")
    print()
    
    # Export entities
    print("Exporting entities...")
    entity_count = export_entities(args.nodes, entities_file)
    print(f"✓ Wrote {entity_count} entities to {entities_file}")
    
    # Export relationships
    print("Exporting relationships...")
    relationship_count = export_relationships(args.edges, relationships_file)
    print(f"✓ Wrote {relationship_count} relationships to {relationships_file}")
    
    # Copy reference documentation
    print()
    print("Copying reference documentation...")
    import shutil
    config_dir = Path('config')
    
    reference_files = [
        'jungian_archetype_mapping.yaml',
        'jungian_traits.yaml',
        'kg_graph_export_schema.yaml'
    ]
    
    for ref_file in reference_files:
        src = config_dir / ref_file
        dst = args.output_dir / ref_file
        if src.exists():
            shutil.copy(src, dst)
            print(f"✓ Copied {ref_file}")
    
    # Create README
    readme_path = args.output_dir / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"""# GraphRAG Knowledge Graph Export

Generated: {Path(args.nodes).stat().st_mtime}

## Contents

### Core Data Files
- **entities.jsonl** - {entity_count} entities (character traits, reasoning patterns, linguistic styles)
- **relationships.jsonl** - {relationship_count} relationships between entities

### Reference Documentation
- **jungian_archetype_mapping.yaml** - Maps the 12 Jungian archetypes and their trait signatures
- **jungian_traits.yaml** - Complete taxonomy of psychological traits used in entity extraction
- **kg_graph_export_schema.yaml** - Schema definition and query examples

## Entity Structure

Each entity in `entities.jsonl` contains:
- `id` - Unique identifier
- `title` - Entity label/name
- `type` - Entity type (CharacterTrait, ReasoningPattern, LinguisticStyle, Drive)
- `description` - Detailed description
- `source_id` - Source document identifier
- `attributes` - Rich metadata including:
  - `importance` - Relevance score (0.0-1.0)
  - `jungian_traits` - Psychological trait tags (desires, fears, strategies, talents, weaknesses, themes)
  - `provenance` - Source tracking (chunk_id, page_num)
  - `fields` - Type-specific additional data

## Relationship Structure

Each relationship in `relationships.jsonl` contains:
- `source` - Source entity ID
- `target` - Target entity ID
- `relationship` - Relationship type
- `description` - Evidence/context for the relationship
- `weight` - Relationship strength (0.0-1.0)
- `confidence` - Extraction confidence (0.0-1.0)
- `source_id` - Source document identifier

## Usage with GraphRAG

1. Import `entities.jsonl` and `relationships.jsonl` into your graph database
2. Use `jungian_archetype_mapping.yaml` to query entities by archetype alignment
3. Filter entities by `importance` score for focused retrieval
4. Leverage `jungian_traits` for semantic similarity searches

## Jungian Archetype System

Entities are tagged with psychological traits that map to 12 Jungian archetypes:

**Ego** (Leave a Mark): Innocent, Hero, Magician  
**Order** (Provide Structure): Caregiver, Ruler, Creator  
**Social** (Connect to Others): Everyman, Lover, Jester  
**Freedom** (Yearn for Paradise): Explorer, Sage, Rebel

See `jungian_archetype_mapping.yaml` for complete trait signatures.
""")
    print(f"✓ Created README.md")
    
    print()
    print("=" * 60)
    print("EXPORT SUMMARY")
    print("=" * 60)
    print(f"Output directory:   {args.output_dir}")
    print(f"Entities:           {entity_count}")
    print(f"Relationships:      {relationship_count}")
    print(f"Reference docs:     {len(reference_files)}")
    print()
    print("✓ Knowledge graph export complete!")
    print()
    print(f"📁 All GraphRAG files are in: {args.output_dir.absolute()}")


if __name__ == '__main__':
    main()
