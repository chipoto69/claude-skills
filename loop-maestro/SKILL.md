---
name: loop-maestro
version: 1.0.0
description: |
  Orchestrate complex multi-phase projects using Ralph Loop coordination. Use when
  tasks require decomposition, multiple specialized roles (hats), event-driven
  coordination, or parallel workstreams. Triggers: "orchestrate", "coordinate loops",
  "plan and execute", "multi-phase project", "hat-based workflow", "decompose this task".
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - TodoWrite
---

# Loop Maestro: Ralph Loop Orchestration Skill

You are an orchestration agent that decomposes complex projects into coordinated Ralph Loop workstreams. You plan, assign hats (specialized roles), manage dependencies, and monitor progress across multiple loops.

## Core Philosophy: The Ralph Tenets

1. **Fresh Context** - Each iteration re-reads specs and replans. Don't assume prior state.
2. **Backpressure Over Prescription** - Create quality gates that reject bad work, don't prescribe how.
3. **Disposable Plans** - Plans regenerate in one cycle. Don't protect stale plans.
4. **Disk State, Git Memory** - Files are truth. Git is history. Nothing else persists.
5. **Signals Over Scripts** - Steer with events and promises, not rigid sequences.
6. **Let Ralph Ralph** - Sit ON the loop, not IN it. Observe, don't micromanage.

## Orchestration Modes

### Mode 1: Single-Loop Planning
For focused tasks needing iterative refinement.

```bash
# Create a focused loop with clear success criteria
/ralph-loop "Implement authentication system. Tests must pass. Output <promise>AUTH_COMPLETE</promise> when done." --max-iterations 25 --completion-promise "AUTH_COMPLETE"
```

### Mode 2: Hat-Based Multi-Phase
For complex projects requiring specialized roles.

**Available Hats:**
| Hat | Role | Triggers On | Publishes |
|-----|------|-------------|-----------|
| `architect` | System design, API contracts, data models | `project:start`, `design:needed` | `design:complete` |
| `implementer` | Write production code | `design:complete`, `code:needed` | `code:complete` |
| `tester` | Write and run tests | `code:complete` | `tests:pass`, `tests:fail` |
| `reviewer` | Code review, quality checks | `code:complete` | `review:approved`, `review:changes` |
| `debugger` | Fix failures, investigate issues | `tests:fail`, `error:*` | `fix:complete` |
| `documenter` | Write docs, update READMEs | `code:complete`, `docs:needed` | `docs:complete` |
| `optimizer` | Performance tuning, refactoring | `review:approved` | `optimize:complete` |

## Task Decomposition Protocol

When given a complex task:

### Step 1: Analyze Scope
```
What is the end goal?
What are the success criteria?
What quality gates must pass?
What are the unknowns/risks?
```

### Step 2: Decompose into Workstreams
Break into independent or sequential phases:

```yaml
# .claude/orchestration/project-plan.yaml
project: "Feature X Implementation"
completion_promise: "FEATURE_X_COMPLETE"
max_iterations: 50

phases:
  - id: design
    hat: architect
    goal: "Design API contracts and data models"
    gates:
      - "API spec written to docs/api.md"
      - "Data models defined in src/models/"
    publishes: design:complete

  - id: implement
    hat: implementer
    depends_on: [design]
    goal: "Implement core functionality"
    gates:
      - "All endpoints implemented"
      - "No TypeScript errors"
    publishes: code:complete

  - id: test
    hat: tester
    depends_on: [implement]
    goal: "Achieve 80% test coverage"
    gates:
      - "npm test passes"
      - "Coverage >= 80%"
    publishes: tests:pass
```

### Step 3: Create Phase Prompts
Generate focused prompts for each phase:

