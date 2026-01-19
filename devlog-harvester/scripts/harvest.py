#!/usr/bin/env python3
"""
DevLog Harvester - Capture development session data.

Collects:
- Git activity (commits, diffs, LOC changes)
- Session context (files touched, tools used)
- Project metadata (tech stack, structure)

Usage:
    python harvest.py                    # Harvest current project
    python harvest.py --project ATLAS    # Harvest specific project
    python harvest.py --since "2 hours"  # Harvest recent activity
    python harvest.py --write            # Write to knowledge-forge
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# Paths
CACHE_DIR = Path.home() / ".cache" / "devlog"
CONFIG_DIR = Path.home() / ".config" / "devlog"
VAULTAGE_PATH = Path.home() / "Documents" / "Vaultage"
PROJECTS_PATH = Path.home() / "ORGANIZED" / "ACTIVE_PROJECTS" / "ARSENAL"


@dataclass
class GitCommit:
    sha: str
    message: str
    author: str
    date: str
    insertions: int = 0
    deletions: int = 0
    files_changed: list = field(default_factory=list)


@dataclass
class FileActivity:
    path: str
    operations: list = field(default_factory=list)
    lines_added: int = 0
    lines_removed: int = 0


@dataclass 
class SessionData:
    project: str
    project_path: str
    harvested_at: str
    period_start: str
    period_end: str
    
    # Git activity
    commits: list = field(default_factory=list)
    total_insertions: int = 0
    total_deletions: int = 0
    
    # Files
    files_touched: list = field(default_factory=list)
    
    # Project stats
    loc_by_language: dict = field(default_factory=dict)
    tech_stack: list = field(default_factory=list)
    
    # Errors & learnings
    errors_encountered: list = field(default_factory=list)
    decisions_made: list = field(default_factory=list)


def run_cmd(cmd: list[str], cwd: str = None) -> tuple[str, int]:
    """Run command and return (output, return_code)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd, timeout=30
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", 1
    except Exception as e:
        return str(e), 1


def detect_project(path: str = None) -> tuple[str, str]:
    """Detect project name and root path from current or given directory."""
    if path:
        project_path = Path(path)
    else:
        project_path = Path.cwd()
    
    # Try to find git root
    git_root, rc = run_cmd(["git", "rev-parse", "--show-toplevel"], str(project_path))
    if rc == 0:
        project_path = Path(git_root)
    
    project_name = project_path.name
    return project_name, str(project_path)


def get_git_commits(project_path: str, since: str = "24 hours ago") -> list[GitCommit]:
    """Get git commits since given time."""
    commits = []
    
    # Get commit list
    cmd = [
        "git", "log", f"--since={since}",
        "--pretty=format:%H|%s|%an|%ai",
        "--shortstat"
    ]
    output, rc = run_cmd(cmd, project_path)
    if rc != 0:
        return commits
    
    lines = output.split('\n')
    current_commit = None
    
    for line in lines:
        if '|' in line and len(line.split('|')) == 4:
            if current_commit:
                commits.append(current_commit)
            
            parts = line.split('|')
            current_commit = GitCommit(
                sha=parts[0][:8],
                message=parts[1],
                author=parts[2],
                date=parts[3]
            )
        elif 'insertion' in line or 'deletion' in line:
            if current_commit:
                # Parse stat line like "3 files changed, 45 insertions(+), 12 deletions(-)"
                ins_match = re.search(r'(\d+) insertion', line)
                del_match = re.search(r'(\d+) deletion', line)
                if ins_match:
                    current_commit.insertions = int(ins_match.group(1))
                if del_match:
                    current_commit.deletions = int(del_match.group(1))
    
    if current_commit:
        commits.append(current_commit)
    
    # Get files changed per commit
    for commit in commits:
        cmd = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit.sha]
        output, rc = run_cmd(cmd, project_path)
        if rc == 0:
            commit.files_changed = [f for f in output.split('\n') if f]
    
    return commits


def get_loc_stats(project_path: str) -> dict:
    """Get lines of code by language using tokei or cloc."""
    loc = {}
    
    # Try tokei first (faster)
    output, rc = run_cmd(["tokei", "--output", "json", project_path])
    if rc == 0:
        try:
            data = json.loads(output)
            for lang, stats in data.items():
                if isinstance(stats, dict) and 'code' in stats:
                    loc[lang] = stats['code']
            return loc
        except json.JSONDecodeError:
            pass
    
    # Fallback to cloc
    output, rc = run_cmd(["cloc", "--json", project_path])
    if rc == 0:
        try:
            data = json.loads(output)
            for lang, stats in data.items():
                if lang not in ['header', 'SUM'] and isinstance(stats, dict):
                    loc[lang] = stats.get('code', 0)
            return loc
        except json.JSONDecodeError:
            pass
    
    return loc


