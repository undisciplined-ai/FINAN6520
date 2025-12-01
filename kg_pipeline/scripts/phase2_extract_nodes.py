#!/usr/bin/env python3
"""
Phase 2: Node Extraction

Sends chunks to LLM to extract schema-compliant nodes.

Usage:
    python scripts/phase2_extract_nodes.py
    
Requires:
    - outputs/chunks.jsonl (from Phase 1)
    - config/persona_schema.yaml
    - prompts/phase1_extraction.txt
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
import time


def get_default_manifest() -> Dict:
    """Get default manifest structure."""
    return {
        "schema_version": "1.1",
        "last_updated": None,
        "processed_files": {},
        "phase_status": {
            "phase0": {},
            "phase1": {},
            "phase2": {},
            "phase2.5": {"last_run": None, "node_count": 0},
            "phase3": {"processed_chunks": set()}
        },
        "doc_counter": 0
    }


def migrate_manifest(manifest: Dict) -> Dict:
    """Migrate old manifest schemas to current version."""
    schema_version = manifest.get('schema_version', '1.0')
    
    if schema_version == '1.0':
        # Add missing phase_status keys with defaults
        default = get_default_manifest()
        if 'phase_status' not in manifest:
            manifest['phase_status'] = default['phase_status']
        else:
            for phase_key, phase_default in default['phase_status'].items():
                manifest['phase_status'].setdefault(phase_key, phase_default)
        
        manifest['schema_version'] = '1.1'
    
    return manifest


def load_manifest(manifest_path: str = "outputs/.manifest.json") -> Dict:
    """Load processing manifest with migration."""
    if not Path(manifest_path).exists():
        return get_default_manifest()
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Migrate if needed
    manifest = migrate_manifest(manifest)
    
    return manifest


def save_manifest(manifest: Dict, manifest_path: str = "outputs/.manifest.json") -> None:
    """Save processing manifest."""
    manifest['last_updated'] = time.time()
    
    # Convert sets to lists for JSON serialization
    if 'phase_status' in manifest and 'phase3' in manifest['phase_status']:
        if 'processed_chunks' in manifest['phase_status']['phase3']:
            if isinstance(manifest['phase_status']['phase3']['processed_chunks'], set):
                manifest['phase_status']['phase3']['processed_chunks'] = list(
                    manifest['phase_status']['phase3']['processed_chunks']
                )
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)


def suggest_workers(chunk_count: int, tier_rpm: int = 2500, manual_override: int = None) -> int:
    """
    Suggest optimal worker count based on chunk count and API tier limits.
    
    Args:
        chunk_count: Number of chunks to process
        tier_rpm: Rate limit (requests per minute) for Anthropic via Vercel Gateway
        manual_override: If set, return this value instead of calculating
    
    Returns:
        Recommended number of workers (4, 8, or 16)
    
    Heuristic:
        - <60 chunks: 4 workers (small jobs, avoid overhead)
        - 60-180 chunks: 8 workers (medium jobs, good balance)
        - >180 chunks: 16 workers (large jobs, maximize throughput)
        
    Caps at 80% of tier RPM to prevent throttling.
    """
    if manual_override:
        logging.info(f"Using manual worker override: {manual_override}")
        return manual_override
    
    # Calculate based on chunk count
    if chunk_count < 60:
        suggested = 4
    elif chunk_count < 180:
        suggested = 8
    else:
        suggested = 16
    
    # Cap at 80% of tier limit to avoid 429s
    max_safe_workers = int(tier_rpm * 0.8 / 60)  # Convert RPM to requests/second
    if suggested > max_safe_workers:
        logging.warning(f"Capping workers from {suggested} to {max_safe_workers} based on tier limit (RPM: {tier_rpm})")
        suggested = max_safe_workers
    
    logging.info(f"Autoscaled workers: {suggested} (chunk_count={chunk_count}, tier_rpm={tier_rpm})")
    return suggested


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


def load_jungian_traits(traits_path: str = "config/jungian_traits.yaml") -> Dict:
    """Load Jungian trait vocabulary."""
    with open(traits_path, 'r') as f:
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


def format_node_types_for_prompt(schema: Dict) -> str:
    """Format node types section for prompt."""
    lines = []
    for node_type, config in schema['node_types'].items():
        lines.append(f"- {node_type}: {config['description']}")
    return '\n'.join(lines)


def format_trait_vocabulary(traits: Dict) -> str:
    """Format Jungian trait vocabulary for prompt (compact version)."""
    vocab = traits['trait_vocabulary']
    lines = []
    
    for category, traits_dict in vocab.items():
        lines.append(f"\n{category.upper()}:")
        for trait_id, trait_info in traits_dict.items():
            # Include just ID and brief description to minimize tokens
            desc = trait_info['description']
            lines.append(f"  - {trait_id}: {desc}")
    
    return '\n'.join(lines)


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
    
    phase1_config = config['phase1']
    
    # Prepare input for Node.js wrapper
    wrapper_input = {
        "model": phase1_config['model'],
        "prompt": prompt,
        "temperature": phase1_config['temperature'],
        "maxTokens": phase1_config['max_tokens']
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


def mint_node_id(doc_id: str, page_id: str, chunk_id: str, type_code: str, seq: int) -> str:
    """Generate node ID following doc-page-chunk-type-seq format."""
    return f"{doc_id}-{page_id}-{chunk_id}-{type_code}-{seq:02d}"


def process_chunk(chunk: Dict, schema: Dict, traits: Dict, prompt_template: str, config: Dict) -> List[Dict]:
    """
    Process a single chunk to extract nodes.
    
    Args:
        chunk: Chunk data from chunks.jsonl
        schema: Persona schema
        prompt_template: Prompt template text
        config: Runtime configuration
    
    Returns:
        List of extracted nodes with minted IDs
    """
    # Format prompt
    node_types_text = format_node_types_for_prompt(schema)
    trait_vocabulary_text = format_trait_vocabulary(traits)
    
    # Escape braces in chunk text to prevent format() errors
    safe_chunk_text = chunk['text'].replace('{', '{{').replace('}', '}}')
    
    prompt = prompt_template.format(
        node_types=node_types_text,
        trait_vocabulary=trait_vocabulary_text,
        doc_id=chunk['doc_id'],
        page_id=chunk['page_id'],
        chunk_id=chunk['chunk_id'],
        chunk_text=safe_chunk_text
    )
    
    # Call LLM
    try:
        response = call_llm(prompt, config)
    except Exception as e:
        logging.error(f"Failed to process chunk {chunk['doc_id']}-{chunk['page_id']}-{chunk['chunk_id']}: {e}")
        return []
    
    # Extract nodes and mint IDs
    nodes = response.get('nodes', [])
    type_counters = defaultdict(int)
    minted_nodes = []
    
    for node in nodes:
        node_type = node.get('type')
        if not node_type or node_type not in schema['node_types']:
            logging.warning(f"Invalid node type: {node_type}")
            continue
        
        # Get type code
        type_code = schema['node_types'][node_type]['code']
        
        # Increment counter for this type
        type_counters[type_code] += 1
        seq = type_counters[type_code]
        
        # Mint ID
        node_id = mint_node_id(
            chunk['doc_id'],
            chunk['page_id'],
            chunk['chunk_id'],
            type_code,
            seq
        )
        
        # Add ID and provenance
        node['id'] = node_id
        node['provenance'] = {
            'doc_id': chunk['doc_id'],
            'page_num': chunk['page_num'],
            'chunk_id': chunk['chunk_id'],
            'extraction_phase': 'phase2'
        }
        
        minted_nodes.append(node)
    
    return minted_nodes


def main():
    # Load environment variables
    load_env_file()
    
    # Load configuration, schema, and Jungian traits
    config = load_config()
    schema = load_schema()
    traits = load_jungian_traits()
    setup_logging(config)
    
    # Check for API key
    api_key_env = config['api_key_env']
    if not os.environ.get(api_key_env):
        logging.error(f"Error: {api_key_env} environment variable not set")
        logging.error("Create .env file with your Vercel AI Gateway API key")
        sys.exit(1)
    
    # Load prompt template
    prompt_template_path = config['phase1']['prompt_template']
    prompt_template = load_prompt_template(prompt_template_path)
    
    # Load manifest
    manifest = load_manifest()
    
    # Load chunks
    chunks_path = "outputs/chunks.jsonl"
    if not Path(chunks_path).exists():
        logging.error(f"Error: {chunks_path} not found. Run Phase 1 first.")
        sys.exit(1)
    
    logging.info("="*60)
    logging.info("Phase 2: Node Extraction")
    logging.info("="*60)
    logging.info(f"Loading chunks from: {chunks_path}")
    
    # Load all chunks
    all_chunks = []
    with open(chunks_path, 'r') as f:
        for line in f:
            all_chunks.append(json.loads(line))
    
    # Filter to only new chunks (not in phase2 status)
    manifest['phase_status'].setdefault('phase2', {})
    processed_chunks = set(manifest['phase_status']['phase2'].keys())
    chunks = [c for c in all_chunks if f"{c['doc_id']}-{c['page_id']}-{c['chunk_id']}" not in processed_chunks]
    
    logging.info(f"Total chunks: {len(all_chunks)}")
    logging.info(f"Already processed: {len(processed_chunks)}")
    logging.info(f"New chunks to process: {len(chunks)}")
    
    if not chunks:
        logging.info("No new chunks to process. Exiting.")
        return
    
    logging.info(f"Model: {config['phase1']['model']}")
    logging.info(f"Output: outputs/nodes.jsonl (append mode)")
    logging.info("")
    
    # Process chunks (parallel or sequential based on config)
    all_nodes = []
    node_type_counts = defaultdict(int)
    
    parallel_config = config.get('parallel', {})
    parallel_enabled = parallel_config.get('enabled', False)
    config_workers = parallel_config.get('max_workers', None)  # None allows autoscaling
    
    # Autoscale workers based on chunk count
    max_workers = suggest_workers(
        chunk_count=len(chunks),
        tier_rpm=2500,  # Conservative estimate for Anthropic via Vercel
        manual_override=config_workers
    )
    
    output_path = "outputs/nodes.jsonl"
    
    if parallel_enabled:
        logging.info(f"Using parallel processing with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunks
            future_to_chunk = {}
            for chunk in chunks:
                future = executor.submit(process_chunk, chunk, schema, traits, prompt_template, config)
                future_to_chunk[future] = chunk
            
            # Collect results as they complete (append mode)
            with open(output_path, 'a') as output_file:
                completed = 0
                for future in as_completed(future_to_chunk):
                    chunk = future_to_chunk[future]
                    chunk_label = f"{chunk['doc_id']}-{chunk['page_id']}-{chunk['chunk_id']}"
                    completed += 1
                    
                    try:
                        nodes = future.result()
                        logging.info(f"[{completed}/{len(chunks)}] ✓ {chunk_label}: {len(nodes)} node(s)")
                        
                        # Write nodes to file
                        for node in nodes:
                            output_file.write(json.dumps(node) + '\n')
                            all_nodes.append(node)
                            node_type_counts[node['type']] += 1
                        
                        # Track in manifest
                        manifest['phase_status']['phase2'][chunk_label] = {
                            'processed': True,
                            'node_count': len(nodes)
                        }
                    except Exception as e:
                        logging.error(f"[{completed}/{len(chunks)}] ✗ {chunk_label}: {e}")
    else:
        logging.info("Using sequential processing")
        
        with open(output_path, 'a') as output_file:
            for i, chunk in enumerate(chunks, 1):
                chunk_label = f"{chunk['doc_id']}-{chunk['page_id']}-{chunk['chunk_id']}"
                logging.info(f"Processing chunk {i}/{len(chunks)}: {chunk_label}")
                
                nodes = process_chunk(chunk, schema, traits, prompt_template, config)
                
                # Write nodes to file
                for node in nodes:
                    output_file.write(json.dumps(node) + '\n')
                    all_nodes.append(node)
                    node_type_counts[node['type']] += 1
                
                # Track in manifest
                manifest['phase_status']['phase2'][chunk_label] = {
                    'processed': True,
                    'node_count': len(nodes)
                }
                
                logging.info(f"  ✓ Extracted {len(nodes)} node(s)")
    
    # Save manifest
    save_manifest(manifest)
    
    # Write metadata about new nodes for Phase 2.5
    metadata_path = "outputs/nodes_new.jsonl"
    with open(metadata_path, 'w') as f:
        for node in all_nodes:
            f.write(json.dumps(node) + '\n')
    
    # Summary
    logging.info("")
    logging.info("="*60)
    logging.info("✅ Phase 2 Complete")
    logging.info(f"Nodes extracted this run: {len(all_nodes)}")
    logging.info(f"New nodes written to: {metadata_path} (for Phase 2.5 incremental processing)")
    logging.info("")
    logging.info("Node counts by type:")
    for node_type, count in sorted(node_type_counts.items()):
        logging.info(f"  {node_type}: {count}")
    logging.info("")
    logging.info(f"Output written to: {output_path}")
    logging.info("="*60)
    
    # Show sample nodes
    if all_nodes:
        logging.info("")
        logging.info("Sample nodes:")
        for node in all_nodes[:3]:
            logging.info(f"  {node['id']} ({node['type']}): {node.get('label', 'N/A')}")


if __name__ == "__main__":
    main()
