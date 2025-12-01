#!/usr/bin/env python3
"""
Phase 4: Persona Sheet Generation

Traverses the knowledge graph to assemble structured persona definitions
with dynamic node selection capability.

Usage:
    python scripts/phase4_generate_persona_sheet.py
    
Requires:
    - outputs/nodes_canonical.jsonl (from Phase 2.5)
    - outputs/edges.jsonl (from Phase 3)
    
Outputs:
    - outputs/persona_sheets.json (structured persona data)
    - outputs/persona_template.txt (prompt template with [SLOTS])
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import yaml


def load_config(config_path: str = "config/run_config.yaml") -> Dict:
    """Load runtime configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def setup_logging(config: Dict) -> None:
    """Configure logging based on config settings."""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_nodes(nodes_path: str) -> Dict[str, Dict]:
    """Load canonical nodes indexed by ID."""
    nodes = {}
    with open(nodes_path, 'r') as f:
        for line in f:
            node = json.loads(line)
            nodes[node['id']] = node
    return nodes


def load_edges(edges_path: str) -> List[Dict]:
    """Load all edges."""
    edges = []
    with open(edges_path, 'r') as f:
        for line in f:
            edges.append(json.loads(line))
    return edges


def build_adjacency_list(edges: List[Dict]) -> Dict[str, List[Tuple[str, str, Dict]]]:
    """
    Build adjacency list for graph traversal.
    
    Returns:
        Dict mapping source_id -> [(target_id, relation, edge_data)]
    """
    adj = defaultdict(list)
    
    for edge in edges:
        source = edge['source_id']
        target = edge['target_id']
        relation = edge['relation']
        adj[source].append((target, relation, edge))
    
    return dict(adj)


def traverse_persona(persona_id: str, nodes: Dict[str, Dict], 
                     adjacency: Dict[str, List[Tuple]], config: Dict) -> Dict:
    """
    Traverse graph from a Persona node to gather all connected components.
    
    Args:
        persona_id: ID of the Persona node
        nodes: All nodes indexed by ID
        adjacency: Adjacency list for edges
        config: Runtime configuration
    
    Returns:
        Structured persona data with all connected nodes
    """
    persona_node = nodes[persona_id]
    
    # Initialize result structure
    result = {
        'persona_id': persona_id,
        'persona': persona_node,
        'values': [],
        'drives': [],
        'reasoning_patterns': [],
        'linguistic_styles': [],
        'constraints': [],
        'metadata': {
            'total_nodes': 1,  # Start with persona
            'total_edges': 0
        }
    }
    
    # Get outgoing edges from persona
    if persona_id not in adjacency:
        logging.warning(f"Persona {persona_id} has no outgoing edges")
        return result
    
    edges = adjacency[persona_id]
    result['metadata']['total_edges'] = len(edges)
    
    # Traverse edges and collect nodes by type
    for target_id, relation, edge_data in edges:
        if target_id not in nodes:
            logging.warning(f"Target node {target_id} not found")
            continue
        
        target_node = nodes[target_id]
        result['metadata']['total_nodes'] += 1
        
        # Package node with edge metadata
        node_with_edge = {
            'node': target_node,
            'edge': {
                'relation': relation,
                'weight': edge_data.get('weight', 0.5),
                'confidence': edge_data.get('confidence', 0.5),
                'evidence': edge_data.get('evidence', '')
            }
        }
        
        # Categorize by relationship type
        if relation == 'persona_has_value':
            result['values'].append(node_with_edge)
        elif relation == 'persona_has_drive':
            result['drives'].append(node_with_edge)
        elif relation == 'persona_uses_reasoning':
            result['reasoning_patterns'].append(node_with_edge)
        elif relation == 'persona_has_style':
            result['linguistic_styles'].append(node_with_edge)
        elif relation == 'persona_constrained_by':
            result['constraints'].append(node_with_edge)
    
    # Sort by weight (highest first)
    result['values'].sort(key=lambda x: x['edge']['weight'], reverse=True)
    result['drives'].sort(key=lambda x: x['edge']['weight'], reverse=True)
    result['reasoning_patterns'].sort(key=lambda x: x['edge']['weight'], reverse=True)
    result['linguistic_styles'].sort(key=lambda x: x['edge']['weight'], reverse=True)
    result['constraints'].sort(key=lambda x: x['edge']['weight'], reverse=True)
    
    # Apply config limits
    phase3_config = config.get('phase3', {})
    max_values = phase3_config.get('max_values', 5)
    max_reasoning = phase3_config.get('max_reasoning', 3)
    max_styles = phase3_config.get('max_styles', 2)
    
    result['values'] = result['values'][:max_values]
    result['reasoning_patterns'] = result['reasoning_patterns'][:max_reasoning]
    result['linguistic_styles'] = result['linguistic_styles'][:max_styles]
    
    return result