def detect_tech_stack(project_path: str) -> list[str]:
    """Detect tech stack from project files."""
    stack = []
    path = Path(project_path)
    
    # Check for common files
    indicators = {
        "package.json": ["Node.js"],
        "requirements.txt": ["Python"],
        "pyproject.toml": ["Python"],
        "Cargo.toml": ["Rust"],
        "go.mod": ["Go"],
        "Gemfile": ["Ruby"],
        "pom.xml": ["Java", "Maven"],
        "build.gradle": ["Java", "Gradle"],
        "next.config.js": ["Next.js"],
        "next.config.ts": ["Next.js"],
        "vite.config.ts": ["Vite"],
        "tailwind.config.js": ["Tailwind CSS"],
        "docker-compose.yml": ["Docker"],
        "Dockerfile": ["Docker"],
        ".github/workflows": ["GitHub Actions"],
        "vercel.json": ["Vercel"],
    }
    
    for file, techs in indicators.items():
        if (path / file).exists():
            stack.extend(techs)
    
    # Check package.json for frameworks
    pkg_json = path / "package.json"
    if pkg_json.exists():
        try:
            with open(pkg_json) as f:
                pkg = json.load(f)
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            framework_map = {
                "react": "React",
                "vue": "Vue.js",
                "svelte": "Svelte",
                "express": "Express.js",
                "fastify": "Fastify",
                "@anthropic-ai/sdk": "Anthropic SDK",
                "openai": "OpenAI SDK",
                "langchain": "LangChain",
            }
            
            for dep, name in framework_map.items():
                if dep in deps:
                    stack.append(name)
        except:
            pass
    
    return list(set(stack))


def get_recent_files(project_path: str, since_hours: int = 24) -> list[FileActivity]:
    """Get recently modified files in project."""
    files = []
    path = Path(project_path)
    
    cutoff = datetime.now() - timedelta(hours=since_hours)
    
    # Use git to find changed files
    cmd = ["git", "diff", "--stat", f"--since={since_hours} hours ago", "HEAD"]
    output, rc = run_cmd(cmd, project_path)
    
    if rc == 0:
        for line in output.split('\n'):
            if '|' in line:
                parts = line.split('|')
                file_path = parts[0].strip()
                
                # Parse changes like "45 +"
                changes = parts[1].strip() if len(parts) > 1 else ""
                added = changes.count('+')
                removed = changes.count('-')
                
                files.append(FileActivity(
                    path=file_path,
                    lines_added=added,
                    lines_removed=removed
                ))
    
    return files


def harvest_session(
    project_path: str = None,
    since: str = "8 hours ago",
    include_loc: bool = True
) -> SessionData:
    """Harvest session data for a project."""
    
    project_name, proj_path = detect_project(project_path)
    
    now = datetime.now()
    
    session = SessionData(
        project=project_name,
        project_path=proj_path,
        harvested_at=now.isoformat(),
        period_start=(now - timedelta(hours=8)).isoformat(),
        period_end=now.isoformat()
    )
    
    # Get git activity
    commits = get_git_commits(proj_path, since)
    session.commits = [asdict(c) for c in commits]
    session.total_insertions = sum(c.insertions for c in commits)
    session.total_deletions = sum(c.deletions for c in commits)
    
    # Get files touched
    files = get_recent_files(proj_path, 24)
    session.files_touched = [asdict(f) for f in files]
    
    # Get LOC stats (optional, can be slow)
    if include_loc:
        session.loc_by_language = get_loc_stats(proj_path)
    
    # Detect tech stack
    session.tech_stack = detect_tech_stack(proj_path)
    
    return session


def save_to_cache(session: SessionData):
    """Save harvested data to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create project-specific cache file
    cache_file = CACHE_DIR / f"{session.project}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(cache_file, 'w') as f:
        json.dump(asdict(session), f, indent=2, default=str)
    
    print(f"Cached to: {cache_file}")
    return cache_file


def get_pending_cache_files(project: str = None) -> list[Path]:
    """Get cached files that haven't been processed."""
    if not CACHE_DIR.exists():
        return []
    
    pattern = f"{project}_*.json" if project else "*.json"
    return sorted(CACHE_DIR.glob(pattern))


def main():
    parser = argparse.ArgumentParser(description="DevLog Harvester")
    parser.add_argument("--project", "-p", help="Project path or name")
    parser.add_argument("--since", "-s", default="8 hours ago", help="Time range")
    parser.add_argument("--no-loc", action="store_true", help="Skip LOC analysis")
    parser.add_argument("--write", "-w", action="store_true", help="Write to knowledge-forge")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    print(f"🔍 Harvesting session data...")
    print(f"   Since: {args.since}")
    
    session = harvest_session(
        project_path=args.project,
        since=args.since,
        include_loc=not args.no_loc
    )
    
    if args.json:
        print(json.dumps(asdict(session), indent=2, default=str))
        return 0
    
    # Print summary
    print(f"\n📊 Session Summary: {session.project}")
    print(f"   Path: {session.project_path}")
    print(f"   Period: {session.period_start[:16]} → {session.period_end[:16]}")
    print(f"\n📝 Git Activity:")
    print(f"   Commits: {len(session.commits)}")
    print(f"   Lines: +{session.total_insertions} / -{session.total_deletions}")
    
    if session.commits:
        print(f"   Recent commits:")
        for c in session.commits[:5]:
            print(f"     - {c['sha']}: {c['message'][:50]}")
    
    print(f"\n📁 Files Touched: {len(session.files_touched)}")
    
    if session.tech_stack:
        print(f"\n🛠️ Tech Stack: {', '.join(session.tech_stack)}")
    
    if session.loc_by_language:
        print(f"\n📈 Lines of Code:")
        sorted_loc = sorted(session.loc_by_language.items(), key=lambda x: -x[1])
        for lang, lines in sorted_loc[:5]:
            print(f"   {lang}: {lines:,}")
    
    # Save to cache
    cache_file = save_to_cache(session)
    
    if args.write:
        print(f"\n📤 Passing to knowledge-forge...")
        # Call knowledge-forge skill
        subprocess.run([
            sys.executable,
            str(Path.home() / ".claude/skills/knowledge-forge/scripts/synthesize.py"),
            "--input", str(cache_file)
        ])
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
