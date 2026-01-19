# Vaultage Inbox Processor Skill

Process and categorize items in the vault inbox using PARA method.

## Configuration

Set your vault path via environment variable:
```bash
export VAULTAGE_PATH="$HOME/Documents/Vaultage"  # Customize to your vault location
```

## Trigger Phrases
- "process inbox"
- "categorize inbox"
- "organize vault inbox"

## Process

1. Scan inbox:
```bash
ls -la "$VAULTAGE_PATH/00_Inbox/"
```

2. For each item, analyze content and suggest destination:
   - **01_Projects**: Has deadline, specific outcome, requires multiple steps
   - **02_Areas**: Ongoing responsibility, no end date, maintenance
   - **03_Resources**: Reference material, might need later, learning
   - **04_Archive**: Completed, no longer relevant, historical

3. Move files with user confirmation:
```bash
mv "$VAULTAGE_PATH/00_Inbox/note.md" "$VAULTAGE_PATH/01_Projects/"
```

## Decision Framework

| Signal | Destination |
|--------|-------------|
| Has due date | 01_Projects |
| "I need to..." | 01_Projects |
| Recurring topic | 02_Areas |
| "How to..." | 03_Resources |
| Historical reference | 04_Archive |
| Completed task | 04_Archive |

## Inbox Health
Target: < 20 items in inbox at any time

## PARA Structure
- 00_Inbox: Unprocessed items
- 01_Projects: Active projects with deadlines
- 02_Areas: Ongoing responsibilities  
- 03_Resources: Reference materials
- 04_Archive: Completed/inactive items
