#!/usr/bin/env python3
"""
Portfolio Forge - Generate static HTML portfolio from Obsidian knowledge base.

Creates:
- Project portfolio page with cards
- Activity timeline
- Statistics dashboard

Usage:
    python generate.py                    # Generate full portfolio
    python generate.py --output ~/Sites   # Custom output directory
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Paths
VAULTAGE_PATH = Path.home() / "Documents" / "Vaultage"
PROJECTS_PATH = VAULTAGE_PATH / "01_Projects"
DEVLOG_PATH = VAULTAGE_PATH / "06_Metadata" / "Developer-Log"
DEFAULT_OUTPUT = VAULTAGE_PATH / "06_Metadata" / "Portfolio"


# HTML Templates
CSS_TEMPLATE = """
:root {
    --bg-primary: #0a0a0a;
    --bg-secondary: #141414;
    --bg-tertiary: #1f1f1f;
    --text-primary: #e5e5e5;
    --text-secondary: #a3a3a3;
    --accent: #3b82f6;
    --accent-hover: #2563eb;
    --border: #262626;
    --success: #22c55e;
    --warning: #f59e0b;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    text-align: center;
    padding: 4rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 3rem;
}

header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

header p {
    color: var(--text-secondary);
    font-size: 1.1rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.stat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 0.25rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.project-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    transition: transform 0.2s, border-color 0.2s;
}

.project-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
}

.project-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.project-name {
    font-size: 1.25rem;
    font-weight: 600;
}

.project-status {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 9999px;
    background: var(--success);
    color: var(--bg-primary);
}

.project-stats {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.project-stats span {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.tech-stack {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
}

.tech-badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
}

.activity-list {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

.activity-item {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 1rem;
}

.activity-item:last-child {
    border-bottom: none;
}

.activity-date {
    color: var(--text-secondary);
    font-size: 0.9rem;
    min-width: 100px;
}

.activity-content {
    flex: 1;
}

.activity-project {
    color: var(--accent);
    font-weight: 500;
}

.activity-commits {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
}

footer {
    text-align: center;
    padding: 2rem;
    color: var(--text-secondary);
    font-size: 0.9rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}

footer a {
    color: var(--accent);
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    header {
        padding: 2rem 0;
    }
    
    header h1 {
        font-size: 1.75rem;
    }
    
    .projects-grid {
        grid-template-columns: 1fr;
    }
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🛠️ Developer Portfolio</h1>
            <p>Auto-generated from development activity</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_projects}</div>
                <div class="stat-label">Active Projects</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_loc}</div>
                <div class="stat-label">Lines of Code</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_commits}</div>
                <div class="stat-label">Total Commits</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{languages_count}</div>
                <div class="stat-label">Languages</div>
            </div>
        </div>
        
        <h2 class="section-title">📁 Projects</h2>
        <div class="projects-grid">
            {projects_html}
        </div>
        
        <h2 class="section-title">📅 Recent Activity</h2>
        <div class="activity-list">
            {activity_html}
        </div>
        
        <footer>
            <p>Generated on {generated_date} by <a href="#">Portfolio Forge</a></p>
            <p>Data sourced from Obsidian knowledge base</p>
        </footer>
    </div>
</body>
</html>
"""

PROJECT_CARD_TEMPLATE = """
<div class="project-card">
    <div class="project-header">
        <span class="project-name">{name}</span>
        <span class="project-status">{status}</span>
    </div>
    <div class="project-stats">
        <span>📝 {loc} lines</span>
        <span>📊 {commits} commits</span>
        <span>📅 {last_activity}</span>
    </div>
    <div class="tech-stack">
        {tech_badges}
    </div>
</div>
"""

ACTIVITY_ITEM_TEMPLATE = """
<div class="activity-item">
    <span class="activity-date">{date}</span>
    <div class="activity-content">
        <span class="activity-project">{project}</span>
        <div class="activity-commits">{summary}</div>
    </div>
