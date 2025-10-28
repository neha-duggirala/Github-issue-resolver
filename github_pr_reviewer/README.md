# PR Reviewer Agent
A lightweight agent to review GitHub pull requests, summarize changes, surface risks, suggest fixes, and optionally post review comments. Designed to be integrated locally, in CI, or as a GitHub Action.

## Features
- Summarize PR diffs and changed files
- Identify potential bugs, style issues, security risks, and missing tests
- Suggest concrete code changes and review comments
- Configurable severity and rule set
- Output as CLI, JSON, or GitHub review comments

## Quickstart

Prerequisites
- Python 3.12+ (or your preferred runtime)
- A GitHub token with repo access (GITHUB_TOKEN)
- An LLM API key if using an external model (e.g., GOOGLE_API_KEY) — optional depending on configuration

Install
```bash
git clone <repo-url>
cd github_pr_reviewer
pip install -r requirements.txt
```

Run locally (example)
```bash
# review a PR by URL
export GITHUB_TOKEN=ghp_xxx
python main.py "Can you please review this PR: https://github.com/neha-duggirala/Github-issue-resolver/pull/2" --verbose
```

## Output formats
- Markdown summary with findings and suggested diffs
- JSON machine-readable report:
    - findings: [{file, line, category, severity, message, suggestion}]
    - metrics: {files_changed, lines_added, lines_removed}
- Direct GitHub review comments (when authorized)


## Contributing
- Open issues for bugs or feature requests
- Fork → branch → PR with tests and changelog entry

## License
MIT — see LICENSE file.

For questions or custom integrations, inspect the config templates and examples in the repo.
