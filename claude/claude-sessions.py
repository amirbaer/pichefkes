#!/usr/bin/env python3
"""List all Claude Code sessions across projects with copy-pasteable resume commands."""

import argparse
import json
import os
import re
import sys
import time
import zlib


# Cache of parsed session metadata, keyed by session file path. Session files are
# large (this machine has 28GB across ~34k files) and mostly immutable once a session
# ends, so re-parsing every file on every run costs minutes on a cold disk. We cache
# the cheap-to-store bits (title, cwd, automated flag, user-message first-lines) keyed
# on the file's (mtime, size) and only re-parse files that actually changed. A changed
# file is append-only in practice, so its entry also records how far it was read ("off")
# and a checksum of the bytes at both ends of that range ("sig"): the next run reads
# only the appended tail, and falls back to a full re-parse if the checksums disagree.
CACHE_VERSION = 1
CACHE_PATH = os.path.join(os.path.expanduser("~"), ".claude", ".claude-sessions-cache.json")

# Rewriting the whole cache (~0.3s for 20MB) costs more than re-reading a small appended
# tail (~300MB/s), so a run that parsed less than this many bytes leaves the cache file
# alone: the tails are re-read next time and the offsets catch up once enough has built up.
SAVE_MIN_PARSED_BYTES = 32_000_000
SIG_BYTES = 256

CTRL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize(name):
    """Normalize a name the same way Claude encodes paths: replace non-alphanumeric with dash."""
    return re.sub(r"[^a-zA-Z0-9]", "-", name)


# directory path -> {normalize(entry): entry} (first entry in listing order wins), or None
# when the path is not a directory. Built once per directory per run: decode_project_path
# used to re-list and re-normalize every entry of a directory for each project under it,
# which cost minutes of CPU across thousands of project folders.
_DIR_NAMES = {}


def _dir_names(path):
    names = _DIR_NAMES.get(path, False)
    if names is False:
        names = None
        if os.path.isdir(path):
            names = {}
            try:
                entries = os.listdir(path)
            except OSError:
                entries = []
            for entry in entries:
                names.setdefault(normalize(entry), entry)
        _DIR_NAMES[path] = names
    return names


def decode_project_path(encoded):
    """Walk filesystem to resolve the ambiguous dash-encoded project path."""
    parts = encoded.lstrip("-").split("-")
    resolved = "/"
    i = 0
    while i < len(parts):
        matched = False
        names = _dir_names(resolved)
        if names:
            for end in range(len(parts), i, -1):
                entry = names.get("-".join(parts[i:end]))
                if entry is not None:
                    resolved = os.path.join(resolved, entry)
                    i = end
                    matched = True
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


# Session lines are compact JSON (no spaces), so a line that matters can be recognised from
# its raw bytes without decoding it: most of a session's bytes are attachment / assistant /
# tool-result lines that never contribute to the listing. A marker only has to be a
# superset test (a false positive just costs one json.loads; the real checks run on the
# decoded object), and it cannot match inside string content, where quotes are escaped.
_TYPE_USER = b'"type":"user"'
_TYPE_TITLE = b'"type":"custom-title"'
_TYPE_TOOL_RESULT = b'"type":"tool_result"'
_TYPE_TEXT = b'"type":"text"'
_KEY_CWD = b'"cwd"'
# `": "` (quote, colon, space, quote) only occurs in JSON with spaces after its colons: in a
# compact line a string value holding it is escaped (`\": \"`). A line that has it is not
# in the format the markers above assume, so it is decoded in full like the old parser did.
_SPACED = b'": "'


