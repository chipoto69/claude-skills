#!/usr/bin/env python3
"""
Knowledge Forge - Synthesize session data into Obsidian notes.

Takes harvested session data and creates:
- Daily session notes (per project)
- Project index notes
- Cross-project developer log
- Architecture documentation

Usage:
    python synthesize.py --input session_data.json
    python synthesize.py --all  # Process all pending cache files
    python synthesize.py --dry-run --input data.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Paths
CACHE_DIR = Path.home() / ".cache" / "devlog"
VAULTAGE_PATH = Path.home() / "Documents" / "Vaultage"
PROJECTS_PATH = VAULTAGE_PATH / "01_Projects"
DEVLOG_PATH = VAULTAGE_PATH / "06_Metadata" / "Developer-Log"


def ensure_dirs():
    """Ensure all required directories exist."""
    PROJECTS_PATH.mkdir(parents=True, exist_ok=True)
    DEVLOG_PATH.mkdir(parents=True, exist_ok=True)


def extract_tags(session_data: dict) -> list[str]:
    """Extract relevant tags from session data."""
    tags = set()
    
    # Add project name as tag
    project = session_data.get("project", "").lower().replace("-", "_")
    if project:
        tags.add(project)
    
    # Add tech stack as tags
    for tech in session_data.get("tech_stack", []):
        tags.add(tech.lower().replace(".", "").replace(" ", "_"))
    
    # Add language tags
    for lang in session_data.get("loc_by_language", {}).keys():
        tags.add(lang.lower())
    
    # Extract from commit messages
    commit_text = " ".join(
        c.get("message", "") for c in session_data.get("commits", [])
    ).lower()
    
    keywords = {
        "feat": "feature",
        "fix": "bugfix", 
        "test": "testing",
        "refactor": "refactoring",
        "docs": "documentation",
        "api": "api",
        "ui": "frontend",
        "db": "database",
    }
    
    for keyword, tag in keywords.items():
        if keyword in commit_text:
            tags.add(tag)
    
    # Always add devlog
    tags.add("devlog")
    
    return sorted(list(tags))


def generate_session_note(session_data: dict) -> str:
    """Generate markdown for a session note."""
    project = session_data.get("project", "Unknown")
    date = datetime.fromisoformat(session_data.get("harvested_at", datetime.now().isoformat()))
    date_str = date.strftime("%Y-%m-%d")
    
    commits = session_data.get("commits", [])
    files = session_data.get("files_touched", [])
    insertions = session_data.get("total_insertions", 0)
    deletions = session_data.get("total_deletions", 0)
    
    tags = extract_tags(session_data)
    
    # Build frontmatter
    frontmatter = f"""---
