#!/bin/bash
# Install git post-commit hook for automatic harvesting
# Usage: ./install-hooks.sh [repo_path]

HOOK_CONTENT='#!/bin/bash
# DevLog Harvester - Post-commit hook
# Automatically capture session context after each commit

# Run harvester in background (non-blocking)
python3 ~/.claude/skills/devlog-harvester/scripts/harvest.py \
    --since "1 hour ago" \
    --no-loc \
    2>/dev/null &

# Disown to prevent blocking
disown
'

install_hook() {
    local repo_path="$1"
    local hooks_dir="$repo_path/.git/hooks"
    local hook_file="$hooks_dir/post-commit"
    
    if [ ! -d "$hooks_dir" ]; then
        echo "Not a git repo: $repo_path"
        return 1
    fi
    
    # Backup existing hook
    if [ -f "$hook_file" ]; then
        cp "$hook_file" "${hook_file}.backup"
        echo "Backed up existing hook to ${hook_file}.backup"
    fi
    
    # Install hook
    echo "$HOOK_CONTENT" > "$hook_file"
    chmod +x "$hook_file"
    
    echo "✅ Installed post-commit hook in: $repo_path"
}

# If repo path provided, install there
if [ -n "$1" ]; then
    install_hook "$1"
    exit 0
fi

# Otherwise, install in all repos under ARSENAL
ARSENAL_PATH="$HOME/ORGANIZED/ACTIVE_PROJECTS/ARSENAL"

if [ -d "$ARSENAL_PATH" ]; then
    echo "Installing hooks in ARSENAL projects..."
    
    for dir in "$ARSENAL_PATH"/*; do
        if [ -d "$dir/.git" ]; then
            install_hook "$dir"
        fi
    done
else
    echo "ARSENAL path not found. Provide a repo path as argument."
    exit 1
fi

echo ""
echo "Done! Hooks will capture session data after each commit."
echo "Data will be stored in ~/.cache/devlog/"
