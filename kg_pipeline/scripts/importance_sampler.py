#!/usr/bin/env python3
"""
Importance-Based Node Sampling Utility

Filters and samples nodes based on calibrated 10-bucket importance system.
Used by downstream phases (Phase 3, Phase 4) to focus processing on high-value nodes.

Usage:
    from importance_sampler import sample_nodes_by_importance
    
    sampled = sample_nodes_by_importance(all_nodes, config, seed=42)
"""

import random
from typing import List, Dict, Tuple


def get_bucket_for_score(importance: float, buckets: Dict) -> Tuple[str, List]:
    """
    Determine which bucket an importance score falls into.
    
    Args:
        importance: Score between 0.0 and 1.0
        buckets: Bucket configuration from run_config.yaml
    
    Returns:
        Tuple of (bucket_name, [min, max, sample_rate])
    """
    for bucket_name, (min_score, max_score, sample_rate) in buckets.items():
        if min_score <= importance <= max_score:
            return bucket_name, [min_score, max_score, sample_rate]
    
    # Default to lowest bucket if out of range
    return "bucket_1", [0.0, 0.09, 0.0]


def sample_nodes_by_importance(
    nodes: List[Dict],
    config: Dict,
    seed: int = None,
    verbose: bool = False
) -> List[Dict]:
    """
    Sample nodes based on importance-based bucket sampling rates.
    
    Args:
        nodes: List of node dictionaries with 'importance' field
        config: Configuration dict with 'importance_sampling' section
        seed: Random seed for reproducibility (optional)
        verbose: Print sampling statistics
    
    Returns:
        List of sampled nodes (subset of input)
    """
    if seed is not None:
        random.seed(seed)
    
    sampling_config = config.get('importance_sampling', {})
    buckets = sampling_config.get('buckets', {})
    
    if not buckets:
        # No sampling config - return all nodes
        return nodes
    
    sampled_nodes = []
    bucket_stats = {name: {"total": 0, "sampled": 0} for name in buckets.keys()}
    
    for node in nodes:
        importance = node.get('importance', 0.5)
        bucket_name, (min_score, max_score, sample_rate) = get_bucket_for_score(importance, buckets)
        
        bucket_stats[bucket_name]["total"] += 1
        
        # Apply sampling rate
        if sample_rate >= 1.0:
            # Always include
            sampled_nodes.append(node)
            bucket_stats[bucket_name]["sampled"] += 1
        elif sample_rate > 0.0:
            # Probabilistic sampling
            if random.random() < sample_rate:
                sampled_nodes.append(node)
                bucket_stats[bucket_name]["sampled"] += 1
        # else: sample_rate == 0.0, exclude node
    
    if verbose:
        print("\n" + "="*60)
        print("IMPORTANCE-BASED SAMPLING RESULTS")
        print("="*60)
        print(f"Original nodes: {len(nodes)}")
        print(f"Sampled nodes:  {len(sampled_nodes)}")
        print(f"Retention rate: {len(sampled_nodes)/len(nodes)*100:.1f}%")
        print("\nPer-bucket breakdown:")
        print(f"{'Bucket':<12} {'Range':<15} {'Rate':<8} {'Total':<8} {'Sampled':<8} {'%':<8}")
        print("-"*60)
        
        for bucket_name, (min_score, max_score, sample_rate) in sorted(buckets.items(), reverse=True):
            stats = bucket_stats[bucket_name]
            if stats["total"] > 0:
                retention = stats["sampled"] / stats["total"] * 100
                print(f"{bucket_name:<12} [{min_score:.2f}-{max_score:.2f}]  {sample_rate*100:>5.0f}%  {stats['total']:>6}  {stats['sampled']:>7}  {retention:>6.1f}%")
        print("="*60)
    
    return sampled_nodes


def get_sampling_summary(nodes: List[Dict], config: Dict) -> Dict:
    """
    Get statistics about how nodes are distributed across importance buckets.
    
    Args:
        nodes: List of node dictionaries
        config: Configuration dict
    
    Returns:
        Dict with bucket distribution stats
    """
    sampling_config = config.get('importance_sampling', {})
    buckets = sampling_config.get('buckets', {})
    
    distribution = {name: 0 for name in buckets.keys()}
    
    for node in nodes:
        importance = node.get('importance', 0.5)
        bucket_name, _ = get_bucket_for_score(importance, buckets)
        distribution[bucket_name] += 1
    
    return {
        "total_nodes": len(nodes),
        "bucket_distribution": distribution
    }


if __name__ == "__main__":
    import yaml
    import json
    import sys
    
    # Example usage: python scripts/importance_sampler.py outputs/nodes_canonical.jsonl
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/importance_sampler.py <nodes_file.jsonl>")
        sys.exit(1)
    
    # Load config
    with open("config/run_config.yaml") as f:
        config = yaml.safe_load(f)
    
    # Load nodes
    nodes = []
    with open(sys.argv[1]) as f:
        for line in f:
            nodes.append(json.loads(line))
    
    print(f"\nLoaded {len(nodes)} nodes from {sys.argv[1]}")
    
    # Show distribution
    summary = get_sampling_summary(nodes, config)
    print(f"\nBucket distribution:")
    for bucket, count in sorted(summary["bucket_distribution"].items(), reverse=True):
        if count > 0:
            pct = count / summary["total_nodes"] * 100
            print(f"  {bucket}: {count} ({pct:.1f}%)")
    
    # Sample and show results
    sampled = sample_nodes_by_importance(nodes, config, seed=42, verbose=True)
