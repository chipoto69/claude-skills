#!/bin/bash
# Initialize orchestration for a new project
set -e

PROJECT_NAME="${1:-Unnamed Project}"
PROJECT_DIR="${2:-.}"

ORCH_DIR="$PROJECT_DIR/.claude/orchestration"
STATE_FILE="$ORCH_DIR/state.json"
PROMPTS_DIR="$ORCH_DIR/prompts"
PLAN_FILE="$ORCH_DIR/project-plan.yaml"

echo "🎭 Loop Maestro: Initializing orchestration"
echo "   Project: $PROJECT_NAME"
echo "   Directory: $PROJECT_DIR"

# Create directories
mkdir -p "$ORCH_DIR" "$PROMPTS_DIR"

# Initialize state file
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << EOF
{
  "project": "$PROJECT_NAME",
  "started": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "current_phase": null,
  "total_iterations": 0,
  "phases": {},
  "events": [],
  "gates_passed": [],
  "gates_pending": []
}
EOF
    echo "✅ Created state file: $STATE_FILE"
else
    echo "⚠️  State file already exists: $STATE_FILE"
fi

# Create plan template if not exists
if [ ! -f "$PLAN_FILE" ]; then
    cat > "$PLAN_FILE" << 'EOF'
# Project Orchestration Plan
# Edit this file to define your project phases

project: "PROJECT_NAME"
completion_promise: "PROJECT_COMPLETE"
max_iterations: 100

# Define phases in execution order
phases:
  - id: design
    hat: architect
    goal: "Design system architecture and API contracts"
    depends_on: []
    gates:
      - "Architecture documented"
      - "API spec complete"
    publishes: design:complete

  - id: implement
    hat: implementer
    goal: "Implement core functionality"
    depends_on: [design]
    gates:
      - "Code compiles/typechecks"
      - "Linting passes"
    publishes: code:complete

  - id: test
    hat: tester
    goal: "Write and run tests"
    depends_on: [implement]
    gates:
      - "All tests pass"
      - "Coverage threshold met"
    publishes: tests:pass

  - id: review
    hat: reviewer
    goal: "Code review and quality check"
    depends_on: [test]
    gates:
      - "No critical issues"
      - "Documentation complete"
    publishes: review:approved

# Hat definitions (customize prompts as needed)
hats:
  architect:
    focus: "System design, API contracts, data models"
    avoid: "Writing implementation code"

  implementer:
    focus: "Production code following designs"
    avoid: "Changing architectural decisions"

  tester:
    focus: "Test coverage, edge cases, reliability"
    avoid: "Changing implementation logic"

  reviewer:
    focus: "Code quality, security, maintainability"
    avoid: "Rewriting code (suggest changes only)"
EOF
    sed -i '' "s/PROJECT_NAME/$PROJECT_NAME/" "$PLAN_FILE" 2>/dev/null || \
    sed -i "s/PROJECT_NAME/$PROJECT_NAME/" "$PLAN_FILE"
    echo "✅ Created plan template: $PLAN_FILE"
else
    echo "⚠️  Plan file already exists: $PLAN_FILE"
fi

# Create a README for the orchestration directory
cat > "$ORCH_DIR/README.md" << 'EOF'
# Orchestration Directory

This directory contains Loop Maestro orchestration files.

## Files

- `state.json` - Current orchestration state (auto-updated)
- `project-plan.yaml` - Project phases and configuration
- `prompts/` - Phase-specific prompts

## Usage

1. Edit `project-plan.yaml` to define your phases
2. Generate prompts: `bash ~/.claude/skills/loop-maestro/scripts/create-phase-prompt.sh <phase-id>`
3. Check status: `bash ~/.claude/skills/loop-maestro/scripts/status.sh`
4. Run phases with `/ralph-loop`

## Do Not Edit

- `state.json` is managed automatically
- Commit `project-plan.yaml` and `prompts/` to git
EOF

echo ""
echo "🎭 Orchestration initialized!"
echo ""
echo "Next steps:"
echo "  1. Edit $PLAN_FILE to define your phases"
echo "  2. Generate phase prompts with:"
echo "     bash ~/.claude/skills/loop-maestro/scripts/create-phase-prompt.sh <phase-id>"
echo "  3. Start orchestration with /ralph-loop using generated prompts"
echo ""
