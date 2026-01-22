#!/usr/bin/env python3
"""
Ralph Loop Runner
Runs Claude Code iterations with automatic commits after each task.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════════════

class Colors:
    PINK = '\033[38;5;218m'
    LAVENDER = '\033[38;5;183m'
    MINT = '\033[38;5;158m'
    PEACH = '\033[38;5;216m'
    SKY = '\033[38;5;117m'
    CORAL = '\033[38;5;210m'
    SAGE = '\033[38;5;151m'
    YELLOW = '\033[38;5;221m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    NC = '\033[0m'

C = Colors

# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def get_project_dir():
    """Get project directory (parent of bin/)."""
    return Path(__file__).resolve().parent.parent

def get_project_name(project_dir: Path) -> str:
    """Get project name from directory name."""
    return project_dir.name

def find_prd_file(project_dir: Path) -> Path | None:
    """Find the active PRD file."""
    ralph_dir = project_dir / ".ralph"

    # Look for prd-NNN.json files, sorted by number descending
    prd_files = list(ralph_dir.glob("prd-*.json"))
    if prd_files:
        prd_files.sort(key=lambda p: p.stem, reverse=True)
        return prd_files[0]

    # Fallback to prd.json
    prd_file = ralph_dir / "prd.json"
    if prd_file.exists():
        return prd_file

    return None

def load_prd(prd_file: Path) -> dict:
    """Load PRD JSON file."""
    with open(prd_file) as f:
        return json.load(f)

def save_prd(prd_file: Path, prd: dict):
    """Save PRD JSON file."""
    with open(prd_file, 'w') as f:
        json.dump(prd, f, indent=2)
        f.write('\n')

def get_prd_title(prd: dict) -> str:
    """Get PRD title."""
    return prd.get('title', 'Untitled PRD')

def count_tasks_by_status(prd: dict) -> dict:
    """Count tasks by status."""
    counts = {'open': 0, 'completed': 0, 'total': 0}
    for story in prd.get('stories', []):
        status = story.get('status', 'open')
        counts[status] = counts.get(status, 0) + 1
        counts['total'] += 1
    return counts

def get_completed_task_ids(prd: dict) -> set:
    """Get set of completed task IDs."""
    return {s['id'] for s in prd.get('stories', []) if s.get('status') == 'completed'}

def deps_met(story: dict, completed_ids: set) -> bool:
    """Check if all dependencies are met."""
    for dep in story.get('dependencies', []):
        if dep not in completed_ids:
            return False
    return True

def get_open_tasks(prd: dict) -> list:
    """Get list of open tasks with dependency status."""
    completed_ids = get_completed_task_ids(prd)
    tasks = []
    for story in prd.get('stories', []):
        if story.get('status') == 'open':
            ready = deps_met(story, completed_ids)
            tasks.append({
                'id': story['id'],
                'title': story['title'],
                'ready': ready,
            })
    return tasks

def get_next_task(prd: dict) -> dict | None:
    """Get next available task (open with deps met)."""
    completed_ids = get_completed_task_ids(prd)
    for story in prd.get('stories', []):
        if story.get('status') == 'open' and deps_met(story, completed_ids):
            return story
    return None

def get_cycle_stage(project_dir: Path) -> str:
    """Get current cycle stage from CYCLE.md."""
    cycle_file = project_dir / ".ralph" / "CYCLE.md"
    if not cycle_file.exists():
        return "Unknown"

    content = cycle_file.read_text()
    for line in content.split('\n'):
        if 'STAGE' in line and '▶' in line:
            # Extract stage name
            stage = line.split('▶')[-1].strip()
            stage = stage.replace('║', '').strip()
            return stage
    return "Unknown"

def run_command(cmd: list, cwd: Path = None, capture: bool = True) -> tuple:
    """Run a command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr

def git_has_changes(project_dir: Path) -> bool:
    """Check if there are uncommitted changes."""
    run_command(['git', 'add', '-A', '.'], cwd=project_dir)
    code, _, _ = run_command(['git', 'diff', '--staged', '--quiet'], cwd=project_dir)
    return code != 0

