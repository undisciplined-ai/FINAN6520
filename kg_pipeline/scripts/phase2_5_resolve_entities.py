#!/usr/bin/env python3
"""
Phase 2.5: Entity Resolution

Deduplicates nodes across chunks by clustering similar concepts and creating
canonical node representations. Updates provenance to track merged nodes.

Usage:
    python scripts/phase2_5_resolve_entities.py
    
Requires:
    - outputs/nodes.jsonl (from Phase 2)
    
Outputs:
    - outputs/nodes_canonical.jsonl (deduplicated nodes)
    - outputs/entity_mapping.json (original_id -> canonical_id mapping)
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set
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


def load_nodes(nodes_path: str) -> List[Dict]:
    """Load all nodes from file."""
    nodes = []
    with open(nodes_path, 'r') as f:
        for line in f:
            nodes.append(json.loads(line))
    return nodes


def calculate_similarity(label1: str, label2: str, desc1: str, desc2: str) -> float:
    """
    Calculate simple text similarity between two nodes.
    Uses label and description overlap.
    
    Returns:
        Similarity score between 0.0 and 1.0
    """
    # Normalize text
    label1_lower = label1.lower()
    label2_lower = label2.lower()
    desc1_lower = desc1.lower()
    desc2_lower = desc2.lower()
    
    # Exact label match
    if label1_lower == label2_lower:
        return 1.0
    
    # Check if one label contains the other
    if label1_lower in label2_lower or label2_lower in label1_lower:
        return 0.85
    
    # Calculate word overlap in labels
    words1 = set(label1_lower.split())
    words2 = set(label2_lower.split())
    
    if not words1 or not words2:
        return 0.0
    
    label_overlap = len(words1 & words2) / len(words1 | words2)
    
    # Calculate word overlap in descriptions
    desc_words1 = set(desc1_lower.split())
    desc_words2 = set(desc2_lower.split())
    
    if desc_words1 and desc_words2:
        desc_overlap = len(desc_words1 & desc_words2) / len(desc_words1 | desc_words2)
    else:
        desc_overlap = 0.0
    
    # Weighted combination (label matters more)
    similarity = (0.7 * label_overlap) + (0.3 * desc_overlap)
    
    return similarity


def cluster_similar_nodes(nodes: List[Dict], similarity_threshold: float = 0.75) -> List[List[Dict]]:
    """
    Cluster nodes by type and similarity.
    
    Args:
        nodes: List of all nodes
        similarity_threshold: Minimum similarity to merge
    
    Returns:
        List of clusters, where each cluster is a list of similar nodes
    """
    # Group nodes by type first
    nodes_by_type = defaultdict(list)
    for node in nodes:
        nodes_by_type[node['type']].append(node)
    
    all_clusters = []
    
    # Process each type separately
    for node_type, type_nodes in nodes_by_type.items():
        clusters = []
        used = set()
        
        for i, node1 in enumerate(type_nodes):
            if i in used:
                continue
            
            # Start new cluster with this node
            cluster = [node1]
            used.add(i)
            
            # Find similar nodes
            for j, node2 in enumerate(type_nodes):
                if j <= i or j in used:
                    continue
                
                # Calculate similarity
                sim = calculate_similarity(
                    node1['label'], node2['label'],
                    node1['description'], node2['description']
                )
                
                if sim >= similarity_threshold:
                    cluster.append(node2)
                    used.add(j)
            
            clusters.append(cluster)
        
        all_clusters.extend(clusters)
    
    return all_clusters


def create_canonical_node(cluster: List[Dict]) -> Dict:
    """
    Create a canonical node from a cluster of similar nodes.
    
    Uses the highest importance node as base, merges provenance from all.
    """
    # Sort by importance (highest first)
    sorted_cluster = sorted(cluster, key=lambda n: n['importance'], reverse=True)
    canonical = sorted_cluster[0].copy()
    
    # Use the first node's ID as canonical ID
    canonical['id'] = sorted_cluster[0]['id']
    
    # Merge provenance from all nodes
    all_provenance = []
    for node in cluster:
        prov = node['provenance'].copy()
        prov['original_id'] = node['id']
        all_provenance.append(prov)
    
    canonical['provenance'] = all_provenance
    
    # Average importance across cluster
    canonical['importance'] = sum(n['importance'] for n in cluster) / len(cluster)
    
    # Merge tags (unique)
    all_tags = set()
    for node in cluster:
        all_tags.update(node.get('tags', []))
    canonical['tags'] = sorted(list(all_tags))
    
    # Add metadata about merging
    canonical['merged_from'] = [n['id'] for n in cluster[1:]]
    canonical['cluster_size'] = len(cluster)
    
    return canonical


def build_entity_mapping(clusters: List[List[Dict]]) -> Dict[str, str]:
    """
    Build mapping from original node IDs to canonical node IDs.
    
    Returns:
        Dict mapping original_id -> canonical_id
    """
    mapping = {}
    
    for cluster in clusters:
        if not cluster:
            continue
        
        # First node in cluster becomes canonical
        canonical_id = cluster[0]['id']
        
        # Map all nodes in cluster to canonical ID
        for node in cluster:
            mapping[node['id']] = canonical_id
    
    return mapping


def main():
    # Load configuration
    config = load_config()
    setup_logging(config)
    
    # Load nodes
    nodes_path = "outputs/nodes.jsonl"
    
    if not Path(nodes_path).exists():
        logging.error(f"Error: {nodes_path} not found. Run Phase 2 first.")
        sys.exit(1)
    
    logging.info("="*60)
    logging.info("Phase 2.5: Entity Resolution")
    logging.info("="*60)
    logging.info(f"Loading nodes from: {nodes_path}")
    
    nodes = load_nodes(nodes_path)
    
    logging.info(f"Loaded {len(nodes)} nodes")
    logging.info("")
    
    # Get similarity threshold from config (default 0.75)
    similarity_threshold = config.get('entity_resolution', {}).get('similarity_threshold', 0.75)
    
    logging.info(f"Clustering similar nodes (threshold: {similarity_threshold})...")
    clusters = cluster_similar_nodes(nodes, similarity_threshold)
    
    # Count singletons vs merged clusters
    singletons = sum(1 for c in clusters if len(c) == 1)
    merged = sum(1 for c in clusters if len(c) > 1)
    total_merged_nodes = sum(len(c) for c in clusters if len(c) > 1)
    
    logging.info(f"Found {len(clusters)} unique concepts:")
    logging.info(f"  - {singletons} unique nodes (no duplicates)")
    logging.info(f"  - {merged} merged clusters ({total_merged_nodes} nodes deduplicated)")
    logging.info("")
    
    # Create canonical nodes
    logging.info("Creating canonical node representations...")
    canonical_nodes = []
    
    for cluster in clusters:
        canonical = create_canonical_node(cluster)
        canonical_nodes.append(canonical)
    
    # Build entity mapping
    entity_mapping = build_entity_mapping(clusters)
    
    # Write canonical nodes
    output_path = "outputs/nodes_canonical.jsonl"
    with open(output_path, 'w') as f:
        for node in canonical_nodes:
            f.write(json.dumps(node) + '\n')
    
    logging.info(f"Wrote {len(canonical_nodes)} canonical nodes to: {output_path}")
    
    # Write entity mapping
    mapping_path = "outputs/entity_mapping.json"
    with open(mapping_path, 'w') as f:
        json.dump(entity_mapping, f, indent=2)
    
    logging.info(f"Wrote entity mapping to: {mapping_path}")
    logging.info("")
    
    # Summary statistics
    logging.info("="*60)
    logging.info("✅ Phase 2.5 Complete")
    logging.info(f"Original nodes: {len(nodes)}")
    logging.info(f"Canonical nodes: {len(canonical_nodes)}")
    logging.info(f"Deduplication rate: {(1 - len(canonical_nodes)/len(nodes))*100:.1f}%")
    logging.info("")
    
    # Show sample merges
    merged_clusters = [c for c in clusters if len(c) > 1]
    if merged_clusters:
        logging.info("Sample merged clusters:")
        for cluster in merged_clusters[:3]:
            canonical_id = cluster[0]['id']
            logging.info(f"  {canonical_id}: merged {len(cluster)} nodes")
            for node in cluster:
                logging.info(f"    - {node['id']}: {node['label']}")
    
    logging.info("="*60)


if __name__ == "__main__":
    main()
