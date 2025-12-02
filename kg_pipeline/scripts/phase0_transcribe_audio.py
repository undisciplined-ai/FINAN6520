#!/usr/bin/env python3
"""
Phase 0: Audio Transcription (M4B Audiobooks)

Transcribes M4B audiobook files to text using OpenAI Whisper API.
Supports parallel processing for large files by splitting into chunks.

Usage:
    python scripts/phase0_transcribe_audio.py /path/to/audiobook.m4b [outputs/transcript.txt]
    
Requires:
    - .env with OPENAI_API_KEY
    - ffmpeg installed (for audio splitting)
    - pydub library
"""

import sys
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
from openai import OpenAI
import time


def suggest_workers(chunk_count: int, tier_rpm: int = 500, manual_override: int = None) -> int:
    """
    Suggest optimal worker count based on chunk count and API tier limits.
    
    Args:
        chunk_count: Number of chunks to process
        tier_rpm: Rate limit (requests per minute) for your OpenAI tier
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


def setup_logging(config: Dict) -> None:
    """Configure logging based on config settings."""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffprobe without loading file."""
    import subprocess
    import json
    
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        audio_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def split_single_chunk(args):
    """Helper function to split a single audio chunk in parallel."""
    import subprocess
    audio_path, start_time, chunk_duration_seconds, chunk_path, chunk_idx, total_chunks = args
    
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output
        '-ss', str(start_time),  # Start time
        '-t', str(chunk_duration_seconds),  # Duration
        '-i', audio_path,  # Input file
        '-vn',  # No video
        '-acodec', 'libmp3lame',  # MP3 codec
        '-ab', '64k',  # Bitrate
        '-ar', '16000',  # Sample rate (Whisper optimized)
        chunk_path
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    
    # Log progress every 5 chunks
    if (chunk_idx + 1) % 5 == 0 or chunk_idx == total_chunks - 1:
        logging.info(f"Split progress: {chunk_idx+1}/{total_chunks} chunks created")
    
    return chunk_path


def split_audio_into_chunks(audio_path: str, chunk_duration_minutes: int = 20, max_workers: int = 8) -> List[str]:
    """
    Split audio file into chunks using ffmpeg in parallel.
    
    Args:
        audio_path: Path to M4B audiobook file
        chunk_duration_minutes: Duration of each chunk in minutes
        max_workers: Number of parallel ffmpeg workers for splitting
    
    Returns:
        List of temporary chunk file paths
    """
    import subprocess
    
    logging.info(f"Analyzing audio file: {audio_path}")
    
    # Get duration without loading entire file
    duration_seconds = get_audio_duration(audio_path)
    duration_minutes = duration_seconds / 60
    chunk_duration_seconds = chunk_duration_minutes * 60
    
    logging.info(f"Audio duration: {duration_minutes:.1f} minutes")
    
    # Calculate number of chunks
    num_chunks = int((duration_seconds + chunk_duration_seconds - 1) / chunk_duration_seconds)
    logging.info(f"Splitting into {num_chunks} chunks of {chunk_duration_minutes} minutes each using {max_workers} workers")
    
    # Create temporary directory for chunks
    temp_dir = tempfile.mkdtemp(prefix="audio_chunks_")
    
    # Prepare all chunk split tasks
    tasks = []
    for i in range(num_chunks):
        start_time = i * chunk_duration_seconds
        chunk_path = os.path.join(temp_dir, f"chunk_{i:04d}.mp3")
        tasks.append((audio_path, start_time, chunk_duration_seconds, chunk_path, i, num_chunks))
    
    # Execute splits in parallel
    chunk_paths = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(split_single_chunk, task) for task in tasks]
        for future in as_completed(futures):
            chunk_path = future.result()
            chunk_paths.append(chunk_path)
    
    # Sort to maintain order
    chunk_paths.sort()
    
    logging.info(f"Audio split complete: {len(chunk_paths)} chunks in {temp_dir}")
    return chunk_paths


