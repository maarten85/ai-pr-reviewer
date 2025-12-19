"""
LLM-powered code review orchestration
"""
from typing import List, Dict, Any
from pathlib import Path
import openai
from utils import setup_logger

logger = setup_logger(__name__)


class LLMReviewer:
    """Orchestrates LLM-based code reviews"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", temperature: float = 0.3, base_url: str = None):
        """
        Initialize LLM reviewer
        
        Args:
            api_key: API key for LLM provider
            model: Model name to use
            temperature: Temperature for generation
            base_url: Optional custom API base URL
        """
        if base_url:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = openai.OpenAI(api_key=api_key)
        
        self.model = model
        self.temperature = temperature
        
        # Load prompts
        prompts_dir = Path(__file__).parent.parent / "prompts"
        with open(prompts_dir / "system_prompt.txt", 'r') as f:
            self.system_prompt_template = f.read()
        with open(prompts_dir / "review_prompt.txt", 'r') as f:
            self.review_prompt_template = f.read()
        
        logger.info(f"Initialized LLM reviewer with model {model}" + (f" at {base_url}" if base_url else ""))
    
    def review_chunk(self, chunk: Dict[str, Any], project_info: Dict[str, str]) -> str:
        """
        Review a single code chunk
        
        Args:
            chunk: Chunk dictionary with file info and diff
            project_info: Project metadata for context
            
        Returns:
            Review text from LLM
        """
        # Format system prompt with project context
        system_prompt = self.system_prompt_template.format(
            project_name=project_info.get('name', 'Unknown'),
            primary_language=project_info.get('language', 'Unknown'),
            framework=project_info.get('framework', 'Unknown'),
        )
        
        # Format review prompt with chunk data
        review_prompt = self.review_prompt_template.format(
            pr_title=chunk['pr_title'],
            pr_description=chunk['pr_description'],
            file_path=chunk['file_path'],
            file_language=chunk['file_language'],
            diff_content=chunk['patch'],
        )
        
        try:
            logger.debug(f"Reviewing {chunk['file_path']}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": review_prompt}
                ],
                temperature=self.temperature,
                max_tokens=2000,
            )
            
            review_text = response.choices[0].message.content
            logger.info(f"Completed review of {chunk['file_path']}")
            
            return review_text
            
        except Exception as e:
            logger.error(f"LLM review failed for {chunk['file_path']}: {e}")
            return f"Error reviewing {chunk['file_path']}: {str(e)}"
    
    def review_all_chunks(self, chunks: List[Dict[str, Any]], project_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Review all chunks and return results
        
        Args:
            chunks: List of chunks to review
            project_info: Project metadata
            
        Returns:
            List of review results
        """
        reviews = []
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Reviewing chunk {i}/{len(chunks)}: {chunk['file_path']}")
            
            review_text = self.review_chunk(chunk, project_info)
            
            reviews.append({
                'file_path': chunk['file_path'],
                'file_language': chunk['file_language'],
                'review': review_text,
            })
        
        logger.info(f"Completed review of {len(reviews)} chunks")
        return reviews
