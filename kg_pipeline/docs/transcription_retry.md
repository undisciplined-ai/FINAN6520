# Audio Transcription with Automatic Retry

## Overview

Phase 0 now includes robust retry logic and chunk-level caching to handle transcription failures gracefully. This is especially important when processing multiple audiobooks where network issues or API rate limits may cause sporadic failures.

## Key Features

### 1. **Chunk-Level Caching**
- Each successfully transcribed chunk is immediately saved to `outputs/transcript_cache/`
- Cache files are named: `{audiobook_name}_chunk_{index:04d}.txt`
- On retry, cached chunks are loaded instantly (no API calls or costs)

### 2. **Automatic Retry Logic**
- Failed chunks are automatically retried up to **3 times** (configurable)
- Only failed chunks are re-attempted, not successful ones
- Detailed statistics reported after each attempt

### 3. **Failure Threshold**
- Pipeline exits with error if failures exceed **20%** (configurable)
- Allows you to catch issues early and investigate before continuing
- Successful chunks remain cached for quick re-run

## Configuration

Edit `config/run_config.yaml`:

```yaml
# Transcription (Phase 0)
transcription:
  max_retries: 3                    # Retry failed chunks up to 3 times
  failure_threshold_percent: 20     # Exit with error if failures exceed this %
  chunk_cache_enabled: true         # Cache successful chunks (always recommended)
```

## Usage Examples

### Standard Pipeline (Automatic Retry)

```bash
# Process single audiobook
python scripts/run_pipeline.py --input inputs/book.m4b --message "Extract personas"

# Process entire directory (20 books)
python scripts/run_pipeline.py --input inputs/ --message "Extract personas"
```

**Behavior:**
- Each book is transcribed with automatic retry
- If a book fails >20% of chunks after 3 attempts, pipeline stops
- Fix the issue, then re-run (cached chunks are reused)

### Manual Retry Script

If the pipeline exits due to failures, use the retry script:

```bash
# Retry specific audiobook
python scripts/retry_failed_transcriptions.py inputs/book.m4b

# Retry all books in directory
python scripts/retry_failed_transcriptions.py inputs/

# Force re-transcription of all chunks (ignore cache)
python scripts/retry_failed_transcriptions.py inputs/book.m4b --force-all
```

## Cost Optimization

### Scenario: 20 Audiobooks @ $2.60 Each

**Without Retry/Caching:**
- If 1 book fails at 80% completion: **Re-process entire book = $2.60**
- If you hit rate limits mid-way: **Start over = $52.00**

**With Retry/Caching:**
- If 1 book fails at 80% completion: **Re-process 20% = $0.52**
- If you hit rate limits mid-way: **Resume from last success = $0.00 - $10.40**

### Example Savings

20 books, 5% random chunk failures:
- **Old approach**: Restart from scratch = $52.00
- **New approach**: Retry only failures = $2.60
- **Savings**: $49.40 (95%)

## Workflow for 20 Books

### 1. Initial Run

```bash
cd /workspaces/FINAN6520/kg_pipeline

# Process all books
python scripts/run_pipeline.py \
  --input inputs/ \
  --message "Extract persona knowledge graph" \
  --clean
```

### 2. If Failures Occur

Check the logs for which books failed:

```
⚠️  Phase 0 Complete with 25.0% failures (threshold: 20%)
Failed chunks: 15 - Consider re-running or investigating errors
```

### 3. Retry Failed Books

```bash
# Option A: Retry just the failed book
python scripts/retry_failed_transcriptions.py inputs/failed_book.m4b

# Option B: Retry all books (skips successful ones automatically)
python scripts/retry_failed_transcriptions.py inputs/
```

### 4. Resume Pipeline

Once all transcripts are complete:

```bash
# Continue from Phase 1 (don't use --clean!)
python scripts/run_pipeline.py \
  --input outputs/transcripts/ \
  --message "Extract persona knowledge graph"
```

## Cache Management

### View Cache Status

```bash
# Count cached chunks
ls -1 outputs/transcript_cache/*.txt | wc -l

# Check specific book's cache
ls outputs/transcript_cache/Make_It_Stick*.txt
```

### Clear Cache

```bash
# Remove all cached chunks (fresh start)
rm -rf outputs/transcript_cache/

# Remove cache for specific book
rm outputs/transcript_cache/Make_It_Stick*.txt
```

## Troubleshooting

### High Failure Rate (>20%)

**Possible causes:**
1. **Rate limiting**: Whisper API has limits. Reduce `max_workers` in config
2. **Network issues**: Temporary connectivity problems
3. **File corruption**: Check audio file integrity
4. **API key issues**: Verify `OPENAI_API_KEY` in `.env`

**Solutions:**
```bash
# Reduce parallel workers (edit config/run_config.yaml)
parallel:
  max_workers: 2  # Down from 4

# Wait 5 minutes and retry
sleep 300
python scripts/retry_failed_transcriptions.py inputs/
```

### Missing Chunks in Output

If you see `[MISSING CHUNK N]` in transcript:

```bash
# Check which chunks failed
grep "MISSING CHUNK" outputs/transcripts/*.txt

# Retry with force mode
python scripts/retry_failed_transcriptions.py inputs/book.m4b --force-all
```

### Cache Not Working

```bash
# Verify cache directory exists
ls -la outputs/transcript_cache/

# Check permissions
chmod -R u+rw outputs/transcript_cache/

# Test with single book
python scripts/phase0_transcribe_audio.py inputs/book.m4b outputs/test.txt
```

## Advanced: Batch Processing Strategy

For processing many books efficiently:

```python
#!/bin/bash
# process_library.sh

for book in inputs/*.m4b; do
    echo "Processing: $book"
    
    # Try transcription
    python scripts/phase0_transcribe_audio.py "$book" "outputs/transcripts/$(basename ${book%.m4b}.txt)"
    
    # If failed, retry immediately
    if [ $? -ne 0 ]; then
        echo "Retrying: $book"
        python scripts/retry_failed_transcriptions.py "$book"
    fi
    
    # Rate limiting: wait 30 seconds between books
    sleep 30
done

echo "All books transcribed! Starting knowledge graph extraction..."
python scripts/run_pipeline.py --input outputs/transcripts/ --message "Extract personas"
```

## Summary

✅ **Automatic retry** - 3 attempts per failed chunk  
✅ **Smart caching** - Never pay to re-transcribe successful chunks  
✅ **Cost efficient** - Save 90%+ on retry costs  
✅ **Resumable** - Continue from any failure point  
✅ **Production ready** - Process 20+ books reliably  

**Estimated cost for 20 books with 5% failure rate:**
- First run: $52.00 (20 books)
- Retries: $2.60 (5% of 20 books)
- **Total: $54.60** vs $104.00 without retry