def get_cache_path(audio_path: str, chunk_index: int) -> Path:
    """Get cache file path for a specific chunk."""
    cache_dir = Path("outputs/transcript_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    audio_name = Path(audio_path).stem
    cache_file = cache_dir / f"{audio_name}_chunk_{chunk_index:04d}.txt"
    return cache_file


def load_cached_chunk(audio_path: str, chunk_index: int) -> str | None:
    """Load cached transcript for a chunk if it exists."""
    cache_file = get_cache_path(audio_path, chunk_index)
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.warning(f"Failed to load cache for chunk {chunk_index}: {e}")
    return None


def save_cached_chunk(audio_path: str, chunk_index: int, transcript: str) -> None:
    """Save transcript to cache for a chunk."""
    cache_file = get_cache_path(audio_path, chunk_index)
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(transcript)
    except Exception as e:
        logging.warning(f"Failed to save cache for chunk {chunk_index}: {e}")


def transcribe_chunk(chunk_path: str, chunk_index: int, client: OpenAI, audio_path: str = None) -> Dict:
    """
    Transcribe a single audio chunk using OpenAI Whisper API.
    Checks cache first to avoid re-transcribing.
    Implements exponential backoff for rate limit errors.
    
    Args:
        chunk_path: Path to audio chunk file
        chunk_index: Index of chunk (for ordering)
        client: OpenAI client instance
        audio_path: Original audio file path (for caching)
    
    Returns:
        Dict with chunk_index and transcript text
    """
    # Check cache first
    if audio_path:
        cached_transcript = load_cached_chunk(audio_path, chunk_index)
        if cached_transcript:
            logging.debug(f"Using cached transcript for chunk {chunk_index}")
            return {
                'chunk_index': chunk_index,
                'transcript': cached_transcript,
                'success': True,
                'cached': True,
                'retries': 0
            }
    
    # Exponential backoff parameters
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries + 1):
        try:
            with open(chunk_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            transcript = response.strip()
            
            # Save to cache
            if audio_path:
                save_cached_chunk(audio_path, chunk_index, transcript)
            
            return {
                'chunk_index': chunk_index,
                'transcript': transcript,
                'success': True,
                'cached': False,
                'retries': attempt
            }
        except Exception as e:
            error_str = str(e)
            is_rate_limit = '429' in error_str or 'rate_limit' in error_str.lower()
            is_server_error = '5' in error_str[:3] if len(error_str) >= 3 else False
            
            if (is_rate_limit or is_server_error) and attempt < max_retries:
                delay = base_delay ** (attempt + 1)
                logging.warning(f"Chunk {chunk_index} hit {'rate limit' if is_rate_limit else 'server error'}, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            
            logging.error(f"Failed to transcribe chunk {chunk_index} after {attempt + 1} attempts: {e}")
            return {
                'chunk_index': chunk_index,
                'transcript': '',
                'success': False,
                'error': error_str,
                'cached': False,
                'retries': attempt
            }


def transcribe_audio_parallel(chunk_paths: List[str], audio_path: str, max_workers: int = 8, max_retries: int = 3) -> Dict:
    """
    Transcribe audio chunks in parallel with automatic retry for failures.
    
    Args:
        chunk_paths: List of chunk file paths
        audio_path: Original audio file path (for caching)
        max_workers: Number of parallel transcription workers
        max_retries: Maximum retry attempts for failed chunks
    
    Returns:
        Dict with 'transcript' (combined text), 'stats' (success metrics), 'failed_chunks' (list)
    """
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    logging.info(f"Transcribing {len(chunk_paths)} chunks with {max_workers} workers...")
    
    results = {}
    failed_indices = set()
    
    # Telemetry tracking
    telemetry = {
        'rate_limit_429s': 0,
        'server_5xxs': 0,
        'total_retries': 0,
        'chunk_latencies': []
    }
    
    # Retry loop
    for attempt in range(max_retries):
        if attempt == 0:
            # First attempt: process all chunks
            chunks_to_process = list(enumerate(chunk_paths))
        else:
            # Retry only failed chunks
            chunks_to_process = [(i, chunk_paths[i]) for i in failed_indices]
            if not chunks_to_process:
                break
            logging.info(f"\nRetry attempt {attempt}/{max_retries-1}: Processing {len(chunks_to_process)} failed chunks...")
        
        start_time = time.time()
        last_progress_log = start_time
        round_results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit chunks for this round
            future_to_index = {}
            for i, chunk_path in chunks_to_process:
                future = executor.submit(transcribe_chunk, chunk_path, i, client, audio_path)
                future_to_index[future] = i
            
            # Collect results as they complete
            completed = 0
            successful = 0
            cached = 0
            
            for future in as_completed(future_to_index):
                chunk_index = future_to_index[future]
                result = future.result()
                round_results[chunk_index] = result
                completed += 1
                
                # Collect telemetry
                if result.get('retries', 0) > 0:
                    telemetry['total_retries'] += result['retries']
                if not result['success']:
                    error = result.get('error', '')
                    if '429' in error or 'rate_limit' in error.lower():
                        telemetry['rate_limit_429s'] += 1
                    elif any(str(code) in error for code in ['500', '502', '503', '504']):
                        telemetry['server_5xxs'] += 1
                
                if result['success']:
                    successful += 1
                    cache_marker = " (cached)" if result.get('cached') else ""
                    if result.get('cached'):
                        cached += 1
                    pct = (completed / len(chunks_to_process)) * 100
                    logging.info(f"[{completed}/{len(chunks_to_process)} | {pct:.0f}%] ✓ Chunk {chunk_index}: {len(result['transcript'])} chars{cache_marker}")
                else:
                    pct = (completed / len(chunks_to_process)) * 100
                    logging.error(f"[{completed}/{len(chunks_to_process)} | {pct:.0f}%] ✗ Chunk {chunk_index}: {result.get('error', 'Unknown error')}")
                
                # Log progress every 30 seconds
                current_time = time.time()
                if current_time - last_progress_log >= 30:
                    elapsed = current_time - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    remaining = len(chunks_to_process) - completed
                    eta_seconds = remaining / rate if rate > 0 else 0
                    logging.info(f"Progress: {completed}/{len(chunks_to_process)} complete ({successful} successful, {cached} cached) | "
                               f"Elapsed: {elapsed/60:.1f}min | ETA: {eta_seconds/60:.1f}min")
                    last_progress_log = current_time
        
        # Update global results and identify failures
        failed_indices = set()
        for chunk_index, result in round_results.items():
            results[chunk_index] = result
            if not result['success']:
                failed_indices.add(chunk_index)
        
        if attempt == 0:
            success_rate = (len(chunk_paths) - len(failed_indices)) / len(chunk_paths) * 100
            logging.info(f"First pass complete: {len(chunk_paths) - len(failed_indices)}/{len(chunk_paths)} successful ({success_rate:.1f}%)")
    
    # Final statistics
    successful_chunks = [i for i in range(len(chunk_paths)) if i in results and results[i]['success']]
    failed_chunks = [i for i in range(len(chunk_paths)) if i not in results or not results[i]['success']]
    
    success_rate = len(successful_chunks) / len(chunk_paths) * 100
    
    logging.info("")
    logging.info("="*60)
    logging.info("Transcription Summary:")
    logging.info(f"  Total chunks: {len(chunk_paths)}")
    logging.info(f"  Successful: {len(successful_chunks)} ({success_rate:.1f}%)")
    logging.info(f"  Failed: {len(failed_chunks)} ({100-success_rate:.1f}%)")
    if failed_chunks:
        logging.warning(f"  Failed chunk indices: {failed_chunks}")
    logging.info("")
    logging.info("Rate Limit Telemetry:")
    logging.info(f"  429 rate limits: {telemetry['rate_limit_429s']}")
    logging.info(f"  5xx server errors: {telemetry['server_5xxs']}")
    logging.info(f"  Total retries: {telemetry['total_retries']}")
    logging.info("="*60)
    
    # Combine transcripts in order
    logging.info("Combining transcripts in order...")
    combined_transcript = []
    
    for i in range(len(chunk_paths)):
        if i in results and results[i]['success']:
            combined_transcript.append(results[i]['transcript'])
        else:
            logging.warning(f"Missing transcript for chunk {i}, inserting placeholder")
            combined_transcript.append(f"[MISSING CHUNK {i}]")
    
    full_transcript = "\n\n".join(combined_transcript)
    
    return {
        'transcript': full_transcript,
        'stats': {
            'total': len(chunk_paths),
            'successful': len(successful_chunks),
            'failed': len(failed_chunks),
            'success_rate': success_rate
        },
        'failed_chunks': failed_chunks
    }


def cleanup_chunks(chunk_paths: List[str]) -> None:
    """Delete temporary chunk files and directory."""
    if not chunk_paths:
        return
    
    temp_dir = os.path.dirname(chunk_paths[0])
    
    for chunk_path in chunk_paths:
        try:
            os.remove(chunk_path)
        except Exception as e:
            logging.warning(f"Failed to delete {chunk_path}: {e}")
    
    try:
        os.rmdir(temp_dir)
        logging.info(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logging.warning(f"Failed to remove directory {temp_dir}: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/phase0_transcribe_audio.py /path/to/audiobook.m4b [output.txt] [--retry-failed]")
        print("  --retry-failed: Only re-transcribe chunks marked as [MISSING CHUNK N]")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    retry_mode = '--retry-failed' in sys.argv
    
    # Determine output path
    if len(sys.argv) >= 3 and not sys.argv[2].startswith('--'):
        output_path = sys.argv[2]
    else:
        output_path = "outputs/transcript.txt"
    
    if not Path(audio_path).exists():
        logging.error(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Load environment and config
    load_env_file()
    config = load_config()
    setup_logging(config)
    
    # Check for OpenAI API key
    if not os.environ.get('OPENAI_API_KEY'):
        logging.error("Error: OPENAI_API_KEY not found in environment")
        logging.error("Add OPENAI_API_KEY=sk-... to .env file")
        sys.exit(1)
    
    logging.info("="*60)
    logging.info("Phase 0: Audio Transcription")
    logging.info("="*60)
    logging.info(f"Input: {audio_path}")
    logging.info(f"Transcript output: {output_path}")
    
    # Get transcription config
    transcription_config = config.get('transcription', {})
    max_retries = transcription_config.get('max_retries', 3)
    failure_threshold = transcription_config.get('failure_threshold_percent', 20)
    
    # Get parallel config
    parallel_config = config.get('parallel', {})
    config_workers = parallel_config.get('max_workers', None)  # None allows autoscaling
    split_workers = min(config_workers or 8, 8)  # Use up to 8 workers for splitting
    
    # Split audio into chunks (parallel)
    chunk_paths = split_audio_into_chunks(audio_path, chunk_duration_minutes=20, max_workers=split_workers)
    
    # Autoscale workers based on chunk count
    max_workers = suggest_workers(
        chunk_count=len(chunk_paths),
        tier_rpm=500,  # Tier 1 limit
        manual_override=config_workers
    )
    
    # Check for retry-only mode
    chunks_to_transcribe = chunk_paths
    if retry_mode and Path(output_path).exists():
        logging.info("Retry mode: scanning existing transcript for failed chunks...")
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        failed_indices = set()
        for match in re.finditer(r'\[MISSING CHUNK (\d+)\]', content):
            failed_indices.add(int(match.group(1)))
        
        if failed_indices:
            logging.info(f"Found {len(failed_indices)} failed chunks to retry: {sorted(failed_indices)}")
            # Filter to only retry failed chunks
            chunks_to_transcribe = [chunk_paths[i] for i in sorted(failed_indices) if i < len(chunk_paths)]
            logging.info(f"Will transcribe {len(chunks_to_transcribe)} chunks")
        else:
            logging.info("No failed chunks found in transcript. Exiting.")
            return
    
    try:
        # Transcribe in parallel with retry
        result = transcribe_audio_parallel(
            chunks_to_transcribe, 
            audio_path,
            max_workers=max_workers,
            max_retries=max_retries
        )
        
        transcript = result['transcript']
        stats = result['stats']
        failed_chunks = result['failed_chunks']
        
        # Save transcript
        Path(output_path).parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        # Check if failure rate exceeds threshold
        failure_rate = 100 - stats['success_rate']
        
        logging.info("")
        logging.info("="*60)
        
        if failure_rate >= failure_threshold:
            logging.warning(f"⚠️  Phase 0 Complete with {failure_rate:.1f}% failures (threshold: {failure_threshold}%)")
            logging.warning(f"Failed chunks: {len(failed_chunks)} - Consider re-running or investigating errors")
        else:
            logging.info("✅ Phase 0 Complete")
        
        logging.info(f"Transcript length: {len(transcript)} characters")
        logging.info(f"Success rate: {stats['success_rate']:.1f}%")
        logging.info(f"Output written to: {output_path}")
        logging.info("="*60)
        
        # Exit with error if too many failures
        if failure_rate >= failure_threshold:
            sys.exit(1)
        
    finally:
        # Cleanup temporary files
        cleanup_chunks(chunk_paths)


if __name__ == "__main__":
    main()
