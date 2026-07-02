#!/usr/bin/env python3
"""List all Claude Code sessions across projects with copy-pasteable resume commands."""

import argparse
import json
import os
import re
import sys
import time


# Cache of parsed session metadata, keyed by session file path. Session files are
# large (this machine has 1.4GB across ~8k files) and mostly immutable once a session
# ends, so re-parsing every file on every run costs minutes on a cold disk. We cache
# the cheap-to-store bits (title, cwd, automated flag, user-message first-lines) keyed
# on the file's (mtime, size) and only re-parse files that actually changed.
CACHE_VERSION = 1
CACHE_PATH = os.path.join(os.path.expanduser("~"), ".claude", ".claude-sessions-cache.json")

CTRL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


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
    msg = CTRL_CHARS.sub("", msg)
    msg = re.sub(r"^[➜$#>]\s*", "", msg)
    msg = re.sub(r"^\S+\s+git:\(.*?\)\s*[✗✓]*\s*", "", msg)
    return msg


def parse_session(fpath):
    """Read a session file once and extract everything the listing/search needs.

    Returns a dict with:
      title     - custom title (control chars stripped), or ""
      cwd       - first cwd seen in the session, or ""
      automated - True if the session's first user message is non-interactive (entrypoint != 'cli')
      msgs      - cleaned first-lines of every user message, in order

    Only the *first line* of each user message is kept (matching the original
    display/search behaviour), so this stays small even for huge sessions.
    """
    title = ""
    cwd = ""
    automated = False
    automated_known = False
    msgs = []
    try:
        with open(fpath, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                obj_type = obj.get("type")
                if obj_type == "custom-title":
                    title = CTRL_CHARS.sub("", obj.get("customTitle", ""))
                elif obj_type == "user":
                    if not automated_known:
                        automated = obj.get("entrypoint") != "cli"
                        automated_known = True
                    msg = _parse_user_msg(obj)
                    if msg:
                        msgs.append(msg)
                if not cwd:
                    line_cwd = obj.get("cwd")
                    if line_cwd:
                        cwd = line_cwd
    except (OSError, UnicodeDecodeError):
        pass
    return {"title": title, "cwd": cwd, "automated": automated, "msgs": msgs}


def meta_from_parsed(parsed, msg_index=None):
    """Derive the display meta (title, chosen prompt, counts, cwd) from parsed data.

    msg_index: None = last message (default)
               0 = first, 1 = second, ...  (from start)
               -1 = last, -2 = second to last, ...  (from end)
    """
    all_msgs = parsed["msgs"]
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
        "title": parsed["title"],
        "prompt": user_msg[:80],
        "total": total,
        "shown": shown_idx + 1,  # 1-based for display
        "cwd": parsed["cwd"],
    }


def searchable_from_parsed(parsed):
    """Searchable text (title + user messages) for a non-deep search, lowercased."""
    return "\n".join([parsed["title"]] + parsed["msgs"]).lower()


def extract_assistant_text(fpath):
    """Extract assistant text from a session for --deep search, lowercased.

    Assistant output is the bulk of a session's bytes, so it's never cached; deep
    search inherently re-reads the file.
    """
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
                if obj.get("type") == "assistant":
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


def get_birth_time(st):
    """Get file creation time from a stat result, falling back to mtime."""
    return getattr(st, "st_birthtime", st.st_mtime)


