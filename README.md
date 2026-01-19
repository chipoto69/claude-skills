# Claude Code Skills Collection

A curated collection of reusable skills for Claude Code / OpenCode that enhance AI-assisted development workflows. These skills provide specialized capabilities for browser automation, knowledge management, code quality, and workflow orchestration.

## Quick Start

1. Clone this repository to your Claude skills directory:
```bash
git clone https://github.com/chipoto69/claude-skills.git ~/.claude/skills
```

2. Skills are automatically loaded by Claude Code when their trigger phrases are detected.

3. Configure environment variables as needed (see individual skill docs).

---

## Skills Overview

### Knowledge Pipeline (Skill Chain)

A powerful 5-skill pipeline that automatically captures your development activity and transforms it into searchable documentation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE CAPTURE PIPELINE                                │
└─────────────────────────────────────────────────────────────────────────────┘

  TRIGGERS                 CAPTURE                TRANSFORM              OUTPUT
  ────────                 ───────                ─────────              ──────

  ┌──────────┐        ┌──────────────┐       ┌───────────────┐     ┌──────────────┐
  │Git Commit│───────▶│   DevLog     │──────▶│  Knowledge    │────▶│   Obsidian   │
  │  Hook    │        │  Harvester   │       │    Forge      │     │    Notes     │
  └──────────┘        └──────────────┘       └───────────────┘     └──────────────┘
                            │                       │                      │
  ┌──────────┐              │                       │                      │
  │ Project  │──────────────┤                       │                      ▼
  │  Switch  │              ▼                       │              ┌──────────────┐
  └──────────┘        ┌──────────────┐              │              │  Portfolio   │
                      │   Project    │──────────────┘              │    HTML      │
  ┌──────────┐        │  Analyzer    │                             └──────────────┘
  │ Scheduled│───────▶└──────────────┘                                    │
  │  (3x/day)│              │                                             │
  └──────────┘              ▼                                             ▼
                      ┌──────────────┐                             ┌──────────────┐
                      │  Obsidian    │◀────────────────────────────│   Static     │
                      │   Bridge     │         orchestrates         │   Site       │
                      └──────────────┘                             └──────────────┘
```

#### Pipeline Skills:

| Skill | Purpose | Trigger |
|-------|---------|---------|
| [devlog-harvester](./devlog-harvester/) | Capture git activity, LOC, tech stack | Git commits, scheduled |
| [project-analyzer](./project-analyzer/) | Deep codebase analysis | `/analyze` |
| [knowledge-forge](./knowledge-forge/) | Transform to Obsidian notes | `/forge` |
| [portfolio-forge](./portfolio-forge/) | Generate static HTML portfolio | `/portfolio` |
| [obsidian-bridge](./obsidian-bridge/) | Orchestrate full pipeline | `/sync` |

---

### Workflow Automation

| Skill | Description | Triggers |
|-------|-------------|----------|
| [loop-maestro](./loop-maestro/) | Orchestrate complex multi-phase projects using Ralph Loops | "orchestrate", "coordinate loops" |
| [pr-review-resolver](./pr-review-resolver/) | Auto-resolve CodeRabbit/Qodo PR comments | "resolve PR comments", "fix review issues" |
| [claudeception](./claudeception/) | Extract reusable skills from work sessions | `/claudeception`, "save this as a skill" |

---

### Browser & Web

| Skill | Description | Triggers |
|-------|-------------|----------|
| [agent-browser](./agent-browser/) | Browser automation for testing and scraping | `agent-browser open`, `agent-browser snapshot` |
| [notebooklm](./notebooklm/) | Query Google NotebookLM for source-grounded answers | "ask my NotebookLM", NotebookLM URLs |
| [web-design-guidelines](./web-design-guidelines/) | Review UI against Web Interface Guidelines | "review my UI", "check accessibility" |

---

### Code Quality

| Skill | Description | Triggers |
|-------|-------------|----------|
| [react-best-practices](./react-best-practices/) | React/Next.js performance optimization | Writing React components |
| [humanizer](./humanizer/) | Remove AI writing patterns from text | "humanize this", editing AI-generated text |

---

### Obsidian/Vaultage Integration

| Skill | Description | Triggers |
|-------|-------------|----------|
| [vaultage-search](./vaultage-search/) | Semantic search across vault | "search vault for", "find in vaultage" |
| [vaultage-capture](./vaultage-capture/) | Quick capture to inbox | "capture to vault", "quick note" |
| [vaultage-inbox](./vaultage-inbox/) | Process inbox with PARA method | "process inbox", "categorize inbox" |
| [vaultage-daily](./vaultage-daily/) | End-of-day review workflow | "daily review", "what did I work on today" |

**Configuration for Vaultage skills:**
```bash
export VAULTAGE_PATH="$HOME/Documents/Vaultage"  # Your Obsidian vault path
```

---

## Architecture

### Skill Structure

Each skill follows a standard structure:

```
skill-name/
├── SKILL.md           # Skill definition with frontmatter
├── scripts/           # Executable scripts (optional)
│   ├── main.py
│   └── helper.sh
├── references/        # Reference documentation (optional)
│   └── api.md
└── README.md          # Detailed documentation (optional)
```

### SKILL.md Format

```yaml
---
name: skill-name
description: |
  Brief description of what the skill does.
  Triggers: "phrase1", "phrase2", "/command"
