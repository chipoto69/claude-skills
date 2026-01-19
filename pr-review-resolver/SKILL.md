---
name: pr-review-resolver
description: |
  Automatically monitor, evaluate, and resolve CodeRabbit and Qodo PR review comments.
  Waits for review bots to comment, evaluates suggestions intelligently, applies fixes,
  and marks comments as resolved. Designed to run in ralph-loop for continuous operation.
  
  Triggers: "resolve PR comments", "fix review issues", "handle coderabbit", 
  "address qodo feedback", "PR review loop", "/pr-resolve"
version: 1.0.0
author: Claude Code
allowed-tools:
  - Bash(gh:*)
  - Bash(git:*)
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Task
---

# PR Review Resolver

Automated workflow for handling CodeRabbit and Qodo PR review comments across all active repositories.

## Overview

This skill monitors PRs for review bot comments, evaluates suggestions, applies fixes intelligently, and resolves comments. It can run continuously in a ralph-loop until all issues are addressed.

## Quick Start

```bash
# Resolve comments on a specific PR
/pr-resolve owner/repo#123

# Resolve comments on current branch's PR
/pr-resolve

# Run in continuous mode (ralph-loop)
/ralph-loop "/pr-resolve owner/repo#123 --loop"
```

## Supported Review Bots

| Bot | Detection | Comment Format |
|-----|-----------|----------------|
| **CodeRabbit** | `coderabbitai[bot]` | Severity markers, diff blocks, committable suggestions |
| **Qodo** | `qodo-code-review[bot]` | Suggestion blocks with direct replacements |

## Workflow

### Phase 1: Discovery
```bash
# Find open PRs with pending review comments
gh pr list --state open --json number,title,author,headRefName

# Get review comments for a PR
gh api repos/{owner}/{repo}/pulls/{pr}/comments
```

### Phase 2: Parse Comments

**CodeRabbit Format:**
```
_⚠️ Potential issue_ | _🔴 Critical_
**Issue title**
Description...

<details>
<summary>🔧 Proposed fix</summary>

```diff
-old code
+new code
```
</details>
```

**Qodo Format:**
```
**Suggestion:** Title
```suggestion
replacement code here
```
```

### Phase 3: Evaluate Each Issue

For each comment, evaluate:

1. **Validity Check**
   - Is the suggestion syntactically correct?
   - Does the file/line still exist?
   - Has it already been addressed?

2. **Impact Assessment**
   - Security issues (🔴 Critical) → High priority
   - Logic bugs (🟠 Major) → Medium priority  
   - Style/lint (🟡 Minor) → Lower priority

3. **Conflict Detection**
   - Check if multiple suggestions target same lines
   - Determine which takes precedence

### Phase 4: Apply Fixes

```bash
# Read the target file
cat path/to/file.py

# Apply the fix (evaluated, not blind)
# For diff blocks: parse and apply hunks
# For suggestion blocks: replace exact lines

# Commit with reference
git add path/to/file.py
git commit -m "fix: address CodeRabbit review - <issue summary>

Resolves review comment: <comment_url>"
```

### Phase 5: Resolve Comments

```bash
# Reply to comment indicating fix
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies \
  -f body="✅ Fixed in commit $(git rev-parse --short HEAD)

Applied the suggested change. The issue has been addressed."

# Push changes
git push
```

### Phase 6: Loop Until Done

If running in ralph-loop mode:
1. Push changes
2. Wait for new review cycle (2-5 minutes)
3. Check for new comments
4. Repeat until no unresolved comments remain
5. Signal completion with `<promise>DONE</promise>`

## Comment Parsing Scripts

### Extract CodeRabbit Issues
```python
import re
import json

def parse_coderabbit_comment(body: str) -> dict:
    """Parse CodeRabbit comment into structured data."""
    result = {
        "severity": None,
        "title": None,
        "description": None,
        "diff": None,
        "suggestion": None
    }
    
    # Extract severity
    if "🔴 Critical" in body:
        result["severity"] = "critical"
    elif "🟠 Major" in body:
        result["severity"] = "major"
    elif "🟡 Minor" in body:
        result["severity"] = "minor"
    
    # Extract diff block
    diff_match = re.search(r'```diff\n(.*?)```', body, re.DOTALL)
    if diff_match:
        result["diff"] = diff_match.group(1)
    
    # Extract committable suggestion
    suggestion_match = re.search(
        r'📝 Committable suggestion.*?```\w*\n(.*?)```', 
        body, re.DOTALL
    )
    if suggestion_match:
        result["suggestion"] = suggestion_match.group(1)
    
    return result
```

