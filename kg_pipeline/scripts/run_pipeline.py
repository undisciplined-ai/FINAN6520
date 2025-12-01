#!/usr/bin/env python3
"""
End-to-end Knowledge Graph Pipeline Runner

Usage:
    python scripts/run_pipeline.py --input /path/to/file.pdf --message "Help me"
    python scripts/run_pipeline.py --input /path/to/audiobook.m4b --message "Help me"
    python scripts/run_pipeline.py --input /path/to/input_folder --message "Help me"

Features:
    - Optional cleanup of outputs directory before running
    - Sequential execution of Phases 0 through 4 (Phase 0 for audio files)
    - Optional execution of Phase 4b (LLM node selection) and Phase 4c (affective governor)
    - Supports PDF and M4B audiobook inputs
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs"
TRANSCRIPTS_DIR = OUTPUT_DIR / "transcripts"
SUPPORTED_EXTENSIONS = {".pdf", ".m4b", ".txt"}


def run_step(name: str, command: List[str]) -> None:
    """Run a pipeline step as a subprocess with logging."""
    logging.info("=" * 60)
    logging.info(name)
    logging.info("=" * 60)
    logging.info("Command: %s", " ".join(command))

    result = subprocess.run(command, cwd=str(BASE_DIR))
    if result.returncode != 0:
        raise RuntimeError(f"Step '{name}' failed with exit code {result.returncode}")


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
        "--message",
        type=str,
        default=None,
        help="Optional user message to drive Phase 4b/4c selections",
    )
    parser.add_argument(
        "--max-delta",
        type=float,
        default=0.3,
        help="Maximum affective change for Phase 4c",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean outputs directory before running",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
        for audio_file in audio_files:
            transcript_path = TRANSCRIPTS_DIR / f"{audio_file.stem}.txt"
            run_step(
                "Phase 0: Audio Transcription",
                [
                    "python",
                    "scripts/phase0_transcribe_audio.py",
                    str(audio_file),
                    str(transcript_path),
                ],
            )
            transcribed_texts.append(transcript_path)
    
    # Phase 1: Chunk inputs (PDFs or transcripts)
    phase1_inputs = pdf_files + text_files + transcribed_texts

    if not phase1_inputs:
        logging.error("No textual inputs available for Phase 1 after preprocessing.")
        sys.exit(1)

    run_step(
        "Phase 1: Text Chunking",
        ["python", "scripts/phase1_chunk_pdfs.py", *[str(path) for path in phase1_inputs]],
    )

    # Phase 2: Node Extraction
    run_step("Phase 2: Node Extraction", ["python", "scripts/phase2_extract_nodes.py"])

    # Phase 2.5: Entity Resolution
    run_step(
        "Phase 2.5: Entity Resolution", ["python", "scripts/phase2_5_resolve_entities.py"]
    )

    # Phase 3: Relationship Extraction
    run_step("Phase 3: Relationship Extraction", ["python", "scripts/phase3_extract_relationships.py"])

    # Phase 4: Persona Sheet Generation
    run_step("Phase 4: Persona Sheet Generation", ["python", "scripts/phase4_generate_persona_sheet.py"])

    if args.message:
        # Phase 4b: LLM-powered node selection
        run_step(
            "Phase 4b: Dynamic Node Selection",
            ["python", "scripts/phase4b_select_nodes.py", "--message", args.message],
        )

        # Phase 4c: Affective Governor
        run_step(
            "Phase 4c: Affective Governor",
            [
                "python",
                "scripts/phase4c_affective_governor.py",
                "--selections",
                "outputs/selected_nodes.json",
                "--max-delta",
                str(args.max_delta),
            ],
        )
    else:
        logging.info("Skipping Phases 4b and 4c (no message provided)")

    logging.info("Pipeline complete!")


if __name__ == "__main__":
    main()