</div>
"""


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}
    
    try:
        end = content.index("---", 3)
        frontmatter = content[3:end].strip()
        
        result = {}
        for line in frontmatter.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                # Handle arrays
                if value.startswith("["):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(",")]
                elif value.startswith('"') or value.startswith("'"):
                    value = value[1:-1]
                
                result[key] = value
        
        return result
    except:
        return {}


def scan_projects() -> list[dict]:
    """Scan Vaultage for project data."""
    projects = []
    
    if not PROJECTS_PATH.exists():
        return projects
    
    for project_dir in PROJECTS_PATH.iterdir():
        if not project_dir.is_dir():
            continue
        
        index_file = project_dir / "_index.md"
        if not index_file.exists():
            continue
        
        content = index_file.read_text()
        frontmatter = parse_frontmatter(content)
        
        # Get session data
        sessions_dir = project_dir / "sessions"
        session_count = 0
        last_activity = None
        total_commits = 0
        
        if sessions_dir.exists():
            sessions = list(sessions_dir.glob("*.md"))
            session_count = len(sessions)
            
            if sessions:
                # Get most recent session
                latest = max(sessions, key=lambda p: p.stem)
                last_activity = latest.stem
                
                # Count commits across sessions
                for session_file in sessions:
                    session_content = session_file.read_text()
                    fm = parse_frontmatter(session_content)
                    total_commits += int(fm.get("commits", 0))
        
        projects.append({
            "name": project_dir.name,
            "path": str(project_dir),
            "status": frontmatter.get("status", "active"),
            "tags": frontmatter.get("tags", []),
            "tech_stack": frontmatter.get("tags", []),  # Derive from tags
            "last_activity": last_activity or "Unknown",
            "sessions": session_count,
            "commits": total_commits,
            "loc": 0,  # Would need to re-analyze
        })
    
    return projects


def scan_activity() -> list[dict]:
    """Scan developer log for activity."""
    activity = []
    
    if not DEVLOG_PATH.exists():
        return activity
    
    for log_file in sorted(DEVLOG_PATH.glob("*.md"), reverse=True)[:30]:
        content = log_file.read_text()
        frontmatter = parse_frontmatter(content)
        
        activity.append({
            "date": log_file.stem,
            "projects": frontmatter.get("projects", []),
            "commits": frontmatter.get("commits", 0),
            "lines_changed": frontmatter.get("lines_changed", "+0/-0"),
        })
    
    return activity


def format_number(n: int) -> str:
    """Format large numbers with K/M suffix."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def generate_portfolio(output_dir: Path):
    """Generate the portfolio HTML files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "css").mkdir(exist_ok=True)
    (output_dir / "data").mkdir(exist_ok=True)
    
    # Write CSS
    (output_dir / "css" / "style.css").write_text(CSS_TEMPLATE)
    
    # Scan data
    projects = scan_projects()
    activity = scan_activity()
    
    # Calculate totals
    total_projects = len(projects)
    total_commits = sum(p["commits"] for p in projects)
    total_loc = sum(p.get("loc", 0) for p in projects)
    
    # Get unique languages/tech
    all_tech = set()
    for p in projects:
        if isinstance(p.get("tech_stack"), list):
            all_tech.update(p["tech_stack"])
    languages_count = len(all_tech)
    
    # Generate project cards HTML
    projects_html = ""
    for project in sorted(projects, key=lambda p: p["last_activity"], reverse=True):
        tech_badges = ""
        tech_stack = project.get("tech_stack", [])
        if isinstance(tech_stack, list):
            for tech in tech_stack[:5]:
                if tech and not tech.startswith("project"):
                    tech_badges += f'<span class="tech-badge">{tech}</span>'
        
        projects_html += PROJECT_CARD_TEMPLATE.format(
            name=project["name"],
            status=project.get("status", "active"),
            loc=format_number(project.get("loc", 0)),
            commits=project.get("commits", 0),
            last_activity=project.get("last_activity", "Unknown"),
            tech_badges=tech_badges
        )
    
    # Generate activity HTML
    activity_html = ""
    for item in activity[:15]:
        projects_list = item.get("projects", [])
        if isinstance(projects_list, list):
            project_names = ", ".join(projects_list) if projects_list else "Various"
        else:
            project_names = str(projects_list)
        
        activity_html += ACTIVITY_ITEM_TEMPLATE.format(
            date=item["date"],
            project=project_names,
            summary=f"{item.get('commits', 0)} commits, {item.get('lines_changed', '+0/-0')}"
        )
    
    if not activity_html:
        activity_html = '<div class="activity-item"><span class="activity-date">No activity yet</span><div class="activity-content">Start coding to see activity here!</div></div>'
    
    # Generate main HTML
    html = HTML_TEMPLATE.format(
        title="Developer Portfolio",
        total_projects=total_projects,
        total_loc=format_number(total_loc),
        total_commits=total_commits,
        languages_count=languages_count,
        projects_html=projects_html,
        activity_html=activity_html,
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    
    (output_dir / "index.html").write_text(html)
    
    # Save data as JSON
    (output_dir / "data" / "projects.json").write_text(
        json.dumps(projects, indent=2, default=str)
    )
    (output_dir / "data" / "activity.json").write_text(
        json.dumps(activity, indent=2, default=str)
    )
    
    print(f"✅ Portfolio generated at: {output_dir}")
    print(f"   - index.html")
    print(f"   - css/style.css")
    print(f"   - data/projects.json")
    print(f"   - data/activity.json")
    
    return output_dir / "index.html"


def main():
    parser = argparse.ArgumentParser(description="Portfolio Forge")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT), 
                       help="Output directory")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    
    print("🎨 Generating portfolio...")
    index_path = generate_portfolio(output_dir)
    
    print(f"\n🌐 Open in browser: file://{index_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