def git_commit(project_dir: Path, message: str):
    """Commit staged changes."""
    run_command(['git', 'add', '-A', '.'], cwd=project_dir)
    run_command(['git', 'commit', '-m', message, '--quiet'], cwd=project_dir)

def git_rev_parse(project_dir: Path) -> str:
    """Get current commit hash."""
    code, stdout, _ = run_command(['git', 'rev-parse', 'HEAD'], cwd=project_dir)
    return stdout.strip() if code == 0 else 'none'

def git_commit_count(project_dir: Path, from_hash: str, to_hash: str) -> int:
    """Count commits between two hashes."""
    code, stdout, _ = run_command(
        ['git', 'rev-list', '--count', f'{from_hash}..{to_hash}'],
        cwd=project_dir
    )
    return int(stdout.strip()) if code == 0 else 0

def git_log_recent(project_dir: Path, count: int = 10) -> list:
    """Get recent commits."""
    code, stdout, _ = run_command(
        ['git', 'log', '--oneline', f'-{count}'],
        cwd=project_dir
    )
    return stdout.strip().split('\n') if code == 0 and stdout.strip() else []

# ═══════════════════════════════════════════════════════════════════
# DISPLAY
# ═══════════════════════════════════════════════════════════════════

def print_header(project_name: str):
    """Print the Ralph header."""
    print()
    print(f"{C.SKY}  ┌─────────────────────────────────────────────────────────┐{C.NC}")
    print(f"{C.SKY}  │{C.NC}     {C.PINK}{project_name}{C.NC} {C.DIM}~ Ralph Loop Runner{C.NC}".ljust(68) + f"{C.SKY}│{C.NC}")
    print(f"{C.SKY}  └─────────────────────────────────────────────────────────┘{C.NC}")
    print()

def print_task_list(tasks: list, indent: str = "  "):
    """Print list of tasks with status indicators."""
    for task in tasks:
        indicator = '→' if task['ready'] else '⏸'
        print(f"{indent}{indicator} {task['id']}: {task['title']}")

def print_completed_tasks(prd: dict, indent: str = "    "):
    """Print completed tasks."""
    for story in prd.get('stories', []):
        if story.get('status') == 'completed':
            print(f"{indent}✓ {story['id']}: {story['title']}")

# ═══════════════════════════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════════════════════════

