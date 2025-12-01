#!/usr/bin/env python3
"""
Phase 3: Relationship Extraction

Identifies edges between nodes within each chunk.

Usage:
    python scripts/phase3_extract_relationships.py
    
Requires:
    - outputs/nodes.jsonl (from Phase 2)
    - config/persona_schema.yaml
    - prompts/phase2_relationships.txt
    - .env with AI_GATEWAY_API_KEY
"""

import sys
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml


def load_env_file(env_path: str = ".env") -> None:
    """Load environment variables from .env file."""
    if not Path(env_path).exists():
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()


def load_config(config_path: str = "config/run_config.yaml") -> Dict:
    """Load runtime configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_schema(schema_path: str = "config/persona_schema.yaml") -> Dict:
    """Load persona schema."""
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


def load_prompt_template(template_path: str) -> str:
    """Load prompt template."""
    with open(template_path, 'r') as f:
        return f.read()


def setup_logging(config: Dict) -> None:
    """Configure logging based on config settings."""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_canonical_nodes(nodes_path: str) -> List[Dict]:
    """
    Load canonical nodes from entity resolution.
    
    Returns:
        List of all canonical nodes
    """
    nodes = []
    with open(nodes_path, 'r') as f:
        for line in f:
            nodes.append(json.loads(line))
    return nodes


def load_entity_mapping(mapping_path: str) -> Dict[str, str]:
    """
    Load entity mapping from Phase 2.5.
    
    Returns:
        Dict mapping original_id -> canonical_id
    """
    with open(mapping_path, 'r') as f:
        return json.load(f)


def group_nodes_by_chunk(nodes: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group canonical nodes by their source chunks.
    Canonical nodes appear in ALL chunks where they were extracted.
    
    Returns:
        Dict mapping chunk_key to list of nodes from that chunk
    """
    nodes_by_chunk = defaultdict(list)
    
    for node in nodes:
        # Canonical nodes have list of provenance (merged sources)
        # Add this node to EVERY chunk it appeared in
        if isinstance(node['provenance'], list):
            provenance_list = node['provenance']
        else:
            provenance_list = [node['provenance']]
        
        for prov in provenance_list:
            chunk_key = f"{prov['doc_id']}-{prov['page_num']:03d}-{prov['chunk_id']}"
            nodes_by_chunk[chunk_key].append(node)
    
    return dict(nodes_by_chunk)


def load_chunks(chunks_path: str) -> Dict[str, Dict]:
    """
    Load chunks and index by chunk key.
    
    Returns:
        Dict mapping chunk_key to chunk data
    """
    chunks = {}
    
    with open(chunks_path, 'r') as f:
        for line in f:
            chunk = json.loads(line)
            chunk_key = f"{chunk['doc_id']}-{chunk['page_num']:03d}-{chunk['chunk_id']}"
            chunks[chunk_key] = chunk
    
    return chunks


def format_edge_types_for_prompt(schema: Dict) -> str:
    """Format edge types section for prompt."""
    lines = []
    for edge_type in schema['edge_types']:
        lines.append(f"- {edge_type['name']}: {edge_type['description']}")
    return '\n'.join(lines)


def format_nodes_for_prompt(nodes: List[Dict]) -> str:
    """Format nodes list for prompt (labels and types only, no IDs)."""
    lines = []
    for node in nodes:
        lines.append(f"- {node['label']} ({node['type']})")
    return '\n'.join(lines)


def match_concept_to_node(concept_label: str, concept_type: str, nodes: List[Dict]) -> str:
    """
    Match a concept label to actual node ID using fuzzy matching.
    
    Args:
        concept_label: Label from LLM response
        concept_type: Type from LLM response
        nodes: List of available nodes
    
    Returns:
        Node ID if match found, None otherwise
    """
    # Filter nodes by type first
    candidates = [n for n in nodes if n['type'] == concept_type]
    
    if not candidates:
        return None
    
    # Exact match on label
    for node in candidates:
        if node['label'].lower() == concept_label.lower():
            return node['id']
    
    # Fuzzy match: check if concept_label is substring of node label or vice versa
    for node in candidates:
        node_label_lower = node['label'].lower()
        concept_label_lower = concept_label.lower()
        
        if concept_label_lower in node_label_lower or node_label_lower in concept_label_lower:
            return node['id']
    
    # No match found
    return None


