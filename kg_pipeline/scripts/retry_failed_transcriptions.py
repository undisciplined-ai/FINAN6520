#!/usr/bin/env python3
"""
Retry Failed Transcription Chunks

Re-processes only failed chunks from previous transcription attempts.
Uses the cached chunk transcripts and identifies missing/failed chunks.

Usage:
    python scripts/retry_failed_transcriptions.py audiobook.m4b
    python scripts/retry_failed_transcriptions.py audiobook.m4b --output outputs/transcript.txt
    
    # Or retry all books in a directory
    python scripts/retry_failed_transcriptions.py inputs/
"""

import sys
import logging
import argparse
from pathlib import Path
from typing import List, Set
import re

# Import from phase0 module
sys.path.insert(0, str(Path(__file__).parent))
from phase0_transcribe_audio import (
    load_env_file, load_config, setup_logging,
    split_audio_into_chunks, transcribe_audio_parallel,
    cleanup_chunks, get_cache_path
)


def find_missing_chunks(audio_path: str, total_chunks: int) -> Set[int]:
    """
    Identify which chunks are missing from cache.
    
    Args:
        audio_path: Path to original audio file
        total_chunks: Total number of chunks expected
    
    Returns:
        Set of missing chunk indices
    """
    missing = set()
    
    for i in range(total_chunks):
        cache_file = get_cache_path(audio_path, i)
        if not cache_file.exists() or cache_file.stat().st_size == 0:
            missing.add(i)
    
    return missing


def detect_failed_chunks_from_transcript(transcript_path: str) -> List[int]:
    """
    Parse transcript file to find [MISSING CHUNK N] placeholders.
    
    Args:
        transcript_path: Path to transcript file
    
    Returns:
        List of failed chunk indices
    """
    if not Path(transcript_path).exists():
        return []
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all [MISSING CHUNK N] markers
    pattern = r'\[MISSING CHUNK (\d+)\]'
    matches = re.findall(pattern, content)
    
    return [int(m) for m in matches]


def main():
    parser = argparse.ArgumentParser(description="Retry failed transcription chunks")
    parser.add_argument(
        "input",
        help="Path to M4B audiobook file or directory"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output transcript path (default: outputs/transcripts/<filename>.txt)"
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="Re-transcribe all chunks, ignoring cache"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    load_env_file()
    config = load_config()
    setup_logging(config)
    
    # Resolve input path
    input_path = Path(args.input)
    
    if not input_path.exists():
        logging.error(f"Input path not found: {input_path}")
        sys.exit(1)
    
    # Get list of audio files
    if input_path.is_dir():
        audio_files = list(input_path.glob("*.m4b"))
        if not audio_files:
            logging.error(f"No .m4b files found in {input_path}")
            sys.exit(1)
    else:
        audio_files = [input_path]
    
    logging.info(f"Found {len(audio_files)} audiobook(s) to process")
    
    # Process each audiobook
    for audio_file in audio_files:
        logging.info("")
        logging.info("="*60)
        logging.info(f"Processing: {audio_file.name}")
        logging.info("="*60)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path("outputs/transcripts") / f"{audio_file.stem}.txt"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get transcription config
        transcription_config = config.get('transcription', {})
        max_retries = transcription_config.get('max_retries', 3)
        
        # Split audio to get chunk count
        chunk_paths = split_audio_into_chunks(str(audio_file), chunk_duration_minutes=20)
        total_chunks = len(chunk_paths)
        
        try:
            if args.force_all:
                logging.info("Force mode: Re-transcribing all chunks")
                # Delete cache
                for i in range(total_chunks):
                    cache_file = get_cache_path(str(audio_file), i)
                    if cache_file.exists():
                        cache_file.unlink()
            else:
                # Check for missing chunks
                missing_from_cache = find_missing_chunks(str(audio_file), total_chunks)
                missing_from_transcript = detect_failed_chunks_from_transcript(str(output_path))
                
                all_missing = missing_from_cache | set(missing_from_transcript)
                
                if not all_missing:
                    logging.info("✅ All chunks already transcribed successfully!")
                    logging.info(f"Skipping {audio_file.name}")
                    continue
                
                logging.info(f"Found {len(all_missing)} missing/failed chunks: {sorted(all_missing)}")
            
            # Run transcription with retry
            parallel_config = config.get('parallel', {})
            max_workers = parallel_config.get('max_workers', 8)
            
            result = transcribe_audio_parallel(
                chunk_paths,
                str(audio_file),
                max_workers=max_workers,
                max_retries=max_retries
            )
            
            # Save transcript
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['transcript'])
            
            stats = result['stats']
            logging.info("")
            logging.info("="*60)
            logging.info(f"✅ Transcript saved: {output_path}")
            logging.info(f"Success rate: {stats['success_rate']:.1f}%")
            logging.info(f"Failed chunks: {len(result['failed_chunks'])}")
            logging.info("="*60)
            
        finally:
            cleanup_chunks(chunk_paths)
    
    logging.info("")
    logging.info("All books processed!")


if __name__ == "__main__":
    main()