def cmd_info(args, project_dir: Path, prd_file: Path, prd: dict):
    """Show current cycle status and PRD details."""
    counts = count_tasks_by_status(prd)

    print(f"  {C.BOLD}{C.LAVENDER}Current Cycle{C.NC}")
    print()

    # Cycle stage
    stage = get_cycle_stage(project_dir)
    print(f"  {C.DIM}Stage{C.NC}         {C.MINT}{stage}{C.NC}")

    # PRD info
    print(f"  {C.DIM}PRD{C.NC}           {C.SAGE}{get_prd_title(prd)}{C.NC}")
    print(f"  {C.DIM}File{C.NC}          {C.SAGE}{prd_file.name}{C.NC}")
    print(f"  {C.DIM}Progress{C.NC}      {C.SAGE}{counts['completed']}{C.NC}{C.DIM}/{C.NC}{C.SAGE}{counts['total']}{C.NC} {C.DIM}tasks completed{C.NC}")
    print()

    # Tasks
    print(f"  {C.BOLD}{C.LAVENDER}Tasks{C.NC}")
    print()

    if counts['completed'] > 0:
        print(f"  {C.DIM}Completed:{C.NC}")
        print_completed_tasks(prd)
        print()

    open_tasks = get_open_tasks(prd)
    if open_tasks:
        print(f"  {C.DIM}Open:{C.NC} {C.DIM}(→ ready, ⏸ blocked){C.NC}")
        print_task_list(open_tasks)
        print()

    # Notes reference
    notes_file = project_dir / ".ralph" / "NOTES.md"
    if notes_file.exists():
        print(f"  {C.BOLD}{C.LAVENDER}Key Notes{C.NC}")
        print()
        print(f"  {C.DIM}See full notes:{C.NC} {C.SAGE}cat .ralph/NOTES.md{C.NC}")
        print()

    # History
    if args.history:
        print(f"  {C.BOLD}{C.LAVENDER}Previous Iterations{C.NC}")
        print()

        runs_dir = project_dir / ".ralph" / "runs"
        if runs_dir.exists() and any(runs_dir.iterdir()):
            for run_dir in sorted(runs_dir.iterdir()):
                if run_dir.is_dir() and not run_dir.name.startswith('.'):
                    print(f"  {C.MINT}▸ {run_dir.name}{C.NC}")

                    manifest = run_dir / "MANIFEST.md"
                    if manifest.exists():
                        content = manifest.read_text()
                        for i, line in enumerate(content.split('\n')):
                            if '## Summary' in line:
                                lines = content.split('\n')
                                if i + 2 < len(lines):
                                    summary = lines[i + 2].strip()
                                    if summary:
                                        print(f"    {C.DIM}{summary}{C.NC}")
                                break

                    prd_file_run = run_dir / "prd.json"
                    if prd_file_run.exists():
                        try:
                            run_prd = load_prd(prd_file_run)
                            task_count = len(run_prd.get('stories', []))
                            print(f"    {C.DIM}Tasks: {task_count}{C.NC}")
                        except:
                            pass
                    print()
        else:
            print(f"  {C.DIM}No previous iterations found{C.NC}")
            print()

        # Recent commits
        print(f"  {C.BOLD}{C.LAVENDER}Recent Commits{C.NC}")
        print()
        commits = git_log_recent(project_dir)
        for commit in commits:
            if commit:
                print(f"  {C.DIM}{commit}{C.NC}")
        print()

def cmd_add(args, project_dir: Path, prd_file: Path, prd: dict):
    """Add a bug or feature request via Claude."""
    issue_text = ' '.join(args.add)
    project_name = get_project_name(project_dir)

    print(f"  {C.LAVENDER}Processing issue with Claude...{C.NC}")
    print()

    notes_file = project_dir / ".ralph" / "NOTES.md"

    prompt = f'''You are adding a bug or feature request to the {project_name} project.

## Issue to Add
"{issue_text}"

## Instructions

1. Read the current PRD: {prd_file}
2. Read the NOTES file: {notes_file}
3. Determine if this is a BUG or FEATURE REQUEST based on the description
4. Create an appropriate task entry for the PRD with:
   - Unique ID (next available number)
   - Clear title
   - Detailed description
   - Dependencies if applicable
   - Status: "open"
5. Add the task to the PRD JSON file
6. If this contains important context or user preferences, also add to NOTES.md
7. Summarize what you added

Be concise. Just add the issue and confirm.
'''

    result = subprocess.run(
        ['claude', '--print', str(project_dir)],
        input=prompt,
        capture_output=False,
        text=True,
    )

    print()
    print(f"  {C.MINT}✓ Issue processed{C.NC}")
    print()

