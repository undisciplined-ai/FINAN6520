#!/usr/bin/env python3
"""
End-to-end Knowledge Graph Pipeline Runner

CRITICAL: MUST RUN FROM VIRTUAL ENVIRONMENT!
    Use: .venv\Scripts\python.exe scripts/run_pipeline.py
    NOT: python scripts/run_pipeline.py (uses system Python without packages)

Usage:
    .venv\Scripts\python.exe scripts/run_pipeline.py --input /path/to/file.pdf
    .venv\Scripts\python.exe scripts/run_pipeline.py --input /path/to/audiobook.m4b
    .venv\Scripts\python.exe scripts/run_pipeline.py --input /path/to/input_folder

Features:
    - Optional cleanup of outputs directory before running
    - Sequential execution of Phases 0 through 4 (Phase 0 for audio files)
    - Automatic backups after each phase
    - Supports PDF, TXT, and M4B audiobook inputs
    - Creates clean GraphRAG export in outputs/graphrag_export/

Requirements:
    - Python packages: faster-whisper, anthropic, vercel-ai-sdk (npm)
    - System: ffmpeg, CUDA 12.x, cuDNN 9.x
    - GPU: NVIDIA with 8GB+ VRAM for local Whisper transcription
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs"
TRANSCRIPTS_DIR = OUTPUT_DIR / "transcripts"
SUPPORTED_EXTENSIONS = {".pdf", ".m4b", ".txt"}


def backup_outputs(phase_label: str) -> None:
    """Create timestamped backup of outputs after a phase."""
    subprocess.run(
        ["python", "scripts/backup_outputs.py", phase_label],
        cwd=str(BASE_DIR)
    )


def run_step(name: str, command: List[str], backup_label: str = None) -> None:
    """
    Run a pipeline step as a subprocess with logging.
    
    IMPORTANT: This function handles environment setup for subprocesses:
    1. Reads Windows registry PATH to find ffmpeg (not in inherited env)
    2. Adds cuDNN/cuBLAS bin directories to PATH for GPU support
    3. Passes complete environment to subprocess
    
    All subprocess calls in this file MUST use sys.executable (venv Python)
    instead of "python" to ensure packages are available.
    """
    import os
    import sys
    logging.info("=" * 60)
    logging.info(name)
    logging.info("=" * 60)
    logging.info("Command: %s", " ".join(command))

    # Prepare environment with all necessary paths
    env = os.environ.copy()
    
    # On Windows, read PATH from registry to ensure we get ffmpeg
    # This is necessary because terminal PATH may not be inherited properly
    if sys.platform == 'win32':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
                system_path = winreg.QueryValueEx(key, 'Path')[0]
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment') as key:
                user_path = winreg.QueryValueEx(key, 'Path')[0]
            # Use registry PATH instead of inherited PATH
            env['PATH'] = system_path + os.pathsep + user_path
        except Exception as e:
            logging.warning(f"Failed to read PATH from registry: {e}")
    
    # Add cuDNN and cuBLAS paths for GPU support (CUDA 12.x)
    # These MUST be in PATH for ctranslate2/faster-whisper to find DLLs
    venv_base = Path(sys.prefix)
    cudnn_path = venv_base / "Lib" / "site-packages" / "nvidia" / "cudnn" / "bin"
    cublas_path = venv_base / "Lib" / "site-packages" / "nvidia" / "cublas" / "bin"
    
    extra_paths = [str(cudnn_path), str(cublas_path)]
    
    # Add these paths to the front of PATH so they take precedence
    env['PATH'] = os.pathsep.join(extra_paths + [env.get('PATH', '')])
    
    result = subprocess.run(command, cwd=str(BASE_DIR), env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Step '{name}' failed with exit code {result.returncode}")
    
    # Create backup if label provided
    if backup_label:
        backup_outputs(backup_label)


def clean_outputs() -> None:
    """Remove existing files from outputs directory."""
    if not OUTPUT_DIR.exists():
        return

    for item in OUTPUT_DIR.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def ensure_outputs_dir() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)


def resolve_input_files(input_paths: List[str]) -> List[Path]:
    """Expand directories into individual supported files."""
    resolved: List[Path] = []

    for raw_path in input_paths:
        path = Path(raw_path)

        if not path.exists():
            logging.warning("Input path not found: %s", path)
            continue

        if path.is_dir():
            for file_path in sorted(path.rglob("*")):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    resolved.append(file_path)
        elif path.suffix.lower() in SUPPORTED_EXTENSIONS:
            resolved.append(path)
        else:
            logging.warning("Skipping unsupported file: %s", path)

    return resolved


def main():
    parser = argparse.ArgumentParser(description="Run the full KG pipeline end-to-end")
    parser.add_argument(
        "--input",
        dest="inputs",
        nargs="+",
        required=True,
        help="Path(s) to input files (PDF or M4B audiobooks)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean outputs directory before running",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing KG instead of starting fresh",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    if args.clean and args.append:
        logging.error("Error: --clean and --append cannot be used together")
        sys.exit(1)

    if args.clean:
        logging.info("Cleaning outputs directory")
        clean_outputs()

    ensure_outputs_dir()

    # Resolve directories/globs into actual files
    resolved_inputs = resolve_input_files(args.inputs)
    if not resolved_inputs:
        logging.error("No valid input files found. Supported extensions: %s", ", ".join(SUPPORTED_EXTENSIONS))
        sys.exit(1)

    audio_files = [p for p in resolved_inputs if p.suffix.lower() == '.m4b']
    pdf_files = [p for p in resolved_inputs if p.suffix.lower() == '.pdf']
    text_files = [p for p in resolved_inputs if p.suffix.lower() == '.txt']

    logging.info(
        "Resolved %d input file(s): %d PDF, %d M4B, %d TXT",
        len(resolved_inputs),
        len(pdf_files),
        len(audio_files),
        len(text_files),
    )
    
    # Phase 0: Transcribe audio files (if any)
    transcribed_texts: List[Path] = []
    if audio_files:
        TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Use local Whisper batch transcription for all audio files at once
        # Assumes all audio files are in the same input directory
        input_dir = audio_files[0].parent if audio_files else None
        
        if input_dir:
            # Run batch transcription with local Whisper (processes all .m4b files in directory)
            run_step(
                "Phase 0: Audio Transcription (Local Whisper GPU)",
                [
                    sys.executable,  # Use current Python interpreter (from venv)
                    "scripts/batch_transcribe_local_whisper.py",
                    "--input-dir", str(input_dir),
                    "--output-dir", str(TRANSCRIPTS_DIR),
                    "--model", "base",
                    "--device", "cuda",
                ],
            )
        
        # Collect transcribed outputs
        for audio_file in audio_files:
            transcript_path = TRANSCRIPTS_DIR / f"{audio_file.stem}.txt"
            if transcript_path.exists():
                transcribed_texts.append(transcript_path)
            else:
                logging.warning(f"Transcript not found for {audio_file.name}")
    
    # Phase 1: Chunk inputs (PDFs or transcripts)
    phase1_inputs = pdf_files + text_files + transcribed_texts

    if not phase1_inputs:
        logging.error("No textual inputs available for Phase 1 after preprocessing.")
        sys.exit(1)

    phase1_cmd = [sys.executable, "scripts/phase1_chunk_pdfs.py", *[str(path) for path in phase1_inputs]]
    if args.append:
        phase1_cmd.append("--append")
    
    run_step(
        "Phase 1: Text Chunking",
        phase1_cmd,
        backup_label="phase1_chunks"
    )

    # Phase 2: Node Extraction
    run_step(
        "Phase 2: Node Extraction",
        [sys.executable, "scripts/phase2_extract_nodes.py"],
        backup_label="phase2_nodes"
    )

    # Phase 2.5: Entity Resolution
    run_step(
        "Phase 2.5: Entity Resolution",
        [sys.executable, "scripts/phase2_5_resolve_entities.py"],
        backup_label="phase2.5_canonical"
    )

    # Phase 3: Relationship Extraction
    run_step(
        "Phase 3: Relationship Extraction",
        [sys.executable, "scripts/phase3_extract_relationships.py"],
        backup_label="phase3_relationships"
    )

    # Phase 4: Export to GraphRAG format
    run_step(
        "Phase 4: GraphRAG Export",
        [sys.executable, "scripts/export_knowledge_graph.py"],
        backup_label=None  # No backup needed - this is the final export
    )

    logging.info("=" * 60)
    logging.info("Pipeline complete!")
    logging.info("=" * 60)
    logging.info("📁 GraphRAG export available at: outputs/graphrag_export/")
    logging.info("   - entities.jsonl")
    logging.info("   - relationships.jsonl")
    logging.info("   - Reference documentation (archetype mappings, schema, traits)")
    logging.info("   - README.md")


if __name__ == "__main__":
    main()