def _feed(state, line):
    """Fold one raw JSONL line into `state`; returns True if it was decoded as a JSON object.

    A line is decoded only when it can change the state: a custom title, a user message
    (except one made purely of tool results, which carries no prompt text once the
    session's first user line has fixed `automated`), or, until a cwd has been seen,
    any line mentioning one.
    """
    if line.find(_SPACED, 0, 512) < 0:
        need_cwd = not state["cwd"] and _KEY_CWD in line
        if _TYPE_USER in line:
            if (state["known"] and not need_cwd
                    and _TYPE_TOOL_RESULT in line and _TYPE_TEXT not in line):
                return False
        elif not need_cwd and _TYPE_TITLE not in line:
            return False
    try:
        obj = json.loads(line)
        if not isinstance(obj, dict):
            return False
        obj_type = obj.get("type")
        if obj_type == "custom-title":
            state["title"] = CTRL_CHARS.sub("", obj.get("customTitle", ""))
        elif obj_type == "user":
            if not state["known"]:
                state["automated"] = obj.get("entrypoint") != "cli"
                state["known"] = True
            msg = _parse_user_msg(obj)
            if msg:
                state["msgs"].append(msg)
        if not state["cwd"]:
            line_cwd = obj.get("cwd")
            if line_cwd:
                state["cwd"] = line_cwd
    except ValueError:  # JSONDecodeError, or bytes that are not valid UTF-8
        return False
    except (AttributeError, TypeError):  # a line shaped unlike a session record
        return True
    return True


def _file_sig(f, off):
    """Checksums of the first and last SIG_BYTES of the first `off` bytes of an open file."""
    head_len = min(SIG_BYTES, off)
    tail_start = max(0, off - SIG_BYTES)
    f.seek(0)
    head = f.read(head_len)
    f.seek(tail_start)
    tail = f.read(off - tail_start)
    return [zlib.crc32(head), zlib.crc32(tail)]


def parse_session(fpath, resume=None):
    """Read a session file once and extract everything the listing/search needs.

    Returns a dict with:
      title     - custom title (control chars stripped), or ""
      cwd       - first cwd seen in the session, or ""
      automated - True if the session's first user message is non-interactive (entrypoint != 'cli')
      msgs      - cleaned first-lines of every user message, in order
      known     - True once the first user message has been seen (`automated` is settled)
      off, sig  - only when the parse can be continued later: the byte offset just past the
                  last newline-terminated line consumed, and checksums of the bytes before it
      read      - bytes read from the file by this call

    Only the *first line* of each user message is kept (matching the original
    display/search behaviour), so this stays small even for huge sessions.

    resume: a cache entry from an earlier parse of this same append-only file (validated by
    `_can_resume`); parsing continues at its offset instead of at byte 0, extending its msgs.
    """
    if resume is not None:
        state = {k: resume[k] for k in ("title", "cwd", "automated", "known", "msgs")}
        start = resume["off"]
    else:
        state = {"title": "", "cwd": "", "automated": False, "known": False, "msgs": []}
        start = 0
    off = start
    sig = None
    try:
        with open(fpath, "rb") as f:
            if start:
                f.seek(start)
            for line in f:
                if line.endswith(b"\n"):
                    _feed(state, line)
                    off += len(line)
                elif _feed(state, line):
                    # A final line with no newline yet that already decodes as JSON: it is in
                    # `state`, but a later run could not tell where it ends, so don't resume.
                    off = None
                    break
            read = f.tell() - start
            if off:
                sig = _file_sig(f, off)
    except OSError:
        off = None
        read = 0
    state["read"] = read
    if off and sig:
        state["off"] = off
        state["sig"] = sig
    return state


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
        # dumps, not dump: only dumps takes the C encoder, dump streams ~1.5M chunks through
        # the pure-Python one (3s of a 4s run for a 20MB cache).
        data = json.dumps({"version": CACHE_VERSION, "entries": entries}, separators=(",", ":"))
        with open(tmp, "w") as f:
            f.write(data)
        os.replace(tmp, path)
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _can_resume(entry, fpath, st):
    """True if a changed file is still the file `entry` was parsed from, grown at the end.

    The entry must carry a resume point, the file must be at least that long, and the bytes
    at both ends of the already-parsed range must still checksum the same (a rewrite that
    drops or edits earlier lines shifts them).
    """
    off, sig = entry.get("off"), entry.get("sig")
    if (not isinstance(off, int) or off <= 0 or st.st_size < off
            or not isinstance(sig, list) or len(sig) != 2
            or not isinstance(entry.get("msgs"), list)
            or not all(k in entry for k in ("title", "cwd", "automated", "known"))):
        return False
    try:
        with open(fpath, "rb") as f:
            return _file_sig(f, off) == sig
    except OSError:
        return False


