#!/usr/bin/env python3
"""
Phase 4c: Affective Governor

Prevents emotional whiplash by enforcing smooth transitions between affective states.
Tracks conversation history and constrains node selections to maintain coherent tone.

Usage:
    python scripts/phase4c_affective_governor.py --history history.jsonl --selections selected_nodes.json
    
Requires:
    - outputs/persona_sheets.json (from Phase 4)
    - outputs/selected_nodes.json (from Phase 4b)
    - conversation_history.jsonl (turn-by-turn state log)
    
Outputs:
    - Approved or constrained node selections
    - Updated conversation history with affective state
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
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


def load_persona_sheet(sheet_path: str) -> Dict:
    """Load persona sheet from Phase 4."""
    with open(sheet_path, 'r') as f:
        sheets = json.load(f)
    
    if not sheets:
        raise ValueError("No persona sheets found")
    
    return sheets[0]


def load_conversation_history(history_path: str) -> List[Dict]:
    """
    Load conversation history from JSONL file.
    Each line is a turn with: {turn_id, message_id, timestamp, selected_nodes, affective_state}
    """
    if not Path(history_path).exists():
        return []
    
    history = []
    with open(history_path, 'r') as f:
        for line in f:
            if line.strip():
                history.append(json.loads(line))
    
    return history


def calculate_affective_state(selections: Dict, persona_sheet: Dict) -> Dict[str, float]:
    """
    Calculate affective state vector from selected nodes.
    
    Returns:
        Dict with affect dimensions: {
            'warmth': 0.0-1.0,
            'formality': 0.0-1.0,
            'directness': 0.0-1.0,
            'intensity': 0.0-1.0
        }
    """
    state = {
        'warmth': 0.5,  # baseline neutral
        'formality': 0.5,
        'directness': 0.5,
        'intensity': 0.5
    }
    
    # Extract affect from selected linguistic styles
    for style_item in selections.get('linguistic_styles', []):
        # Need to look up full node data from persona sheet
        node_id = style_item['node_id']
        
        # Find full node in persona sheet
        full_node = None
        for item in persona_sheet['linguistic_styles']:
            if item['node']['id'] == node_id:
                full_node = item['node']
                break
        
        if not full_node:
            continue
        
        fields = full_node.get('fields', {})
        
        # Map formality
        formality_map = {'casual': 0.2, 'professional': 0.5, 'formal': 0.8}
        state['formality'] = formality_map.get(fields.get('formality', 'professional'), 0.5)
        
        # Map directness
        directness_map = {'indirect': 0.3, 'balanced': 0.5, 'direct': 0.8}
        state['directness'] = directness_map.get(fields.get('directness', 'balanced'), 0.5)
        
        # Parse affect modulation for warmth
        affect_text = fields.get('affect_modulation', '').lower()
        if 'warm' in affect_text or 'encouraging' in affect_text:
            state['warmth'] = 0.7
        elif 'neutral' in affect_text:
            state['warmth'] = 0.5
        elif 'serious' in affect_text or 'firm' in affect_text:
            state['warmth'] = 0.3
    
    # Adjust intensity based on sentiment and node importance
    sentiment = selections['metadata']['sentiment']
    if sentiment['negative'] > 0.2:
        state['intensity'] = 0.7  # More intense when user struggling
    elif sentiment['positive'] > 0.2:
        state['intensity'] = 0.6  # Moderately intense when excited
    else:
        state['intensity'] = 0.4  # Lower intensity for neutral exchanges
    
    return state


def calculate_affective_delta(prev_state: Dict[str, float], curr_state: Dict[str, float]) -> float:
    """
    Calculate Euclidean distance between affective states.
    
    Returns:
        Delta value (0.0 = identical, higher = more different)
    """
    if not prev_state:
        return 0.0
    
    dimensions = ['warmth', 'formality', 'directness', 'intensity']
    
    sum_squares = 0.0
    for dim in dimensions:
        diff = curr_state.get(dim, 0.5) - prev_state.get(dim, 0.5)
        sum_squares += diff ** 2
    
    delta = (sum_squares / len(dimensions)) ** 0.5
    
    return delta


def constrain_selections(selections: Dict, persona_sheet: Dict, 
                         prev_state: Optional[Dict[str, float]], 
                         max_delta: float) -> Tuple[Dict, bool, str]:
    """
    Constrain node selections to respect max affective delta.
    
    Args:
        selections: Proposed node selections from Phase 4b
        persona_sheet: Full persona data
        prev_state: Previous turn's affective state
        max_delta: Maximum allowed affective change
    
    Returns:
        Tuple of (constrained_selections, was_modified, reasoning)
    """
    # Calculate proposed affective state
    proposed_state = calculate_affective_state(selections, persona_sheet)
    
    # If no previous state, accept as-is (first turn)
    if not prev_state:
        return selections, False, "First turn - no constraint applied"
    
    # Calculate delta
    delta = calculate_affective_delta(prev_state, proposed_state)
    
    # If within bounds, accept
    if delta <= max_delta:
        return selections, False, f"Delta {delta:.3f} within limit {max_delta}"
    
    # Delta too high - need to constrain
    logging.warning(f"Affective delta {delta:.3f} exceeds max {max_delta}")
    logging.warning(f"Previous state: {prev_state}")
    logging.warning(f"Proposed state: {proposed_state}")
    
    # Simple constraint strategy: blend proposed with previous
    # Move toward proposed state but cap the delta
    constrained_state = {}
    scale_factor = max_delta / delta  # How much of the move to allow
    
    for dim in ['warmth', 'formality', 'directness', 'intensity']:
        prev_val = prev_state.get(dim, 0.5)
        prop_val = proposed_state.get(dim, 0.5)
        
        # Interpolate: prev + scale_factor * (prop - prev)
        constrained_state[dim] = prev_val + scale_factor * (prop_val - prev_val)
    
    reasoning = f"Delta {delta:.3f} exceeded limit {max_delta}. Applied scaling factor {scale_factor:.3f} to constrain transition."
    
    # For now, we don't have a mechanism to "adjust" node selections to hit exact affective target
    # In a full implementation, you'd re-score nodes to find combination closest to constrained_state
    # For MVP, we just log the constraint and return original (with warning)
    
    logging.warning("⚠ Affective governor constraint triggered")
    logging.warning(f"Recommended state adjustment: {constrained_state}")
    logging.warning("Note: Current implementation logs constraint but doesn't modify node selection")
    logging.warning("Future enhancement: Re-select nodes to match constrained affective target")
    
    return selections, True, reasoning


def append_to_history(history_path: str, turn_data: Dict) -> None:
    """Append turn data to conversation history JSONL."""
    with open(history_path, 'a') as f:
        f.write(json.dumps(turn_data) + '\n')


def main():
    parser = argparse.ArgumentParser(description="Affective governor for smooth persona transitions")
    parser.add_argument('--selections', '-s', type=str, required=True, 
                        help="Path to selected_nodes.json from Phase 4b")
    parser.add_argument('--history', type=str, default='outputs/conversation_history.jsonl',
                        help="Path to conversation history JSONL")
    parser.add_argument('--max-delta', type=float, default=0.3,
                        help="Maximum allowed affective state change (0.0-1.0)")
    parser.add_argument('--message-id', type=str, default=None,
                        help="AI SDK message ID for this turn (optional)")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    setup_logging(config)
    
    # Load persona sheet
    sheet_path = "outputs/persona_sheets.json"
    
    if not Path(sheet_path).exists():
        logging.error(f"Error: {sheet_path} not found. Run Phase 4 first.")
        sys.exit(1)
    
    if not Path(args.selections).exists():
        logging.error(f"Error: {args.selections} not found. Run Phase 4b first.")
        sys.exit(1)
    
    logging.info("="*60)
    logging.info("Phase 4c: Affective Governor")
    logging.info("="*60)
    
    persona_sheet = load_persona_sheet(sheet_path)
    
    with open(args.selections, 'r') as f:
        selections = json.load(f)
    
    # Load conversation history
    history = load_conversation_history(args.history)
    
    logging.info(f"Persona: {persona_sheet['persona']['label']}")
    logging.info(f"Conversation history: {len(history)} turn(s)")
    logging.info(f"Max affective delta: {args.max_delta}")
    logging.info("")
    
    # Get previous affective state
    prev_state = None
    if history:
        prev_state = history[-1].get('affective_state')
        logging.info(f"Previous affective state: {prev_state}")
    else:
        logging.info("First turn - no previous state")
    
    # Calculate proposed state
    proposed_state = calculate_affective_state(selections, persona_sheet)
    logging.info(f"Proposed affective state: {proposed_state}")
    
    # Calculate delta
    if prev_state:
        delta = calculate_affective_delta(prev_state, proposed_state)
        logging.info(f"Affective delta: {delta:.3f}")
    else:
        delta = 0.0
    
    logging.info("")
    
    # Apply governor constraints
    constrained_selections, was_modified, reasoning = constrain_selections(
        selections, persona_sheet, prev_state, args.max_delta
    )
    
    if was_modified:
        logging.warning("⚠ AFFECTIVE CONSTRAINT TRIGGERED")
        logging.warning(f"Reasoning: {reasoning}")
        logging.info("")
    else:
        logging.info("✓ Selection approved by affective governor")
        logging.info(f"Reasoning: {reasoning}")
        logging.info("")
    
    # Record turn in history
    turn_data = {
        'turn_id': len(history) + 1,
        'message_id': args.message_id or f"turn-{len(history) + 1}",
        'timestamp': datetime.utcnow().isoformat(),
        'user_message': selections['metadata']['message'],
        'selected_nodes': {
            'values': [s['node_id'] for s in constrained_selections.get('values', [])],
            'drives': [s['node_id'] for s in constrained_selections.get('drives', [])],
            'reasoning_patterns': [s['node_id'] for s in constrained_selections.get('reasoning_patterns', [])],
            'linguistic_styles': [s['node_id'] for s in constrained_selections.get('linguistic_styles', [])]
        },
        'affective_state': proposed_state,
        'affective_delta': delta,
        'was_constrained': was_modified,
        'constraint_reasoning': reasoning
    }
    
    append_to_history(args.history, turn_data)
    logging.info(f"Turn recorded to: {args.history}")
    
    # Display summary
    print("\n" + "="*60)
    print("AFFECTIVE GOVERNANCE SUMMARY")
    print("="*60)
    print(f"Turn: {turn_data['turn_id']}")
    print(f"Message: {turn_data['user_message'][:60]}...")
    print("")
    print("Affective State:")
    for dim, val in proposed_state.items():
        indicator = "↑" if prev_state and val > prev_state.get(dim, 0.5) else "↓" if prev_state and val < prev_state.get(dim, 0.5) else "→"
        print(f"  {dim:12s}: {val:.2f} {indicator}")
    print("")
    print(f"Delta: {delta:.3f} / {args.max_delta} {'⚠ CONSTRAINED' if was_modified else '✓ APPROVED'}")
    print("="*60)


if __name__ == "__main__":
    main()
