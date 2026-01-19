# Vaultage Search Skill

Search the Obsidian vault using semantic embeddings or SQL queries on frontmatter.

## Configuration

Set your vault path via environment variable:
```bash
export VAULTAGE_PATH="$HOME/Documents/Vaultage"  # Customize to your vault location
```

## Trigger Phrases
- "search vault for"
- "find in vaultage"
- "query vault notes"
- "semantic search"

## Usage

### Semantic Search (embeddings-based)
```bash
python "$VAULTAGE_PATH/.claude/skills/vault-search/scripts/search.py" --query "your search query" --n-results 10
```

Options:
- `--query`: Search query text
- `--n-results`: Number of results (default 10)
- `--folder`: Filter to specific folder
- `--where`: JSON filter for metadata

### SQL Query (frontmatter database)
```bash
python "$VAULTAGE_PATH/.claude/skills/vault-search/scripts/dataview.py" "SELECT path, title FROM notes WHERE status = 'active' ORDER BY modified DESC LIMIT 20"
```

Available columns: path, folder, filename, title, status, priority, due, tags, created, modified

### Rebuild Index
```bash
python "$VAULTAGE_PATH/.claude/skills/vault-search/scripts/index.py"
```

## Setup

The search scripts require:
- Python 3.10+
- sqlite-vec or chromadb for embeddings
- sentence-transformers for embedding generation

Install dependencies:
```bash
pip install chromadb sentence-transformers pyyaml
```

## PARA Structure
- 00_Inbox: Unprocessed items
- 01_Projects: Active projects with deadlines
- 02_Areas: Ongoing responsibilities
- 03_Resources: Reference materials
- 04_Archive: Completed/inactive items
