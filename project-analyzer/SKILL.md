---
name: project-analyzer
description: |
  Deep analysis of project codebases - LOC, dependencies, architecture, git history.
  Generates comprehensive project profiles for documentation and portfolio.
  
  Triggers: "analyze project", "project stats", "codebase analysis", "/analyze"
version: 1.0.0
author: Claude Code
allowed-tools:
  - Bash(git:*)
  - Bash(tokei:*)
  - Bash(cloc:*)
  - Bash(tree:*)
  - Read
  - Glob
  - Grep
---

# Project Analyzer

Deep analysis of project codebases for documentation and portfolio generation.

## Capabilities

### Code Statistics
- Lines of code by language
- File count and distribution
- Comment density
- Code complexity metrics

### Dependency Analysis
- Direct dependencies
- Dev dependencies
- Outdated packages
- Security vulnerabilities

### Git Analytics
- Total commits
- Contributors
- Activity timeline
- Commit frequency patterns

### Architecture Detection
- Framework identification
- Design patterns used
- Module structure
- API surface

## Usage

```bash
# Analyze current project
/analyze

# Analyze specific project
/analyze --project ~/projects/my-app

# Generate full report
/analyze --full --output report.md
```

## Output Format

```yaml
project:
  name: my-project
  path: /path/to/project
  created: 2025-10-15
  last_activity: 2026-01-19
  
code:
  total_lines: 45230
  languages:
    Python: 28450
    TypeScript: 12340
    YAML: 2100
    Markdown: 2340
  files: 234
  
git:
  total_commits: 847
  contributors: 3
  first_commit: 2025-10-15
  last_commit: 2026-01-19
  commit_frequency: 12/week
  
stack:
  frameworks: [FastAPI, Next.js, LangChain]
  databases: [PostgreSQL, Qdrant]
  infrastructure: [Docker, Vercel]
  
health:
  test_coverage: 78%
  doc_coverage: 65%
  dependency_freshness: 89%
```

## Integration

Feeds into:
- `knowledge-forge` for Obsidian notes
- `portfolio-forge` for static site generation

## Requirements

Install analysis tools:
```bash
# Code statistics (choose one)
brew install tokei  # Fast, Rust-based
brew install cloc   # Comprehensive, Perl-based

# For tree visualization
brew install tree
```
