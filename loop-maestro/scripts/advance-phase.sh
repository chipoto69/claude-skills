#!/bin/bash
# Mark current phase complete and advance to next
set -e

PHASE_ID="${1:-}"
ITERATIONS="${2:-0}"
PROJECT_DIR="${3:-.}"
ORCH_DIR="$PROJECT_DIR/.claude/orchestration"
STATE_FILE="$ORCH_DIR/state.json"

if [ -z "$PHASE_ID" ]; then
    echo "Usage: advance-phase.sh <phase-id> [iterations] [project-dir]"
    echo ""
    echo "Marks a phase as complete and records iteration count."
    exit 1
fi

if [ ! -f "$STATE_FILE" ]; then
    echo "❌ No state file found. Run init-project.sh first."
    exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "🎭 Advancing phase: $PHASE_ID"

# Update state file with jq if available
if command -v jq &> /dev/null; then
    # Mark phase complete
    TMP_FILE=$(mktemp)
    cat "$STATE_FILE" | jq \
        --arg phase "$PHASE_ID" \
        --arg ts "$TIMESTAMP" \
        --argjson iter "$ITERATIONS" \
        '.phases[$phase] = {"status": "complete", "iterations": $iter, "completed_at": $ts} |
         .events += [{"event": ($phase + ":complete"), "timestamp": $ts}] |
         .total_iterations += $iter' \
        > "$TMP_FILE"
    mv "$TMP_FILE" "$STATE_FILE"

    echo "✅ Phase '$PHASE_ID' marked complete"
    echo "   Iterations: $ITERATIONS"
    echo "   Timestamp: $TIMESTAMP"
else
    echo "⚠️  jq not installed - manual state update required"
    echo ""
    echo "Add to $STATE_FILE:"
    echo "  phases.$PHASE_ID = {\"status\": \"complete\", \"iterations\": $ITERATIONS}"
fi

echo ""
echo "📋 Next steps:"
echo "   1. Check status: bash ~/.claude/skills/loop-maestro/scripts/status.sh"
echo "   2. Generate next phase prompt"
echo "   3. Run: /ralph-loop \"\$(cat .claude/orchestration/prompts/NEXT-phase.md)\""
