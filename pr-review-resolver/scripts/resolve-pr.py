#!/usr/bin/env python3
"""
PR Review Resolver - Automated CodeRabbit/Qodo comment handler.

Usage:
    python resolve-pr.py <owner> <repo> <pr_number> [--loop] [--dry-run]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    UNKNOWN = "unknown"


class Bot(Enum):
    CODERABBIT = "coderabbitai[bot]"
    QODO = "qodo-code-review[bot]"
    UNKNOWN = "unknown"


@dataclass
class ReviewComment:
    """Parsed review comment from CodeRabbit or Qodo."""
    id: int
    bot: Bot
    severity: Severity
    path: str
    line: Optional[int]
    body: str
    diff: Optional[str]
    suggestion: Optional[str]
    title: Optional[str]
    url: str
    
    @property
    def priority(self) -> int:
        """Lower number = higher priority."""
        priorities = {
            Severity.CRITICAL: 1,
            Severity.MAJOR: 2,
            Severity.MINOR: 3,
            Severity.UNKNOWN: 4
        }
        return priorities.get(self.severity, 5)


def run_gh(args: list[str], capture: bool = True) -> str:
    """Run gh CLI command and return output."""
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if result.returncode != 0 and capture:
        print(f"Error running gh: {result.stderr}", file=sys.stderr)
    return result.stdout if capture else ""


def get_pr_comments(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all review comments for a PR."""
    output = run_gh([
        "api", f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
        "--paginate"
    ])
    try:
        return json.loads(output) if output else []
    except json.JSONDecodeError:
        return []


def detect_bot(username: str) -> Bot:
    """Detect which review bot made the comment."""
    if "coderabbit" in username.lower():
        return Bot.CODERABBIT
    elif "qodo" in username.lower():
        return Bot.QODO
    return Bot.UNKNOWN


def parse_severity(body: str) -> Severity:
    """Extract severity from CodeRabbit comment."""
    if "🔴 Critical" in body or "_🔴 Critical_" in body:
        return Severity.CRITICAL
    elif "🟠 Major" in body or "_🟠 Major_" in body:
        return Severity.MAJOR
    elif "🟡 Minor" in body or "_🟡 Minor_" in body:
        return Severity.MINOR
    return Severity.UNKNOWN


def extract_diff(body: str) -> Optional[str]:
    """Extract diff block from comment."""
    match = re.search(r'```diff\n(.*?)```', body, re.DOTALL)
    return match.group(1).strip() if match else None


def extract_suggestion(body: str) -> Optional[str]:
    """Extract suggestion block (Qodo style or CodeRabbit committable)."""
    # Try Qodo format first
    match = re.search(r'```suggestion\n(.*?)```', body, re.DOTALL)
    if match:
        return match.group(1)
    
    # Try CodeRabbit committable suggestion
    match = re.search(
        r'📝 Committable suggestion.*?```[\w]*\n(.*?)```',
        body, re.DOTALL
    )
    if match:
        return match.group(1)
    
    return None


def extract_title(body: str, bot: Bot) -> Optional[str]:
    """Extract issue title from comment."""
    if bot == Bot.QODO:
        match = re.search(r'\*\*Suggestion:\*\*\s*(.+?)(?:\n|$)', body)
        return match.group(1).strip() if match else None
    else:
        # CodeRabbit: first bold text after severity
        match = re.search(r'\*\*([^*]+)\*\*', body)
        return match.group(1).strip() if match else None


def parse_comment(raw: dict) -> Optional[ReviewComment]:
    """Parse raw API response into ReviewComment."""
    user = raw.get("user", {}).get("login", "")
    bot = detect_bot(user)
    
    if bot == Bot.UNKNOWN:
        return None
    
    body = raw.get("body", "")
    
    return ReviewComment(
        id=raw.get("id"),
        bot=bot,
        severity=parse_severity(body),
        path=raw.get("path", ""),
        line=raw.get("line") or raw.get("original_line"),
        body=body,
        diff=extract_diff(body),
        suggestion=extract_suggestion(body),
        title=extract_title(body, bot),
        url=raw.get("html_url", "")
    )


