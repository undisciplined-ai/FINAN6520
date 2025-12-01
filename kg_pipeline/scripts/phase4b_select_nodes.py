#!/usr/bin/env python3
"""
Phase 4b: Dynamic Node Selection

Selects which nodes to activate in each slot based on conversation context.
Uses LLM semantic understanding for intelligent, context-aware node selection.

Usage:
    python scripts/phase4b_select_nodes.py --message "I'm struggling with this project"
    
Requires:
    - outputs/persona_sheets.json (from Phase 4)
    - prompts/phase4b_node_selection.txt
    - .env with AI_GATEWAY_API_KEY
    
Outputs:
    - Selected node IDs for each slot type
    - LLM reasoning for selections
"""

import sys
import json
import logging
import argparse
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
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
    
    # Return first persona sheet
    return sheets[0]


def load_prompt_template(template_path: str) -> str:
    """Load prompt template."""
    with open(template_path, 'r') as f:
        return f.read()


def load_conversation_history(history_path: str) -> List[Dict]:
    """Load recent conversation history."""
    if not Path(history_path).exists():
        return []
    
    history = []
    with open(history_path, 'r') as f:
        for line in f:
            if line.strip():
                history.append(json.loads(line))
    
    # Return last 3 turns for context
    return history[-3:]


def format_nodes_for_prompt(items: List[Dict], node_type: str) -> str:
    """Format nodes for LLM prompt."""
    if not items:
        return f"(No {node_type} nodes available)"
    
    lines = []
    for item in items:
        node = item['node']
        lines.append(f"- ID: {node['id']}")
        lines.append(f"  Label: {node['label']}")
        lines.append(f"  Description: {node['description']}")
        
        # Include key fields based on type
        fields = node.get('fields', {})
        if node['type'] == 'Value':
            lines.append(f"  Principle: {fields.get('principle', 'N/A')}")
            lines.append(f"  Directive: {fields.get('behavioral_directive', 'N/A')}")
        elif node['type'] == 'Drive':
            lines.append(f"  Goal: {fields.get('goal_description', 'N/A')}")
            lines.append(f"  Motivation: {fields.get('motivation', 'N/A')}")
        elif node['type'] == 'ReasoningPattern':
            lines.append(f"  Trigger: {fields.get('trigger', 'N/A')}")
            lines.append(f"  Response: {fields.get('preferred_response', 'N/A')}")
        elif node['type'] == 'LinguisticStyle':
            lines.append(f"  Formality: {fields.get('formality', 'N/A')}")
            lines.append(f"  Affect: {fields.get('affect_modulation', 'N/A')}")
        
        lines.append("")
    
    return "\n".join(lines)


def format_history_for_prompt(history: List[Dict]) -> str:
    """Format conversation history for LLM."""
    if not history:
        return "(No previous conversation)"
    
    lines = []
    for turn in history:
        lines.append(f"Turn {turn['turn_id']}:")
        lines.append(f"  User: {turn['user_message'][:80]}...")
        lines.append(f"  Affective State: warmth={turn['affective_state']['warmth']:.2f}, "
                    f"formality={turn['affective_state']['formality']:.2f}, "
                    f"directness={turn['affective_state']['directness']:.2f}")
        lines.append("")
    
    return "\n".join(lines)


