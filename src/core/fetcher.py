"""
GitHub API integration for fetching PR data
"""
from typing import Dict, List, Any, Optional
from github import Github, GithubException
from ..utils import setup_logger

logger = setup_logger(__name__)


class PRFetcher:
    """Fetches Pull Request data from GitHub"""
    
    def __init__(self, github_token: str, repo_name: str):
        """
        Initialize PR fetcher
        
        Args:
            github_token: GitHub personal access token
            repo_name: Repository name in format 'owner/repo'
        """
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
        logger.info(f"Initialized PR fetcher for {repo_name}")
    
    def get_pr_data(self, pr_number: int) -> Dict[str, Any]:
        """
        Fetch PR metadata and files
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Dictionary containing PR data
        """
        try:
            pr = self.repo.get_pull(pr_number)
            
            logger.info(f"Fetching PR #{pr_number}: {pr.title}")
            
            # Get changed files
            files = []
            for file in pr.get_files():
                files.append({
                    'filename': file.filename,
                    'status': file.status,  # added, modified, removed, renamed
                    'additions': file.additions,
                    'deletions': file.deletions,
                    'changes': file.changes,
                    'patch': file.patch if hasattr(file, 'patch') else None,
                    'sha': file.sha,
                })
            
            pr_data = {
                'number': pr.number,
                'title': pr.title,
                'description': pr.body or '',
                'author': pr.user.login,
                'state': pr.state,
                'created_at': pr.created_at.isoformat(),
                'updated_at': pr.updated_at.isoformat(),
                'base_branch': pr.base.ref,
                'head_branch': pr.head.ref,
                'files': files,
                'commits_count': pr.commits,
                'additions': pr.additions,
                'deletions': pr.deletions,
                'changed_files': pr.changed_files,
            }
            
            logger.info(f"Fetched {len(files)} files from PR #{pr_number}")
            return pr_data
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise
    
    def post_review_comment(self, pr_number: int, comment_body: str) -> None:
        """
        Post a review comment to the PR
        
        Args:
            pr_number: Pull request number
            comment_body: Markdown-formatted comment body
        """
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(comment_body)
            logger.info(f"Posted review comment to PR #{pr_number}")
            
        except GithubException as e:
            logger.error(f"Failed to post comment: {e}")
            raise
    
    def get_project_info(self) -> Dict[str, str]:
        """
        Get project information for context
        
        Returns:
            Dictionary with project metadata
        """
        try:
            return {
                'name': self.repo.name,
                'full_name': self.repo.full_name,
                'description': self.repo.description or '',
                'language': self.repo.language or 'Unknown',
                'default_branch': self.repo.default_branch,
            }
        except GithubException as e:
            logger.error(f"Failed to get project info: {e}")
            return {
                'name': 'Unknown',
                'language': 'Unknown',
            }
