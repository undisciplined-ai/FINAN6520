#!/usr/bin/env python3
"""
Batch Transcription with Local Faster-Whisper (GPU)

Uses faster-whisper for local GPU-accelerated transcription.
Much faster and cheaper than API, but requires CUDA-capable GPU.

CRITICAL SETUP NOTES:
1. MUST be called from run_pipeline.py with venv Python (sys.executable)
2. Requires ffmpeg in PATH (handled by run_pipeline.py via registry)
3. Requires cuDNN 9.x DLLs (registered below before imports)
4. All subprocess calls MUST pass env=os.environ to inherit PATH

Requirements:
    pip install faster-whisper nvidia-cudnn-cu12 nvidia-cublas-cu12
    System: ffmpeg, CUDA 12.x runtime
    GPU: NVIDIA with 8GB+ VRAM (16GB recommended for large models)
"""

# CRITICAL: Register DLL directories BEFORE importing faster_whisper/ctranslate2
# This ensures Windows can find cuDNN/cuBLAS DLLs when ctranslate2 loads
import os
import sys
from pathlib import Path

if sys.platform == 'win32':
    # Add cuDNN and cuBLAS DLL directories for Windows DLL search
    # These paths are also in PATH (set by run_pipeline.py), but os.add_dll_directory()
    # is more reliable for finding DLLs at import time
    venv_base = Path(sys.prefix)
    cudnn_bin = venv_base / 'Lib' / 'site-packages' / 'nvidia' / 'cudnn' / 'bin'
    cublas_bin = venv_base / 'Lib' / 'site-packages' / 'nvidia' / 'cublas' / 'bin'
    
    if cudnn_bin.exists():
        os.add_dll_directory(str(cudnn_bin))
    if cublas_bin.exists():
        os.add_dll_directory(str(cublas_bin))

# Now safe to import other modules
import argparse
import json
import logging
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Tuple

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None


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
    output_cache_path: Path