def get_parsed(fpath, st, cache):
    """Return parsed session data for fpath, using the cache when the file is unchanged.

    Returns (parsed_dict, parsed_bytes): parsed_bytes is None for a cache hit, else the
    number of bytes read to bring the entry up to date. A file that only grew is read from
    where the cached parse stopped. On a miss the entry in `cache` is replaced.
    """
    resume = None
    if cache is not None:
        entry = cache.get(fpath)
        if entry:
            if entry.get("mtime") == st.st_mtime and entry.get("size") == st.st_size:
                return entry, None
            if _can_resume(entry, fpath, st):
                resume = entry
    parsed = parse_session(fpath, resume)
    if cache is not None:
        entry = {
            "mtime": st.st_mtime,
            "size": st.st_size,
            "title": parsed["title"],
            "cwd": parsed["cwd"],
            "automated": parsed["automated"],
            "known": parsed["known"],
            "msgs": parsed["msgs"],
        }
        if "off" in parsed:
            entry["off"] = parsed["off"]
            entry["sig"] = parsed["sig"]
        cache[fpath] = entry
    return parsed, parsed["read"]


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

    When `limit` is an int, the scan stops at the newest `limit` matching sessions — the
    rest are never opened, with or without a search/dir filter (newest first, so they are
    the same sessions a full scan would put first). Without a limit every file is examined.

    Returns (sessions, seen_paths, misses, parsed_bytes):
      sessions     - list of (mtime, btime, proj_dir, session_id, meta)
      seen_paths   - set of every session file that currently exists (for cache pruning)
      misses       - number of files that had to be parsed (cache misses)
      parsed_bytes - bytes read from session files to serve those misses
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

    full_scan = not isinstance(limit, int)

    sessions = []
    misses = 0
    parsed_bytes = 0
    for mtime, btime, st, fpath, sid, decoded in records:
        parsed, cost = get_parsed(fpath, st, cache)
        if cost is not None:
            misses += 1
            parsed_bytes += cost

        if not include_auto and parsed["automated"]:
            continue

        # `claude --resume <id>` finds a session under ~/.claude/projects/<normalize(cwd)>/,
        # so the directory we display and cd into must re-encode to this session's project
        # folder. parsed["cwd"] is the *first* cwd in the session; if the session used /cd it
        # can diverge from the folder (normalize won't match), so fall back to the decoded
        # folder path, which always round-trips. Both normalize to the same folder for
        # sessions that never changed directory, so this is a no-op there.
        cwd = parsed["cwd"]
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

        meta = meta_from_parsed(parsed, msg_index=msg_index)
        sessions.append((mtime, btime, proj_dir, sid, meta))
        if not full_scan and len(sessions) >= limit:
            break

    return sessions, seen_paths, misses, parsed_bytes


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

    # For a row resume, parse only enough sessions to reach the requested row instead of
    # scanning every file. A listing only warms the cache for the top ~limit sessions (not
    # all of them), so scanning fully here is a cold re-parse of every session file — tens
    # of thousands on a busy machine, which looks like a hang. Capping the scan at get_row
    # keeps a valid resume fast; a row beyond the true total never reaches the cap, so the
    # loop falls through to a full scan and the "Have N sessions" error stays accurate.
    if get_row is not None and get_row > 0:
        collect_limit = get_row
    else:
        collect_limit = limit

    sessions, seen_paths, misses, parsed_bytes = collect_sessions(
        projects_dir, msg_idx, include_auto=args.auto, search=args.search,
        dir_filter=dir_filter, deep=args.deep, limit=collect_limit, cache=active_cache,
    )

    # Persist the cache: prune entries for files that no longer exist, and write only
    # when something worth keeping changed (stale entries were dropped, or enough was
    # parsed that re-reading it next time would cost more than rewriting the cache).
    if use_cache:
        pruned = {k: v for k, v in cache.items() if k in seen_paths}
        if (parsed_bytes >= SAVE_MIN_PARSED_BYTES or len(pruned) != len(cache)
                or args.rebuild_cache):
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