version: 1.0.0
author: Your Name
allowed-tools:
  - Bash(git:*)
  - Read
  - Write
---

# Skill Name

Detailed documentation here...
```

---

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) or [OpenCode](https://github.com/opencode-ai/opencode)
- Python 3.10+ (for pipeline skills)
- Git

### Optional Dependencies

```bash
# For code statistics (devlog-harvester, project-analyzer)
brew install tokei  # or: brew install cloc

# For browser automation (agent-browser)
pip install playwright
playwright install

# For semantic search (vaultage-search)
pip install chromadb sentence-transformers
```

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/chipoto69/claude-skills.git ~/.claude/skills
```

2. **Configure environment variables** (add to `~/.zshrc` or `~/.bashrc`):
```bash
# For Vaultage/Obsidian integration
export VAULTAGE_PATH="$HOME/Documents/Vaultage"

# For NotebookLM (optional)
export NOTEBOOKLM_EMAIL="your-email@gmail.com"
```

3. **Install git hooks** (for automatic harvesting):
```bash
bash ~/.claude/skills/obsidian-bridge/scripts/install-hooks.sh
```

4. **Set up scheduled rollups** (optional):
```bash
# Add to crontab for 3x daily knowledge synthesis
crontab -e
# Add: 0 9,14,21 * * * ~/.claude/skills/obsidian-bridge/scripts/scheduled-rollup.sh
```

---

## Usage Examples

### Knowledge Pipeline

```bash
# Manual harvest of current project
python ~/.claude/skills/devlog-harvester/scripts/harvest.py --since "8 hours ago"

# Run full pipeline
python ~/.claude/skills/obsidian-bridge/scripts/run-pipeline.py

# Generate portfolio
python ~/.claude/skills/portfolio-forge/scripts/generate.py
```

### In Claude Code

```
User: /sync
Agent: Running knowledge pipeline...
       ✅ Harvested 5 commits
       ✅ Created session note
       ✅ Updated portfolio

User: search vault for "authentication patterns"
Agent: Found 3 relevant notes:
       1. ATLAS-main/sessions/2026-01-15.md
       2. Resources/OAuth-Guide.md
       ...
```

---

## Skill Chaining

Skills can be chained together for complex workflows:

```
┌────────────────────────────────────────────────────────────────┐
│                      EXAMPLE: PR Workflow                       │
└────────────────────────────────────────────────────────────────┘

  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   Commit    │────▶│  Harvester  │────▶│    Forge    │
  │   Changes   │     │  captures   │     │  documents  │
  └─────────────┘     └─────────────┘     └─────────────┘
         │
         ▼
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │  Create PR  │────▶│  CodeRabbit │────▶│  PR-Resolve │
  │             │     │   reviews   │     │  fixes auto │
  └─────────────┘     └─────────────┘     └─────────────┘
```

---

## Contributing

1. Fork the repository
2. Create a new skill directory following the standard structure
3. Add comprehensive SKILL.md with:
   - Clear trigger phrases
   - Usage examples
   - Required tools/permissions
4. Test the skill locally
5. Submit a pull request

---

## License

MIT License - See [LICENSE](./LICENSE) for details.

---

## Acknowledgments

- Built for [Claude Code](https://claude.ai/code) and [OpenCode](https://github.com/opencode-ai/opencode)
- Inspired by the Obsidian community and PARA methodology
- ASCII diagrams for maximum compatibility
