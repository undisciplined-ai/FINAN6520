#!/usr/bin/env python3
"""
Validate KG pipeline outputs against persona_schema.yaml.

Usage:
    python scripts/validate_outputs.py examples/nodes.jsonl
    python scripts/validate_outputs.py outputs/nodes.jsonl outputs/edges.jsonl
"""

import sys
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Set


def load_schema(schema_path: str = "config/persona_schema.yaml") -> Dict:
    """Load and parse the persona schema YAML."""
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


def validate_id_format(node_id: str, expected_type_code: str) -> List[str]:
    """Validate node ID follows doc-page-chunk-type-seq format."""
    errors = []
    pattern = r'^doc\d{3}-p\d{3}-c\d{2}-([A-Z]{3})-\d{2}$'
    match = re.match(pattern, node_id)
    
    if not match:
        errors.append(f"ID '{node_id}' does not match format doc###-p###-c##-XXX-##")
    elif match.group(1) != expected_type_code:
        errors.append(f"ID '{node_id}' has type code '{match.group(1)}' but expected '{expected_type_code}'")
    
    return errors


def validate_node(node: Dict, schema: Dict) -> List[str]:
    """Validate a single node against schema."""
    errors = []
    
    # Check required common fields
    required_common = ['id', 'type', 'label', 'description', 'tags', 'importance', 'fields', 'provenance']
    for field in required_common:
        if field not in node:
            errors.append(f"Node {node.get('id', 'UNKNOWN')} missing required field: {field}")
    
    if 'type' not in node:
        errors.append(f"Node {node.get('id', 'UNKNOWN')} missing 'type' field")
        return errors
    
    node_type = node['type']
    
    # Check if node type is valid
    if node_type not in schema['node_types']:
        errors.append(f"Node {node['id']} has invalid type: {node_type}")
        return errors
    
    type_config = schema['node_types'][node_type]
    expected_code = type_config['code']
    
    # Validate ID format
    if 'id' in node:
        errors.extend(validate_id_format(node['id'], expected_code))
    
    # Validate importance range
    if 'importance' in node:
        importance = node['importance']
        if not isinstance(importance, (int, float)) or not (0.0 <= importance <= 1.0):
            errors.append(f"Node {node['id']} importance must be float 0.0-1.0, got {importance}")
    
    # Validate tags is a list
    if 'tags' in node and not isinstance(node['tags'], list):
        errors.append(f"Node {node['id']} tags must be a list")
    
    # Validate type-specific fields
    if 'fields' not in node:
        errors.append(f"Node {node['id']} missing 'fields' object")
        return errors
    
    fields = node['fields']
    required_fields = type_config['fields']
    
    for field_name, field_type in required_fields.items():
        if field_name not in fields:
            errors.append(f"Node {node['id']} missing required field: fields.{field_name}")
            continue
        
        value = fields[field_name]
        
        # Type checking
        if field_type == 'string' and not isinstance(value, str):
            errors.append(f"Node {node['id']} field '{field_name}' must be string, got {type(value).__name__}")
        elif field_type == 'float' and not isinstance(value, (int, float)):
            errors.append(f"Node {node['id']} field '{field_name}' must be float, got {type(value).__name__}")
        elif field_type.startswith('list[') and not isinstance(value, list):
            errors.append(f"Node {node['id']} field '{field_name}' must be list, got {type(value).__name__}")
        elif field_type.startswith('enum['):
            # Extract allowed values from enum definition
            allowed_values = field_type[5:-1].split(', ')
            if value not in allowed_values:
                errors.append(f"Node {node['id']} field '{field_name}' must be one of {allowed_values}, got '{value}'")
    
    # Validate provenance fields
    if 'provenance' in node:
        prov = node['provenance']
        required_prov = ['doc_id', 'doc_name', 'page_num', 'chunk_id', 'extraction_phase']
        for field in required_prov:
            if field not in prov:
                errors.append(f"Node {node['id']} missing provenance field: {field}")
    
    return errors


def validate_edge(edge: Dict, node_ids: Set[str], schema: Dict) -> List[str]:
    """Validate a single edge against schema."""
    errors = []
    
    # Check required fields
    required_fields = ['source_id', 'target_id', 'relation', 'weight', 'confidence']
    for field in required_fields:
        if field not in edge:
            errors.append(f"Edge missing required field: {field}")
    
    if 'source_id' not in edge or 'target_id' not in edge:
        return errors
    
    edge_id = f"{edge.get('source_id', '?')} -> {edge.get('target_id', '?')}"
    
    # Check if referenced nodes exist
    if edge['source_id'] not in node_ids:
        errors.append(f"Edge {edge_id} references non-existent source_id: {edge['source_id']}")
    if edge['target_id'] not in node_ids:
        errors.append(f"Edge {edge_id} references non-existent target_id: {edge['target_id']}")
    
    # Check if relation type is valid
    if 'relation' in edge:
        valid_relations = [et['name'] for et in schema['edge_types']]
        if edge['relation'] not in valid_relations:
            errors.append(f"Edge {edge_id} has invalid relation: {edge['relation']}")
    
    # Validate weight and confidence ranges
    for field in ['weight', 'confidence']:
        if field in edge:
            value = edge[field]
            if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
                errors.append(f"Edge {edge_id} {field} must be float 0.0-1.0, got {value}")
    
    return errors


def validate_file(filepath: str, schema: Dict, node_ids: Set[str] = None) -> tuple[List[str], Set[str]]:
    """Validate a JSONL file. Returns (errors, node_ids_found)."""
    errors = []
    new_node_ids = set()
    
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"{filepath}:{line_num} - Invalid JSON: {e}")
                    continue
                
                # Determine if this is a node or edge
                if 'type' in obj:  # It's a node
                    node_errors = validate_node(obj, schema)
                    if node_errors:
                        errors.extend([f"{filepath}:{line_num} - {err}" for err in node_errors])
                    if 'id' in obj:
                        new_node_ids.add(obj['id'])
                
                elif 'source_id' in obj:  # It's an edge
                    if node_ids is None:
                        errors.append(f"{filepath}:{line_num} - Cannot validate edges without nodes loaded first")
                    else:
                        edge_errors = validate_edge(obj, node_ids, schema)
                        if edge_errors:
                            errors.extend([f"{filepath}:{line_num} - {err}" for err in edge_errors])
                
                else:
                    errors.append(f"{filepath}:{line_num} - Unknown object type (neither node nor edge)")
    
    except FileNotFoundError:
        errors.append(f"File not found: {filepath}")
    
    return errors, new_node_ids


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_outputs.py <nodes.jsonl> [edges.jsonl]")
        sys.exit(1)
    
    schema = load_schema()
    all_errors = []
    
    # Validate nodes first
    nodes_file = sys.argv[1]
    print(f"Validating nodes: {nodes_file}")
    node_errors, node_ids = validate_file(nodes_file, schema)
    all_errors.extend(node_errors)
    print(f"  Found {len(node_ids)} nodes")
    
    # Validate edges if provided
    if len(sys.argv) > 2:
        edges_file = sys.argv[2]
        print(f"Validating edges: {edges_file}")
        edge_errors, _ = validate_file(edges_file, schema, node_ids)
        all_errors.extend(edge_errors)
    
    # Report results
    print("\n" + "="*60)
    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} error(s) found\n")
        for error in all_errors:
            print(f"  ❌ {error}")
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED: All files conform to schema")
        sys.exit(0)


if __name__ == "__main__":
    main()