def validate_edge_type(relation_type: str, source_type: str, target_type: str) -> bool:
    """
    Validate that an edge type matches source/target type constraints.
    
    Args:
        relation_type: Proposed edge type from LLM
        source_type: Source node type
        target_type: Target node type
    
    Returns:
        True if valid, False otherwise
    """
    # Define edge type constraints
    edge_constraints = {
        'persona_has_value': ('Persona', 'Value'),
        'persona_has_drive': ('Persona', 'Drive'),
        'persona_uses_reasoning': ('Persona', 'ReasoningPattern'),
        'persona_has_style': ('Persona', 'LinguisticStyle'),
        'persona_constrained_by': ('Persona', 'Constraint'),
        'value_conflicts_with': ('Value', 'Value'),
        'drive_blocked_by': ('Drive', 'Drive'),
        'reasoning_supports': ('ReasoningPattern', 'ReasoningPattern')
    }
    
    if relation_type not in edge_constraints:
        return False
    
    expected_source, expected_target = edge_constraints[relation_type]
    return source_type == expected_source and target_type == expected_target


def call_llm(prompt: str, config: Dict) -> Dict:
    """
    Call Vercel AI Gateway via Node.js wrapper.
    
    Args:
        prompt: Formatted prompt text
        config: Runtime configuration
    
    Returns:
        Parsed JSON response from LLM
    """
    import subprocess
    
    phase2_config = config['phase2']
    
    # Prepare input for Node.js wrapper
    wrapper_input = {
        "model": phase2_config['model'],
        "prompt": prompt,
        "temperature": phase2_config['temperature'],
        "maxTokens": phase2_config['max_tokens']
    }
    
    try:
        # Call Node.js wrapper
        result = subprocess.run(
            ['node', 'scripts/ai_gateway_wrapper.mjs'],
            input=json.dumps(wrapper_input),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            raise RuntimeError(f"AI Gateway call failed: {error_msg}")
        
        # Parse response
        response = json.loads(result.stdout)
        
        if 'error' in response:
            raise RuntimeError(f"AI Gateway error: {response['error']}")
        
        # Extract text and parse JSON
        assistant_message = response['text']
        parsed = parse_llm_response(assistant_message)
        
        # Log token usage
        if 'usage' in response:
            usage = response['usage']
            logging.debug(f"Token usage: {usage.get('totalTokens', 'N/A')} total")
        
        return parsed
    
    except subprocess.TimeoutExpired:
        logging.error("LLM request timed out")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse response: {e}")
        raise
    except Exception as e:
        logging.error(f"LLM call failed: {e}")
        raise


def parse_llm_response(response_text: str) -> Dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    text = response_text.strip()
    
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Failed to parse JSON: {e}\nResponse: {text[:500]}...")


def process_chunk(chunk_key: str, nodes: List[Dict], chunk: Dict, 
                  schema: Dict, prompt_template: str, config: Dict) -> List[Dict]:
    """
    Process a single chunk to extract relationships using two-stage approach:
    1. LLM identifies semantic relationships (no IDs)
    2. Deterministically match concepts to nodes and validate types
    
    Args:
        chunk_key: Chunk identifier
        nodes: List of nodes from this chunk
        chunk: Chunk data with text
        schema: Persona schema
        prompt_template: Prompt template text
        config: Runtime configuration
    
    Returns:
        List of extracted edges with valid IDs and types
    """
    # Skip if less than 2 nodes
    if len(nodes) < 2:
        logging.debug(f"Chunk {chunk_key} has only {len(nodes)} node(s), skipping relationship extraction")
        return []
    
    # Format prompt (concepts only, no IDs)
    nodes_text = format_nodes_for_prompt(nodes)
    
    # Escape braces in chunk text to prevent format() errors
    safe_chunk_text = chunk['text'].replace('{', '{{').replace('}', '}}')
    
    prompt = prompt_template.format(
        nodes=nodes_text,
        chunk_text=safe_chunk_text
    )
    
    # Stage 1: Get semantic relationships from LLM
    try:
        response = call_llm(prompt, config)
    except Exception as e:
        logging.error(f"Failed to process chunk {chunk_key}: {e}")
        return []
    
    # Extract relationships (semantic descriptions)
    relationships = response.get('relationships', [])
    
    if not relationships:
        logging.debug(f"No relationships found in chunk {chunk_key}")
        return []
    
    # Stage 2: Match concepts to nodes and validate types
    valid_edges = []
    
    for rel in relationships:
        source_label = rel.get('source_concept')
        source_type = rel.get('source_type')
        target_label = rel.get('target_concept')
        target_type = rel.get('target_type')
        rel_desc = rel.get('relationship_description', '')
        
        if not all([source_label, source_type, target_label, target_type]):
            logging.warning(f"Incomplete relationship data: {rel}")
            continue
        
        # Match source concept to node
        source_id = match_concept_to_node(source_label, source_type, nodes)
        if not source_id:
            logging.warning(f"Could not match source concept: {source_label} ({source_type})")
            continue
        
        # Match target concept to node
        target_id = match_concept_to_node(target_label, target_type, nodes)
        if not target_id:
            logging.warning(f"Could not match target concept: {target_label} ({target_type})")
            continue
        
        # Get relation type from LLM response
        relation_type = rel.get('relation_type')
        if not relation_type:
            logging.warning(f"Missing relation_type in relationship: {rel}")
            continue
        
        # Validate type constraints
        if not validate_edge_type(relation_type, source_type, target_type):
            logging.warning(f"Invalid edge type: {relation_type} for {source_type}→{target_type}")
            continue
        
        # Build valid edge
        edge = {
            'source_id': source_id,
            'target_id': target_id,
            'relation': relation_type,
            'weight': rel.get('weight', 0.5),
            'confidence': rel.get('confidence', 0.5),
            'evidence': rel.get('evidence', '')
        }
        
        valid_edges.append(edge)
    
    return valid_edges


def main():
    # Load environment variables
    load_env_file()
    
    # Load configuration and schema
    config = load_config()
    schema = load_schema()
    setup_logging(config)
    
    # Check for API key
    api_key_env = config['api_key_env']
    if not os.environ.get(api_key_env):
        logging.error(f"Error: {api_key_env} environment variable not set")
        logging.error("Create .env file with your Vercel AI Gateway API key")
        sys.exit(1)
    
    # Load prompt template
    prompt_template_path = config['phase2']['prompt_template']
    prompt_template = load_prompt_template(prompt_template_path)
    
    # Load canonical nodes and entity mapping
    nodes_path = "outputs/nodes_canonical.jsonl"
    mapping_path = "outputs/entity_mapping.json"
    chunks_path = "outputs/chunks.jsonl"
    
    if not Path(nodes_path).exists():
        logging.error(f"Error: {nodes_path} not found. Run Phase 2.5 first.")
        sys.exit(1)
    
    if not Path(chunks_path).exists():
        logging.error(f"Error: {chunks_path} not found. Run Phase 1 first.")
        sys.exit(1)
    
    logging.info("="*60)
    logging.info("Phase 3: Relationship Extraction")
    logging.info("="*60)
    logging.info(f"Loading canonical nodes from: {nodes_path}")
    logging.info(f"Loading chunks from: {chunks_path}")
    
    canonical_nodes = load_canonical_nodes(nodes_path)
    nodes_by_chunk = group_nodes_by_chunk(canonical_nodes)
    chunks = load_chunks(chunks_path)
    
    logging.info(f"Loaded {len(nodes_by_chunk)} chunk(s) with nodes")
    logging.info(f"Model: {config['phase2']['model']}")
    logging.info(f"Output: outputs/edges.jsonl")
    logging.info("")
    
    # Pass 1: Local relationships (within chunks)
    logging.info("")
    logging.info("Pass 1: Extracting local relationships (within-chunk)...")
    all_edges = []
    edge_type_counts = defaultdict(int)
    seen_edges = set()  # Track (source_id, target_id, relation) to deduplicate
    
    parallel_config = config.get('parallel', {})
    parallel_enabled = parallel_config.get('enabled', False)
    max_workers = parallel_config.get('max_workers', 4)
    
    output_path = "outputs/edges.jsonl"
    
    if parallel_enabled:
        logging.info(f"Using parallel processing with {max_workers} workers")
        
        chunk_items = sorted(nodes_by_chunk.items())
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunks for local pass
            future_to_chunk = {}
            for chunk_key, nodes in chunk_items:
                if chunk_key not in chunks:
                    logging.warning(f"Chunk {chunk_key} not found in chunks.jsonl, skipping")
                    continue
                
                chunk = chunks[chunk_key]
                future = executor.submit(process_chunk, chunk_key, nodes, chunk, schema, prompt_template, config)
                future_to_chunk[future] = (chunk_key, len(nodes))
            
            # Collect results as they complete and deduplicate
            with open(output_path, 'w') as output_file:
                completed = 0
                for future in as_completed(future_to_chunk):
                    chunk_key, node_count = future_to_chunk[future]
                    completed += 1
                    
                    try:
                        edges = future.result()
                        
                        # Deduplicate and write edges
                        new_edges = 0
                        for edge in edges:
                            edge_key = (edge['source_id'], edge['target_id'], edge['relation'])
                            if edge_key not in seen_edges:
                                seen_edges.add(edge_key)
                                output_file.write(json.dumps(edge) + '\n')
                                all_edges.append(edge)
                                edge_type_counts[edge['relation']] += 1
                                new_edges += 1
                        
                        dup_count = len(edges) - new_edges
                        logging.info(f"[{completed}/{len(future_to_chunk)}] ✓ {chunk_key}: {new_edges} edge(s) ({dup_count} duplicates)")
                    except Exception as e:
                        logging.error(f"[{completed}/{len(future_to_chunk)}] ✗ {chunk_key}: {e}")
    else:
        logging.info("Using sequential processing")
        
        with open(output_path, 'w') as output_file:
            for i, (chunk_key, nodes) in enumerate(sorted(nodes_by_chunk.items()), 1):
                logging.info(f"Processing chunk {i}/{len(nodes_by_chunk)}: {chunk_key} ({len(nodes)} nodes)")
                
                if chunk_key not in chunks:
                    logging.warning(f"Chunk {chunk_key} not found in chunks.jsonl, skipping")
                    continue
                
                chunk = chunks[chunk_key]
                edges = process_chunk(chunk_key, nodes, chunk, schema, prompt_template, config)
                
                # Deduplicate and write edges to file
                new_edges = 0
                for edge in edges:
                    edge_key = (edge['source_id'], edge['target_id'], edge['relation'])
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        output_file.write(json.dumps(edge) + '\n')
                        all_edges.append(edge)
                        edge_type_counts[edge['relation']] += 1
                        new_edges += 1
                
                logging.info(f"  ✓ Extracted {new_edges} edge(s) ({len(edges) - new_edges} duplicates filtered)")
    
    # Pass 2: Global relationships (cross-chunk for high-importance nodes)
    # This runs AFTER local pass completes (regardless of parallel/sequential mode)
    logging.info("")
    logging.info("Pass 2: Extracting global relationships (cross-chunk)...")
    
    # Get high-importance nodes across all chunks
    importance_threshold = config.get('phase2', {}).get('importance_threshold', 0.7)
    high_importance_nodes = [n for n in canonical_nodes if n['importance'] >= importance_threshold]
    
    if len(high_importance_nodes) >= 2:
        logging.info(f"Found {len(high_importance_nodes)} high-importance nodes (threshold: {importance_threshold})")
        
        # Create a virtual "global" context with all high-importance nodes
        # Use combined text from their source chunks as context
        global_context_chunks = []
        for node in high_importance_nodes:
            if isinstance(node['provenance'], list):
                prov = node['provenance'][0]
            else:
                prov = node['provenance']
            
            chunk_key = f"{prov['doc_id']}-{prov['page_num']:03d}-{prov['chunk_id']}"
            if chunk_key in chunks:
                global_context_chunks.append(chunks[chunk_key]['text'])
        
        # Combine context (limit to reasonable size)
        global_context = "\n\n...\n\n".join(global_context_chunks[:5])  # Max 5 chunks
        
        # Create pseudo-chunk for global extraction
        pseudo_chunk = {
            'text': global_context
        }
        
        global_edges = process_chunk('global', high_importance_nodes, pseudo_chunk, schema, prompt_template, config)
        
        # Deduplicate and write global edges (append mode since file was closed after local pass)
        with open(output_path, 'a') as output_file:
            new_edges = 0
            for edge in global_edges:
                edge_key = (edge['source_id'], edge['target_id'], edge['relation'])
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    output_file.write(json.dumps(edge) + '\n')
                    all_edges.append(edge)
                    edge_type_counts[edge['relation']] += 1
                    new_edges += 1
        
        logging.info(f"  ✓ Extracted {new_edges} cross-chunk edge(s) ({len(global_edges) - new_edges} duplicates filtered)")
    else:
        logging.info(f"Skipping global pass: only {len(high_importance_nodes)} high-importance nodes")
    
    # Summary
    logging.info("")
    logging.info("="*60)
    logging.info("✅ Phase 3 Complete")
    logging.info(f"Total edges extracted: {len(all_edges)}")
    logging.info("")
    logging.info("Edge counts by type:")
    for edge_type, count in sorted(edge_type_counts.items()):
        logging.info(f"  {edge_type}: {count}")
    logging.info("")
    logging.info(f"Output written to: {output_path}")
    logging.info("="*60)
    
    # Show sample edges
    if all_edges:
        logging.info("")
        logging.info("Sample edges:")
        for edge in all_edges[:3]:
            logging.info(f"  {edge['source_id']} → {edge['target_id']} ({edge['relation']})")


if __name__ == "__main__":
    main()
