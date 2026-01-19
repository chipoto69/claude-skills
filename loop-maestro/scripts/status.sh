#!/bin/bash
# Check orchestration status
set -e

PROJECT_DIR="${1:-.}"
ORCH_DIR="$PROJECT_DIR/.claude/orchestration"
STATE_FILE="$ORCH_DIR/state.json"
PLAN_FILE="$ORCH_DIR/project-plan.yaml"

if [ ! -f "$STATE_FILE" ]; then
    echo "❌ No orchestration state found."
    echo "   Run: bash ~/.claude/skills/loop-maestro/scripts/init-project.sh"
    exit 1
fi

echo "🎭 Loop Maestro Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Parse state file
PROJECT=$(cat "$STATE_FILE" | grep -o '"project": *"[^"]*"' | cut -d'"' -f4)
STARTED=$(cat "$STATE_FILE" | grep -o '"started": *"[^"]*"' | cut -d'"' -f4)
CURRENT=$(cat "$STATE_FILE" | grep -o '"current_phase": *"[^"]*"' | cut -d'"' -f4)
ITERATIONS=$(cat "$STATE_FILE" | grep -o '"total_iterations": *[0-9]*' | grep -o '[0-9]*')

echo "Project: $PROJECT"
echo "Started: $STARTED"
echo "Total Iterations: ${ITERATIONS:-0}"
echo ""

# Check for active ralph loop
RALPH_STATE=".claude/.ralph-loop.local.md"
if [ -f "$PROJECT_DIR/$RALPH_STATE" ]; then
    echo "🔄 Active Ralph Loop Detected"
    RALPH_ITER=$(grep -o 'iteration: [0-9]*' "$PROJECT_DIR/$RALPH_STATE" 2>/dev/null | grep -o '[0-9]*' || echo "?")
    echo "   Current Iteration: $RALPH_ITER"
    echo ""
fi

echo "📋 Phase Status:"
echo ""

# If we have jq, use it for better parsing
if command -v jq &> /dev/null; then
    cat "$STATE_FILE" | jq -r '
        .phases | to_entries[] |
        "   " +
        (if .value.status == "complete" then "✅"
         elif .value.status == "in_progress" then "🔄"
         else "⏳" end) +
        " " + .key +
        " (" + (.value.iterations | tostring) + " iterations)" +
        (if .value.status then " - " + .value.status else "" end)
    ' 2>/dev/null || echo "   (No phases recorded yet)"
else
    # Fallback without jq
    echo "   (Install jq for detailed phase status)"
    grep -o '"[^"]*": *{"status"' "$STATE_FILE" 2>/dev/null | \
        sed 's/"//g' | sed 's/: *{status//' | \
        while read phase; do
            echo "   - $phase"
        done || echo "   (No phases recorded yet)"
fi

echo ""

# Show recent events
echo "📡 Recent Events:"
if command -v jq &> /dev/null; then
    cat "$STATE_FILE" | jq -r '.events[-5:][] | "   " + .timestamp + " → " + .event' 2>/dev/null || echo "   (No events yet)"
else
    echo "   (Install jq for event history)"
fi

echo ""

# Show pending gates
echo "🚧 Pending Gates:"
if command -v jq &> /dev/null; then
    PENDING=$(cat "$STATE_FILE" | jq -r '.gates_pending[]' 2>/dev/null)
    if [ -n "$PENDING" ]; then
        echo "$PENDING" | while read gate; do
            echo "   ⬜ $gate"
        done
    else
        echo "   (No pending gates)"
    fi
else
    echo "   (Install jq for gate status)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