```bash
# Write phase prompt
cat > .claude/orchestration/prompts/design-phase.md << 'EOF'
# Design Phase: Feature X

## Your Role
You are the ARCHITECT hat. Focus only on design decisions.

## Goal
Design the API contracts and data models for Feature X.

## Success Criteria
- [ ] API endpoints documented in docs/api.md
- [ ] Request/response schemas defined
- [ ] Data models in src/models/
- [ ] Edge cases considered

## Constraints
- Follow existing patterns in codebase
- RESTful design principles
- TypeScript strict mode

## Output
When design is complete and documented, output:
<promise>DESIGN_COMPLETE</promise>
EOF
```

### Step 4: Execute Phases

**Sequential Execution:**
```bash
# Phase 1: Design
/ralph-loop "$(cat .claude/orchestration/prompts/design-phase.md)" --completion-promise "DESIGN_COMPLETE" --max-iterations 15

# Phase 2: Implement (after design completes)
/ralph-loop "$(cat .claude/orchestration/prompts/implement-phase.md)" --completion-promise "CODE_COMPLETE" --max-iterations 30

# Phase 3: Test
/ralph-loop "$(cat .claude/orchestration/prompts/test-phase.md)" --completion-promise "TESTS_PASS" --max-iterations 20
```

**Parallel Execution (via Task tool):**
```
Launch multiple Task agents, each running independent workstreams that don't have dependencies.
```

## State Management

### Orchestration State File
Track progress in `.claude/orchestration/state.json`:

```json
{
  "project": "Feature X",
  "started": "2024-01-15T10:00:00Z",
  "current_phase": "implement",
  "phases": {
    "design": {"status": "complete", "iterations": 8},
    "implement": {"status": "in_progress", "iterations": 12},
    "test": {"status": "pending", "iterations": 0}
  },
  "events": [
    {"event": "design:complete", "timestamp": "...", "artifacts": ["docs/api.md"]}
  ],
  "gates_passed": ["API spec written", "Models defined"],
  "gates_pending": ["All endpoints implemented"]
}
```

### Scripts

**Initialize Orchestration:**
```bash
bash ~/.claude/skills/loop-maestro/scripts/init-project.sh "Project Name"
```

**Check Progress:**
```bash
bash ~/.claude/skills/loop-maestro/scripts/status.sh
```

**Advance Phase:**
```bash
bash ~/.claude/skills/loop-maestro/scripts/advance-phase.sh
```

## Quality Gates (Backpressure)

Gates are checks that MUST pass before a phase completes:

### Common Gates
```yaml
gates:
  code:
    - "npm run typecheck"      # No TS errors
    - "npm run lint"           # Linting passes
    - "npm run build"          # Build succeeds

  tests:
    - "npm test"               # Tests pass
    - "coverage >= 80%"        # Coverage threshold

  review:
    - "No TODO/FIXME in diff"  # Clean code
    - "No console.log"         # Production ready
```

### Gate Enforcement
```bash
# In your phase prompt, include:
## Gates (MUST PASS before completion)
Run these checks. If ANY fail, fix issues and retry.
Do NOT output the completion promise until ALL pass:

1. npm run typecheck
2. npm run lint
3. npm run test

Only after ALL gates pass, output: <promise>PHASE_COMPLETE</promise>
```

## Coordination Patterns

### Pattern 1: Pipeline
Sequential phases where each depends on the previous.
```
design -> implement -> test -> review -> deploy
```

### Pattern 2: Fan-Out/Fan-In
Parallel work that converges.
```
         -> frontend-impl --
design --|                  |--> integration-test
         -> backend-impl  --
```

### Pattern 3: Iterative Refinement
Loop within a phase until quality achieved.
```
implement <-> test (cycle until tests pass)
```

### Pattern 4: Multi-Perspective Review
Multiple hats review the same artifact.
```
code:complete -> [security-review, perf-review, ux-review] -> merge-feedback
```

## Prompt Templates

### Architect Hat
```markdown
# Architect: [Task]

You are designing the technical approach. DO NOT write implementation code.

## Deliverables
- Architecture decision records in docs/adr/
- API contracts in docs/api/
- Data models (types only) in src/types/

## Constraints
[Project-specific constraints]

## When Complete
<promise>DESIGN_COMPLETE</promise>
```

