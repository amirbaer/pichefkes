# Ralph Loop - Development Iteration System

**For Claude: Read this file to understand how iterations work in this project.**

---

## What is the Ralph Loop?

The Ralph Loop is a **bash-based iteration system** that runs Claude Code in fresh sessions to complete tasks from a PRD (Product Requirements Document). Named after Ralph Wiggum from The Simpsons, it embodies persistent iteration despite setbacks.

### Why Fresh Sessions Matter

```
Context Window Effectiveness:
├── 0 - 100k tokens:    ✅ HIGH QUALITY - Claude is "smart"
└── 100k - 200k tokens: ❌ DEGRADED - Context rot sets in
```

Each Ralph iteration starts a **new Claude session** with fresh context, avoiding quality degradation. State persists through **files**, not conversation history.

---

## Quick Start

1. **Copy this folder** to your project as `.ralph/`
2. **Update NOTES.md** with your project context
3. **Create a PRD** in `.ralph/runs/run-001-description/prd.json`
4. **Run the loop**: `./.ralph/ralph run`

---

## The Development Cycle

We work in cycles. **Know which stage you're in:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT CYCLE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. DISCUSS & MAP          ←── You are here? Check CYCLE.md    │
│      • Talk with user about bugs/features                        │
│      • Explore codebase to understand scope                      │
│      • Document findings                                         │
│                        ↓                                         │
│   2. DESIGN PRD                                                  │
│      • Convert discussion into structured tasks                  │
│      • Break features into atomic, executable tasks              │
│      • Estimate scope and dependencies                           │
│                        ↓                                         │
│   3. EXECUTE PRD                                                 │
│      • Run ralph loop (./.ralph/ralph run)                       │
│      • Each iteration: pick task → implement → commit            │
│      • Track progress in progress.txt                            │
│                        ↓                                         │
│   4. EVALUATE                                                    │
│      • Review what was accomplished                              │
│      • Test the implementation                                   │
│      • Document learnings                                        │
│                        ↓                                         │
│   5. NEW CYCLE                                                   │
│      • Archive completed PRD                                     │
│      • Start fresh discussion                                    │
│      • Loop back to step 1                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Current cycle stage is tracked in:** `.ralph/CYCLE.md`

---

## Key Files

| File | Purpose | When to Update |
|------|---------|----------------|
| `.ralph/CYCLE.md` | Current stage in development cycle | When moving between stages |
| `.ralph/NOTES.md` | Important user directives & insights | During conversations |
| `.ralph/runs/run-NNN-*/prd.json` | Task list for current iteration | During PRD design |
| `.ralph/runs/run-NNN-*/progress.txt` | Log of what was done each iteration | After each task |

---

## For Claude: How to Work in Each Stage

### Stage 1: DISCUSS & MAP

**Your job:** Understand what the user wants and explore the problem space.

- Listen to bugs, feature requests, and pain points
- Explore relevant code to understand current state
- Ask clarifying questions
- **Document insights in `.ralph/NOTES.md`** - especially:
  - User preferences and constraints
  - Technical decisions made
  - Things NOT to do (learned constraints)
  - Context that won't fit in the PRD

### Stage 2: DESIGN PRD

**Your job:** Convert discussion into actionable tasks.

PRD Format (`prd.json`):
```json
{
  "id": "001",
  "title": "Feature Name",
  "created": "2026-01-23",
  "status": "active",
  "stories": [
    {
      "id": "001",
      "title": "Set up infrastructure",
      "description": "Create the basic project structure",
      "status": "open",
      "dependencies": []
    }
  ]
}
```

**Task Quality Rules:**
- ❌ NO vague tasks: "improve testing"
- ✅ YES specific tasks: "Create Dockerfile for Ubuntu 22.04 with systemd support"
- Each task = one atomic change that can be committed independently

**Milestone Tasks:**
Use milestones for verification checkpoints. Ralph will pause and prompt for manual verification when a milestone completes.

Mark a task as a milestone by:
- Using an ID starting with "M" (e.g., "M01", "M02")
- Setting `"category": "milestone"` in the task
- Including "milestone" in the task title

### Stage 3: EXECUTE PRD

**Your job:** Complete tasks one at a time.

Each iteration:
1. Read `prd.json` - find first task with `status: "open"`
2. Read `progress.txt` - see what was tried before
3. Read `NOTES.md` - remember user constraints
4. Implement the task
5. Mark task `status: "completed"` in PRD
6. Log what you did in `progress.txt`
7. Commit changes

**If a task fails:**
- Document what you tried in `progress.txt`
- Next iteration will see this and try a different approach

### Stage 4: EVALUATE

**Your job:** Review and test.

- Run tests
- Check that features work as expected
- Document any issues found
- Update `NOTES.md` with learnings

### Stage 5: NEW CYCLE

**Your job:** Archive and reset.

1. Move completed PRD to `.ralph/runs/run-NNN-description/`
2. Update `CYCLE.md` to "DISCUSS & MAP"
3. Ready for new conversation

---

## Important: NOTES.md

**This is your memory across iterations.**

The user will give you directives, preferences, and context during conversations. Much of this won't fit in the PRD but is crucial to remember.

**Always update NOTES.md with:**
- User preferences ("I want X, not Y")
- Constraints ("Don't use library Z")
- Decisions made ("We chose approach A because...")
- Context that future Claude needs
- Things that went wrong and why

---

## Quick Reference

### Check Current Stage
```bash
cat .ralph/CYCLE.md
```

### Start Ralph Loop
```bash
./.ralph/ralph run
```

### View Progress
```bash
cat .ralph/runs/run-001-*/progress.txt
```

### View User Notes
```bash
cat .ralph/NOTES.md
```

---

## The Ralph Philosophy

> "Files and git are memory, not the model context."

- State persists through **files**, not conversation
- Each session is **fresh** - no accumulated context noise
- **Document everything** - future you/Claude depends on it
- **Fail gracefully** - log what was tried, let next iteration adapt

---

**Remember:** You're part of a continuous development process. What you document today helps the next iteration succeed tomorrow.
