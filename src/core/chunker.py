"""
Diff chunking logic to split large PRs into manageable pieces
"""
from typing import List, Dict, Any
from ..utils import setup_logger, should_skip_file, get_file_language

logger = setup_logger(__name__)


class DiffChunker:
    """Chunks PR diffs into manageable pieces for LLM review"""
    
    def __init__(self, max_tokens_per_chunk: int = 4000, skip_patterns: List[str] = None):
        """
        Initialize diff chunker
        
        Args:
            max_tokens_per_chunk: Maximum tokens per chunk (approximate)
            skip_patterns: File patterns to skip
        """
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.skip_patterns = skip_patterns or []
        logger.info(f"Initialized chunker with max {max_tokens_per_chunk} tokens per chunk")
    
    def chunk_pr_files(self, files: List[Dict[str, Any]], pr_title: str, pr_description: str) -> List[Dict[str, Any]]:
        """
        Chunk PR files into reviewable pieces
        
        Args:
            files: List of file dictionaries from PR
            pr_title: PR title for context
            pr_description: PR description for context
            
        Returns:
            List of chunks ready for review
        """
        chunks = []
        
        for file in files:
            filename = file['filename']
            
            # Skip files based on patterns
            if should_skip_file(filename, self.skip_patterns):
                logger.debug(f"Skipping file: {filename}")
                continue
            
            # Skip files without patches (binary files, etc.)
            if not file.get('patch'):
                logger.debug(f"Skipping file without patch: {filename}")
                continue
            
            # Skip very large files (>500 lines changed)
            if file.get('changes', 0) > 500:
                logger.warning(f"Skipping large file: {filename} ({file['changes']} changes)")
                continue
            
            # Create chunk for this file
            chunk = {
                'file_path': filename,
                'file_language': get_file_language(filename),
                'file_status': file['status'],
                'additions': file['additions'],
                'deletions': file['deletions'],
                'patch': file['patch'],
                'pr_title': pr_title,
                'pr_description': pr_description,
            }
            
            chunks.append(chunk)
            logger.debug(f"Created chunk for {filename}")
        
        logger.info(f"Created {len(chunks)} chunks from {len(files)} files")
        return chunks
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation)
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def split_large_patch(self, patch: str, max_lines: int = 100) -> List[str]:
        """
        Split a large patch into smaller hunks
        
        Args:
            patch: Diff patch content
            max_lines: Maximum lines per split
            
        Returns:
            List of patch segments
        """
        lines = patch.split('\n')
        
        if len(lines) <= max_lines:
            return [patch]
        
        # Split by diff hunks (lines starting with @@)
        hunks = []
        current_hunk = []
        
        for line in lines:
            if line.startswith('@@') and current_hunk:
                hunks.append('\n'.join(current_hunk))
                current_hunk = [line]
            else:
                current_hunk.append(line)
        
        if current_hunk:
            hunks.append('\n'.join(current_hunk))
        
        return hunks
