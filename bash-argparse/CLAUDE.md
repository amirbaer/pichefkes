# bashargparse - Claude Context

**Read this file first when starting any session.**

---

## Starting a Session

### 1. Check for Other Active Claudes

```bash
ls .claude/active/claude-*.txt
```

If other Claudes are working, read their files to avoid conflicts.

### 2. Register Your Work

```bash
echo "Your task description" > .claude/active/claude-$(date +%Y%m%d-%H%M%S).txt
```

**Delete this file when done.**

### 3. Check Development Cycle Stage

```bash
cat .ralph/CYCLE.md
```

Then read:
- `.ralph/NOTES.md` - User directives and constraints
- `.ralph/prd.json` - Current task list (if in execute stage)

---

## Project Overview

bashargparse - (Add project description here)

---

## Key Files

| File | Purpose |
|------|---------|
| `.claude/active/README.md` | Multi-Claude coordination |
| `.ralph/README.md` | How the iteration system works |
| `.ralph/NOTES.md` | User directives & constraints |
| `.ralph/CYCLE.md` | Current development stage |

---

## Development Cycle

```
1. DISCUSS & MAP  -> Talk with user, explore, document in NOTES.md
2. DESIGN PRD     -> Convert discussion into structured tasks
3. EXECUTE PRD    -> Run ralph loop (./bin/ralph.sh)
4. EVALUATE       -> Test, review, document learnings
5. NEW CYCLE      -> Archive and start fresh
```

Check current stage: `cat .ralph/CYCLE.md`

---

## Quick Commands

```bash
# Check cycle stage
cat .ralph/CYCLE.md

# View notes
cat .ralph/NOTES.md

# Run ralph loop
./bin/ralph.sh

# Show status
./bin/ralph.sh -i
```

---

## Remember

- Check for active Claudes before starting
- Register your work in `.claude/active/`
- Read NOTES.md for user constraints
- Delete your active file when done
