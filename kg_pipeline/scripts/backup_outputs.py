#!/usr/bin/env python3
"""
Backup utility for pipeline outputs.

Creates timestamped backups of outputs directory with optional phase label.

Usage:
    python scripts/backup_outputs.py [phase_label]
    
Examples:
    python scripts/backup_outputs.py phase1_chunks
    python scripts/backup_outputs.py phase2_nodes
    python scripts/backup_outputs.py phase2.5_canonical
"""

import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime


def backup_outputs(phase_label: str = None) -> Path:
    """
    Create timestamped backup of outputs directory.
    
    Args:
        phase_label: Optional label to append (e.g., 'phase1_chunks')
    
    Returns:
        Path to backup directory
    """
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build backup directory name
    if phase_label:
        backup_name = f"{timestamp}_{phase_label}"
    else:
        backup_name = timestamp
    
    # Create backup directory
    backup_dir = Path("backups") / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy outputs
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        logging.warning("No outputs directory found, creating empty backup")
        return backup_dir
    
    # Copy all files and subdirectories
    for item in outputs_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, backup_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, backup_dir / item.name, dirs_exist_ok=True)
    
    logging.info(f"✅ Backup created: {backup_dir}")
    return backup_dir


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    # Get optional phase label from command line
    phase_label = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create backup
    backup_dir = backup_outputs(phase_label)
    
    print(f"\n{'='*60}")
    print(f"Backup Location: {backup_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
