# Development Cycle Status

**For Claude: Check this file to know which stage of the development cycle we're in.**

---

## Current Stage

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ▶ STAGE 3: EXECUTE PRD                                     ║
║                                                               ║
║   PRD is ready. Run ./bin/ralph.sh to execute tasks.          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Current PRD:** `prd.json` (bashargparse - Bash Implementation of argparse)

---

## Stage Details

| Stage | Status | Description |
|-------|--------|-------------|
| 1. DISCUSS & MAP | ✅ Done | Requirements gathered from user |
| 2. DESIGN PRD | ✅ Done | PRD created with 15 tasks |
| 3. EXECUTE PRD | ◀ Current | Ready to run ralph loop |
| 4. EVALUATE | ⏳ Pending | Test and review results |
| 5. NEW CYCLE | ⏳ Pending | Archive and start fresh |

---

## Cycle History

### Cycle 1 (Current) - bashargparse Implementation
- **Started:** 2026-01-22
- **Focus:** Create bash implementation of Python's argparse
- **PRD:** prd.json (15 tasks)
- **Status:** Ready to execute

---

## What to Do in Each Stage

### If Stage 1 (DISCUSS & MAP)
- Explore requirements with user
- Document insights in NOTES.md
- Don't start coding yet

### If Stage 2 (DESIGN PRD)
- Convert discussion into structured tasks
- Create/update prd.json
- Each task should be atomic and specific

### If Stage 3 (EXECUTE PRD) <- YOU ARE HERE
- Run: `./bin/ralph.sh`
- Or manually: Read prd.json, work on next open task
- Read NOTES.md for constraints
- Implement, commit, update progress.txt

### If Stage 4 (EVALUATE)
- Run tests
- Review what was accomplished
- Document learnings in NOTES.md

### If Stage 5 (NEW CYCLE)
- Archive PRD to runs/run-NNN/
- Update this file to Stage 1
- Ready for new discussion

---

## Quick Commands

```bash
# Run ralph loop
./bin/ralph.sh

# Show status
./bin/ralph.sh -i

# View PRD
cat .ralph/prd.json

# View notes
cat .ralph/NOTES.md
```

---

**Last Updated:** 2026-01-22