def call_llm(prompt: str, config: Dict) -> Dict:
    """
    Call Vercel AI Gateway via Node.js wrapper for node selection.
    
    Args:
        prompt: Formatted prompt text
        config: Runtime configuration
    
    Returns:
        Parsed JSON response from LLM
    """
    phase2_config = config['phase2']
    
    # Prepare input for Node.js wrapper
    wrapper_input = {
        "model": phase2_config['model'],
        "prompt": prompt,
        "temperature": 0.2,  # Slightly higher for more nuanced selection
        "maxTokens": 2000
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


def select_nodes_for_slots(persona_sheet: Dict, message: str, history: List[Dict], 
                           prompt_template: str, config: Dict) -> Dict:
    """
    Use LLM to select best-fit nodes for each slot type based on semantic understanding.
    
    Args:
        persona_sheet: Full persona data from Phase 4
        message: User's message
        history: Recent conversation history
        prompt_template: Template for LLM prompt
        config: Runtime configuration
    
    Returns:
        Dict with selected nodes per slot type and LLM reasoning
    """
    # Format node information for prompt
    values_text = format_nodes_for_prompt(persona_sheet.get('values', []), 'Value')
    drives_text = format_nodes_for_prompt(persona_sheet.get('drives', []), 'Drive')
    reasoning_text = format_nodes_for_prompt(persona_sheet.get('reasoning_patterns', []), 'ReasoningPattern')
    styles_text = format_nodes_for_prompt(persona_sheet.get('linguistic_styles', []), 'LinguisticStyle')
    
    constraints_text = "\n".join([
        f"- {item['node']['label']}: {item['node']['description']}"
        for item in persona_sheet.get('constraints', [])
    ])
    
    history_text = format_history_for_prompt(history)
    
    # Build prompt
    prompt = prompt_template.format(
        user_message=message,
        conversation_history=history_text,
        values=values_text,
        drives=drives_text,
        reasoning_patterns=reasoning_text,
        styles=styles_text,
        constraints=constraints_text
    )
    
    logging.info("Calling LLM for node selection...")
    
    # Call LLM
    try:
        response = call_llm(prompt, config)
    except Exception as e:
        logging.error(f"Failed to get LLM selection: {e}")
        raise
    
    # Extract selections
    llm_selections = response.get('selections', {})
    affective_assessment = response.get('affective_assessment', {})
    
    # Reformat to match expected output structure
    selections = {
        'values': llm_selections.get('values', []),
        'drives': llm_selections.get('drives', []),
        'reasoning_patterns': llm_selections.get('reasoning_patterns', []),
        'linguistic_styles': llm_selections.get('linguistic_styles', []),
        'constraints': persona_sheet.get('constraints', []),
        'metadata': {
            'message': message,
            'affective_assessment': affective_assessment,
            'llm_reasoning': True
        }
    }
    
    # Log selections
    logging.info(f"LLM selected {len(selections['values'])} value(s), "
                f"{len(selections['drives'])} drive(s), "
                f"{len(selections['reasoning_patterns'])} reasoning pattern(s), "
                f"{len(selections['linguistic_styles'])} style(s)")
    logging.info("")
    
    return selections


def format_selection_report(selections: Dict) -> str:
    """Format selection results for display."""
    lines = []
    
    lines.append("="*60)
    lines.append("DYNAMIC NODE SELECTION REPORT (LLM-Powered)")
    lines.append("="*60)
    lines.append("")
    
    lines.append(f"User Message: {selections['metadata']['message']}")
    lines.append("")
    
    # Affective assessment from LLM
    affective = selections['metadata'].get('affective_assessment', {})
    if affective:
        lines.append("LLM Affective Assessment:")
        lines.append(f"  User Emotion: {affective.get('user_emotion', 'N/A')}")
        lines.append(f"  Recommended Warmth: {affective.get('recommended_warmth', 'N/A')}")
        lines.append(f"  Recommended Directness: {affective.get('recommended_directness', 'N/A')}")
        if affective.get('transition_notes'):
            lines.append(f"  Transition: {affective.get('transition_notes')}")
        lines.append("")
    
    lines.append("-"*60)
    lines.append("SELECTED NODES")
    lines.append("-"*60)
    lines.append("")
    
    # Values
    if selections['values']:
        lines.append(f"Values ({len(selections['values'])} selected):")
        for item in selections['values']:
            lines.append(f"  ✓ {item['node_id']}")
            lines.append(f"    Relevance: {item.get('relevance_score', 'N/A')}")
            lines.append(f"    Reasoning: {item.get('reasoning', 'N/A')}")
        lines.append("")
    
    # Drives
    if selections['drives']:
        lines.append(f"Drives ({len(selections['drives'])} selected):")
        for item in selections['drives']:
            lines.append(f"  ✓ {item['node_id']}")
            lines.append(f"    Relevance: {item.get('relevance_score', 'N/A')}")
            lines.append(f"    Reasoning: {item.get('reasoning', 'N/A')}")
        lines.append("")
    
    # Reasoning
    if selections['reasoning_patterns']:
        lines.append(f"Reasoning Patterns ({len(selections['reasoning_patterns'])} selected):")
        for item in selections['reasoning_patterns']:
            lines.append(f"  ✓ {item['node_id']}")
            lines.append(f"    Relevance: {item.get('relevance_score', 'N/A')}")
            lines.append(f"    Reasoning: {item.get('reasoning', 'N/A')}")
        lines.append("")
    
    # Styles
    if selections['linguistic_styles']:
        lines.append(f"Communication Styles ({len(selections['linguistic_styles'])} selected):")
        for item in selections['linguistic_styles']:
            lines.append(f"  ✓ {item['node_id']}")
            lines.append(f"    Relevance: {item.get('relevance_score', 'N/A')}")
            lines.append(f"    Reasoning: {item.get('reasoning', 'N/A')}")
        lines.append("")
    
    # Constraints (always active)
    if selections['constraints']:
        lines.append(f"Active Constraints ({len(selections['constraints'])} always enforced):")
        for item in selections['constraints']:
            lines.append(f"  ⚠ {item['node']['label']}")
        lines.append("")
    
    lines.append("="*60)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="LLM-powered dynamic node selection based on semantic understanding")
    parser.add_argument('--message', '-m', type=str, required=True, help="User message to analyze")
    parser.add_argument('--output', '-o', type=str, default='outputs/selected_nodes.json', 
                        help="Output path for selections JSON")
    parser.add_argument('--history', type=str, default='outputs/conversation_history.jsonl',
                        help="Path to conversation history")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_env_file()
    
    # Load configuration
    config = load_config()
    setup_logging(config)
    
    # Check for API key
    api_key_env = config['api_key_env']
    if not os.environ.get(api_key_env):
        logging.error(f"Error: {api_key_env} environment variable not set")
        logging.error("Create .env file with your Vercel AI Gateway API key")
        sys.exit(1)
    
    # Load persona sheet
    sheet_path = "outputs/persona_sheets.json"
    
    if not Path(sheet_path).exists():
        logging.error(f"Error: {sheet_path} not found. Run Phase 4 first.")
        sys.exit(1)
    
    # Load prompt template
    prompt_template_path = "prompts/phase4b_node_selection.txt"
    if not Path(prompt_template_path).exists():
        logging.error(f"Error: {prompt_template_path} not found.")
        sys.exit(1)
    
    logging.info("="*60)
    logging.info("Phase 4b: Dynamic Node Selection (LLM-Powered)")
    logging.info("="*60)
    logging.info(f"Loading persona sheet from: {sheet_path}")
    
    persona_sheet = load_persona_sheet(sheet_path)
    prompt_template = load_prompt_template(prompt_template_path)
    history = load_conversation_history(args.history)
    
    logging.info(f"Persona: {persona_sheet['persona']['label']}")
    logging.info(f"Available nodes: {persona_sheet['metadata']['total_nodes']}")
    logging.info(f"Conversation history: {len(history)} recent turn(s)")
    logging.info(f"Model: {config['phase2']['model']}")
    logging.info("")
    
    # Select nodes based on message using LLM
    selections = select_nodes_for_slots(persona_sheet, args.message, history, prompt_template, config)
    
    # Write selections to file
    output_path = args.output
    with open(output_path, 'w') as f:
        json.dump(selections, f, indent=2)
    
    logging.info(f"Wrote selections to: {output_path}")
    logging.info("")
    
    # Display report
    report = format_selection_report(selections)
    print("\n" + report)


if __name__ == "__main__":
    main()
