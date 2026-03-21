#!/usr/bin/env bash
# Workspace save/load for Claude Code sessions
# Usage: wsave [name], wlist, wload <name>, wdel <name>

WORKSPACE_DIR="$HOME/.claude/workspaces"

# zsh arrays are 1-indexed, bash 0-indexed
if [[ -n "$ZSH_VERSION" ]]; then
    _WS_ARR_BASE=1
else
    _WS_ARR_BASE=0
fi

_ws_encode_path() {
    # Encode a path the same way Claude does: replace non-alphanumeric with '-'
    echo "$1" | sed 's/[^a-zA-Z0-9]/-/g'
}

_ws_session_branch() {
    # Extract gitBranch from a JSONL session file (first occurrence)
    python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    for line in f:
        try:
            b = json.loads(line).get('gitBranch')
            if b:
                print(b)
                sys.exit(0)
        except Exception:
            pass
" "$1" 2>/dev/null
}

_ws_random_name() {
    # Pick a random animal name for the workspace
    local animals=(
        ant bat bee bug cat cod cow cub doe dog eel elk emu ewe fox gnu hen hog jay kit
        lark lynx mink mole moth newt oryx puma ram rook seal slug swan toad vole wasp
        wolf wren yak asp boar carp clam colt crab crow dart deer dove duck fawn flea
        foal frog gnat goat gull hare hawk ibis kite kiwi lamb lion loon mule owl pony
        quail raven robin shark skunk sloth snail snake squid stork trout viper whale
    )
    local n=${#animals[@]}
    # Use $RANDOM (bash) or SRANDOM/RANDOM (zsh)
    local idx=$(( RANDOM % n ))
    echo "${animals[$idx]}"
}

_ws_tmux_tabs() {
    # Output tab entries for all windows in the current tmux session.
    # Format: "window_name" for plain shells, "window_name:uuid" for claude sessions.
    [[ -z "$TMUX" ]] && return 1

    # Map pane PID -> window name
    local win_info
    win_info=$(tmux list-windows -F '#{pane_pid} #{window_name}' 2>/dev/null) || return 1

    # Snapshot process table once
    local ps_snap
    ps_snap=$(ps -A -o pid=,ppid=,args=)

    echo "$win_info" | while IFS=' ' read -r pane_pid win_name; do
        [[ -n "$pane_pid" ]] || continue

        # Check if this pane has a claude child process
        _cl=$(echo "$ps_snap" | awk -v p="$pane_pid" '$2 == p && /claude/ {print; exit}')

        if [[ -z "$_cl" ]]; then
            echo "$win_name"
        else
            _cpid=$(echo "$_cl" | awk '{print $1}')
            _uuid=""

            if [[ "$_cl" == *"--resume"* ]]; then
                _uuid=$(echo "$_cl" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
            else
                _cwd=$(lsof -p "$_cpid" -Fn 2>/dev/null | awk '/^fcwd/{getline; sub(/^n/,""); print; exit}')
                if [[ -n "$_cwd" ]]; then
                    _enc=$(_ws_encode_path "$_cwd")
                    _pdir="$HOME/.claude/projects/${_enc}"
                    if [[ -d "$_pdir" ]]; then
                        _newest=$(ls -t "$_pdir"/*.jsonl 2>/dev/null | head -1)
                        [[ -n "$_newest" ]] && _uuid=$(basename "$_newest" .jsonl)
                    fi
                fi
            fi

            if [[ -n "$_uuid" ]]; then
                echo "${win_name}:${_uuid}"
            else
                echo "$win_name"
            fi
        fi
    done
}

wsave() {
    local name="$1"
    local dir="$(pwd)"
    local branch="$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null)"

    if [[ -z "$branch" ]]; then
        echo "error: not in a git repository"
        return 1
    fi

    # Auto-name: random animal
    if [[ -z "$name" ]]; then
        name="$(_ws_random_name)"
        # Avoid collisions
        while [[ -f "$WORKSPACE_DIR/${name}.ws" ]]; do
            name="$(_ws_random_name)"
        done
    fi

    mkdir -p "$WORKSPACE_DIR"

    local encoded_path="$(_ws_encode_path "$dir")"
    local project_dir="$HOME/.claude/projects/${encoded_path}"

    if [[ ! -d "$project_dir" ]]; then
        echo "error: no Claude project dir found at $project_dir"
        return 1
    fi

    local ws_file="$WORKSPACE_DIR/${name}.ws"
    local saved="$(date -u +%Y-%m-%dT%H:%M:%S)"

    # Write header
    cat > "$ws_file" <<EOF
dir=$dir
branch=$branch
saved=$saved
EOF

    local count=0

    if [[ -n "$TMUX" ]]; then
        # Inside tmux: save tabs with window names and claude UUIDs
        local tab_entry
        while IFS= read -r tab_entry; do
            [[ -n "$tab_entry" ]] || continue
            echo "tab=$tab_entry" >> "$ws_file"
            [[ "$tab_entry" == *:* ]] && count=$((count + 1))
        done < <(_ws_tmux_tabs)
        echo "saved workspace '$name' ($count sessions from tmux) -> $ws_file"
    else
        # Outside tmux: fall back to branch scanning (no tab names available)
        for jsonl in "$project_dir"/*.jsonl; do
            [[ -f "$jsonl" ]] || continue
            local uuid="$(basename "$jsonl" .jsonl)"
            local session_branch="$(_ws_session_branch "$jsonl")"

            if [[ "$session_branch" == "$branch" ]]; then
                echo "session=$uuid" >> "$ws_file"
                count=$((count + 1))
            fi
        done
        echo "saved workspace '$name' ($count sessions from branch scan) -> $ws_file"
    fi
}

wlist() {
    mkdir -p "$WORKSPACE_DIR"

    local ws_files=()
    for f in "$WORKSPACE_DIR"/*.ws; do
        [[ -f "$f" ]] && ws_files+=("$f")
    done
    if [[ ${#ws_files[@]} -eq 0 ]]; then
        echo "no saved workspaces"
        return 0
    fi

    local dim=$'\033[90m'
    local cyan=$'\033[36m'
    local rst=$'\033[0m'

    # Collect rows to compute column widths
    local names=() dirs=() repos=() branches=() counts=() tab_counts=() dates=() date_colors=()

    for ws_file in "${ws_files[@]}"; do
        local name="" dir="" branch="" saved="" session_count=0 tab_count=0

        while IFS='=' read -r key value || [[ -n "$key" ]]; do
            case "$key" in
                dir) dir="$value" ;;
                branch) branch="$value" ;;
                saved) saved="$value" ;;
                session) session_count=$((session_count + 1)) ;;
                tab) tab_count=$((tab_count + 1)); [[ "$value" == *:* ]] && session_count=$((session_count + 1)) ;;
            esac
        done < "$ws_file"

        name="$(basename "$ws_file" .ws)"
        local repo="$(basename "$dir")"
        dir="${dir/#$HOME/~}"

        local short_date="" date_color="$dim"
        if [[ -n "$saved" ]]; then
            short_date="$(date -j -f "%Y-%m-%dT%H:%M:%S" "$saved" "+%b %d %H:%M" 2>/dev/null || echo "$saved")"
            # Age-based color (matches claude-sessions.py)
            local saved_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$saved" "+%s" 2>/dev/null)
            local now_epoch=$(date "+%s")
            if [[ -n "$saved_epoch" ]]; then
                age_hours=$(( (now_epoch - saved_epoch) / 3600 ))
                if (( age_hours < 1 )); then
                    date_color=$'\033[38;5;48m'    # bright green - just now
                elif (( age_hours < 6 )); then
                    date_color=$'\033[38;5;114m'   # muted green - today recent
                elif (( age_hours < 24 )); then
                    date_color=$'\033[38;5;229m'   # yellow - today earlier
                elif (( age_hours < 48 )); then
                    date_color=$'\033[38;5;216m'   # light orange - yesterday
                elif (( age_hours < 168 )); then
                    date_color=$'\033[38;5;249m'   # light gray - this week
                else
                    date_color=$'\033[38;5;242m'   # dim gray - older
                fi
            fi
        fi

        names+=("$name")
        dirs+=("$dir")
        repos+=("$repo")
        branches+=("$branch")
        counts+=("$session_count")
        tab_counts+=("$tab_count")
        dates+=("$short_date")
        date_colors+=("$date_color")
    done

    # Compute max widths
    local wn=4 wd=3 wr=4 wb=6  # header lengths
    local _n
    for _n in "${names[@]}"; do (( ${#_n} > wn )) && wn=${#_n}; done
    for _n in "${dirs[@]}"; do (( ${#_n} > wd )) && wd=${#_n}; done
    for _n in "${repos[@]}"; do (( ${#_n} > wr )) && wr=${#_n}; done
    for _n in "${branches[@]}"; do (( ${#_n} > wb )) && wb=${#_n}; done

    # Header
    printf "${dim}%-${wn}s  %-${wd}s  %-${wr}s  %-${wb}s  %4s  %4s  %s${rst}\n" \
        "NAME" "DIR" "REPO" "BRANCH" "TABS" "SESS" "SAVED"

    # Rows — use paste to iterate parallel arrays (zsh/bash portable)
    local idx=0
    while [[ $idx -lt ${#names[@]} ]]; do
        # zsh arrays are 1-indexed, bash 0-indexed; access via offset from first element
        local _name="${names[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _dir="${dirs[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _repo="${repos[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _branch="${branches[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _count="${counts[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _tabs="${tab_counts[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _date="${dates[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _dcol="${date_colors[$((idx + ${_WS_ARR_BASE:-0}))]}"

        local tabs_str=""
        [[ "$_tabs" -gt 0 ]] && tabs_str="$_tabs"

        printf "${cyan}%-${wn}s${rst}  %-${wd}s  %-${wr}s  %-${wb}s  %4s  %4d  ${_dcol}%s${rst}\n" \
            "$_name" "$_dir" "$_repo" "$_branch" "$tabs_str" "$_count" "$_date"
        idx=$((idx + 1))
    done
}

wload() {
    local name="$1"
    if [[ -z "$name" ]]; then
        echo "usage: wload <name>"
        echo "available workspaces:"
        wlist
        return 1
    fi

    local ws_file="$WORKSPACE_DIR/${name}.ws"
    if [[ ! -f "$ws_file" ]]; then
        echo "error: workspace '$name' not found"
        return 1
    fi

    local dir branch
    local tabs=()      # "win_name:uuid" or "win_name"
    local sessions=()  # legacy: bare uuids

    while IFS='=' read -r key value || [[ -n "$key" ]]; do
        case "$key" in
            dir) dir="$value" ;;
            branch) branch="$value" ;;
            tab) tabs+=("$value") ;;
            session) sessions+=("$value") ;;
        esac
    done < "$ws_file"

    local tmux_session="ws-${name}"

    # If tmux session already exists, just attach
    if tmux has-session -t "$tmux_session" 2>/dev/null; then
        echo "attaching to existing tmux session '$tmux_session'"
        tmux attach-session -t "$tmux_session"
        return 0
    fi

    if [[ ${#tabs[@]} -gt 0 ]]; then
        # New format: restore tabs with original window names
        local first=1 win_idx=0
        local tab_entry
        for tab_entry in "${tabs[@]}"; do
            local win_name uuid=""
            if [[ "$tab_entry" == *:* ]]; then
                win_name="${tab_entry%%:*}"
                uuid="${tab_entry#*:}"
            else
                win_name="$tab_entry"
            fi

            if [[ $first -eq 1 ]]; then
                tmux new-session -d -s "$tmux_session" -c "$dir"
                tmux rename-window -t "$tmux_session:${win_idx}" "$win_name"
                first=0
            else
                tmux new-window -t "$tmux_session" -n "$win_name" -c "$dir"
            fi

            if [[ -n "$uuid" ]]; then
                tmux send-keys -t "$tmux_session:${win_idx}" "claude --resume ${uuid}" Enter
            fi
            win_idx=$((win_idx + 1))
        done
    else
        # Legacy format: bare session UUIDs
        tmux new-session -d -s "$tmux_session" -c "$dir"
        tmux rename-window -t "$tmux_session:0" "shell"

        local i=1
        for uuid in "${sessions[@]}"; do
            tmux new-window -t "$tmux_session" -n "claude-${i}" -c "$dir"
            tmux send-keys -t "$tmux_session:${i}" "claude --resume ${uuid}" Enter
            i=$((i + 1))
        done
    fi

    # Select first window and attach
    tmux select-window -t "$tmux_session:0"
    tmux attach-session -t "$tmux_session"
}

wdel() {
    local name="$1"
    if [[ -z "$name" ]]; then
        echo "usage: wdel <name>"
        echo "available workspaces:"
        wlist
        return 1
    fi

    local ws_file="$WORKSPACE_DIR/${name}.ws"
    if [[ ! -f "$ws_file" ]]; then
        echo "error: workspace '$name' not found"
        return 1
    fi

    command rm "$ws_file"
    echo "deleted workspace '$name'"
}
