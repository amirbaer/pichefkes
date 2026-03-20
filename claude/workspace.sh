#!/usr/bin/env bash
# Workspace save/load for Claude Code sessions
# Usage: wsave [name], wlist, wload <name>

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

    # Find sessions matching this branch
    local count=0
    for jsonl in "$project_dir"/*.jsonl; do
        [[ -f "$jsonl" ]] || continue
        local uuid="$(basename "$jsonl" .jsonl)"
        local session_branch="$(_ws_session_branch "$jsonl")"

        if [[ "$session_branch" == "$branch" ]]; then
            echo "session=$uuid" >> "$ws_file"
            count=$((count + 1))
        fi
    done

    echo "saved workspace '$name' ($count sessions) -> $ws_file"
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
    local names=() dirs=() repos=() branches=() counts=() dates=()

    for ws_file in "${ws_files[@]}"; do
        local name="" dir="" branch="" saved="" session_count=0

        while IFS='=' read -r key value || [[ -n "$key" ]]; do
            case "$key" in
                dir) dir="$value" ;;
                branch) branch="$value" ;;
                saved) saved="$value" ;;
                session) session_count=$((session_count + 1)) ;;
            esac
        done < "$ws_file"

        name="$(basename "$ws_file" .ws)"
        local repo="$(basename "$dir")"
        dir="${dir/#$HOME/~}"

        local short_date=""
        if [[ -n "$saved" ]]; then
            short_date="$(date -j -f "%Y-%m-%dT%H:%M:%S" "$saved" "+%b %d %H:%M" 2>/dev/null || echo "$saved")"
        fi

        names+=("$name")
        dirs+=("$dir")
        repos+=("$repo")
        branches+=("$branch")
        counts+=("$session_count")
        dates+=("$short_date")
    done

    # Compute max widths
    local wn=4 wd=3 wr=4 wb=6  # header lengths
    local _n
    for _n in "${names[@]}"; do (( ${#_n} > wn )) && wn=${#_n}; done
    for _n in "${dirs[@]}"; do (( ${#_n} > wd )) && wd=${#_n}; done
    for _n in "${repos[@]}"; do (( ${#_n} > wr )) && wr=${#_n}; done
    for _n in "${branches[@]}"; do (( ${#_n} > wb )) && wb=${#_n}; done

    # Header
    printf "${dim}%-${wn}s  %-${wd}s  %-${wr}s  %-${wb}s  %4s  %s${rst}\n" \
        "NAME" "DIR" "REPO" "BRANCH" "SESS" "SAVED"

    # Rows — use paste to iterate parallel arrays (zsh/bash portable)
    local idx=0
    while [[ $idx -lt ${#names[@]} ]]; do
        # zsh arrays are 1-indexed, bash 0-indexed; access via offset from first element
        local _name="${names[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _dir="${dirs[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _repo="${repos[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _branch="${branches[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _count="${counts[$((idx + ${_WS_ARR_BASE:-0}))]}"
        local _date="${dates[$((idx + ${_WS_ARR_BASE:-0}))]}"

        printf "${cyan}%-${wn}s${rst}  %-${wd}s  %-${wr}s  %-${wb}s  %4d  ${dim}%s${rst}\n" \
            "$_name" "$_dir" "$_repo" "$_branch" "$_count" "$_date"
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
    local sessions=()

    while IFS='=' read -r key value || [[ -n "$key" ]]; do
        case "$key" in
            dir) dir="$value" ;;
            branch) branch="$value" ;;
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

    # Create tmux session with window 0 as shell in repo dir
    tmux new-session -d -s "$tmux_session" -c "$dir"
    tmux rename-window -t "$tmux_session:0" "shell"

    # Create a window for each Claude session
    local i=1
    for uuid in "${sessions[@]}"; do
        tmux new-window -t "$tmux_session" -n "claude-${i}" -c "$dir"
        tmux send-keys -t "$tmux_session:${i}" "claude --resume ${uuid}" Enter
        i=$((i + 1))
    done

    # Select window 0 and attach
    tmux select-window -t "$tmux_session:0"
    tmux attach-session -t "$tmux_session"
}