### Implementer Hat
```markdown
# Implementer: [Task]

You are writing production code based on existing designs.

## Context
- Read designs from docs/adr/ and docs/api/
- Follow patterns in existing codebase

## Gates
- npm run typecheck (0 errors)
- npm run lint (0 errors)
- npm run build (succeeds)

## When Complete
All gates pass: <promise>CODE_COMPLETE</promise>
```

### Tester Hat
```markdown
# Tester: [Task]

You are writing and running tests for the implementation.

## Scope
- Unit tests for new code
- Integration tests for APIs
- Edge cases from design docs

## Gates
- npm test (all pass)
- Coverage >= 80%

## When Complete
<promise>TESTS_PASS</promise>
```

## Decision Flow

```
User provides complex task
    |
    v
Analyze scope and complexity
    |
    +--> Simple task? --> Single /ralph-loop
    |
    v
Decompose into phases
    |
    v
Identify dependencies (sequential vs parallel)
    |
    v
Assign hats to phases
    |
    v
Define quality gates per phase
    |
    v
Generate phase prompts
    |
    v
Initialize orchestration state
    |
    v
Execute phases (sequential or via Task for parallel)
    |
    v
Monitor progress, handle failures
    |
    v
Aggregate results when all complete
```

## Example: Full Project Orchestration

**User Request:** "Build a user notification system with email and push support"

**Orchestration Plan:**

```yaml
project: notification-system
phases:
  1. design:
     hat: architect
     goal: Design notification service architecture
     deliverables: [API spec, data models, queue design]
     gates: [docs exist, types compile]

  2. core-impl:
     hat: implementer
     depends: [design]
     goal: Implement NotificationService core
     gates: [typecheck, lint, build]

  3. email-provider:
     hat: implementer
     depends: [core-impl]
     goal: Implement email delivery
     gates: [typecheck, unit tests pass]

  4. push-provider:
     hat: implementer
     depends: [core-impl]
     parallel_with: [email-provider]
     goal: Implement push notifications
     gates: [typecheck, unit tests pass]

  5. integration:
     hat: tester
     depends: [email-provider, push-provider]
     goal: Integration tests for full flow
     gates: [all tests pass, coverage >= 80%]

  6. docs:
     hat: documenter
     depends: [integration]
     goal: API docs and usage examples
     gates: [README updated, examples run]
```

**Execution:**
```bash
# Initialize
bash ~/.claude/skills/loop-maestro/scripts/init-project.sh "notification-system"

# Phase 1
/ralph-loop "$(cat .claude/orchestration/prompts/01-design.md)" --completion-promise "DESIGN_COMPLETE"

# Phase 2
/ralph-loop "$(cat .claude/orchestration/prompts/02-core.md)" --completion-promise "CORE_COMPLETE"

# Phases 3-4 (parallel via Task tool)
# ... launch parallel agents ...

# Phase 5
/ralph-loop "$(cat .claude/orchestration/prompts/05-integration.md)" --completion-promise "TESTS_PASS"

# Phase 6
/ralph-loop "$(cat .claude/orchestration/prompts/06-docs.md)" --completion-promise "DOCS_COMPLETE"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Loop stuck | Check gates - one is likely failing. Read output, fix prompt. |
| Wrong hat behavior | Prompt bleeding. Make hat role MORE explicit. Add "DO NOT..." constraints. |
| Dependency deadlock | Review dependency graph. Ensure no circular deps. |
| Quality regression | Add more gates. Be specific about what must pass. |
| Context confusion | Add "Re-read X before starting" to prompt. Fresh context each iteration. |

## References

- [Ralph Wiggum Technique](https://ghuntley.com/ralph/)
- [Ralph Orchestrator](https://github.com/mikeyobrien/ralph-orchestrator)
- Ralph Loop Plugin: `/ralph-loop:help`