def cmd_run(args, project_dir: Path, prd_file: Path, prd: dict):
    """Run the Ralph loop."""
    project_name = get_project_name(project_dir)
    counts = count_tasks_by_status(prd)
    open_tasks = get_open_tasks(prd)
    next_task = get_next_task(prd)

    # Show plan
    print(f"  {C.BOLD}{C.LAVENDER}PRD:{C.NC} {C.SAGE}{get_prd_title(prd)}{C.NC}")
    print(f"  {C.DIM}File:{C.NC} {C.SAGE}{prd_file.name}{C.NC}")
    print()
    print(f"  {C.BOLD}{C.LAVENDER}Configuration:{C.NC}")
    print(f"  {C.DIM}Project{C.NC}       {C.SAGE}{project_dir}{C.NC}")
    print(f"  {C.DIM}Max iters{C.NC}     {C.SAGE}{args.max_iterations}{C.NC}")
    print(f"  {C.DIM}Tasks open{C.NC}    {C.SAGE}{counts['open']}{C.NC}")
    print()

    if counts['open'] == 0:
        print(f"  {C.MINT}✓ All tasks already complete!{C.NC}")
        print()
        return

    print(f"  {C.BOLD}{C.LAVENDER}Open Tasks:{C.NC} {C.DIM}(→ ready, ⏸ waiting on deps){C.NC}")
    print_task_list(open_tasks)
    print()

    if next_task:
        print(f"  {C.BOLD}{C.YELLOW}First task to execute:{C.NC}")
        print(f"  {C.MINT}▸ {next_task['id']}{C.NC} {C.SAGE}{next_task['title']}{C.NC}")
        print()
    else:
        print(f"  {C.CORAL}✗ No tasks available (check dependencies){C.NC}")
        print()
        return

    # Confirmation
    if not args.yes:
        print(f"  {C.SKY}─────────────────────────────────────────────────────────{C.NC}")
        print()
        print(f"  {C.YELLOW}Ready to start Ralph loop.{C.NC}")
        print(f"  {C.DIM}This will run Claude Code up to {args.max_iterations} times.{C.NC}")
        print()

        try:
            reply = input("  Proceed? [y/N] ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()
            print()
            print(f"  {C.PEACH}Cancelled.{C.NC}")
            print()
            return

        print()

        if reply not in ('y', 'yes'):
            print(f"  {C.PEACH}Cancelled.{C.NC}")
            print()
            return

    # Setup
    progress_file = project_dir / ".ralph" / "progress.txt"
    notes_file = project_dir / ".ralph" / "NOTES.md"

    if not progress_file.exists():
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(
            "# Progress Log\n\n"
            "_This file is automatically updated after each Ralph iteration._\n\n"
            "---\n\n"
        )

    # Commit any uncommitted changes
    if git_has_changes(project_dir):
        print(f"  {C.PEACH}Found uncommitted changes from previous run{C.NC}")
        git_commit(
            project_dir,
            f"[{project_name}] Recover uncommitted changes from previous run\n\n"
            "Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
        )
        print(f"  {C.MINT}✓ Previous changes committed{C.NC}")
        print()

    # Main loop
    for i in range(1, args.max_iterations + 1):
        # Reload PRD each iteration
        prd = load_prd(prd_file)
        counts = count_tasks_by_status(prd)
        next_task = get_next_task(prd)

        print(f"  {C.SKY}─────────────────────────────────────────────────────────{C.NC}")
        print()
        print(f"  {C.LAVENDER}Iteration {C.PINK}{i}{C.LAVENDER} of {C.PINK}{args.max_iterations}{C.NC}    {C.DIM}remaining: {counts['open']} tasks{C.NC}")

        if counts['open'] == 0:
            print(f"  {C.MINT}✓ All tasks complete{C.NC}")
            print()
            break

        if not next_task:
            print(f"  {C.CORAL}✗ No available tasks (check dependencies){C.NC}")
            print()
            break

        print(f"  {C.MINT}▸ {next_task['id']}{C.NC} {C.SAGE}{next_task['title']}{C.NC}")
        print()

        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_before = git_rev_parse(project_dir)

        # Run Claude
        prompt = f'''You are working on the {project_name} project.

## Instructions

1. Read the PRD file: {prd_file}
2. Read progress file: {progress_file}
3. Read notes file: {notes_file} (important user constraints!)
4. Find the FIRST task with status "open" whose dependencies are all "completed"
5. Work on that ONE task completely
6. When done:
   - Update the PRD: change the task's status from "open" to "completed"
   - Append to progress.txt what you did, including:
     - Task ID and title
     - What was accomplished
     - Any files created/modified
     - Any issues encountered
   - Make sure all your work is saved to files

## Important Rules

- Complete ONE task per iteration, then stop
- Read NOTES.md for user constraints
- Create all necessary directories and files
- Write working, tested code
- Update both the PRD AND progress.txt before finishing
- If a task cannot be completed, document why in progress.txt and move on

Start by reading the PRD and progress files, then work on the next available task.
'''

        print(f"  {C.DIM}Claude is working on task {next_task['id']}...{C.NC}")

        result = subprocess.run(
            ['claude', '--print', '--dangerously-skip-permissions', str(project_dir)],
            input=prompt,
            capture_output=True,
            text=True,
        )

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"  {C.DIM}Completed at {end_time}{C.NC}")
        print()

        # Check commits
        commit_after = git_rev_parse(project_dir)

        if commit_before != commit_after and commit_before != 'none':
            commits_made = git_commit_count(project_dir, commit_before, commit_after)
            print(f"  {C.MINT}✓ Claude made {commits_made} commit(s){C.NC}")

        # Commit any remaining changes
        if git_has_changes(project_dir):
            git_commit(
                project_dir,
                f"[{project_name}] Iteration {i}: {next_task['title']}\n\n"
                f"Task: {next_task['id']}\n"
                f"Time: {start_time} - {end_time}\n\n"
                "Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
            )
            print(f"  {C.MINT}✓ Additional changes committed{C.NC}")
        elif commit_before == commit_after:
            print(f"  {C.PEACH}○ No changes{C.NC}")

        print()
        time.sleep(1)

    # Summary
    prd = load_prd(prd_file)
    counts = count_tasks_by_status(prd)

    print(f"  {C.SKY}─────────────────────────────────────────────────────────{C.NC}")
    print()
    print(f"  {C.LAVENDER}Loop complete{C.NC}")
    print(f"  {C.DIM}Iterations:{C.NC} {C.SAGE}{i}{C.NC}    {C.DIM}Remaining:{C.NC} {C.SAGE}{counts['open']}{C.NC}")
    print()
    print(f"  {C.PEACH}Don't forget to push:{C.NC} {C.DIM}git push{C.NC}")
    print()

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Ralph Loop Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  ./bin/ralph.sh           # Run with confirmation
  ./bin/ralph.sh -y        # Skip confirmation
  ./bin/ralph.sh -y 10     # 10 iterations, no confirm
  ./bin/ralph.sh 20        # 20 iterations with confirm
  ./bin/ralph.sh -i        # Show current status
  ./bin/ralph.sh -iH       # Show status with history
  ./bin/ralph.sh -a "bug description"
  ./bin/ralph.sh -a "FR: add new feature"
