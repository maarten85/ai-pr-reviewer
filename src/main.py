"""
AI PR Reviewer - Main Entry Point
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core import PRFetcher, DiffChunker, LLMReviewer, ResponseFormatter
from utils import Config, setup_logger

logger = setup_logger("ai-pr-reviewer")


def main():
    """Main entry point for AI PR Reviewer"""
    try:
        # Load configuration
        config = Config()
        
        # Check if enabled
        if not config.is_enabled():
            logger.info("AI PR Review is disabled in configuration")
            return
        
        # Get PR information from environment
        pr_number = int(os.getenv('PR_NUMBER', 0))
        repo_name = os.getenv('REPO_NAME', '')
        
        if not pr_number or not repo_name:
            logger.error("PR_NUMBER and REPO_NAME environment variables are required")
            sys.exit(1)
        
        logger.info(f"Starting AI review for PR #{pr_number} in {repo_name}")
        
        # Initialize components
        fetcher = PRFetcher(config.github_token, repo_name)
        chunker = DiffChunker(
            max_tokens_per_chunk=4000,
            skip_patterns=config.skip_patterns
        )
        reviewer = LLMReviewer(
            api_key=config.llm_api_key,
            model=config.llm_model,
            temperature=config.llm_temperature,
            base_url=config.llm_base_url if config.llm_base_url else None
        )
        formatter = ResponseFormatter()
        
        # Fetch PR data
        logger.info("Fetching PR data...")
        pr_data = fetcher.get_pr_data(pr_number)
        project_info = fetcher.get_project_info()
        
        # Check file count
        if len(pr_data['files']) > config.max_files:
            logger.warning(f"PR has {len(pr_data['files'])} files, exceeds max {config.max_files}")
            comment = f"""# 🤖 AI Code Review
            
**PR Too Large**

This PR has {len(pr_data['files'])} files, which exceeds the maximum of {config.max_files} files for automated review.

Please consider:
- Breaking this PR into smaller, focused changes
- Requesting manual review from team members

*Automated review is skipped for very large PRs to ensure quality feedback.*
"""
            fetcher.post_review_comment(pr_number, comment)
            return
        
        # Chunk files
        logger.info("Chunking PR files...")
        chunks = chunker.chunk_pr_files(
            files=pr_data['files'],
            pr_title=pr_data['title'],
            pr_description=pr_data['description']
        )
        
        if not chunks:
            logger.info("No files to review (all skipped or no changes)")
            return
        
        # Review chunks
        logger.info(f"Reviewing {len(chunks)} chunks...")
        reviews = reviewer.review_all_chunks(chunks, project_info)
        
        # Format and post response
        logger.info("Formatting review comment...")
        comment = formatter.aggregate_reviews(reviews, pr_data)
        
        logger.info("Posting review comment to PR...")
        fetcher.post_review_comment(pr_number, comment)
        
        logger.info("✅ AI PR Review completed successfully!")
        
    except Exception as e:
        logger.error(f"AI PR Review failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