class BatchTranscriberLocal:
    """Manages local GPU transcription across multiple audiobooks."""
    
    def __init__(self, model_size: str = "base", device: str = "cuda", compute_type: str = "float16"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.progress_map: Dict[str, BookProgress] = {}
        self.model = None  # Initialize lazily
        self.overall_completed = 0
        self.overall_total = 0
        self.overall_lock = Lock()
        
    def setup_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get audio duration in seconds using ffprobe.
        
        CRITICAL: Must pass env=os.environ so subprocess inherits PATH from run_pipeline.py
        (which reads Windows registry to find ffmpeg).
        """
        import subprocess
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    
    def split_audio_chunk(self, args: Tuple) -> str:
        """
        Split a single audio chunk using ffmpeg.
        
        CRITICAL: Must pass env=os.environ so subprocess inherits PATH from run_pipeline.py
        (which reads Windows registry to find ffmpeg).
        """
        import subprocess
        
        audio_path, start_time, duration, chunk_path, book_name, chunk_idx, total_chunks, start_time_global = args
        
        cmd = [
            'ffmpeg', '-y', '-ss', str(start_time), '-t', str(duration),
            '-i', audio_path, '-vn', '-acodec', 'libmp3lame',
            '-ab', '64k', '-ar', '16000', chunk_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True, env=os.environ)
        
        # Calculate progress metrics
        elapsed = time.time() - start_time_global
        completed = chunk_idx + 1
        progress_pct = (completed / total_chunks) * 100
        
        # Calculate ETA
        if elapsed > 0:
            rate = completed / elapsed
            remaining = total_chunks - completed
            eta_seconds = remaining / rate if rate > 0 else 0
            eta_str = f"{eta_seconds:.0f}s" if eta_seconds < 120 else f"{eta_seconds/60:.1f}min"
        else:
            eta_str = "calculating..."
        
        # Log progress for every chunk
        logging.info(f"[{book_name}] Split {completed}/{total_chunks} ({progress_pct:.0f}%) | Elapsed: {elapsed:.1f}s | ETA: {eta_str}")
        
        return chunk_path
    
    def split_audiobook(self, audio_path: Path, chunk_duration_min: int = 20) -> Tuple[str, List[str]]:
        """Split one audiobook into chunks."""
        book_name = audio_path.stem
        logging.info(f"[{book_name}] Analyzing and splitting audio...")
        
        duration_sec = self.get_audio_duration(str(audio_path))
        chunk_duration_sec = chunk_duration_min * 60
        num_chunks = int((duration_sec + chunk_duration_sec - 1) / chunk_duration_sec)
        
        logging.info(f"[{book_name}] Duration: {duration_sec/60:.1f} min → {num_chunks} chunks")
        logging.info(f"[{book_name}] Starting split process...")
        
        # Create temp directory for this book
        temp_dir = tempfile.mkdtemp(prefix=f"audio_chunks_{book_name}_")
        
        # Prepare split tasks with timing info
        start_time_global = time.time()
        tasks = []
        for i in range(num_chunks):
            start_time = i * chunk_duration_sec
            chunk_path = os.path.join(temp_dir, f"chunk_{i:04d}.mp3")
            tasks.append((str(audio_path), start_time, chunk_duration_sec, chunk_path, book_name, i, num_chunks, start_time_global))
        
        # Split in parallel
        chunk_paths = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.split_audio_chunk, task) for task in tasks]
            for future in as_completed(futures):
                chunk_paths.append(future.result())
        
        chunk_paths.sort()
        
        total_split_time = time.time() - start_time_global
        logging.info(f"[{book_name}] ✅ Split complete: {len(chunk_paths)} chunks in {total_split_time:.1f}s ({total_split_time/60:.2f} min)")
        
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
    
    def transcribe_chunk(self, task: ChunkTask) -> Tuple[str, int, bool, str]:
        """Transcribe a single chunk using local Whisper."""
        # Check cache first
        cached = self.load_cached_chunk(task.output_cache_path)
        if cached:
            return (task.book_name, task.chunk_index, True, cached)
        
        try:
            # Transcribe using faster-whisper
            segments, info = self.model.transcribe(
                task.chunk_path,
                beam_size=5,
                language="en",  # Change if needed
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine all segments
            transcript = " ".join([segment.text for segment in segments]).strip()
            
            # Cache successful transcription
            self.save_chunk_cache(task.output_cache_path, transcript)
            
            return (task.book_name, task.chunk_index, True, transcript)
            
        except Exception as e:
            logging.error(f"[{task.book_name}] Chunk {task.chunk_index}: {e}")
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
        """Execute batch transcription with local Whisper."""
        # Initialize Whisper model
        if WhisperModel is None:
            logging.error("faster-whisper not installed. Run: pip install faster-whisper")
            sys.exit(1)
        
        logging.info(f"Loading Whisper model '{self.model_size}' on {self.device}...")
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        logging.info(f"✓ Model loaded successfully")
        
        # Find all audiobooks
        audio_files = sorted(input_dir.glob("*.m4b"))
        if not audio_files:
            logging.error(f"No M4B files found in {input_dir}")
            sys.exit(1)
        
        logging.info("="*60)
        logging.info("Batch Transcription - Local Whisper (GPU)")
        logging.info("="*60)
        logging.info(f"Audiobooks: {len(audio_files)}")
        logging.info(f"Model: {self.model_size}")
        logging.info(f"Device: {self.device}")
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
        
        # Phase 2: Build transcription queue
        logging.info("\n🎯 Phase 2: Transcribing with local Whisper...")
        
        all_tasks = []
        for book_name, chunk_paths in book_chunks_map.items():
            for chunk_idx, chunk_path in enumerate(chunk_paths):
                task = ChunkTask(
                    book_name=book_name,
                    chunk_index=chunk_idx,
                    chunk_path=chunk_path,
                    output_cache_path=self.get_cache_path(book_name, chunk_idx)
                )
                all_tasks.append(task)
        
        self.overall_total = len(all_tasks)
        logging.info(f"Total chunks to transcribe: {self.overall_total}")
        
        # Phase 3: Transcribe - single-threaded for GPU efficiency
        start_time = time.time()
        chunks_since_cleanup = 0
        
        for task in all_tasks:
            try:
                book_name, chunk_index, success, transcript = self.transcribe_chunk(task)
                self.update_progress(book_name, chunk_index, success, transcript)
                chunks_since_cleanup += 1
                
                # Periodic GPU memory cleanup (every 50 chunks to prevent memory leaks)
                if chunks_since_cleanup >= 50:
                    import gc
                    import torch
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    chunks_since_cleanup = 0
                    
            except Exception as e:
                # Log error but continue with next chunk
                logging.error(f"Failed to transcribe {task.book_name} chunk {task.chunk_index}: {e}")
                self.update_progress(task.book_name, task.chunk_index, False, "")
        
        elapsed = time.time() - start_time
        logging.info(f"\n⏱️  Total transcription time: {elapsed/60:.1f} minutes ({elapsed/3600:.2f} hours)")
        
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
        
        successful_books = 0
        partial_books = 0
        failed_books = 0
        
        for book_name, progress in self.progress_map.items():
            if progress.success_rate == 100.0:
                status = "✅"
                successful_books += 1
            elif progress.success_rate > 0:
                status = "⚠️"
                partial_books += 1
            else:
                status = "❌"
                failed_books += 1
            
            logging.info(f"{status} {book_name}: {progress.success_rate:.1f}% success")
        
        logging.info("="*60)
        logging.info(f"📊 Summary: {successful_books} complete | {partial_books} partial | {failed_books} failed")
        logging.info("="*60)


def main():
    parser = argparse.ArgumentParser(description="Batch transcription with local Whisper (GPU)")
    parser.add_argument("--input-dir", type=str, default="inputs", help="Input directory")
    parser.add_argument("--output-dir", type=str, default="outputs/transcripts", help="Output directory")
    parser.add_argument("--model", type=str, default="base", 
                       choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
                       help="Whisper model size (base recommended for speed/quality balance)")
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"],
                       help="Device to use (cuda for GPU, cpu for CPU)")
    
    args = parser.parse_args()
    
    transcriber = BatchTranscriberLocal(
        model_size=args.model,
        device=args.device,
        compute_type="float16" if args.device == "cuda" else "int8"
    )
    transcriber.setup_logging()
    transcriber.run(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir)
    )
    
    # Explicit success exit
    sys.exit(0)


if __name__ == "__main__":
    main()
