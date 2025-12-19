# AI PR Reviewer

An intelligent GitHub Pull Request review agent powered by AI that provides automated code reviews, security checks, and testing suggestions.

## Features

### Core Capabilities (v0.1)
- **PR Summarization**: Automatically summarizes what changed and why
- **Code-level Review**: Identifies logic errors, missing error handling, and code duplication
- **Quality & Style**: Checks naming conventions, code structure, and documentation
- **Testing**: Detects missing tests and suggests test cases
- **Security**: Basic security checks for unsafe input handling

### Planned Features
- Framework-specific checks
- Performance analysis
- Architecture-level critique
- Interactive `/ai-review` commands
- Team-specific guideline awareness

## Architecture

```
GitHub Webhook / GitHub Action
        ↓
   Fetch PR data
        ↓
   Chunk code diffs
        ↓
      LLM review
        ↓
 Aggregate comments
        ↓
Post results to PR
```

## Quick Start

### Prerequisites
- Python 3.9+
- GitHub Personal Access Token with `repo` scope
- OpenAI API key (or other LLM provider)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-pr-reviewer.git
cd ai-pr-reviewer

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
# Edit .env with your API keys
```

### GitHub Action Setup

Add to your repository's `.github/workflows/ai-review.yml`:

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, reopened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: AI PR Review
        uses: yourusername/ai-pr-reviewer@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Configuration

Create a `.ai-review.yml` in your repository root:

```yaml
# AI PR Reviewer Configuration
enabled: true
max_files: 50
skip_patterns:
  - "*.min.js"
  - "package-lock.json"
  - "*.generated.*"
review_mode: balanced  # strict, balanced, or lenient
focus_areas:
  - security
  - testing
  - performance
```

## Usage

The agent automatically reviews PRs when:
- A new PR is opened
- New commits are pushed to an existing PR
- PR is reopened

### Review Output

The agent posts a single comment with:
- **PR Summary**: High-level overview
- **Major Issues**: Critical problems requiring immediate attention
- **Minor Issues**: Suggestions for improvement
- **Test Suggestions**: Missing test cases
- **Overall Assessment**: Final verdict

## Development

### Project Structure

```
ai-pr-reviewer/
├── src/
│   ├── core/
│   │   ├── fetcher.py       # GitHub API integration
│   │   ├── chunker.py       # Diff chunking logic
│   │   ├── reviewer.py      # LLM review orchestration
│   │   └── responder.py     # GitHub comment posting
│   ├── prompts/
│   │   ├── system.txt       # System prompt template
│   │   └── review.txt       # Review prompt template
│   ├── utils/
│   │   ├── config.py        # Configuration management
│   │   └── logger.py        # Logging utilities
│   └── main.py              # Entry point
├── tests/
├── .github/
│   └── workflows/
│       └── ai-review.yml
├── requirements.txt
├── .env.example
└── README.md
```

### Running Tests

```bash
pytest tests/
```

## Roadmap

### v0.1 — Basic PR Reviewer ✅
- PR summarization
- 3-10 actionable comments
- Basic security checks

### v0.2 — Smarter Agent (In Progress)
- Per-file analysis
- Major vs minor issue classification
- Testing suggestions

### v0.3 — Team Integration
- Team-guideline awareness
- Auto-labeling (`ai-reviewed`)
- Reduced false positives

### v1.0 — Fully Interactive
- `/ai-review` command support
- Security/performance modes
- Incremental re-review

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/ai-pr-reviewer/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/ai-pr-reviewer/discussions)