date: {date_str}
project: {project}
type: session-log
tags: [{", ".join(tags)}]
commits: {len(commits)}
lines_changed: "+{insertions}/-{deletions}"
harvested_at: {session_data.get('harvested_at', '')}
---
"""
    
    # Build content
    content = f"# Session Log: {project}\n\n"
    content += f"**Date**: {date.strftime('%B %d, %Y')}\n"
    content += f"**Period**: {session_data.get('period_start', '')[:16]} → {session_data.get('period_end', '')[:16]}\n\n"
    
    # Summary
    if commits:
        commit_types = {}
        for c in commits:
            msg = c.get("message", "")
            ctype = msg.split(":")[0].split("(")[0] if ":" in msg else "other"
            commit_types[ctype] = commit_types.get(ctype, 0) + 1
        
        summary_parts = []
        type_descriptions = {
            "feat": "new features",
            "fix": "bug fixes",
            "test": "tests",
            "refactor": "refactoring",
            "docs": "documentation",
        }
        for ctype, count in commit_types.items():
            desc = type_descriptions.get(ctype, ctype)
            summary_parts.append(f"{count} {desc}")
        
        content += f"## Summary\n"
        content += f"This session included {', '.join(summary_parts)}.\n\n"
    
    # Commits section
    if commits:
        content += "## Commits\n\n"
        for c in commits:
            sha = c.get("sha", "")[:8]
            msg = c.get("message", "")
            ins = c.get("insertions", 0)
            dels = c.get("deletions", 0)
            content += f"- `{sha}` {msg} (+{ins}/-{dels})\n"
        content += "\n"
    
    # Files changed
    if files:
        content += "## Files Changed\n\n"
        content += "| File | Lines |\n"
        content += "|------|-------|\n"
        for f in files[:20]:  # Limit to 20 files
            path = f.get("path", "")
            added = f.get("lines_added", 0)
            removed = f.get("lines_removed", 0)
            content += f"| `{path}` | +{added}/-{removed} |\n"
        
        if len(files) > 20:
            content += f"\n*...and {len(files) - 20} more files*\n"
        content += "\n"
    
    # Tech stack
    tech_stack = session_data.get("tech_stack", [])
    if tech_stack:
        content += f"## Tech Stack\n"
        content += f"{', '.join(tech_stack)}\n\n"
    
    # LOC stats
    loc = session_data.get("loc_by_language", {})
    if loc:
        content += "## Code Statistics\n\n"
        total = sum(loc.values())
        content += f"**Total Lines**: {total:,}\n\n"
        content += "| Language | Lines | % |\n"
        content += "|----------|-------|---|\n"
        for lang, lines in sorted(loc.items(), key=lambda x: -x[1])[:10]:
            pct = (lines / total * 100) if total > 0 else 0
            content += f"| {lang} | {lines:,} | {pct:.1f}% |\n"
        content += "\n"
    
    # Related links
    content += "## Related\n\n"
    content += f"- [[{project}/_index|{project} Overview]]\n"
    
    # Previous day link
    prev_date = (date - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
    content += f"- [[{project}/sessions/{prev_date}|Previous Session]]\n"
    
    return frontmatter + content


def generate_project_index(project_name: str, session_data: dict) -> str:
    """Generate or update project index note."""
    date = datetime.now()
    
    tags = [project_name.lower().replace("-", "_"), "project"]
    for tech in session_data.get("tech_stack", []):
        tags.append(tech.lower().replace(".", "").replace(" ", "_"))
    
    frontmatter = f"""---
project: {project_name}
type: project-index
last_updated: {date.strftime("%Y-%m-%d")}
status: active
tags: [{", ".join(sorted(set(tags)))}]
---
"""
    
    content = f"# {project_name}\n\n"
    
    # Quick stats
    loc = session_data.get("loc_by_language", {})
    total_loc = sum(loc.values()) if loc else 0
    
    content += "## Quick Stats\n\n"
    content += "| Metric | Value |\n"
    content += "|--------|-------|\n"
    content += f"| Total Lines | {total_loc:,} |\n"
    content += f"| Languages | {', '.join(list(loc.keys())[:5])} |\n"
    content += f"| Last Activity | {date.strftime('%Y-%m-%d')} |\n\n"
    
    # Tech stack
    tech_stack = session_data.get("tech_stack", [])
    if tech_stack:
        content += "## Tech Stack\n\n"
        for tech in tech_stack:
            content += f"- {tech}\n"
        content += "\n"
    
    # Recent sessions
    content += "## Recent Sessions\n\n"
    content += f"- [[sessions/{date.strftime('%Y-%m-%d')}]]\n\n"
    
    # Links
    content += "## Documentation\n\n"
    content += "- [[architecture|Architecture]]\n"
    content += "- [[changelog|Changelog]]\n"
    
    return frontmatter + content


def generate_devlog_entry(sessions: list[dict]) -> str:
    """Generate cross-project developer log entry."""
    date = datetime.now()
    date_str = date.strftime("%Y-%m-%d")
    
    # Aggregate stats
    total_commits = sum(len(s.get("commits", [])) for s in sessions)
    total_insertions = sum(s.get("total_insertions", 0) for s in sessions)
    total_deletions = sum(s.get("total_deletions", 0) for s in sessions)
    projects = list(set(s.get("project", "") for s in sessions))
    
    all_tags = set(["devlog", "daily"])
    for s in sessions:
        all_tags.update(extract_tags(s))
    
    frontmatter = f"""---
