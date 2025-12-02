#!/usr/bin/env python3
"""
Query Knowledge Graph by Jungian Archetype
-------------------------------------------
Filters entities and relationships to extract archetype-aligned subgraphs.

Reads:
  - outputs/entities.jsonl
  - outputs/relationships.jsonl
  - config/jungian_traits.yaml
  - config/jungian_archetype_mapping.yaml

Usage:
  python scripts/query_by_archetype.py --archetype Sage [--threshold 0.6] [--top-k 20]
  python scripts/query_by_archetype.py --archetype Hero --output outputs/hero_subgraph.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
import argparse
import yaml


def load_archetype_signature(
    archetype_name: str,
    mapping_file: Path
) -> Dict[str, Any]:
    """Load the trait signature for a given archetype."""
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mappings = yaml.safe_load(f)
    
    archetypes_dict = mappings.get('archetypes', {})
    
    # Try exact match first
    if archetype_name in archetypes_dict:
        result = archetypes_dict[archetype_name].copy()
        result['name'] = archetype_name
        return result
    
    # Try case-insensitive match
    for name, data in archetypes_dict.items():
        if name.lower() == archetype_name.lower():
            result = data.copy()
            result['name'] = name
            return result
    
    raise ValueError(f"Archetype '{archetype_name}' not found in mapping")


def compute_trait_score(
    entity_traits: Dict[str, List[str]],
    archetype_data: Dict[str, Any],
    weights: Dict[str, float]
) -> float:
    """
    Score an entity against an archetype signature using weighted trait overlap.
    
    Returns normalized score [0, 1] based on trait matches weighted by category.
    """
    archetype_signature = archetype_data.get('trait_signature', {})
    
    total_score = 0.0
    max_possible = 0.0
    
    for category, weight in weights.items():
        entity_values = set(entity_traits.get(category, []))
        signature_values = set(archetype_signature.get(category, []))
        
        if not signature_values:
            continue
        
        # Calculate overlap ratio
        overlap = len(entity_values & signature_values)
        possible = len(signature_values)
        
        category_score = (overlap / possible) * weight
        total_score += category_score
        max_possible += weight
    
    return total_score / max_possible if max_possible > 0 else 0.0


def load_entities(entities_file: Path) -> List[Dict[str, Any]]:
    """Load all entities from JSONL file."""
    entities = []
    with open(entities_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entities.append(json.loads(line))
    return entities


def load_relationships(relationships_file: Path) -> List[Dict[str, Any]]:
    """Load all relationships from JSONL file."""
    relationships = []
    with open(relationships_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                relationships.append(json.loads(line))
    return relationships


def score_entities(
    entities: List[Dict[str, Any]],
    archetype_data: Dict[str, Any],
    weights: Dict[str, float]
) -> List[tuple]:
    """
    Score all entities against archetype signature.
    
    Returns list of (entity, score) tuples sorted by score descending.
    """
    scored = []
    
    for entity in entities:
        traits = entity.get('attributes', {}).get('jungian_traits', {})
        score = compute_trait_score(traits, archetype_data, weights)
        scored.append((entity, score))
    
    return sorted(scored, key=lambda x: x[1], reverse=True)


def filter_relationships(
    relationships: List[Dict[str, Any]],
    entity_ids: Set[str]
) -> List[Dict[str, Any]]:
    """Filter relationships where both endpoints are in the entity set."""
    return [
        rel for rel in relationships
        if rel['source'] in entity_ids and rel['target'] in entity_ids
    ]


def format_subgraph_result(
    entities_scored: List[tuple],
    relationships: List[Dict[str, Any]],
    archetype_name: str,
    cardinal: str
) -> Dict[str, Any]:
    """Format query result as structured JSON."""
    return {
        'archetype': archetype_name,
        'cardinal_orientation': cardinal,
        'entity_count': len(entities_scored),
        'relationship_count': len(relationships),
        'entities': [
            {
                'id': e['id'],
                'title': e['title'],
                'type': e['type'],
                'description': e['description'],
                'importance': e['attributes']['importance'],
                'archetype_score': score,
                'traits': e['attributes']['jungian_traits']
            }
            for e, score in entities_scored
        ],
        'relationships': relationships
    }


def main():
    parser = argparse.ArgumentParser(
        description='Query knowledge graph by Jungian archetype'
    )
    parser.add_argument(
        '--archetype',
        required=True,
        help='Archetype name (e.g., Sage, Hero, Ruler)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.6,
        help='Minimum normalized score for entity inclusion (default: 0.6)'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        help='Limit to top K entities (overrides threshold)'
    )
    parser.add_argument(
        '--entities',
        type=Path,
        default=Path('outputs/entities.jsonl'),
        help='Path to entities file'
    )
    parser.add_argument(
        '--relationships',
        type=Path,
        default=Path('outputs/relationships.jsonl'),
        help='Path to relationships file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output JSON file (default: print to stdout)'
    )
    
    args = parser.parse_args()
    
    # Check input files
    if not args.entities.exists():
        print(f"❌ Entities file not found: {args.entities}", file=sys.stderr)
        sys.exit(1)
    
    if not args.relationships.exists():
        print(f"❌ Relationships file not found: {args.relationships}", file=sys.stderr)
        sys.exit(1)
    
    # Load configuration
    config_dir = Path('config')
    mapping_file = config_dir / 'jungian_archetype_mapping.yaml'
    
    if not mapping_file.exists():
        print(f"❌ Archetype mapping not found: {mapping_file}", file=sys.stderr)
        sys.exit(1)
    
    # Load archetype signature
    print(f"Loading archetype signature for '{args.archetype}'...", file=sys.stderr)
    try:
        archetype_sig = load_archetype_signature(args.archetype, mapping_file)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ Archetype: {archetype_sig['name']}", file=sys.stderr)
    print(f"  Cardinal: {archetype_sig.get('orientation', 'unknown')}", file=sys.stderr)
    trait_sig = archetype_sig.get('trait_signature', {})
    print(f"  Desires: {', '.join(trait_sig.get('desires', []))}", file=sys.stderr)
    print(f"  Fears: {', '.join(trait_sig.get('fears', []))}", file=sys.stderr)
    print(file=sys.stderr)
    
    # Define trait category weights (from schema)
    weights = {
        'desires': 3.0,
        'fears': 3.0,
        'strategies': 2.0,
        'talents': 2.0,
        'weaknesses': 1.5,
        'themes': 1.0
    }
    
    # Load data
    print("Loading entities and relationships...", file=sys.stderr)
    entities = load_entities(args.entities)
    all_relationships = load_relationships(args.relationships)
    print(f"✓ Loaded {len(entities)} entities, {len(all_relationships)} relationships", file=sys.stderr)
    print(file=sys.stderr)
    
    # Score entities
    print("Scoring entities against archetype signature...", file=sys.stderr)
    scored_entities = score_entities(entities, archetype_sig, weights)
    
    # Apply threshold or top-k filter
    if args.top_k:
        filtered = scored_entities[:args.top_k]
        print(f"✓ Selected top {len(filtered)} entities", file=sys.stderr)
    else:
        filtered = [(e, s) for e, s in scored_entities if s >= args.threshold]
        print(f"✓ Found {len(filtered)} entities with score ≥ {args.threshold}", file=sys.stderr)
    
    if not filtered:
        print(f"⚠️  No entities matched archetype '{args.archetype}'", file=sys.stderr)
        print("   Try lowering --threshold or check archetype name", file=sys.stderr)
        sys.exit(0)
    
    # Filter relationships to induced subgraph
    entity_ids = {e['id'] for e, _ in filtered}
    subgraph_rels = filter_relationships(all_relationships, entity_ids)
    print(f"✓ Induced subgraph has {len(subgraph_rels)} relationships", file=sys.stderr)
    print(file=sys.stderr)
    
    # Format result
    result = format_subgraph_result(
        filtered,
        subgraph_rels,
        archetype_sig['name'],
        archetype_sig.get('orientation', 'unknown')
    )
    
    # Output
    output_json = json.dumps(result, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"✓ Wrote subgraph to {args.output}", file=sys.stderr)
    else:
        print(output_json)
    
    # Summary to stderr
    print(file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("ARCHETYPE QUERY SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Archetype:      {archetype_sig['name']}", file=sys.stderr)
    print(f"Cardinal:       {archetype_sig.get('orientation', 'unknown')}", file=sys.stderr)
    print(f"Entities:       {len(filtered)}", file=sys.stderr)
    print(f"Relationships:  {len(subgraph_rels)}", file=sys.stderr)
    print(f"Avg Score:      {sum(s for _, s in filtered) / len(filtered):.3f}", file=sys.stderr)
    print(file=sys.stderr)
    print("Top 5 Entities:", file=sys.stderr)
    for i, (entity, score) in enumerate(filtered[:5], 1):
        print(f"  {i}. {entity['title']} ({entity['type']}) - score: {score:.3f}", file=sys.stderr)


if __name__ == '__main__':
    main()