### Extract Qodo Issues
```python
def parse_qodo_comment(body: str) -> dict:
    """Parse Qodo comment into structured data."""
    result = {
        "title": None,
        "suggestion": None
    }
    
    # Extract title
    title_match = re.search(r'\*\*Suggestion:\*\*\s*(.+)', body)
    if title_match:
        result["title"] = title_match.group(1).strip()
    
    # Extract suggestion block
    suggestion_match = re.search(r'```suggestion\n(.*?)```', body, re.DOTALL)
    if suggestion_match:
        result["suggestion"] = suggestion_match.group(1)
    
    return result
```

## Evaluation Criteria

### When to Apply a Suggestion

✅ **Apply when:**
- Suggestion is syntactically valid
- Target lines exist and match expected content
- Change doesn't introduce new issues
- Security fix (always prioritize)
- Clear bug fix with obvious improvement

⚠️ **Evaluate carefully when:**
- Suggestion conflicts with project conventions
- Multiple suggestions affect same code
- Change has broader implications
- Refactoring suggestion (may need context)

❌ **Skip when:**
- Target code has already changed
- Suggestion would break functionality
- False positive detection
- Requires human decision (architectural)

### Priority Order

1. 🔴 **Critical** - Security vulnerabilities, data loss risks
2. 🟠 **Major** - Logic bugs, error handling issues
3. 🟡 **Minor** - Style, lint, documentation

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub personal access token | Required |
| `PR_RESOLVE_AUTO_PUSH` | Auto-push after fixes | `true` |
| `PR_RESOLVE_WAIT_TIME` | Seconds to wait for new reviews | `300` |
| `PR_RESOLVE_MAX_ITERATIONS` | Max loop iterations | `10` |

## Example Session

```
User: /pr-resolve chipoto69/ATLAS-CORPUS#4 --loop

Agent: 🔍 Fetching PR #4 from chipoto69/ATLAS-CORPUS...

Found 30 review comments:
- coderabbitai[bot]: 28 comments (5 critical, 12 major, 11 minor)
- qodo-code-review[bot]: 2 comments

📋 Processing by priority...

[1/30] 🔴 CRITICAL: launchd plist will fail due to unexpanded $HOME
  File: corpus/avatars/templates/candysoul/bootstrap/README.md
  Issue: Heredoc uses single quotes preventing variable expansion
  
  Evaluating fix...
  ✅ Fix is valid and addresses the issue
  
  Applying: Changed 'EOF' to EOF for variable expansion
  Committed: abc1234

[2/30] 🔴 CRITICAL: Avoid "curl | bash" in Quick Start
  File: corpus/avatars/templates/candysoul/bootstrap/README.md
  Issue: Encourages execution of unreviewed remote code
  
  Evaluating fix...
  ✅ Suggested download-inspect-run flow is safer
  
  Applying: Added safer installation instructions
  Committed: def5678

... (continues through all issues)

📤 Pushing changes...
⏳ Waiting 5 minutes for new review cycle...
🔄 Checking for new comments...

No new unresolved comments found.
<promise>DONE</promise>

✅ All review comments resolved!
- Fixed: 28 issues
- Skipped: 2 (already addressed)
- Commits: 15
```

## Integration with ralph-loop

This skill is designed to work with oh-my-opencode's ralph-loop:

```bash
/ralph-loop "/pr-resolve chipoto69/ATLAS-CORPUS#4"
```

The loop will:
1. Process all current comments
2. Push fixes
3. Wait for CodeRabbit/Qodo to re-review
4. Address any new comments
5. Repeat until `<promise>DONE</promise>`

## Files Modified

The skill creates no persistent files. All state is managed through:
- Git commits (fix history)
- GitHub API (comment status)
- PR conversation thread (resolution replies)

## Troubleshooting

### "Comment already resolved"
The comment may have been addressed in a previous run. Check git log for related commits.

### "Cannot apply diff - context mismatch"
The target code has changed since the review. Re-fetch the file and manually verify the fix.

### "Rate limited by GitHub API"
Wait for rate limit reset or use a token with higher limits.

### "Suggestion introduces syntax error"
Skip the suggestion and flag for human review. Log the issue.