def read_file(path: str) -> Optional[str]:
    """Read file contents."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return None


def apply_diff(file_path: str, diff: str, dry_run: bool = False) -> bool:
    """Apply a diff to a file."""
    # Parse diff for - and + lines
    old_lines = []
    new_lines = []
    
    for line in diff.split('\n'):
        if line.startswith('-') and not line.startswith('---'):
            old_lines.append(line[1:])
        elif line.startswith('+') and not line.startswith('+++'):
            new_lines.append(line[1:])
    
    if not old_lines and not new_lines:
        return False
    
    content = read_file(file_path)
    if content is None:
        print(f"  ❌ File not found: {file_path}")
        return False
    
    # Try to find and replace the old content
    old_content = '\n'.join(old_lines)
    new_content = '\n'.join(new_lines)
    
    if old_content not in content:
        print(f"  ⚠️ Context mismatch - old content not found")
        return False
    
    if dry_run:
        print(f"  🔍 Would replace:\n    -{old_content[:100]}...\n    +{new_content[:100]}...")
        return True
    
    updated = content.replace(old_content, new_content, 1)
    Path(file_path).write_text(updated)
    return True


def apply_suggestion(file_path: str, line: int, suggestion: str, dry_run: bool = False) -> bool:
    """Apply a suggestion block to specific lines."""
    content = read_file(file_path)
    if content is None:
        print(f"  ❌ File not found: {file_path}")
        return False
    
    lines = content.split('\n')
    
    if line is None or line < 1 or line > len(lines):
        print(f"  ⚠️ Invalid line number: {line}")
        return False
    
    if dry_run:
        print(f"  🔍 Would replace line {line}:\n    -{lines[line-1][:80]}...\n    +{suggestion[:80]}...")
        return True
    
    # Replace the line(s) with suggestion
    suggestion_lines = suggestion.rstrip('\n').split('\n')
    lines[line-1:line] = suggestion_lines
    
    Path(file_path).write_text('\n'.join(lines))
    return True


def commit_fix(path: str, comment: ReviewComment) -> Optional[str]:
    """Commit the fix with appropriate message."""
    severity_emoji = {
        Severity.CRITICAL: "🔴",
        Severity.MAJOR: "🟠", 
        Severity.MINOR: "🟡",
        Severity.UNKNOWN: "📝"
    }
    
    emoji = severity_emoji.get(comment.severity, "📝")
    title = comment.title or "review feedback"
    
    # Stage the file
    subprocess.run(["git", "add", path], check=True)
    
    # Create commit message
    msg = f"fix: {emoji} {title[:50]}\n\nAddresses {comment.bot.value} review comment\nSeverity: {comment.severity.value}\nRef: {comment.url}"
    
    result = subprocess.run(
        ["git", "commit", "-m", msg],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        # Get commit hash
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip()
        return sha
    
    return None


def reply_to_comment(owner: str, repo: str, pr: int, comment_id: int, sha: str):
    """Reply to comment indicating the fix."""
    body = f"✅ Fixed in commit `{sha}`\n\nThe suggested change has been applied and committed."
    
    run_gh([
        "api", f"repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies",
        "-f", f"body={body}"
    ])


def process_comments(
    owner: str, 
    repo: str, 
    pr: int, 
    dry_run: bool = False
) -> tuple[int, int, int]:
    """Process all review comments. Returns (fixed, skipped, errors)."""
    
    print(f"\n🔍 Fetching comments for {owner}/{repo}#{pr}...")
    raw_comments = get_pr_comments(owner, repo, pr)
    
    # Parse and filter bot comments
    comments = []
    for raw in raw_comments:
        parsed = parse_comment(raw)
        if parsed and (parsed.diff or parsed.suggestion):
            comments.append(parsed)
    
    if not comments:
        print("✅ No actionable review comments found.")
        return 0, 0, 0
    
    # Sort by priority
    comments.sort(key=lambda c: c.priority)
    
    # Group by bot
    coderabbit = [c for c in comments if c.bot == Bot.CODERABBIT]
    qodo = [c for c in comments if c.bot == Bot.QODO]
    
    print(f"\n📋 Found {len(comments)} actionable comments:")
    print(f"   - CodeRabbit: {len(coderabbit)}")
    print(f"   - Qodo: {len(qodo)}")
    
    # Count by severity
    critical = sum(1 for c in comments if c.severity == Severity.CRITICAL)
    major = sum(1 for c in comments if c.severity == Severity.MAJOR)
    minor = sum(1 for c in comments if c.severity == Severity.MINOR)
    
    print(f"   - 🔴 Critical: {critical}")
    print(f"   - 🟠 Major: {major}")
    print(f"   - 🟡 Minor: {minor}")
    
    fixed = 0
    skipped = 0
    errors = 0
    
    for i, comment in enumerate(comments, 1):
        severity_icon = {
            Severity.CRITICAL: "🔴",
            Severity.MAJOR: "🟠",
            Severity.MINOR: "🟡"
        }.get(comment.severity, "📝")
        
        print(f"\n[{i}/{len(comments)}] {severity_icon} {comment.title or 'Review comment'}")
        print(f"   File: {comment.path}")
        print(f"   Bot: {comment.bot.value}")
        
        # Try to apply fix
        success = False
        
        if comment.diff:
            print("   Applying diff...")
            success = apply_diff(comment.path, comment.diff, dry_run)
        elif comment.suggestion and comment.line:
            print("   Applying suggestion...")
            success = apply_suggestion(
                comment.path, comment.line, comment.suggestion, dry_run
            )
        else:
            print("   ⚠️ No applicable fix found in comment")
            skipped += 1
            continue
        
        if success:
            if dry_run:
                print("   ✅ Would apply successfully")
                fixed += 1
            else:
                sha = commit_fix(comment.path, comment)
                if sha:
                    print(f"   ✅ Committed: {sha}")
                    reply_to_comment(owner, repo, pr, comment.id, sha)
                    fixed += 1
                else:
                    print("   ⚠️ Commit failed (no changes?)")
                    skipped += 1
        else:
            print("   ❌ Failed to apply fix")
            errors += 1
    
    return fixed, skipped, errors


def push_changes() -> bool:
    """Push committed changes."""
    result = subprocess.run(
        ["git", "push"],
        capture_output=True, text=True
    )
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="PR Review Resolver")
    parser.add_argument("owner", help="Repository owner")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument("pr", type=int, help="PR number")
    parser.add_argument("--loop", action="store_true", help="Run in loop mode")
    parser.add_argument("--dry-run", action="store_true", help="Don't apply changes")
    parser.add_argument("--wait", type=int, default=300, help="Seconds to wait between loops")
    parser.add_argument("--max-iterations", type=int, default=10, help="Max loop iterations")
    
    args = parser.parse_args()
    
    iteration = 0
    total_fixed = 0
    
    while True:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"Iteration {iteration}/{args.max_iterations}")
        print(f"{'='*60}")
        
        fixed, skipped, errors = process_comments(
            args.owner, args.repo, args.pr, args.dry_run
        )
        
        total_fixed += fixed
        
        print(f"\n📊 Summary: {fixed} fixed, {skipped} skipped, {errors} errors")
        
        if not args.loop:
            break
        
        if fixed == 0:
            print("\n✅ No more issues to fix!")
            print("<promise>DONE</promise>")
            break
        
        if iteration >= args.max_iterations:
            print(f"\n⚠️ Reached max iterations ({args.max_iterations})")
            break
        
        if not args.dry_run:
            print("\n📤 Pushing changes...")
            if push_changes():
                print("   ✅ Pushed successfully")
            else:
                print("   ❌ Push failed")
                break
        
        print(f"\n⏳ Waiting {args.wait}s for review bots to re-analyze...")
        time.sleep(args.wait)
    
    print(f"\n🎉 Total fixed across all iterations: {total_fixed}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
