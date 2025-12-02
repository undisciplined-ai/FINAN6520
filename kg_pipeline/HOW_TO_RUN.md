# How to Run the KG Pipeline

## ⚠️ CRITICAL: Use Virtual Environment Python

**NEVER run with system Python!** The pipeline requires packages installed in the virtual environment.

### ✅ CORRECT Way to Run:
```powershell
cd "c:\Users\KaiHarmer\KG Pipeline\FINAN6520\kg_pipeline"
& "C:\Users\KaiHarmer\KG Pipeline\FINAN6520\.venv\Scripts\python.exe" scripts/run_pipeline.py --input "inputs/Eric [B002V5J0M6].m4b" --clean
```

### ❌ WRONG (will fail with missing packages):
```powershell
python scripts/run_pipeline.py --input "inputs/Eric [B002V5J0M6].m4b"
```

## Why This Matters

1. **System Python** (`python` command) = Python 3.13 from `C:\Users\KaiHarmer\AppData\Local\Programs\Python\Python313\`
   - Does NOT have: faster-whisper, anthropic, numpy, etc.
   - Will fail immediately

2. **Venv Python** (`.venv\Scripts\python.exe`) = Python 3.13 in virtual environment
   - Has ALL required packages installed
   - Has cuDNN/cuBLAS paths configured
   - Properly configured for GPU transcription

## Environment Requirements

### Python Packages (installed in venv):
- `faster-whisper` - Local GPU Whisper transcription
- `nvidia-cudnn-cu12` - CUDA Deep Neural Network library
- `nvidia-cublas-cu12` - CUDA Basic Linear Algebra library
- `anthropic` - Claude API for entity extraction
- Standard: `numpy`, `pandas`, `pyyaml`, etc.

### System Requirements:
- **ffmpeg** - Audio processing (must be in Windows PATH)
  - Install via: `winget install Gyan.FFmpeg`
  - Location: Usually in `C:\Users\<user>\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\bin`

- **NVIDIA GPU with CUDA 12.x**
  - Minimum 8GB VRAM (16GB recommended)
  - CUDA runtime installed
  - cuDNN 9.x (installed via pip above)

### Node.js Requirements:
```powershell
cd kg_pipeline
npm install
```
Required packages: `ai`, `@ai-sdk/anthropic` (for Claude API wrapper)

## Pipeline Phases

The pipeline runs automatically through:

1. **Phase 0**: Audio Transcription (Local Whisper GPU)
   - Splits M4B into 20-min chunks
   - Transcribes with VAD filtering
   - ~20s per 20-min chunk on RTX 4080

2. **Phase 1**: Text Chunking
   - Chunks transcripts into 1400-token segments
   - 200-token overlap for context

3. **Phase 2**: Node Extraction (Claude API)
   - Extracts character traits, reasoning patterns, etc.
   - Uses Jungian archetype taxonomy

4. **Phase 2.5**: Entity Resolution
   - Deduplicates similar entities
   - Creates canonical entity set

5. **Phase 3**: Relationship Extraction (Claude API)
   - Extracts relationships between entities
   - Includes confidence scores

6. **Phase 4**: GraphRAG Export
   - Creates clean `outputs/graphrag_export/` folder
   - Contains: entities.jsonl, relationships.jsonl
   - Includes: archetype mappings, schema docs, README

## Output Location

**All GraphRAG files**: `kg_pipeline/outputs/graphrag_export/`

This is a clean, self-contained folder with everything needed:
- ✅ entities.jsonl
- ✅ relationships.jsonl  
- ✅ jungian_archetype_mapping.yaml
- ✅ jungian_traits.yaml
- ✅ kg_graph_export_schema.yaml
- ✅ README.md

## Troubleshooting

### Error: "Could not locate cudnn_ops64_9.dll"
**Fix**: Make sure you're using venv Python (`.venv\Scripts\python.exe`), not system Python

### Error: "FileNotFoundError: ffmpeg"
**Fix**: 
1. Install ffmpeg: `winget install Gyan.FFmpeg`
2. Restart terminal to refresh PATH
3. Or run pipeline from venv Python which reads registry PATH

### Error: "ModuleNotFoundError: No module named 'faster_whisper'"
**Fix**: You're using system Python instead of venv Python. Use `.venv\Scripts\python.exe`

### Error: "CUDA out of memory"
**Fix**: Use smaller Whisper model:
```powershell
# Edit run_pipeline.py line 177 to use "tiny" or "small" instead of "base"
```

## Performance Notes

- **Eric audiobook** (213 min):
  - Phase 0 (Transcription): ~4 minutes on RTX 4080
  - Phase 2 (Node Extraction): ~15 minutes (API limited)
  - Phase 3 (Relationships): ~10 minutes (API limited)
  - **Total**: ~30 minutes end-to-end

- **Costs**:
  - Phase 0: $0 (local GPU)
  - Phases 2-3: ~$0.50 per book (Claude 3.5 Haiku)

## Quick Reference

```powershell
# Single audiobook
& "C:\Users\KaiHarmer\KG Pipeline\FINAN6520\.venv\Scripts\python.exe" scripts/run_pipeline.py --input "inputs/Eric [B002V5J0M6].m4b" --clean

# Multiple audiobooks (entire folder)
& "C:\Users\KaiHarmer\KG Pipeline\FINAN6520\.venv\Scripts\python.exe" scripts/run_pipeline.py --input "inputs/" --clean

# Append to existing KG (don't start fresh)
& "C:\Users\KaiHarmer\KG Pipeline\FINAN6520\.venv\Scripts\python.exe" scripts/run_pipeline.py --input "inputs/new_book.m4b" --append
```
