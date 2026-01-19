---
name: devlog-harvester
description: |
  Automatically harvest session data, git activity, and project context.
  Smart triggers: git commits, project switches, time-based (3x daily), idle detection.
  Feeds into knowledge-forge for Obsidian storage.
  
  Triggers: "harvest session", "capture work", "log activity", "/harvest"
version: 1.0.0
author: Claude Code
allowed-tools:
  - Bash(git:*)
  - Bash(gh:*)
  - Bash(tokei:*)
  - Read
  - Write
  - Grep
  - Glob
---

# DevLog Harvester

Captures development session data through smart, non-intrusive triggers.

## Trigger Mechanisms

### 1. Git Commit Hook (Primary)
Every commit triggers a mini-harvest capturing:
- Files changed in commit
- Commit message (intent)
- Session context at commit time

### 2. Time-Based Rollups (3x Daily)
Scheduled at: 9:00, 14:00, 21:00
- Aggregates accumulated data
- Writes to Obsidian via knowledge-forge

### 3. Project Switch Detection
When changing project directories:
- Flush current project's accumulated data
- Initialize harvester for new project

### 4. Idle Flush (30 min)
After 30 minutes of no tool calls:
- Flush accumulated session data
- Prevents data loss

## Data Captured

### Per-Session Data
```yaml
session:
  project: ATLAS-main
  started: 2026-01-19T09:15:00
  ended: 2026-01-19T12:30:00
  duration_minutes: 195
  
files_touched:
  - path: src/api/client.py
    operations: [read, edit, read]
    lines_changed: +45/-12
    
  - path: tests/test_api.py
    operations: [create, edit]
    lines_changed: +120/-0

git_activity:
  commits: 3
  messages:
    - "feat(api): add chat endpoint"
    - "test: add API client tests"
    - "fix: handle timeout errors"
  total_insertions: 165
  total_deletions: 12

tools_used:
  Edit: 12
  Read: 45
  Bash: 23
  Grep: 8

errors_encountered:
  - type: "ImportError"
    file: "src/api/client.py"
    resolution: "Added missing httpx dependency"

decisions_made:
  - "Used httpx instead of requests for async support"
  - "Added retry logic with exponential backoff"
```

## Usage

### Manual Harvest
```bash
# Harvest current session
/harvest

# Harvest specific project
/harvest --project ATLAS-main

# Harvest and immediately write to Obsidian
/harvest --write
```

### Automatic (via hooks)
The harvester runs automatically when:
- You make a git commit
- You switch projects (cd to different repo)
- 3x daily at scheduled times
- After 30 minutes of inactivity

## Integration Points

### Input Sources
- Git history (`git log`, `git diff`)
- Session transcripts (`~/.claude/transcripts/`)
- Tool usage (from session context)
- AGI-memory recalls

### Output Destinations
- → `knowledge-forge` (for synthesis)
- → `obsidian-bridge` (for storage)
- → Local cache (`~/.cache/devlog/`)

## Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Triggers  │────▶│  Harvester  │────▶│    Cache    │
│  (various)  │     │   Engine    │     │  (staging)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                         On rollup/flush       │
                                               ▼
                                        ┌─────────────┐
                                        │  knowledge  │
                                        │    forge    │
                                        └─────────────┘
```

## Configuration

Set in `~/.config/devlog/config.yaml`:
```yaml
harvester:
  # Rollup times (24h format)
  rollup_times: ["09:00", "14:00", "21:00"]
  
  # Idle threshold before flush (minutes)
  idle_threshold: 30
  
  # Cache directory
  cache_dir: ~/.cache/devlog
  
  # Projects to track (empty = all)
  tracked_projects: []
  
  # Projects to ignore
  ignored_projects:
    - node_modules
    - .git
```

## Files

- `scripts/harvest.py` - Main harvester engine
- `scripts/git-post-commit-hook.sh` - Git hook installer
- `scripts/scheduler.py` - Time-based trigger daemon
