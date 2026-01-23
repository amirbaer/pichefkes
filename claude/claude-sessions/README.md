# Claude Session Coordination System

A lightweight system for coordinating multiple Claude Code instances and documenting work across sessions.

## Purpose

1. **Prevent conflicts** when multiple Claude instances work simultaneously
2. **Document sessions** for future Claude instances to understand context
3. **Enable fast context reload** at the start of new sessions

---

## Quick Start

### To use in your project:

1. Copy this folder to your project as `.claude/`
2. At session start, check for active work: `ls .claude/active/claude-*.txt`
3. Before starting work, create a lock file
4. Document your session before ending

---

## Directory Structure

```
.claude/
├── README.md              # This file
├── active/                # Coordination locks (prevent conflicts)
│   └── README.md          # How to use lock files
├── sessions/              # Session documentation
│   └── YYYY-MM-DD_description.md
└── templates/
    └── SESSION_LOG.md     # Template for session documentation
```

---

## Components

### 1. Active Coordination (`active/`)

Prevents multiple Claude instances from conflicting by using simple lock files.

**How it works:**
- When starting work, create: `active/claude-YYYYMMDD-HHMMSS.txt`
- Write a one-line description of what you're doing
- Delete the file when done

**Check before starting:**
```bash
ls .claude/active/claude-*.txt
```

See `active/README.md` for full details.

### 2. Session Documentation (`sessions/`)

Log what was done in each session for future Claude instances.

**Naming convention:** `YYYY-MM-DD_brief-description.md`

**Contents:**
- Context at session start
- What was accomplished
- Key decisions made
- Artifacts created/modified
- Recommendations for next session

See `templates/SESSION_LOG.md` for the full template.

---

## For Claude: Session Workflow

### At Session Start

1. **Check for active work:**
   ```bash
   ls .claude/active/claude-*.txt
   ```
   If files exist, coordinate or wait.

2. **Read recent sessions:**
   ```bash
   ls -lt .claude/sessions/ | head -5
   ```
   Read the most recent for context.

3. **Create your lock file:**
   ```bash
   echo "Working on feature X" > .claude/active/claude-$(date +%Y%m%d-%H%M%S).txt
   ```

### During Session

- Keep your lock file updated if scope changes
- Note important decisions for the session log

### At Session End

1. **Document the session:**
   Create `.claude/sessions/YYYY-MM-DD_description.md`
   Use the template in `templates/SESSION_LOG.md`

2. **Remove your lock file:**
   ```bash
   rm .claude/active/claude-*.txt
   ```

---

## Best Practices

### For Coordination

- **Always check** for active work before starting
- **Be specific** in lock file descriptions
- **Delete promptly** when done
- **Stale files** (>1 hour) can be safely removed

### For Documentation

- **Write for future Claude**, not for yourself
- **Capture the "why"**, not just the "what"
- **Include context** that won't be obvious from code
- **Note user preferences** expressed during session

---

## Integration with Ralph

If using the Ralph Loop system:

- **Ralph runs** are tracked in `.ralph/runs/`
- **Session docs** go here in `.claude/sessions/`
- Ralph handles task execution; this handles session context
- Document Ralph run progress in session logs

---

## Files in This Package

```
claude-sessions/
├── README.md              # This documentation
├── active/
│   └── README.md          # Active coordination guide
├── sessions/
│   └── .gitkeep           # Placeholder
└── templates/
    └── SESSION_LOG.md     # Session documentation template
```

---

## Customization

### Add Project-Specific Context

Create additional files as needed:
- `CONTEXT_INDEX.md` - Quick index of important files
- `PROJECT_SUMMARY.md` - Current state overview
- `DECISIONS.md` - Architectural decisions log

### Integrate with Your Workflow

The coordination system is flexible:
- Add more lock file metadata if needed
- Extend session template for your domain
- Add automation scripts if desired

---

**Remember:** The goal is to make every Claude session productive by preserving context and preventing conflicts.