def generate_persona_template(persona_data: Dict) -> str:
    """
    Generate a prompt template with [SLOT] placeholders for dynamic selection.
    
    Args:
        persona_data: Structured persona data from graph traversal
    
    Returns:
        Formatted prompt template string
    """
    persona = persona_data['persona']
    fields = persona.get('fields', {})
    
    template_parts = []
    
    # Header
    template_parts.append("# PERSONA DEFINITION")
    template_parts.append("")
    template_parts.append(f"## Identity")
    template_parts.append(f"{fields.get('identity_statement', 'N/A')}")
    template_parts.append("")
    
    # Worldview
    template_parts.append(f"## Worldview")
    template_parts.append(f"{fields.get('worldview', 'N/A')}")
    template_parts.append("")
    
    # Values (with slots)
    template_parts.append(f"## Core Values")
    template_parts.append(f"*[Contextually select from {len(persona_data['values'])} available values]*")
    template_parts.append("")
    for i, item in enumerate(persona_data['values'], 1):
        node = item['node']
        node_fields = node.get('fields', {})
        template_parts.append(f"[VALUE_{i}]")
        template_parts.append(f"- **{node['label']}**")
        template_parts.append(f"  - Principle: {node_fields.get('principle', 'N/A')}")
        template_parts.append(f"  - Directive: {node_fields.get('behavioral_directive', 'N/A')}")
        template_parts.append(f"  - Context: {node_fields.get('application_context', 'N/A')}")
        template_parts.append("")
    
    # Drives (with slots)
    template_parts.append(f"## Active Drives")
    template_parts.append(f"*[Contextually select from {len(persona_data['drives'])} available drives]*")
    template_parts.append("")
    for i, item in enumerate(persona_data['drives'], 1):
        node = item['node']
        node_fields = node.get('fields', {})
        template_parts.append(f"[DRIVE_{i}]")
        template_parts.append(f"- **{node['label']}**")
        template_parts.append(f"  - Goal: {node_fields.get('goal_description', 'N/A')}")
        template_parts.append(f"  - Motivation: {node_fields.get('motivation', 'N/A')}")
        template_parts.append(f"  - Stakes: {node_fields.get('stakes', 'N/A')}")
        template_parts.append("")
    
    # Reasoning Patterns (with slots)
    template_parts.append(f"## Reasoning Patterns")
    template_parts.append(f"*[Contextually select from {len(persona_data['reasoning_patterns'])} available patterns]*")
    template_parts.append("")
    for i, item in enumerate(persona_data['reasoning_patterns'], 1):
        node = item['node']
        node_fields = node.get('fields', {})
        template_parts.append(f"[REASONING_{i}]")
        template_parts.append(f"- **{node['label']}**")
        template_parts.append(f"  - Trigger: {node_fields.get('trigger', 'N/A')}")
        template_parts.append(f"  - Response: {node_fields.get('preferred_response', 'N/A')}")
        template_parts.append(f"  - Failure Mode: {node_fields.get('failure_mode', 'N/A')}")
        template_parts.append("")
    
    # Communication Style (with slots)
    template_parts.append(f"## Communication Style")
    template_parts.append(f"*[Contextually select from {len(persona_data['linguistic_styles'])} available styles]*")
    template_parts.append("")
    for i, item in enumerate(persona_data['linguistic_styles'], 1):
        node = item['node']
        node_fields = node.get('fields', {})
        template_parts.append(f"[STYLE_{i}]")
        template_parts.append(f"- **{node['label']}**")
        template_parts.append(f"  - Formality: {node_fields.get('formality', 'N/A')}")
        template_parts.append(f"  - Directness: {node_fields.get('directness', 'N/A')}")
        template_parts.append(f"  - Verbosity: {node_fields.get('verbosity', 'N/A')}")
        template_parts.append(f"  - Affect: {node_fields.get('affect_modulation', 'N/A')}")
        template_parts.append("")
    
    # Constraints
    template_parts.append(f"## Operational Constraints")
    for item in persona_data['constraints']:
        node = item['node']
        node_fields = node.get('fields', {})
        template_parts.append(f"- **{node['label']}**")
        template_parts.append(f"  - Role: {node_fields.get('role', 'N/A')}")
        template_parts.append(f"  - Limits: {', '.join(node_fields.get('capability_limits', []))}")
        template_parts.append(f"  - Bounds: {node_fields.get('response_bounds', 'N/A')}")
        template_parts.append("")
    
    # Footer
    template_parts.append("---")
    template_parts.append("")
    template_parts.append("*Note: [SLOT] markers indicate dynamic selection points.*")
    template_parts.append("*The active nodes for each slot should be selected based on:*")
    template_parts.append("*- Current conversation context*")
    template_parts.append("*- User message sentiment/topic*")
    template_parts.append("*- Previous affective state (with governance)*")
    
    return "\n".join(template_parts)


