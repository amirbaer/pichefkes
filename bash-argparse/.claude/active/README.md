# Active Claude State - Coordination System

**Purpose**: Prevent conflicts when multiple Claude instances work simultaneously.

## How It Works

When a Claude starts working on something:
1. Create a file: `claude-<timestamp>.txt`
2. Write one concise line describing the work
3. Delete the file when done

## Format

**Filename**: `claude-YYYYMMDD-HHMMSS.txt`

**Content**: Single line with what you're doing
```
Implementing argument parser core logic
```

## Check Before Starting Work

```bash
ls .claude/active/claude-*.txt
```

If you see other active work that might conflict, either:
- Wait for it to finish
- Confirm with user
- Coordinate to avoid the same files
- Work on a different task

## Cleanup

- **Delete your file** when done (very important!)
- Stale files (>1 hour old) can be safely removed

## Example Workflow

```bash
# Starting work
echo "Adding --help flag implementation" > .claude/active/claude-20260122-143022.txt

# ... do the work ...

# Done
rm .claude/active/claude-20260122-143022.txt
```
