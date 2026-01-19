# Vaultage Daily Review Skill

End-of-day reflection workflow for the Obsidian vault.

## Configuration

Set your vault path via environment variable:
```bash
export VAULTAGE_PATH="$HOME/Documents/Vaultage"  # Customize to your vault location
```

## Trigger Phrases
- "daily review"
- "end of day review"
- "what did I work on today"

## Process

1. Find today's modified notes:
```bash
find "$VAULTAGE_PATH" -name "*.md" -mtime 0 -type f 2>/dev/null | grep -v ".obsidian" | grep -v ".trash"
```

2. Analyze progress and insights from modified notes

3. Create daily review note at:
```
$VAULTAGE_PATH/06_Metadata/Daily/YYYY-MM-DD - Daily Review.md
```

## Output Format

```markdown
---
date: {{date}}
type: daily-review
---

# Daily Review - {{date}}

## Accomplished
- [What was completed]

## Progress Made
- [Incremental progress on ongoing work]

## Insights Captured
- [New learnings or realizations]

## Blocked On
- [Obstacles encountered]

## Questions Raised
- [New questions that emerged]

## Tomorrow's Focus
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

## Open Loops
- [Unfinished threads to revisit]
```

## PARA Structure
- 00_Inbox: Unprocessed items
- 01_Projects: Active projects with deadlines
- 02_Areas: Ongoing responsibilities
- 03_Resources: Reference materials
- 04_Archive: Completed/inactive items
- 06_Metadata: System files, daily reviews, templates
