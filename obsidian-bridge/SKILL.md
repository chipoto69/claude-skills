---
name: obsidian-bridge
description: |
  Orchestrates the knowledge capture pipeline: harvester → analyzer → forge → obsidian.
  Manages automatic triggers via hooks and coordinates skill chaining.
  
  Triggers: "sync to obsidian", "update knowledge base", "run pipeline", "/sync"
version: 1.0.0
author: Claude Code
allowed-tools:
  - Bash(python:*)
  - Bash(git:*)
  - Read
  - Write
---

# Obsidian Bridge

Master orchestrator for the knowledge capture and documentation pipeline.

## Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE PIPELINE                                    │
└──────────────────────────────────────────────────────────────────────────────┘

  TRIGGERS              CAPTURE              TRANSFORM             OUTPUT
  ────────              ───────              ─────────             ──────
                        
  ┌─────────┐       ┌─────────────┐      ┌───────────────┐     ┌──────────────┐
  │Git Commit│──────▶│   DevLog    │─────▶│   Knowledge   │────▶│   Obsidian   │
  └─────────┘       │  Harvester  │      │     Forge     │     │    Notes     │
                    └─────────────┘      └───────────────┘     └──────────────┘
  ┌─────────┐              │                    │                     │
  │ Project │──────────────┤                    │                     │
  │ Switch  │              ▼                    │                     ▼
  └─────────┘       ┌─────────────┐             │              ┌──────────────┐
                    │   Project   │─────────────┘              │   Portfolio  │
  ┌─────────┐       │  Analyzer   │                            │     HTML     │
  │ 3x Daily│───────▶─────────────┘                            └──────────────┘
  │ Rollup  │              │
  └─────────┘              ▼
                    ┌─────────────┐
  ┌─────────┐       │    AGI      │
  │  Idle   │───────▶│   Memory   │
  │ 30 min  │       │  Integration│
  └─────────┘       └─────────────┘
```

## Automatic Triggers

### 1. Git Commit Hook
Install with:
```bash
python ~/.claude/skills/obsidian-bridge/scripts/install-hooks.py
```

This adds a post-commit hook to all tracked repos that:
- Captures commit context
- Stages data for next rollup

### 2. Time-Based Rollups
Add to crontab:
```bash
# 3x daily rollups at 9am, 2pm, 9pm
0 9,14,21 * * * ~/.claude/skills/obsidian-bridge/scripts/scheduled-rollup.sh
```

### 3. Project Switch Detection
The harvester monitors PWD changes and flushes data when switching projects.

### 4. Idle Flush
After 30 minutes of no activity, accumulated data is flushed.

## Usage

### Manual Full Pipeline
```bash
# Run complete pipeline for current project
/sync

# Run for specific project
/sync --project ATLAS-main

# Dry run (preview only)
/sync --dry-run
```

### Individual Steps
```bash
# Just harvest
python ~/.claude/skills/devlog-harvester/scripts/harvest.py

# Just synthesize
python ~/.claude/skills/knowledge-forge/scripts/synthesize.py --all

# Just generate portfolio
python ~/.claude/skills/portfolio-forge/scripts/generate.py
```

## Integration with AGI-Memory

The bridge syncs with AGI-memory MCP:

```python
# On harvest, also store to AGI-memory
mcp_memory_remember(
    content=f"Session on {project}: {commits} commits, {summary}",
    type="episodic",
    importance=0.7,
    concepts=["project:{project}", "devlog"]
)
```

This enables:
- Cross-session recall ("What did I work on last week?")
- Project context retrieval
- Pattern recognition across sessions

## Integration with ATLAS

If ATLAS knowledge base is detected, the bridge:
1. Exports session notes in ATLAS-compatible format
2. Syncs to ATLAS mind.mv2 via memvid
3. Enables ATLAS agents to access development context

## Configuration

`~/.config/devlog/config.yaml`:
```yaml
pipeline:
  # Enable automatic triggers
  auto_commit_harvest: true
  auto_rollup: true
  rollup_times: ["09:00", "14:00", "21:00"]
  
  # Idle detection
  idle_threshold_minutes: 30
  
  # AGI-memory integration
  sync_to_agi_memory: true
  
  # ATLAS integration
  atlas_integration: true
  atlas_mind_path: ~/.claude/mind.mv2
  
  # Portfolio generation
  auto_portfolio: daily  # or: on_sync, manual
  portfolio_output: ~/Documents/Vaultage/06_Metadata/Portfolio
  
  # Projects to track (empty = all)
  tracked_projects: []
  
  # Projects to ignore
  ignored_projects:
    - node_modules
    - .git
    - __pycache__
```

## Skill Chain Commands

Run the full chain:
```bash
/chain harvest → analyze → forge → portfolio
```

Or use the shorthand:
```bash
/sync --full
```

## Files

- `scripts/run-pipeline.py` - Main orchestrator
- `scripts/install-hooks.py` - Git hook installer
- `scripts/scheduled-rollup.sh` - Cron script
- `scripts/agi-memory-sync.py` - AGI-memory integration
