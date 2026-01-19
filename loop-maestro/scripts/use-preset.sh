#!/bin/bash
# Initialize a project from a preset template
set -e

PRESET="${1:-}"
PROJECT_NAME="${2:-}"
PROJECT_DIR="${3:-.}"

SKILL_DIR="$HOME/.claude/skills/loop-maestro"
PRESETS_FILE="$SKILL_DIR/templates/presets.yaml"
ORCH_DIR="$PROJECT_DIR/.claude/orchestration"

if [ -z "$PRESET" ]; then
    echo "🎭 Loop Maestro: Available Presets"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if [ -f "$PRESETS_FILE" ]; then
        # List presets
        grep -E "^[a-z].*:$" "$PRESETS_FILE" | grep -v "  " | sed 's/:$//' | while read preset; do
            DESC=$(grep -A1 "^${preset}:" "$PRESETS_FILE" | grep "description:" | sed 's/.*description: *"//' | sed 's/"$//')
            echo "  $preset"
            echo "    $DESC"
            echo ""
        done
    fi

    echo "Usage: use-preset.sh <preset-name> <project-name> [project-dir]"
    echo ""
    echo "Example:"
    echo "  use-preset.sh feature-development \"User Auth Feature\""
    exit 0
fi

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ Project name required"
    echo "Usage: use-preset.sh <preset-name> <project-name> [project-dir]"
    exit 1
fi

echo "🎭 Loop Maestro: Loading preset '$PRESET'"
echo "   Project: $PROJECT_NAME"
echo ""

# First, run init
bash "$SKILL_DIR/scripts/init-project.sh" "$PROJECT_NAME" "$PROJECT_DIR"

# Extract phases from preset
PLAN_FILE="$ORCH_DIR/project-plan.yaml"

if [ -f "$PRESETS_FILE" ]; then
    # Find the preset section and extract it
    # This is simplified - in production you'd use yq

    IN_PRESET=false
    INDENT=0

    echo "# Project Plan generated from preset: $PRESET" > "$PLAN_FILE"
    echo "project: \"$PROJECT_NAME\"" >> "$PLAN_FILE"
    echo "completion_promise: \"PROJECT_COMPLETE\"" >> "$PLAN_FILE"
    echo "max_iterations: 100" >> "$PLAN_FILE"
    echo "" >> "$PLAN_FILE"

    while IFS= read -r line; do
        if [[ "$line" =~ ^${PRESET}:$ ]]; then
            IN_PRESET=true
            continue
        fi

        if [ "$IN_PRESET" = true ]; then
            # Check if we've hit another top-level key (no leading space)
            if [[ "$line" =~ ^[a-z] ]] && [[ ! "$line" =~ ^[[:space:]] ]]; then
                break
            fi

            # Skip description line
            if [[ "$line" =~ description: ]]; then
                continue
            fi

            # Output the line (remove one level of indentation)
            echo "${line#  }" >> "$PLAN_FILE"
        fi
    done < "$PRESETS_FILE"

    echo ""
    echo "✅ Preset '$PRESET' loaded into project plan"
    echo ""
    echo "📋 Phases:"
    grep "id:" "$PLAN_FILE" 2>/dev/null | sed 's/.*id: /   - /' || echo "   (Check plan file)"
    echo ""
    echo "Next steps:"
    echo "  1. Review/customize: $PLAN_FILE"
    echo "  2. Generate prompts for each phase:"
    echo "     bash $SKILL_DIR/scripts/create-phase-prompt.sh <phase-id>"
    echo "  3. Run first phase with /ralph-loop"
else
    echo "⚠️  Presets file not found: $PRESETS_FILE"
fi
