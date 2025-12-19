"""
Response formatting and GitHub comment posting
"""
from typing import List, Dict, Any
from datetime import datetime
from ..utils import setup_logger

logger = setup_logger(__name__)


class ResponseFormatter:
    """Formats and aggregates review results into GitHub comments"""
    
    def __init__(self):
        """Initialize response formatter"""
        logger.info("Initialized response formatter")
    
    def aggregate_reviews(self, reviews: List[Dict[str, Any]], pr_data: Dict[str, Any]) -> str:
        """
        Aggregate individual file reviews into a single comment
        
        Args:
            reviews: List of review results
            pr_data: PR metadata
            
        Returns:
            Formatted markdown comment
        """
        # Parse reviews to extract structured sections
        all_summaries = []
        all_major_issues = []
        all_minor_issues = []
        all_test_suggestions = []
        all_assessments = []
        
        for review in reviews:
            sections = self._parse_review(review['review'])
            
            if sections.get('PR_SUMMARY'):
                all_summaries.append(f"**{review['file_path']}**: {sections['PR_SUMMARY']}")
            
            if sections.get('MAJOR_ISSUES'):
                for issue in sections['MAJOR_ISSUES']:
                    all_major_issues.append(f"- **{review['file_path']}**: {issue}")
            
            if sections.get('MINOR_ISSUES'):
                for issue in sections['MINOR_ISSUES']:
                    all_minor_issues.append(f"- **{review['file_path']}**: {issue}")
            
            if sections.get('TEST_SUGGESTIONS'):
                for suggestion in sections['TEST_SUGGESTIONS']:
                    all_test_suggestions.append(f"- **{review['file_path']}**: {suggestion}")
            
            if sections.get('OVERALL_ASSESSMENT'):
                all_assessments.append(sections['OVERALL_ASSESSMENT'])
        
        # Build final comment
        comment = self._build_comment(
            pr_data=pr_data,
            summaries=all_summaries,
            major_issues=all_major_issues,
            minor_issues=all_minor_issues,
            test_suggestions=all_test_suggestions,
            assessments=all_assessments,
        )
        
        logger.info("Aggregated reviews into final comment")
        return comment
    
    def _parse_review(self, review_text: str) -> Dict[str, Any]:
        """
        Parse structured review text into sections
        
        Args:
            review_text: Raw review text from LLM
            
        Returns:
            Dictionary of parsed sections
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in review_text.split('\n'):
            line = line.strip()
            
            # Detect section headers
            if line.startswith('PR_SUMMARY:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'PR_SUMMARY'
                current_content = []
            elif line.startswith('MAJOR_ISSUES:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'MAJOR_ISSUES'
                current_content = []
            elif line.startswith('MINOR_ISSUES:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'MINOR_ISSUES'
                current_content = []
            elif line.startswith('TEST_SUGGESTIONS:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'TEST_SUGGESTIONS'
                current_content = []
            elif line.startswith('OVERALL_ASSESSMENT:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'OVERALL_ASSESSMENT'
                current_content = []
            elif current_section and line:
                current_content.append(line)
        
        # Add last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Parse lists
        for key in ['MAJOR_ISSUES', 'MINOR_ISSUES', 'TEST_SUGGESTIONS']:
            if key in sections:
                items = [item.strip('- ').strip() for item in sections[key].split('\n') if item.strip().startswith('-')]
                sections[key] = items if items else []
        
        return sections
    
    def _build_comment(
        self,
        pr_data: Dict[str, Any],
        summaries: List[str],
        major_issues: List[str],
        minor_issues: List[str],
        test_suggestions: List[str],
        assessments: List[str],
    ) -> str:
        """
        Build the final markdown comment
        
        Args:
            pr_data: PR metadata
            summaries: List of file summaries
            major_issues: List of major issues
            minor_issues: List of minor issues
            test_suggestions: List of test suggestions
            assessments: List of overall assessments
            
        Returns:
            Formatted markdown comment
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        comment_parts = [
            "# 🤖 AI Code Review",
            "",
            f"**PR**: #{pr_data['number']} - {pr_data['title']}",
            f"**Author**: @{pr_data['author']}",
            f"**Files Changed**: {pr_data['changed_files']} (+{pr_data['additions']} -{pr_data['deletions']})",
            f"**Reviewed**: {timestamp}",
            "",
            "---",
            "",
        ]
        
        # Major Issues
        if major_issues:
            comment_parts.extend([
                "## 🔴 Major Issues",
                "",
                *major_issues,
                "",
            ])
        
        # Minor Issues
        if minor_issues:
            comment_parts.extend([
                "## 🟡 Minor Issues & Suggestions",
                "",
                *minor_issues,
                "",
            ])
        
        # Test Suggestions
        if test_suggestions:
            comment_parts.extend([
                "## 🧪 Test Suggestions",
                "",
                *test_suggestions,
                "",
            ])
        
        # Overall Assessment
        if assessments:
            comment_parts.extend([
                "## 📊 Overall Assessment",
                "",
                *assessments,
                "",
            ])
        
        # No issues found
        if not major_issues and not minor_issues and not test_suggestions:
            comment_parts.extend([
                "## ✅ No Issues Found",
                "",
                "The code looks good! No major issues or suggestions at this time.",
                "",
            ])
        
        # Footer
        comment_parts.extend([
            "---",
            "",
            "*This review was generated by AI. Please use your judgment and verify suggestions.*",
        ])
        
        return '\n'.join(comment_parts)