def main():
    # Load configuration
    config = load_config()
    setup_logging(config)
    
    # Load graph data
    nodes_path = "outputs/nodes_canonical.jsonl"
    edges_path = "outputs/edges.jsonl"
    
    if not Path(nodes_path).exists():
        logging.error(f"Error: {nodes_path} not found. Run Phase 2.5 first.")
        sys.exit(1)
    
    if not Path(edges_path).exists():
        logging.error(f"Error: {edges_path} not found. Run Phase 3 first.")
        sys.exit(1)
    
    logging.info("="*60)
    logging.info("Phase 4: Persona Sheet Generation")
    logging.info("="*60)
    logging.info(f"Loading nodes from: {nodes_path}")
    logging.info(f"Loading edges from: {edges_path}")
    
    nodes = load_nodes(nodes_path)
    edges = load_edges(edges_path)
    
    logging.info(f"Loaded {len(nodes)} nodes and {len(edges)} edges")
    logging.info("")
    
    # Build adjacency list
    adjacency = build_adjacency_list(edges)
    
    # Find all Persona nodes
    persona_nodes = [nid for nid, node in nodes.items() if node['type'] == 'Persona']
    
    if not persona_nodes:
        logging.error("No Persona nodes found in graph")
        sys.exit(1)
    
    logging.info(f"Found {len(persona_nodes)} Persona node(s)")
    logging.info("")
    
    # Process each persona
    all_persona_data = []
    
    for persona_id in persona_nodes:
        persona = nodes[persona_id]
        logging.info(f"Processing Persona: {persona['label']}")
        
        # Traverse graph
        persona_data = traverse_persona(persona_id, nodes, adjacency, config)
        
        logging.info(f"  Values: {len(persona_data['values'])}")
        logging.info(f"  Drives: {len(persona_data['drives'])}")
        logging.info(f"  Reasoning: {len(persona_data['reasoning_patterns'])}")
        logging.info(f"  Styles: {len(persona_data['linguistic_styles'])}")
        logging.info(f"  Constraints: {len(persona_data['constraints'])}")
        logging.info(f"  Total nodes: {persona_data['metadata']['total_nodes']}")
        logging.info("")
        
        all_persona_data.append(persona_data)
    
    # Write structured JSON
    output_path = "outputs/persona_sheets.json"
    with open(output_path, 'w') as f:
        json.dump(all_persona_data, f, indent=2)
    
    logging.info(f"Wrote persona sheets to: {output_path}")
    
    # Generate template for first persona
    if all_persona_data:
        template = generate_persona_template(all_persona_data[0])
        
        template_path = "outputs/persona_template.txt"
        with open(template_path, 'w') as f:
            f.write(template)
        
        logging.info(f"Wrote persona template to: {template_path}")
    
    logging.info("")
    logging.info("="*60)
    logging.info("✅ Phase 4 Complete")
    logging.info("="*60)
    
    # Summary
    if all_persona_data:
        first_persona = all_persona_data[0]
        logging.info("")
        logging.info(f"Persona: {first_persona['persona']['label']}")
        logging.info(f"Total components: {first_persona['metadata']['total_nodes']} nodes")
        logging.info(f"Available for dynamic selection:")
        logging.info(f"  - {len(first_persona['values'])} values")
        logging.info(f"  - {len(first_persona['drives'])} drives")
        logging.info(f"  - {len(first_persona['reasoning_patterns'])} reasoning patterns")
        logging.info(f"  - {len(first_persona['linguistic_styles'])} communication styles")
        logging.info(f"  - {len(first_persona['constraints'])} constraints")


if __name__ == "__main__":
    main()