'''
    )

    parser.add_argument('-y', '--yes', action='store_true',
                        help='Skip confirmation prompt')
    parser.add_argument('-i', '--info', action='store_true',
                        help='Show current cycle status and PRD details')
    parser.add_argument('-H', '--history', action='store_true',
                        help='Include previous iteration history (use with -i)')
    parser.add_argument('-a', '--add', nargs='+', metavar='DESC',
                        help='Add a bug or feature request (processed by Claude)')
    parser.add_argument('max_iterations', nargs='?', type=int, default=20,
                        help='Maximum iterations (default: 20)')

    args = parser.parse_args()

    # Setup
    project_dir = get_project_dir()
    project_name = get_project_name(project_dir)
    prd_file = find_prd_file(project_dir)

    # Header
    print_header(project_name)

    # Validate PRD
    if not prd_file:
        if args.info or args.history:
            print(f"  {C.PEACH}No PRD file found{C.NC}")
            print(f"  {C.DIM}Create one at: .ralph/prd.json{C.NC}")
            print()

            # Still show cycle stage
            stage = get_cycle_stage(project_dir)
            print(f"  {C.DIM}Current stage:{C.NC} {C.MINT}{stage}{C.NC}")
            print()
            return
        else:
            print(f"  {C.CORAL}Error: No PRD file found{C.NC}")
            print(f"  {C.DIM}Create one at: .ralph/prd.json{C.NC}")
            print()
            sys.exit(1)

    prd = load_prd(prd_file)

    # Route to command
    if args.add:
        cmd_add(args, project_dir, prd_file, prd)
    elif args.info or args.history:
        cmd_info(args, project_dir, prd_file, prd)
    else:
        cmd_run(args, project_dir, prd_file, prd)

if __name__ == '__main__':
    main()