def load_cache(path):
    """Load the parsed-session cache. Returns {} on any problem or version mismatch."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("version") != CACHE_VERSION:
        return {}
    entries = data.get("entries")
    return entries if isinstance(entries, dict) else {}


def save_cache(path, entries):
    """Atomically write the cache (temp file + rename). Failures are non-fatal."""
    tmp = path + ".tmp.%d" % os.getpid()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp, "w") as f:
            json.dump({"version": CACHE_VERSION, "entries": entries}, f)
        os.replace(tmp, path)
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass


def get_parsed(fpath, st, cache):
    """Return parsed session data for fpath, using the cache when the file is unchanged.

    Returns (parsed_dict, was_cached). On a miss, parses the file and stores the
    result in `cache` (mutated in place).
    """
    if cache is not None:
        entry = cache.get(fpath)
        if entry and entry.get("mtime") == st.st_mtime and entry.get("size") == st.st_size:
            return entry, True
    parsed = parse_session(fpath)
    if cache is not None:
        cache[fpath] = {
            "mtime": st.st_mtime,
            "size": st.st_size,
            "title": parsed["title"],
            "cwd": parsed["cwd"],
            "automated": parsed["automated"],
            "msgs": parsed["msgs"],
        }
    return parsed, False


def iter_session_files(projects_dir):
    """Yield (fpath, session_id, decoded_project_dir) for every session file.

    decode_project_path (which walks the filesystem) runs at most once per project,
    and only for projects that actually contain sessions.
    """
    for proj in os.listdir(projects_dir):
        proj_path = os.path.join(projects_dir, proj)
        if not os.path.isdir(proj_path):
            continue
        decoded = None
        for f in os.listdir(proj_path):
            if not f.endswith(".jsonl"):
                continue
            if decoded is None:
                decoded = decode_project_path(proj)
            yield os.path.join(proj_path, f), f[: -len(".jsonl")], decoded


def collect_sessions(projects_dir, msg_index, include_auto=False, search=None,
                     dir_filter=None, deep=False, limit=None, cache=None):
    """Collect and sort sessions (newest first).

    When there is no search or dir filter and `limit` is a positive int, only the
    newest `limit` matching sessions are parsed (lazy) — the rest are never opened.
    A search/dir filter forces a full scan since every file must be examined.

    Returns (sessions, seen_paths, misses):
      sessions   - list of (mtime, btime, proj_dir, session_id, meta)
      seen_paths - set of every session file that currently exists (for cache pruning)
      misses     - number of files that had to be parsed (cache misses)
    """
    search_lower = search.lower() if search else None
    dir_filter_norm = dir_filter.rstrip("/").lower() if dir_filter else None
    dir_filter_is_abs = bool(dir_filter) and os.path.isabs(dir_filter)

    # Cheap first pass: stat every file (metadata only, no reads) so we can sort by
    # recency before deciding which files are worth parsing.
    records = []  # (mtime, btime, st, fpath, session_id, decoded)
    seen_paths = set()
    for fpath, sid, decoded in iter_session_files(projects_dir):
        try:
            st = os.stat(fpath)
        except OSError:
            continue
        seen_paths.add(fpath)
        records.append((st.st_mtime, get_birth_time(st), st, fpath, sid, decoded))

    # Newest first. Tie-break by btime then decoded dir then id; identical float
    # mtimes across files are effectively impossible, so this matches the old order.
    records.sort(key=lambda r: (r[0], r[1], r[5], r[4]), reverse=True)

    full_scan = bool(search_lower) or bool(dir_filter_norm) or not isinstance(limit, int)

    sessions = []
    misses = 0
    for mtime, btime, st, fpath, sid, decoded in records:
        parsed, was_cached = get_parsed(fpath, st, cache)
        if not was_cached:
            misses += 1

        if not include_auto and parsed["automated"]:
            continue

        meta = meta_from_parsed(parsed, msg_index=msg_index)
        # `claude --resume <id>` finds a session under ~/.claude/projects/<normalize(cwd)>/,
        # so the directory we display and cd into must re-encode to this session's project
        # folder. meta["cwd"] is the *first* cwd in the session; if the session used /cd it
        # can diverge from the folder (normalize won't match), so fall back to the decoded
        # folder path, which always round-trips. Both normalize to the same folder for
        # sessions that never changed directory, so this is a no-op there.
        cwd = meta["cwd"]
        if cwd and normalize(cwd) == normalize(decoded):
            proj_dir = cwd
        else:
            proj_dir = decoded

        if dir_filter_norm:
            proj_lower = proj_dir.rstrip("/").lower()
            if dir_filter_is_abs:
                if not proj_lower.startswith(dir_filter_norm):
                    continue
            else:
                if dir_filter_norm not in proj_lower:
                    continue

        if search_lower:
            base = proj_dir.lower() + "\n" + searchable_from_parsed(parsed)
            if search_lower in base:
                pass
            elif deep and search_lower in extract_assistant_text(fpath):
                pass
            else:
                continue

        sessions.append((mtime, btime, proj_dir, sid, meta))
        if not full_scan and len(sessions) >= limit:
            break

    return sessions, seen_paths, misses


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
    parser.add_argument("--no-cache", action="store_true",
                        help="bypass the metadata cache (always re-parse every file)")
    parser.add_argument("--rebuild-cache", action="store_true",
                        help="ignore the existing cache and rebuild it from scratch")
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

    use_cache = not args.no_cache
    cache = {} if (not use_cache or args.rebuild_cache) else load_cache(CACHE_PATH)
    # `cache=None` disables lookups/stores entirely inside collect_sessions.
    active_cache = cache if use_cache else None

    default_limit = None if (args.search or args.dir) else 20
    limit = args.limit if args.limit is not None else default_limit
    get_row = args.row

    # For a row resume we scan fully: the row may exceed the display limit, and the
    # "Have N sessions" error on a bad row must report the true total. This runs after
    # a listing (cache warm), so the full scan is cheap.
    collect_limit = None if get_row is not None else limit

    sessions, seen_paths, misses = collect_sessions(
        projects_dir, msg_idx, include_auto=args.auto, search=args.search,
        dir_filter=dir_filter, deep=args.deep, limit=collect_limit, cache=active_cache,
    )

    # Persist the cache: prune entries for files that no longer exist, and write only
    # when something actually changed (a parse happened or stale entries were dropped).
    if use_cache:
        pruned = {k: v for k, v in cache.items() if k in seen_paths}
        if misses > 0 or len(pruned) != len(cache) or args.rebuild_cache:
            save_cache(CACHE_PATH, pruned)

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
