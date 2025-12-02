#!/usr/bin/env python3
"""
Batch Transcription with Shared Worker Queue

Strategy:
1. Split all audiobooks into chunks in parallel (8 splitting workers)
2. Queue all chunks from all books into a shared transcription queue
3. 8 transcription workers pull from shared queue continuously
4. Each book tracks its own chunks and stitches them back together in order
5. Live progress updates show status for each book independently

This maximizes throughput - workers never idle, all books progress simultaneously.
"""

import argparse
import logging
import os
import sys
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from threading import Lock
import yaml
import time

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


@dataclass
class BookProgress:
    """Track progress for a single audiobook."""
    name: str
    total_chunks: int
    completed_chunks: int = 0
    failed_chunks: List[int] = field(default_factory=list)
    chunk_transcripts: Dict[int, str] = field(default_factory=dict)
    lock: Lock = field(default_factory=Lock)
    
    @property
    def success_rate(self) -> float:
        if self.total_chunks == 0:
            return 0.0
        return (self.completed_chunks / self.total_chunks) * 100


@dataclass
class ChunkTask:
    """A single chunk transcription task."""
    book_name: str
    chunk_index: int
    chunk_path: str
    audio_path: str
    output_cache_path: Path


class BatchTranscriber:
    """Manages shared queue transcription across multiple audiobooks."""
    
    def __init__(self, max_workers: int = 8, max_retries: int = 3):
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.progress_map: Dict[str, BookProgress] = {}
        self.openai_client = None  # Initialize lazily after env is loaded
        self.telemetry = {
            'rate_limit_429s': 0,
            'server_5xxs': 0,
            'total_retries': 0
        }
        self.telemetry_lock = Lock()
        self.overall_completed = 0
        self.overall_total = 0
        self.overall_lock = Lock()
        
    def load_config(self) -> Dict:
        """Load runtime configuration."""
        config_path = Path(__file__).parent.parent / "config" / "run_config.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds."""
        import subprocess
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    
    def split_audio_chunk(self, args: Tuple) -> str:
        """Split a single audio chunk using ffmpeg."""
        import subprocess
        audio_path, start_time, duration, chunk_path = args
        
        cmd = [
            'ffmpeg', '-y', '-ss', str(start_time), '-t', str(duration),
            '-i', audio_path, '-vn', '-acodec', 'libmp3lame',
            '-ab', '64k', '-ar', '16000', chunk_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return chunk_path
    
    def split_audiobook(self, audio_path: Path, chunk_duration_min: int = 20) -> Tuple[str, List[str]]:
        """Split one audiobook into chunks."""
        book_name = audio_path.stem
        logging.info(f"[{book_name}] Analyzing and splitting audio...")
        
        duration_sec = self.get_audio_duration(str(audio_path))
        chunk_duration_sec = chunk_duration_min * 60
        num_chunks = int((duration_sec + chunk_duration_sec - 1) / chunk_duration_sec)
        
        logging.info(f"[{book_name}] Duration: {duration_sec/60:.1f} min → {num_chunks} chunks")
        
        # Create temp directory for this book
        temp_dir = tempfile.mkdtemp(prefix=f"audio_chunks_{book_name}_")
        
        # Prepare split tasks
        tasks = []
        for i in range(num_chunks):
            start_time = i * chunk_duration_sec
            chunk_path = os.path.join(temp_dir, f"chunk_{i:04d}.mp3")
            tasks.append((str(audio_path), start_time, chunk_duration_sec, chunk_path))
        
        # Split in parallel
        chunk_paths = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.split_audio_chunk, task) for task in tasks]
            for future in as_completed(futures):
                chunk_paths.append(future.result())
        
        chunk_paths.sort()
        logging.info(f"[{book_name}] ✅ Split complete: {len(chunk_paths)} chunks")
        
        return book_name, chunk_paths
    
    def get_cache_path(self, book_name: str, chunk_index: int) -> Path:
        """Get cache file path for a chunk."""
        cache_dir = Path("outputs/transcript_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{book_name}_chunk_{chunk_index:04d}.txt"
    
    def load_cached_chunk(self, cache_path: Path) -> str | None:
        """Load cached transcript if it exists."""
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
        return None
    
    def save_chunk_cache(self, cache_path: Path, transcript: str):
        """Save transcript to cache."""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
        except Exception as e:
            logging.warning(f"Failed to cache chunk: {e}")
    
    def transcribe_chunk_with_retry(self, task: ChunkTask) -> Tuple[str, int, bool, str]:
        """Transcribe a single chunk with retry logic."""
        # Check cache first
        cached = self.load_cached_chunk(task.output_cache_path)
        if cached:
            return (task.book_name, task.chunk_index, True, cached)
        
        # Attempt transcription with retries
        for attempt in range(self.max_retries):
            try:
                with open(task.chunk_path, 'rb') as audio_file:
                    response = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                
                transcript = response.strip()
                
                # Cache successful transcription
                self.save_chunk_cache(task.output_cache_path, transcript)
                
                return (task.book_name, task.chunk_index, True, transcript)
                
            except Exception as e:
                error_str = str(e).lower()
                
                if '429' in error_str or 'rate limit' in error_str:
                    with self.telemetry_lock:
                        self.telemetry['rate_limit_429s'] += 1
                        self.telemetry['total_retries'] += 1
                    wait_time = (2 ** attempt) * 2
                    logging.warning(f"[{task.book_name}] Chunk {task.chunk_index}: Rate limit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    
                elif '5' in error_str and 'server' in error_str:
                    with self.telemetry_lock:
                        self.telemetry['server_5xxs'] += 1
                        self.telemetry['total_retries'] += 1
                    wait_time = (2 ** attempt) * 1
                    logging.warning(f"[{task.book_name}] Chunk {task.chunk_index}: Server error, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    
                else:
                    logging.error(f"[{task.book_name}] Chunk {task.chunk_index}: {e}")
                    return (task.book_name, task.chunk_index, False, f"[MISSING CHUNK {task.chunk_index}]")
        
        # All retries exhausted
        return (task.book_name, task.chunk_index, False, f"[MISSING CHUNK {task.chunk_index}]")
    
    def update_progress(self, book_name: str, chunk_index: int, success: bool, transcript: str):
        """Update progress for a book after chunk completes."""
        progress = self.progress_map[book_name]
        
        with progress.lock:
            progress.completed_chunks += 1
            progress.chunk_transcripts[chunk_index] = transcript
            
            if not success:
                progress.failed_chunks.append(chunk_index)
            
            # Log progress for every chunk
            status = "✓" if success else "✗"
            logging.info(
                f"[{book_name}] {status} Chunk {chunk_index+1}/{progress.total_chunks} "
                f"({progress.success_rate:.1f}% success)"
            )
        
        # Update and log overall progress
        with self.overall_lock:
            self.overall_completed += 1
            if self.overall_completed % 10 == 0 or self.overall_completed == self.overall_total:
                pct = (self.overall_completed / self.overall_total * 100) if self.overall_total > 0 else 0
                active_books = sum(1 for p in self.progress_map.values() if p.completed_chunks < p.total_chunks)
                logging.info(
                    f"📊 Overall: {self.overall_completed}/{self.overall_total} chunks "
                    f"({pct:.1f}%) | Active books: {active_books}"
                )
    
    def assemble_transcript(self, book_name: str, output_path: Path):
        """Stitch chunks back together in order and save."""
        progress = self.progress_map[book_name]
        
        # Assemble in order
        transcript_parts = []
        for i in range(progress.total_chunks):
            transcript_parts.append(progress.chunk_transcripts.get(i, f"[MISSING CHUNK {i}]"))
        
        full_transcript = "\n\n".join(transcript_parts)
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_transcript)
        
        logging.info(
            f"[{book_name}] ✅ Transcript complete: {len(full_transcript)} chars, "
            f"{progress.success_rate:.1f}% success"
        )
        
        if progress.failed_chunks:
            logging.warning(f"[{book_name}] Failed chunks: {progress.failed_chunks}")
    
    def run(self, input_dir: Path, output_dir: Path):
        """Execute batch transcription with shared queue."""
        # Initialize OpenAI client now that env is loaded
        if OpenAI is None:
            logging.error("openai package not installed. Run: pip install openai")
            sys.exit(1)
        self.openai_client = OpenAI()
        
        # Find all audiobooks
        audio_files = sorted(input_dir.glob("*.m4b"))
        if not audio_files:
            logging.error(f"No M4B files found in {input_dir}")
            sys.exit(1)
        
        logging.info("="*60)
        logging.info("Batch Transcription - Shared Queue Strategy")
        logging.info("="*60)
        logging.info(f"Audiobooks: {len(audio_files)}")
        logging.info(f"Workers: {self.max_workers}")
        logging.info("="*60)
        
        # Phase 1: Split all audiobooks in parallel
        logging.info("\n📦 Phase 1: Splitting all audiobooks...")
        
        book_chunks_map: Dict[str, List[str]] = {}
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.split_audiobook, audio_file) for audio_file in audio_files]
            for future in as_completed(futures):
                book_name, chunk_paths = future.result()
                book_chunks_map[book_name] = chunk_paths
                
                # Initialize progress tracking
                self.progress_map[book_name] = BookProgress(
                    name=book_name,
                    total_chunks=len(chunk_paths)
                )
        
        # Phase 2: Build shared transcription queue
        logging.info("\n🎯 Phase 2: Transcribing from shared queue...")
        
        all_tasks = []
        for book_name, chunk_paths in book_chunks_map.items():
            audio_path = next(f for f in audio_files if f.stem == book_name)
            for chunk_idx, chunk_path in enumerate(chunk_paths):
                task = ChunkTask(
                    book_name=book_name,
                    chunk_index=chunk_idx,
                    chunk_path=chunk_path,
                    audio_path=str(audio_path),
                    output_cache_path=self.get_cache_path(book_name, chunk_idx)
                )
                all_tasks.append(task)
        
        self.overall_total = len(all_tasks)
        logging.info(f"Total chunks to transcribe: {self.overall_total}")
        
        # Phase 3: Transcribe from shared queue with worker pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.transcribe_chunk_with_retry, task) for task in all_tasks]
            
            for future in as_completed(futures):
                book_name, chunk_index, success, transcript = future.result()
                self.update_progress(book_name, chunk_index, success, transcript)
        
        # Phase 4: Assemble and save transcripts
        logging.info("\n📝 Phase 3: Assembling transcripts...")
        
        for book_name in book_chunks_map.keys():
            output_path = output_dir / f"{book_name}.txt"
            self.assemble_transcript(book_name, output_path)
        
        # Cleanup temp files
        logging.info("\n🧹 Cleaning up temporary files...")
        for chunk_paths in book_chunks_map.values():
            if chunk_paths:
                temp_dir = os.path.dirname(chunk_paths[0])
                for chunk_path in chunk_paths:
                    try:
                        os.remove(chunk_path)
                    except Exception:
                        pass
                try:
                    os.rmdir(temp_dir)
                except Exception:
                    pass
        
        # Final summary
        logging.info("\n" + "="*60)
        logging.info("Batch Transcription Complete")
        logging.info("="*60)
        
        for book_name, progress in self.progress_map.items():
            status = "✅" if progress.success_rate == 100 else "⚠️"
            logging.info(f"{status} {book_name}: {progress.success_rate:.1f}% success")
        
        logging.info("")
        logging.info("Rate Limit Telemetry:")
        logging.info(f"  429 rate limits: {self.telemetry['rate_limit_429s']}")
        logging.info(f"  5xx server errors: {self.telemetry['server_5xxs']}")
        logging.info(f"  Total retries: {self.telemetry['total_retries']}")
        logging.info("="*60)


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


def main():
    parser = argparse.ArgumentParser(description="Batch transcription with shared queue")
    parser.add_argument("--input-dir", type=str, default="inputs", help="Input directory")
    parser.add_argument("--output-dir", type=str, default="outputs/transcripts", help="Output directory")
    parser.add_argument("--workers", type=int, default=8, help="Number of transcription workers")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_env_file()
    
    # Check for OpenAI API key
    if not os.environ.get('OPENAI_API_KEY'):
        logging.error("Error: OPENAI_API_KEY not found in environment")
        logging.error("Add OPENAI_API_KEY=sk-... to .env file")
        sys.exit(1)
    
    transcriber = BatchTranscriber(max_workers=args.workers)
    transcriber.setup_logging()
    transcriber.run(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir)
    )


if __name__ == "__main__":
    main()
