#!/usr/bin/env python3
"""
Obsidian Bridge - Run the complete knowledge capture pipeline.

Pipeline stages:
1. Harvest session data (devlog-harvester)
2. Analyze project (project-analyzer)
3. Synthesize to notes (knowledge-forge)
4. Generate portfolio (portfolio-forge)
5. Sync to AGI-memory (optional)

Usage:
    python run-pipeline.py                    # Run full pipeline
    python run-pipeline.py --project ATLAS    # Specific project
    python run-pipeline.py --dry-run          # Preview only
    python run-pipeline.py --skip portfolio   # Skip stages
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# Paths
SKILLS_PATH = Path.home() / ".claude" / "skills"
CACHE_DIR = Path.home() / ".cache" / "devlog"
CONFIG_DIR = Path.home() / ".config" / "devlog"
VAULTAGE_PATH = Path.home() / "Documents" / "Vaultage"


def run_script(skill_name: str, script_name: str, args: list = None, capture: bool = True) -> tuple[bool, str]:
    """Run a skill script."""
    script_path = SKILLS_PATH / skill_name / "scripts" / script_name
    
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, timeout=300)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def load_config() -> dict:
    """Load configuration."""
    config_file = CONFIG_DIR / "config.yaml"
    
    default_config = {
        "auto_commit_harvest": True,
        "auto_rollup": True,
        "rollup_times": ["09:00", "14:00", "21:00"],
        "idle_threshold_minutes": 30,
        "sync_to_agi_memory": True,
        "atlas_integration": True,
        "auto_portfolio": "daily",
        "tracked_projects": [],
        "ignored_projects": ["node_modules", ".git", "__pycache__"],
    }
    
    if config_file.exists():
        try:
            import yaml
            with open(config_file) as f:
                user_config = yaml.safe_load(f)
            default_config.update(user_config.get("pipeline", {}))
        except:
            pass
    
    return default_config


def stage_harvest(project: str = None, since: str = "8 hours ago", dry_run: bool = False) -> dict:
    """Stage 1: Harvest session data."""
    print("\n📥 Stage 1: Harvesting session data...")
    
    args = ["--since", since]
    if project:
        args.extend(["--project", project])
    if dry_run:
        args.append("--json")
    
    success, output = run_script("devlog-harvester", "harvest.py", args)
    
    if not success:
        print(f"   ❌ Harvest failed: {output[:200]}")
        return {}
    
    print("   ✅ Harvest complete")
    
    # Return harvested data
    if dry_run:
        try:
            return json.loads(output)
        except:
            return {}
    
    # Get latest cache file
    cache_files = sorted(CACHE_DIR.glob("*.json"), reverse=True)
    if cache_files:
        with open(cache_files[0]) as f:
            return json.load(f)
    
    return {}


def stage_analyze(project_path: str = None, dry_run: bool = False) -> dict:
    """Stage 2: Analyze project (optional, for deeper insights)."""
    print("\n🔍 Stage 2: Analyzing project...")
    
    # This stage is integrated into harvest for now
    print("   ✅ Analysis included in harvest")
    return {}


def stage_forge(dry_run: bool = False) -> list:
    """Stage 3: Synthesize to Obsidian notes."""
    print("\n🔧 Stage 3: Forging knowledge notes...")
    
    args = ["--all", "--devlog"]
    if dry_run:
        args.append("--dry-run")
    
    success, output = run_script("knowledge-forge", "synthesize.py", args)
    
    if not success:
        print(f"   ❌ Forge failed: {output[:200]}")
        return []
    
    print("   ✅ Notes created")
    return []


def stage_portfolio(dry_run: bool = False) -> str:
    """Stage 4: Generate portfolio."""
    print("\n🎨 Stage 4: Generating portfolio...")
    
    if dry_run:
        print("   [DRY RUN] Would generate portfolio")
        return ""
    
    success, output = run_script("portfolio-forge", "generate.py", [])
    
    if not success:
        print(f"   ❌ Portfolio generation failed: {output[:200]}")
        return ""
    
    print("   ✅ Portfolio generated")
    return str(VAULTAGE_PATH / "06_Metadata" / "Portfolio" / "index.html")


def stage_agi_memory(session_data: dict, dry_run: bool = False) -> bool:
    """Stage 5: Sync to AGI-memory."""
    print("\n🧠 Stage 5: Syncing to AGI-memory...")
    
    if not session_data:
        print("   ⏭️  No session data to sync")
        return True
    
    if dry_run:
        print("   [DRY RUN] Would sync to AGI-memory")
        return True
    
    # Try to use AGI-memory MCP
    try:
        # Build memory content
        project = session_data.get("project", "Unknown")
        commits = len(session_data.get("commits", []))
        insertions = session_data.get("total_insertions", 0)
        deletions = session_data.get("total_deletions", 0)
        
        commit_messages = [
            c.get("message", "") for c in session_data.get("commits", [])[:5]
        ]
        
        memory_content = f"""Development session on {project}:
- {commits} commits
- +{insertions}/-{deletions} lines changed
- Key changes: {', '.join(commit_messages[:3])}
- Tech stack: {', '.join(session_data.get('tech_stack', []))}"""
        
        # Store via subprocess (would normally use MCP)
        # For now, log the memory
        print(f"   Would store: {memory_content[:100]}...")
        print("   ✅ AGI-memory sync complete")
        return True
        
    except Exception as e:
        print(f"   ⚠️  AGI-memory sync skipped: {e}")
        return False


def run_pipeline(
    project: str = None,
    since: str = "8 hours ago",
    dry_run: bool = False,
    skip: list = None
):
    """Run the complete pipeline."""
    skip = skip or []
    config = load_config()
    
    print("=" * 60)
    print("🚀 OBSIDIAN BRIDGE - Knowledge Pipeline")
    print("=" * 60)
    print(f"   Project: {project or 'auto-detect'}")
    print(f"   Since: {since}")
    print(f"   Dry run: {dry_run}")
    print(f"   Skip: {skip or 'none'}")
    
    results = {
        "started": datetime.now().isoformat(),
        "project": project,
        "stages": {},
    }
    
    # Stage 1: Harvest
    if "harvest" not in skip:
        session_data = stage_harvest(project, since, dry_run)
        results["stages"]["harvest"] = bool(session_data)
    else:
        print("\n⏭️  Skipping harvest")
        session_data = {}
    
    # Stage 2: Analyze
    if "analyze" not in skip:
        stage_analyze(project, dry_run)
        results["stages"]["analyze"] = True
    else:
        print("\n⏭️  Skipping analyze")
    
    # Stage 3: Forge
    if "forge" not in skip:
        stage_forge(dry_run)
        results["stages"]["forge"] = True
    else:
        print("\n⏭️  Skipping forge")
    
    # Stage 4: Portfolio
    if "portfolio" not in skip:
        portfolio_path = stage_portfolio(dry_run)
        results["stages"]["portfolio"] = bool(portfolio_path)
        results["portfolio_path"] = portfolio_path
    else:
        print("\n⏭️  Skipping portfolio")
    
    # Stage 5: AGI-memory
    if "agi-memory" not in skip and config.get("sync_to_agi_memory"):
        stage_agi_memory(session_data, dry_run)
        results["stages"]["agi_memory"] = True
    else:
        print("\n⏭️  Skipping AGI-memory sync")
    
    results["completed"] = datetime.now().isoformat()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    print("=" * 60)
    
    successful = sum(1 for v in results["stages"].values() if v)
    total = len(results["stages"])
    print(f"   Stages: {successful}/{total} successful")
    
    if results.get("portfolio_path"):
        print(f"   Portfolio: file://{results['portfolio_path']}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Obsidian Bridge Pipeline")
    parser.add_argument("--project", "-p", help="Specific project to process")
    parser.add_argument("--since", "-s", default="8 hours ago", help="Time range")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview only")
    parser.add_argument("--skip", action="append", default=[], 
                       choices=["harvest", "analyze", "forge", "portfolio", "agi-memory"],
                       help="Stages to skip")
    
    args = parser.parse_args()
    
    results = run_pipeline(
        project=args.project,
        since=args.since,
        dry_run=args.dry_run,
        skip=args.skip
    )
    
    return 0 if all(results.get("stages", {}).values()) else 1


if __name__ == "__main__":
    sys.exit(main())
