---
name: knowledge-forge
description: |
  Synthesizes harvested session data and project analysis into structured 
  Obsidian-compatible markdown notes with proper frontmatter, tags, and links.
  
  Triggers: "synthesize notes", "create project notes", "forge knowledge", "/forge"
version: 1.0.0
author: Claude Code
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
---

# Knowledge Forge

Transforms raw harvested data into beautiful, interconnected Obsidian notes.

## What It Creates

### Session Notes (Daily Rollups)
```markdown
---
date: 2026-01-19
project: ATLAS-main
type: session-log
tags: [devlog, atlas, python, api]
commits: 5
lines_changed: "+234/-45"
---

# Session Log: ATLAS-main

## Summary
Implemented chat API endpoints and added comprehensive test coverage.

## Commits
- `abc1234` feat(api): add chat endpoint
- `def5678` test: add API client tests
- `ghi9012` fix: handle timeout errors

## Files Changed
| File | Changes |
|------|---------|
| src/api/client.py | +45/-12 |
| tests/test_api.py | +120/-0 |

## Decisions Made
- Used httpx for async HTTP support
- Implemented exponential backoff for retries

## Related
- [[ATLAS-main/_index]]
- [[2026-01-18]] (previous session)
```

### Project Index Notes
```markdown
---
project: ATLAS-main
type: project-index
created: 2025-10-15
last_updated: 2026-01-19
status: active
tags: [project, atlas, python, ai]
---

# ATLAS-main

> AI-powered knowledge management and agent orchestration platform.

## Quick Stats
| Metric | Value |
|--------|-------|
| Total Lines | 45,230 |
| Languages | Python, TypeScript, YAML |
| Commits | 847 |
| Contributors | 3 |

## Tech Stack
- **Backend**: FastAPI, LangChain
- **Frontend**: Next.js, Tailwind
- **Database**: PostgreSQL, Qdrant
- **Infrastructure**: Docker, Vercel

## Recent Activity
![[sessions/2026-01-19]]
![[sessions/2026-01-18]]

## Architecture
![[architecture]]

## Changelog
![[changelog]]
```

### Architecture Notes
Auto-generated from codebase analysis:
```markdown
---
project: ATLAS-main
type: architecture
generated: 2026-01-19
---

# Architecture: ATLAS-main

## Directory Structure
```
ATLAS-main/
├── src/
│   ├── api/          # FastAPI endpoints
│   ├── agents/       # LangChain agents
│   ├── models/       # Pydantic models
│   └── utils/        # Shared utilities
├── dashboard/        # Next.js frontend
├── tests/           # Test suite
└── docs/            # Documentation
```

## Key Components
...
```

## Tag Generation

Automatically generates tags based on:
- Tech stack detected
- File types modified
- Commit message keywords
- Project category

Example tag extraction:
```python
content = "Implemented FastAPI endpoint for chat"
# Generates: [api, fastapi, chat, backend]
```

## Link Generation

Creates bidirectional links:
- `[[project/_index]]` - Project home
- `[[sessions/YYYY-MM-DD]]` - Daily sessions
- `[[Developer-Log/YYYY-MM-DD]]` - Cross-project daily
- `[[project/architecture]]` - Architecture docs
- `[[project/changelog]]` - Changelog

## Usage

```bash
# Synthesize from cached harvest data
python synthesize.py --input ~/.cache/devlog/ATLAS_20260119.json

# Synthesize all pending cache files
python synthesize.py --all

# Preview without writing
python synthesize.py --dry-run --input data.json
```

## Output Locations

Notes are written to Vaultage:
```
~/Documents/Vaultage/
├── 01_Projects/
│   └── {project}/
│       ├── _index.md
│       ├── sessions/
│       │   └── YYYY-MM-DD.md
│       ├── architecture.md
│       └── changelog.md
└── 06_Metadata/
    └── Developer-Log/
        └── YYYY-MM-DD.md
```
