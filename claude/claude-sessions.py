#!/usr/bin/env python3
"""List all Claude Code sessions across projects with copy-pasteable resume commands."""

import argparse
import json
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


def _parse_user_msg(obj):
    """Extract cleaned text from a user message object."""
    content = obj.get("message", {}).get("content", "")
    if isinstance(content, list):
        content = " ".join(
            b.get("text", "") for b in content if b.get("type") == "text"
        )
    msg = content.strip().split("\n")[0].strip()
    msg = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", msg)
    msg = re.sub(r"^[➜$#>]\s*", "", msg)
    msg = re.sub(r"^\S+\s+git:\(.*?\)\s*[✗✓]*\s*", "", msg)
    return msg


def extract_session_meta(fpath, msg_index=None):
    """Extract custom title, user messages, and cwd from a session file.

    msg_index: None = last message (default)
               0 = first, 1 = second, ...  (from start)
               -1 = last, -2 = second to last, ...  (from end)
    """
    all_msgs = []
    custom_title = ""
    cwd = ""
    try:
        with open(fpath, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "custom-title":
                    title = obj.get("customTitle", "")
                    custom_title = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", title)
                if obj.get("type") == "user":
                    msg = _parse_user_msg(obj)
                    if msg:
                        all_msgs.append(msg)
                if not cwd:
                    line_cwd = obj.get("cwd")
                    if line_cwd:
                        cwd = line_cwd
    except (OSError, UnicodeDecodeError):
        pass

    total = len(all_msgs)
    user_msg = ""
    shown_idx = 0
    if all_msgs:
        idx = msg_index if msg_index is not None else -1
        try:
            user_msg = all_msgs[idx]
            shown_idx = idx if idx >= 0 else total + idx
        except IndexError:
            if idx < 0:
                user_msg = all_msgs[-1]
                shown_idx = total - 1
            else:
                user_msg = all_msgs[0]
                shown_idx = 0

    return {
        "title": custom_title,
        "prompt": user_msg[:80],
        "total": total,
        "shown": shown_idx + 1,  # 1-based for display
        "cwd": cwd,
    }


def get_birth_time(fpath):
    """Get file creation time, falling back to mtime if birthtime unavailable."""
    st = os.stat(fpath)
    return getattr(st, "st_birthtime", st.st_mtime)


def extract_searchable_text(fpath, deep=False):
    """Extract all searchable text from a session: title + all user messages (+ assistant text if deep)."""
    parts = []
    try:
        with open(fpath, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "custom-title":
                    parts.append(obj.get("customTitle", ""))
                if obj.get("type") == "user":
                    msg = _parse_user_msg(obj)
                    if msg:
                        parts.append(msg)
                if deep and obj.get("type") == "assistant":
                    content = obj.get("message", {}).get("content", "")
                    if isinstance(content, list):
                        for b in content:
                            if b.get("type") == "text":
                                parts.append(b.get("text", ""))
                    elif isinstance(content, str):
                        parts.append(content)
    except (OSError, UnicodeDecodeError):
        pass
    return "\n".join(parts).lower()


def collect_sessions(projects_dir, msg_index, include_auto=False, search=None, dir_filter=None, deep=False):
    """Collect and sort all sessions."""
    search_lower = search.lower() if search else None
    dir_filter_norm = dir_filter.rstrip("/").lower() if dir_filter else None
    dir_filter_is_abs = dir_filter_norm and os.path.isabs(dir_filter) if dir_filter else False
    sessions = []
    for proj in os.listdir(projects_dir):
        proj_path = os.path.join(projects_dir, proj)
        if not os.path.isdir(proj_path):
            continue
        decoded = decode_project_path(proj)
        for f in os.listdir(proj_path):
            if f.endswith(".jsonl"):
                fpath = os.path.join(proj_path, f)
                if not include_auto and is_automated_session(fpath):
                    continue
                meta = extract_session_meta(fpath, msg_index=msg_index)
                proj_dir = meta["cwd"] or decoded
                if dir_filter_norm:
                    proj_lower = proj_dir.rstrip("/").lower()
                    if dir_filter_is_abs:
                        if not proj_lower.startswith(dir_filter_norm):
                            continue
                    else:
                        if dir_filter_norm not in proj_lower:
                            continue
                if search_lower:
                    haystack = proj_dir.lower() + "\n" + extract_searchable_text(fpath, deep=deep)
                    if search_lower not in haystack:
                        continue
                btime = get_birth_time(fpath)
                mtime = os.stat(fpath).st_mtime
                session_id = f.replace(".jsonl", "")
                sessions.append((mtime, btime, proj_dir, session_id, meta))
    sessions.sort(reverse=True)
    return sessions


def is_automated_session(fpath):
    """Check if a session is non-interactive (entrypoint != 'cli')."""
    try:
        with open(fpath, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "user":
                    return obj.get("entrypoint") != "cli"
    except (OSError, UnicodeDecodeError):
        pass
    return False


def main():
    parser = argparse.ArgumentParser(
        description="List Claude Code sessions",
        epilog="Message selection: default=last, --first=first, +N=Nth from start, -N=Nth from end. "
               "Pass a row number to resume that session.",
    )
    parser.add_argument("row", nargs="?", type=int, default=None,
                        help="open session at this row number")
    parser.add_argument("-n", "--limit", type=int, default=None,
                        help="max sessions to list (default: 20)")
    parser.add_argument("--first", action="store_true", help="show first user message instead of last")
    parser.add_argument("--msg", type=int, default=None, metavar="N",
                        help="message index: +N from start (0-based), -N from end")
    parser.add_argument("--print", "-p", action="store_true", dest="print_only",
                        help="print the resume command instead of running it")
    parser.add_argument("--search", "-s", type=str, default=None, metavar="TERM",
                        help="search sessions by title, user messages, and project path")
    parser.add_argument("--dir", "-d", type=str, default=None, metavar="PATH",
                        help="filter sessions by project directory (substring match)")
    parser.add_argument("--deep", action="store_true",
                        help="search assistant responses too (slower)")
    parser.add_argument("--auto", action="store_true",
                        help="include automated sessions (hidden by default)")
    args, unknown = parser.parse_known_args()

    # Support bare +N / -N without --msg
    if args.msg is None and not args.first:
        for arg in unknown:
            if re.match(r"^[+-]\d+$", arg):
                args.msg = int(arg)
                break

    if args.first:
        msg_idx = 0
    elif args.msg is not None:
        msg_idx = args.msg
    else:
        msg_idx = None

    home = os.path.expanduser("~")
    projects_dir = os.path.join(home, ".claude", "projects")

    if not os.path.isdir(projects_dir):
        print("No Claude sessions found.", file=sys.stderr)
        sys.exit(1)

    dir_filter = args.dir
    if dir_filter:
        expanded = os.path.abspath(os.path.expanduser(dir_filter))
        if os.path.isdir(expanded):
            dir_filter = expanded
        # else keep as-is for substring match

    sessions = collect_sessions(projects_dir, msg_idx, include_auto=args.auto, search=args.search, dir_filter=dir_filter, deep=args.deep)

    default_limit = None if (args.search or args.dir) else 20
    limit = args.limit if args.limit is not None else default_limit
    get_row = args.row

    if get_row is not None:
        idx = get_row - 1
        if idx < 0 or idx >= len(sessions):
            print(f"Invalid row {get_row}. Have {len(sessions)} sessions.", file=sys.stderr)
            sys.exit(1)
        _, _, proj_dir, sid, _ = sessions[idx]
        if args.print_only:
            cmd = f'cd "{proj_dir}" && claude --resume {sid}'
            if sys.stdout.isatty():
                print(f"\033[38;5;242m{cmd}\033[0m")
            else:
                print(cmd)
            sys.exit(0)
        if not os.path.isdir(proj_dir):
            print(f"Original project directory no longer exists: {proj_dir}", file=sys.stderr)
            print(f"Resume manually from any dir with: claude --resume {sid}", file=sys.stderr)
            sys.exit(1)
        os.chdir(proj_dir)
        os.execvp("claude", ["claude", "--resume", sid])

    display = sessions[:limit]
    use_color = sys.stdout.isatty()
    now = time.time()

    # Build rows
    rows = []
    for i, (mtime, btime, proj_dir, sid, meta) in enumerate(display, 1):
        created_ts = time.strftime("%b %d %H:%M", time.localtime(btime))
        active_ts = time.strftime("%b %d %H:%M", time.localtime(mtime))
        if time.strftime("%b %d", time.localtime(btime)) == time.strftime("%b %d", time.localtime(mtime)):
            active_ts = time.strftime("%H:%M", time.localtime(mtime))
        short_dir = proj_dir.replace(home, "~", 1)
        short_hash = sid[:8]
        rows.append((i, mtime, btime, created_ts, active_ts, short_dir, short_hash, meta))

    # Compute column widths for alignment
    max_idx_w = len(str(len(rows)))
    max_created_len = max((len(r[3]) for r in rows), default=0)
    max_active_len = max((len(r[4]) for r in rows), default=0)
    max_dir_len = max((len(r[5]) for r in rows), default=0)
    max_counter_len = max(
        (len(f"[{r[7]['shown']}/{r[7]['total']}]") for r in rows if r[7]["total"] > 0),
        default=0,
    )

    for row_idx, mtime, btime, created_ts, active_ts, short_dir, short_hash, meta in rows:
        age_hours = (now - mtime) / 3600
        title = meta["title"]
        prompt = meta["prompt"]
        total = meta["total"]
        shown = meta["shown"]

        summary = title or prompt or ""
        dir_pad = max_dir_len - len(short_dir)
        created_pad = max_created_len - len(created_ts)
        active_pad = max_active_len - len(active_ts)

        if total > 0:
            counter = f"[{shown}/{total}]"
        else:
            counter = ""
        counter_pad = max_counter_len - len(counter)

        if not use_color:
            line = f"{row_idx:>{max_idx_w}}  {created_ts}{' ' * created_pad} → {active_ts}{' ' * active_pad}  {short_hash}  {short_dir}{' ' * dir_pad}"
            if summary:
                line += f"  {counter}{' ' * counter_pad}  {summary}"
            print(line)
            continue

        # Time color by age (based on last activity)
        if age_hours < 1:
            time_color = "\033[38;5;48m"   # bright green - just now
        elif age_hours < 6:
            time_color = "\033[38;5;114m"  # muted green - today recent
        elif age_hours < 24:
            time_color = "\033[38;5;229m"  # yellow - today earlier
        elif age_hours < 48:
            time_color = "\033[38;5;216m"  # light orange - yesterday
        elif age_hours < 168:
            time_color = "\033[38;5;249m"  # light gray - this week
        else:
            time_color = "\033[38;5;242m"  # dim gray - older

        reset = "\033[0m"
        idx_color = "\033[38;5;245m"      # gray index
        hash_color = "\033[38;5;245m"     # gray hash
        dir_color = "\033[38;5;183m"      # light purple
        dim = "\033[38;5;242m"            # dim comment
        title_color = "\033[38;5;215m"    # orange for custom titles
        counter_color = "\033[38;5;110m"  # soft blue
        arrow_color = "\033[38;5;240m"    # dim arrow

        idx_str = f"{idx_color}{row_idx:>{max_idx_w}}{reset}"
        created_str = f"{dim}{created_ts}{reset}{' ' * created_pad}"
        active_str = f"{time_color}{active_ts}{reset}{' ' * active_pad}"
        arrow_str = f"{arrow_color}→{reset}"
        hash_str = f"{hash_color}{short_hash}{reset}"
        dir_str = f"{dir_color}{short_dir}{reset}{' ' * dir_pad}"

        if title:
            comment = f"  {counter_color}{counter}{reset}{' ' * counter_pad}  {title_color}{title}{reset}"
        elif prompt:
            comment = f"  {counter_color}{counter}{reset}{' ' * counter_pad}  {dim}{prompt}{reset}"
        else:
            comment = ""

        print(f"{idx_str}  {created_str} {arrow_str} {active_str}  {hash_str}  {dir_str}{comment}")


if __name__ == "__main__":
    main()