date: {date_str}
type: developer-log
projects: [{", ".join(projects)}]
commits: {total_commits}
lines_changed: "+{total_insertions}/-{total_deletions}"
tags: [{", ".join(sorted(all_tags))}]
---
"""
    
    content = f"# Developer Log: {date.strftime('%B %d, %Y')}\n\n"
    
    # Daily summary
    content += "## Summary\n\n"
    content += f"- **Projects Touched**: {len(projects)}\n"
    content += f"- **Total Commits**: {total_commits}\n"
    content += f"- **Lines Changed**: +{total_insertions} / -{total_deletions}\n\n"
    
    # Per-project breakdown
    content += "## Project Activity\n\n"
    for session in sessions:
        project = session.get("project", "Unknown")
        commits = len(session.get("commits", []))
        ins = session.get("total_insertions", 0)
        dels = session.get("total_deletions", 0)
        
        content += f"### [[01_Projects/{project}/_index|{project}]]\n\n"
        content += f"- Commits: {commits}\n"
        content += f"- Changes: +{ins}/-{dels}\n"
        
        # List commits
        for c in session.get("commits", [])[:5]:
            content += f"- `{c.get('sha', '')[:8]}` {c.get('message', '')}\n"
        content += "\n"
    
    # Navigation
    prev_date = (date - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
    next_date = (date + __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
    
    content += "## Navigation\n\n"
    content += f"← [[{prev_date}|Yesterday]] | [[{next_date}|Tomorrow]] →\n"
    
    return frontmatter + content


def write_note(path: Path, content: str, dry_run: bool = False):
    """Write note to file."""
    if dry_run:
        print(f"[DRY RUN] Would write to: {path}")
        print(f"Content preview:\n{content[:500]}...")
        return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"✅ Written: {path}")


def process_session(
    session_data: dict, 
    dry_run: bool = False
) -> list[Path]:
    """Process a single session, creating all necessary notes."""
    ensure_dirs()
    
    project = session_data.get("project", "Unknown")
    date = datetime.fromisoformat(
        session_data.get("harvested_at", datetime.now().isoformat())
    )
    date_str = date.strftime("%Y-%m-%d")
    
    created_files = []
    
    # 1. Create project directory
    project_dir = PROJECTS_PATH / project
    project_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir = project_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)
    
    # 2. Create session note
    session_note_path = sessions_dir / f"{date_str}.md"
    session_content = generate_session_note(session_data)
    write_note(session_note_path, session_content, dry_run)
    created_files.append(session_note_path)
    
    # 3. Create/update project index
    index_path = project_dir / "_index.md"
    if not index_path.exists() or not dry_run:
        index_content = generate_project_index(project, session_data)
        write_note(index_path, index_content, dry_run)
        created_files.append(index_path)
    
    return created_files


def main():
    parser = argparse.ArgumentParser(description="Knowledge Forge - Synthesize to Obsidian")
    parser.add_argument("--input", "-i", help="Input JSON file from harvester")
    parser.add_argument("--all", "-a", action="store_true", help="Process all pending cache")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview without writing")
    parser.add_argument("--devlog", "-d", action="store_true", help="Also create devlog entry")
    
    args = parser.parse_args()
    
    if not args.input and not args.all:
        print("Error: Provide --input file or use --all to process cache")
        return 1
    
    sessions = []
    
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            return 1
        
        with open(input_path) as f:
            session_data = json.load(f)
        sessions.append(session_data)
    
    if args.all:
        cache_files = sorted(CACHE_DIR.glob("*.json"))
        print(f"Found {len(cache_files)} cached sessions")
        
        for cache_file in cache_files:
            try:
                with open(cache_file) as f:
                    session_data = json.load(f)
                sessions.append(session_data)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {cache_file}")
    
    if not sessions:
        print("No sessions to process")
        return 0
    
    print(f"\n🔧 Processing {len(sessions)} session(s)...\n")
    
    all_created = []
    for session in sessions:
        created = process_session(session, args.dry_run)
        all_created.extend(created)
    
    # Create cross-project devlog
    if args.devlog or len(sessions) > 1:
        date_str = datetime.now().strftime("%Y-%m-%d")
        devlog_path = DEVLOG_PATH / f"{date_str}.md"
        devlog_content = generate_devlog_entry(sessions)
        write_note(devlog_path, devlog_content, args.dry_run)
        all_created.append(devlog_path)
    
    print(f"\n✨ Created {len(all_created)} notes")
    
    # Trigger embedding update
    if not args.dry_run:
        print("\n📊 Triggering embedding update...")
        embedding_script = VAULTAGE_PATH / ".claude/skills/vault-search/scripts/index.py"
        if embedding_script.exists():
            import subprocess
            subprocess.run([sys.executable, str(embedding_script), "--vault-path", str(VAULTAGE_PATH)])
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
