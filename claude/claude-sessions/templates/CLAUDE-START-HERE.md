# Claude Start Here - {PROJECT_NAME}

**Read this file at the beginning of every Claude session.**

---

## Quick Context

**What is this project?**
{One paragraph description of the project}

**Current State:**
{Brief summary of where the project is - what's working, what's in progress}

**Primary Goal:**
{What we're trying to accomplish}

---

## Repository Structure

```
{project}/
├── {folder1}/          # {description}
├── {folder2}/          # {description}
├── .claude/            # Claude context and coordination
│   ├── active/         # Lock files for multi-instance coordination
│   └── sessions/       # Session documentation
└── {etc}
```

---

## Quick Start for Claude

### 1. Check for Active Work
```bash
ls .claude/active/claude-*.txt
```
If files exist, coordinate or wait.

### 2. Read Recent Context
```bash
ls -lt .claude/sessions/ | head -3
```
Read the most recent session log for context.

### 3. Create Your Lock
```bash
echo "Working on {task}" > .claude/active/claude-$(date +%Y%m%d-%H%M%S).txt
```

### 4. When Done
- Document session in `.claude/sessions/`
- Remove your lock file

---

## Core Concepts

### {Concept 1}
{Explanation}

### {Concept 2}
{Explanation}

---

## Common Tasks

### {Task 1 - e.g., "Run Tests"}
```bash
{command}
```

### {Task 2 - e.g., "Build Project"}
```bash
{command}
```

---

## Current Work

### In Progress
- {task 1}
- {task 2}

### Blocked On
- {blocker if any}

### Recently Completed
- {recent completion}

---

## User Preferences

- {preference 1 - e.g., "Prefer simple solutions over clever ones"}
- {preference 2 - e.g., "Always run tests before committing"}
- {preference 3}

---

## Important Files

| File | Purpose | When to Read |
|------|---------|--------------|
| `{path}` | {purpose} | {when} |
| `{path}` | {purpose} | {when} |

---

## Don't Forget

- [ ] Check for active Claude sessions before starting
- [ ] Document your session before ending
- [ ] Remove your lock file when done
- [ ] {project-specific reminder}

---

## Getting Help

- **Project docs**: `{path to docs}`
- **Session logs**: `.claude/sessions/`
- **Ask user**: When in doubt, ask!

---

*Last updated: {date}*
