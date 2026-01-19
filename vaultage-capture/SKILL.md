# Vaultage Quick Capture Skill

Quickly capture thoughts, ideas, or notes to the vault inbox.

## Configuration

Set your vault path via environment variable:
```bash
export VAULTAGE_PATH="$HOME/Documents/Vaultage"  # Customize to your vault location
```

## Trigger Phrases
- "capture to vault"
- "quick note"
- "add to inbox"
- "remember this"

## Process

1. Create timestamped note in inbox:
```bash
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
FILENAME="${DATE} - ${TIME} - Quick Capture.md"
```

2. Write to inbox with frontmatter:
```markdown
---
date: {{date}}
type: capture
status: inbox
source: claude-code
---

# {{title}}

{{content}}

---
*Captured via Claude Code*
```

3. File location:
```
$VAULTAGE_PATH/00_Inbox/{{filename}}
```

## Voice Memo Integration (Optional)

For voice memos, create a transcription script:
```bash
$VAULTAGE_PATH/.scripts/transcribe-voice-memo.sh /path/to/audio.m4a
```

Requires:
- GEMINI_API_KEY environment variable (for transcription)
- ffmpeg installed
- jq installed

## PARA Structure
- 00_Inbox: Unprocessed items (capture destination)
- 01_Projects: Active projects with deadlines
- 02_Areas: Ongoing responsibilities
- 03_Resources: Reference materials
- 04_Archive: Completed/inactive items
