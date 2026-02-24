#!/usr/bin/env python3
"""List all Claude Code sessions across projects with copy-pasteable resume commands."""

import os
import re
import sys
import time


def normalize(name):
    """Normalize a name the same way Claude encodes paths: replace non-alphanumeric with dash."""
    return re.sub(r"[^a-zA-Z0-9]", "-", name)


def decode_project_path(encoded):
    """Walk filesystem to resolve the ambiguous dash-encoded project path."""
    parts = encoded.lstrip("-").split("-")
    resolved = "/"
    i = 0
    while i < len(parts):
        matched = False
        if os.path.isdir(resolved):
            try:
                entries = os.listdir(resolved)
            except PermissionError:
                entries = []
            for end in range(len(parts), i, -1):
                target = "-".join(parts[i:end])
                for entry in entries:
                    if normalize(entry) == target:
                        resolved = os.path.join(resolved, entry)
                        i = end
                        matched = True
                        break
                if matched:
                    break
        if not matched:
            resolved = os.path.join(resolved, parts[i])
            i += 1
    return resolved


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20

    home = os.path.expanduser("~")
    projects_dir = os.path.join(home, ".claude", "projects")

    if not os.path.isdir(projects_dir):
        print("No Claude sessions found.", file=sys.stderr)
        sys.exit(1)

    sessions = []
    for proj in os.listdir(projects_dir):
        proj_path = os.path.join(projects_dir, proj)
        if not os.path.isdir(proj_path):
            continue
        for f in os.listdir(proj_path):
            if f.endswith(".jsonl"):
                fpath = os.path.join(proj_path, f)
                mtime = os.path.getmtime(fpath)
                session_id = f.replace(".jsonl", "")
                decoded = decode_project_path(proj)
                sessions.append((mtime, decoded, session_id))

    use_color = sys.stdout.isatty()

    sessions.sort(reverse=True)
    now = time.time()
    for mtime, proj_dir, sid in sessions[:limit]:
        ts = time.strftime("%b %d %H:%M", time.localtime(mtime))
        age_hours = (now - mtime) / 3600

        if not use_color:
            print(f'{ts}  cd "{proj_dir}" && claude --resume {sid}')
            continue

        # Time color: green <1h, yellow <24h, dim gray older
        if age_hours < 1:
            time_color = "\033[32m"      # green
        elif age_hours < 24:
            time_color = "\033[33m"      # yellow
        else:
            time_color = "\033[90m"      # dim gray

        reset = "\033[0m"
        cyan = "\033[36m"
        white = "\033[97m"
        dim = "\033[90m"

        print(
            f"{time_color}{ts}{reset}  "
            f"{cyan}cd{reset} {white}\"{proj_dir}\"{reset} "
            f"{dim}&&{reset} "
            f"{cyan}claude --resume{reset} {white}{sid}{reset}"
        )


if __name__ == "__main__":
    main()
