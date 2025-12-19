"""
Configuration management for AI PR Reviewer
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the AI PR Reviewer"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to .ai-review.yml file (optional)
        """
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        
    def _find_config_file(self) -> str:
        """Find .ai-review.yml in current directory or parent directories"""
        current = Path.cwd()
        
        while current != current.parent:
            config_file = current / ".ai-review.yml"
            if config_file.exists():
                return str(config_file)
            current = current.parent
            
        # Use default config if not found
        return str(Path(__file__).parent.parent.parent / "config" / ".ai-review.example.yml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self.config_path}, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "enabled": True,
            "max_files": 50,
            "max_file_size_kb": 500,
            "skip_patterns": [
                "*.min.js", "*.min.css", "package-lock.json",
                "yarn.lock", "*.generated.*", "dist/**", "build/**"
            ],
            "review_mode": "balanced",
            "min_confidence": 0.7,
            "focus_areas": ["security", "testing", "performance", "maintainability"],
            "llm": {
                "model": "gpt-4-turbo-preview",
                "temperature": 0.3,
                "max_tokens": 2000
            },
            "guidelines": []
        }
    
    @property
    def github_token(self) -> str:
        """Get GitHub token from environment"""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        return token
    
    @property
    def llm_api_key(self) -> str:
        """Get LLM API key from environment (supports custom key names)"""
        # Try custom key name first, then fall back to OPENAI_API_KEY
        key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("LLM_API_KEY or OPENAI_API_KEY environment variable is required")
        return key
    
    @property
    def llm_base_url(self) -> str:
        """Get LLM API base URL from environment"""
        return os.getenv("LLM_BASE_URL", "")
    
    @property
    def llm_model(self) -> str:
        """Get LLM model name"""
        return os.getenv("LLM_MODEL", self.config.get("llm", {}).get("model", "gpt-4-turbo-preview"))
    
    @property
    def llm_temperature(self) -> float:
        """Get LLM temperature"""
        return float(os.getenv("LLM_TEMPERATURE", self.config.get("llm", {}).get("temperature", 0.3)))
    
    @property
    def max_files(self) -> int:
        """Get maximum number of files to review"""
        return int(os.getenv("MAX_FILES_PER_PR", self.config.get("max_files", 50)))
    
    @property
    def skip_patterns(self) -> List[str]:
        """Get file patterns to skip"""
        return self.config.get("skip_patterns", [])
    
    @property
    def focus_areas(self) -> List[str]:
        """Get focus areas for review"""
        return self.config.get("focus_areas", [])
    
    @property
    def guidelines(self) -> List[str]:
        """Get team-specific guidelines"""
        return self.config.get("guidelines", [])
    
    def is_enabled(self) -> bool:
        """Check if AI review is enabled"""
        return self.config.get("enabled", True)
