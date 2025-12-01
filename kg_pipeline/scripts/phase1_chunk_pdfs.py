#!/usr/bin/env python3
"""
Phase 1: Text Ingestion & Chunking

Extracts text from PDFs or text files and creates token-aware chunks with provenance metadata.

Usage:
    python scripts/phase1_chunk_pdfs.py input.pdf [input2.pdf ...]
    python scripts/phase1_chunk_pdfs.py outputs/transcript.txt
    python scripts/phase1_chunk_pdfs.py pdfs/*.pdf
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import yaml

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken not installed. Run: pip install tiktoken")
    sys.exit(1)


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


def count_tokens(text: str, tokenizer_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken."""
    encoding = tiktoken.get_encoding(tokenizer_name)
    return len(encoding.encode(text))


def chunk_text(text: str, chunk_size: int, overlap: int, tokenizer: str) -> List[str]:
    """
    Split text into token-aware chunks with overlap.
    
    Args:
        text: Text to chunk
        chunk_size: Target tokens per chunk
        overlap: Token overlap between chunks
        tokenizer: Tokenizer name for tiktoken
    
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Split into words (simple tokenization)
    words = text.split()
    if not words:
        return []
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(words):
        # Build chunk by adding words until we hit token limit
        chunk_words = []
        current_tokens = 0
        
        for i in range(start_idx, len(words)):
            test_chunk = ' '.join(words[start_idx:i+1])
            test_tokens = count_tokens(test_chunk, tokenizer)
            
            if test_tokens > chunk_size and chunk_words:
                # Hit limit, stop here
                break
            
            chunk_words.append(words[i])
            current_tokens = test_tokens
        
        if not chunk_words:
            # Edge case: single word exceeds chunk_size
            chunk_words = [words[start_idx]]
            start_idx += 1
        else:
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            # Calculate overlap position
            if start_idx + len(chunk_words) >= len(words):
                # Last chunk
                break
            
            # Move forward by (chunk_size - overlap) worth of words
            # Approximate by ratio of tokens to words
            if len(chunk_words) > 1:
                overlap_words = max(1, int(len(chunk_words) * (overlap / chunk_size)))
                start_idx += len(chunk_words) - overlap_words
            else:
                start_idx += 1
    
    return chunks


def process_pdf(pdf_path: str, doc_num: int, config: Dict, output_file) -> int:
    """
    Process a single PDF file and write chunks to output.
    
    Args:
        pdf_path: Path to PDF file
        doc_num: Document number for ID generation
        config: Runtime configuration
        output_file: File handle for writing chunks
    
    Returns:
        Number of chunks created
    """
    pdf_name = Path(pdf_path).name
    doc_id = f"doc{doc_num:03d}"
    
    chunk_size = config['chunk_size']
    overlap = config['chunk_overlap']
    tokenizer = config['tokenizer']
    
    total_chunks = 0
    
    logging.info(f"Processing {pdf_name} as {doc_id}")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_id = f"p{page_num:03d}"
                
                # Extract text
                text = page.extract_text()
                if text is None or not text.strip():
                    logging.debug(f"  {doc_id}-{page_id}: Empty page, skipping")
                    continue
                
                # Chunk the page text
                chunks = chunk_text(text, chunk_size, overlap, tokenizer)
                
                if not chunks:
                    logging.debug(f"  {doc_id}-{page_id}: No chunks created")
                    continue
                
                # Write chunks with provenance
                for chunk_num, chunk_content in enumerate(chunks, start=1):
                    chunk_id = f"c{chunk_num:02d}"
                    
                    chunk_obj = {
                        "doc_id": doc_id,
                        "page_id": page_id,
                        "chunk_id": chunk_id,
                        "text": chunk_content,
                        "page_num": page_num
                    }
                    
                    output_file.write(json.dumps(chunk_obj) + '\n')
                    total_chunks += 1
                
                logging.debug(f"  {doc_id}-{page_id}: Created {len(chunks)} chunk(s)")
    
    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}")
        raise
    
    return total_chunks


def process_text_file(text_path: str, doc_num: int, config: Dict, output_file) -> int:
    """
    Process a plain text file (e.g., from audio transcription) into chunks.
    
    Args:
        text_path: Path to text file
        doc_num: Document number for ID generation
        config: Runtime configuration
        output_file: Open file handle for output
    
    Returns:
        Number of chunks created
    """
    doc_id = f"doc{doc_num:03d}"
    doc_name = Path(text_path).stem
    
    logging.info(f"Processing {doc_name} as {doc_id}")
    
    # Read text file
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if not text.strip():
        logging.warning(f"  {doc_name} is empty, skipping")
        return 0
    
    # Chunk the text
    chunks = chunk_text(
        text,
        config['chunk_size'],
        config['chunk_overlap'],
        config['tokenizer']
    )
    
    # Write chunks with provenance
    total_chunks = 0
    for chunk_id, text_chunk in enumerate(chunks, start=1):
        chunk_data = {
            'doc_id': doc_id,
            'page_num': 1,  # Text files don't have pages
            'page_id': f"p{1:03d}",
            'chunk_id': f"c{chunk_id:02d}",
            'text': text_chunk,
            'token_count': count_tokens(text_chunk, config['tokenizer'])
        }
        
        output_file.write(json.dumps(chunk_data) + '\n')
        total_chunks += 1
    
    return total_chunks


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/phase1_chunk_pdfs.py <input_file> [input_file2 ...]")
        print("Example: python scripts/phase1_chunk_pdfs.py pdfs/*.pdf")
        print("Example: python scripts/phase1_chunk_pdfs.py outputs/transcript.txt")
        sys.exit(1)
    
    # Load configuration
    config = load_config()
    setup_logging(config)
    
    input_files = sys.argv[1:]
    output_path = "outputs/chunks.jsonl"
    
    logging.info("="*60)
    logging.info("Phase 1: Text Ingestion & Chunking")
    logging.info("="*60)
    logging.info(f"Files to process: {len(input_files)}")
    logging.info(f"Chunk size: {config['chunk_size']} tokens")
    logging.info(f"Overlap: {config['chunk_overlap']} tokens")
    logging.info(f"Output: {output_path}")
    logging.info("")
    
    # Create output directory if needed
    Path("outputs").mkdir(exist_ok=True)
    
    # Create document index mapping
    document_index = {}
    total_chunks = 0
    
    with open(output_path, 'w') as output_file:
        for doc_num, input_path in enumerate(input_files, start=1):
            if not Path(input_path).exists():
                logging.warning(f"File not found: {input_path}, skipping")
                continue
            
            # Detect file type
            file_ext = Path(input_path).suffix.lower()
            
            # Store document mapping
            doc_id = f"doc{doc_num:03d}"
            document_index[doc_id] = str(Path(input_path).name)
            
            if file_ext == '.pdf':
                if not PDFPLUMBER_AVAILABLE:
                    logging.error("pdfplumber not installed. Run: pip install pdfplumber")
                    sys.exit(1)
                chunks_created = process_pdf(input_path, doc_num, config, output_file)
            elif file_ext == '.txt':
                chunks_created = process_text_file(input_path, doc_num, config, output_file)
            else:
                logging.warning(f"Unsupported file type: {file_ext}, skipping {input_path}")
                continue
            
            total_chunks += chunks_created
            logging.info(f"  ✓ {Path(input_path).name}: {chunks_created} chunks")
    
    # Write document index
    index_path = "outputs/document_index.json"
    with open(index_path, 'w') as f:
        json.dump(document_index, f, indent=2)
    
    logging.info("")
    logging.info("="*60)
    logging.info(f"✅ Phase 1 Complete")
    logging.info(f"Total chunks created: {total_chunks}")
    logging.info(f"Output written to: {output_path}")
    logging.info(f"Document index written to: {index_path}")
    logging.info("="*60)
    
    # Show sample of first few chunks
    if total_chunks > 0:
        logging.info("")
        logging.info("Sample chunks:")
        with open(output_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 3:
                    break
                chunk = json.loads(line)
                preview = chunk['text'][:100].replace('\n', ' ')
                logging.info(f"  {chunk['doc_id']}-{chunk['page_id']}-{chunk['chunk_id']}: {preview}...")


if __name__ == "__main__":
    main()
