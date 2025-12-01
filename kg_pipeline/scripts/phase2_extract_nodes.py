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


def format_node_types_for_prompt(schema: Dict) -> str:
    """Format node types section for prompt."""
    lines = []
    for node_type, config in schema['node_types'].items():
        lines.append(f"- {node_type}: {config['description']}")
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


def process_chunk(chunk: Dict, schema: Dict, prompt_template: str, config: Dict) -> List[Dict]:
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
    
    # Escape braces in chunk text to prevent format() errors
    safe_chunk_text = chunk['text'].replace('{', '{{').replace('}', '}}')
    
    prompt = prompt_template.format(
        node_types=node_types_text,
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
            'doc_name': chunk['doc_name'],
            'page_num': chunk['page_num'],
            'chunk_id': chunk['chunk_id'],
            'extraction_phase': 'phase2'
        }
        
        minted_nodes.append(node)
    
    return minted_nodes


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
    prompt_template_path = config['phase1']['prompt_template']
    prompt_template = load_prompt_template(prompt_template_path)
    
    # Load chunks
    chunks_path = "outputs/chunks.jsonl"
    if not Path(chunks_path).exists():
        logging.error(f"Error: {chunks_path} not found. Run Phase 1 first.")
        sys.exit(1)
    
    logging.info("="*60)
    logging.info("Phase 2: Node Extraction")
    logging.info("="*60)
    logging.info(f"Loading chunks from: {chunks_path}")
    
    chunks = []
    with open(chunks_path, 'r') as f:
        for line in f:
            chunks.append(json.loads(line))
    
    logging.info(f"Loaded {len(chunks)} chunk(s)")
    logging.info(f"Model: {config['phase1']['model']}")
    logging.info(f"Output: outputs/nodes.jsonl")
    logging.info("")
    
    # Process chunks
    all_nodes = []
    node_type_counts = defaultdict(int)
    
    output_path = "outputs/nodes.jsonl"
    with open(output_path, 'w') as output_file:
        for i, chunk in enumerate(chunks, 1):
            chunk_label = f"{chunk['doc_id']}-{chunk['page_id']}-{chunk['chunk_id']}"
            logging.info(f"Processing chunk {i}/{len(chunks)}: {chunk_label}")
            
            nodes = process_chunk(chunk, schema, prompt_template, config)
            
            # Write nodes to file
            for node in nodes:
                output_file.write(json.dumps(node) + '\n')
                all_nodes.append(node)
                node_type_counts[node['type']] += 1
            
            logging.info(f"  ✓ Extracted {len(nodes)} node(s)")
    
    # Summary
    logging.info("")
    logging.info("="*60)
    logging.info("✅ Phase 2 Complete")
    logging.info(f"Total nodes extracted: {len(all_nodes)}")
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
