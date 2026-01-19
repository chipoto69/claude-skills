#!/bin/bash
# Generate a phase prompt from the project plan
set -e

PHASE_ID="${1:-}"
PROJECT_DIR="${2:-.}"
ORCH_DIR="$PROJECT_DIR/.claude/orchestration"
PLAN_FILE="$ORCH_DIR/project-plan.yaml"
PROMPTS_DIR="$ORCH_DIR/prompts"

if [ -z "$PHASE_ID" ]; then
    echo "Usage: create-phase-prompt.sh <phase-id> [project-dir]"
    echo ""
    echo "Available phases (from project-plan.yaml):"
    if [ -f "$PLAN_FILE" ]; then
        grep "^  - id:" "$PLAN_FILE" | sed 's/  - id: /   /'
    else
        echo "   (No plan file found)"
    fi
    exit 1
fi

if [ ! -f "$PLAN_FILE" ]; then
    echo "❌ No project plan found: $PLAN_FILE"
    echo "   Run init-project.sh first"
    exit 1
fi

mkdir -p "$PROMPTS_DIR"

OUTPUT_FILE="$PROMPTS_DIR/${PHASE_ID}-phase.md"

echo "🎭 Generating prompt for phase: $PHASE_ID"

# Extract phase info (basic YAML parsing without yq)
# This is a simplified parser - for complex plans, use yq

# Find the phase block
IN_PHASE=false
HAT=""
GOAL=""
GATES=""
PUBLISHES=""

while IFS= read -r line; do
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*id:[[:space:]]*$PHASE_ID ]]; then
        IN_PHASE=true
        continue
    fi

    if [ "$IN_PHASE" = true ]; then
        # Check if we've hit the next phase
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*id: ]]; then
            break
        fi

        if [[ "$line" =~ hat:[[:space:]]*(.+) ]]; then
            HAT="${BASH_REMATCH[1]}"
        fi
        if [[ "$line" =~ goal:[[:space:]]*\"(.+)\" ]]; then
            GOAL="${BASH_REMATCH[1]}"
        fi
        if [[ "$line" =~ publishes:[[:space:]]*(.+) ]]; then
            PUBLISHES="${BASH_REMATCH[1]}"
        fi
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*\"(.+)\" ]] && [ -n "$GATES" ]; then
            GATES="$GATES\n- ${BASH_REMATCH[1]}"
        elif [[ "$line" =~ gates: ]]; then
            GATES="gates"
        fi
    fi
done < "$PLAN_FILE"

if [ -z "$HAT" ]; then
    echo "⚠️  Could not find phase '$PHASE_ID' in plan"
    echo "   Check your project-plan.yaml"
    exit 1
fi

# Get project name
PROJECT=$(grep "^project:" "$PLAN_FILE" | sed 's/project: *//' | tr -d '"')

# Generate the prompt
cat > "$OUTPUT_FILE" << EOF
# ${HAT^} Phase: $PHASE_ID

## Project
$PROJECT

## Your Role
You are wearing the **${HAT^^}** hat. Stay focused on this role.

## Goal
$GOAL

## Context
- Re-read relevant files before starting each iteration
- Check what was done in previous iterations (git log, file changes)
- Build incrementally on previous work

## Deliverables
$(echo -e "$GATES" | grep -v "^gates$" | sed 's/^//')

## Quality Gates
Before outputting the completion promise, ALL of these must pass:

EOF

# Add gates as checklist
echo -e "$GATES" | grep -v "^gates$" | while read gate; do
    if [ -n "$gate" ]; then
        echo "- [ ] $gate" >> "$OUTPUT_FILE"
    fi
done

cat >> "$OUTPUT_FILE" << EOF

## Constraints
- Stay in your lane (${HAT} role only)
- Follow existing codebase patterns
- Do not skip quality gates
- If blocked, document the blocker clearly

## Completion
When ALL gates pass and deliverables are complete, output:

\`\`\`
<promise>${PUBLISHES^^}</promise>
\`\`\`

Do NOT output the promise until everything is verified.
EOF

echo "✅ Created prompt: $OUTPUT_FILE"
echo ""
echo "To run this phase:"
echo "   /ralph-loop \"\$(cat $OUTPUT_FILE)\" --completion-promise \"${PUBLISHES^^}\" --max-iterations 25"
