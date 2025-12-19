"""
File filtering utilities
"""
import fnmatch
from pathlib import Path
from typing import List


def should_skip_file(file_path: str, skip_patterns: List[str]) -> bool:
    """
    Check if a file should be skipped based on patterns
    
    Args:
        file_path: Path to the file
        skip_patterns: List of glob patterns to skip
        
    Returns:
        True if file should be skipped, False otherwise
    """
    file_path_obj = Path(file_path)
    
    for pattern in skip_patterns:
        # Check filename
        if fnmatch.fnmatch(file_path_obj.name, pattern):
            return True
        
        # Check full path for directory patterns
        if fnmatch.fnmatch(file_path, pattern):
            return True
        
        # Check if any parent directory matches
        for parent in file_path_obj.parents:
            if fnmatch.fnmatch(str(parent), pattern.rstrip('/**')):
                return True
    
    return False


def get_file_language(file_path: str) -> str:
    """
    Detect programming language from file extension
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name or 'unknown'
    """
    extension_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript React',
        '.jsx': 'JavaScript React',
        '.java': 'Java',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.cs': 'C#',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'C/C++ Header',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.sql': 'SQL',
        '.sh': 'Shell',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.json': 'JSON',
        '.xml': 'XML',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.md': 'Markdown',
    }
    
    ext = Path(file_path).suffix.lower()
    return extension_map.get(ext, 'Unknown')
