#!/usr/bin/env bash
#
# rc-sync — keep rc files (~/.bashrc, ~/.tmux.conf, .alias, ...) available even
# when Google Drive is NOT mounted, while still syncing edits across machines.
#
# Why: the old setup symlinked these files INTO Google Drive. If Drive wasn't
# mounted yet at login (fresh boot, slow mount), the symlinks were broken and
# bash/tmux silently fell back to defaults. rc-sync fixes that by keeping each
# rc file as a REAL LOCAL file in $HOME (always readable) and reconciling it
# with Drive's canonical copy only when Drive is available.
#
# Reconcile rule: newest-wins by mtime, BOTH directions. `cp -p` preserves
# mtimes, so a settled pair copies nothing (no ping-pong). An edit on any
# machine wins on the next sync; a machine that's offline just keeps its local
# copy until Drive comes back.
#
# Usage:
#   rc-sync sync           reconcile local <-> Drive now (default; safe, idempotent)
#   rc-sync sync --quiet    same, but silent unless something changes (used at login)
#   rc-sync install         migrate any Drive symlinks -> local files, install this
#                           script to ~/.local/bin/rc-sync, wire it into shell
#                           startup, then run an initial sync
#   rc-sync status          show each managed file's state
#   rc-sync --help
#
# Standalone: needs only bash + stat/cp/mktemp. Safe to wget and run.

set -u

# ---- rc files rc-sync manages (names under $HOME and under rc-files-hidden) --
RC_FILES=(
    .alias
    .bashrc
    .git-completion.bash
    .inputrc
    .screenrc
    .tmux.conf
    .vimrc
)

SELF_DEST="$HOME/.local/bin/rc-sync"
HOOK_MARK="rc-sync hook"          # idempotency marker written into startup files
QUIET=0

# Startup files to wire the login-time sync into. bash_profile is prepended so
# the sync runs BEFORE it sources ~/.bashrc; the others are appended (they run
# before their interactive rc anyway).
STARTUP_PREPEND=( "$HOME/.bash_profile" )
STARTUP_APPEND=( "$HOME/.zprofile" "$HOME/.zshrc" )

RED=$'\033[0;31m'; GRN=$'\033[0;32m'; YLW=$'\033[1;33m'; NC=$'\033[0m'
info() { [ "$QUIET" -eq 1 ] && return 0; printf '%s[rc-sync]%s %s\n' "$GRN" "$NC" "$*"; }
warn() { printf '%s[rc-sync]%s %s\n' "$YLW" "$NC" "$*" >&2; }
err()  { printf '%s[rc-sync]%s %s\n' "$RED" "$NC" "$*" >&2; }

# ---- locate Google Drive's rc-files-hidden (ported from setup-new-computer.sh)
find_rc_hidden() {
    local sub="worktables/tech/code/rc-files-hidden" gd
    if [ -d "$HOME/Library/CloudStorage" ]; then
        for gd in "$HOME/Library/CloudStorage"/GoogleDrive-*/"My Drive"; do
            [ -d "$gd/$sub" ] && { printf '%s\n' "$gd/$sub"; return 0; }
        done
    fi
    for gd in "$HOME"/*"Google Drive"*/"My Drive"; do
        [ -d "$gd/$sub" ] && { printf '%s\n' "$gd/$sub"; return 0; }
    done
    [ -d "/Volumes/GoogleDrive/My Drive/$sub" ] && \
        { printf '%s\n' "/Volumes/GoogleDrive/My Drive/$sub"; return 0; }
    return 1
}

# mtime in epoch seconds — BSD (macOS) then GNU fallback
mtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null; }

# ---- reconcile local files with Drive (newest-wins both ways) ----------------
do_sync() {
    local rc
    if ! rc="$(find_rc_hidden)"; then
        info "Google Drive not mounted — keeping local rc files as-is."
        return 0
    fi
    local name remote local rt lt
    for name in "${RC_FILES[@]}"; do
        remote="$rc/$name"; local="$HOME/$name"
        [ -e "$remote" ] || continue
        # A leftover symlink (old setup) or missing file: seed a real local copy.
        if [ -L "$local" ] || [ ! -e "$local" ]; then
            [ -L "$local" ] && rm -f "$local"
            cp -p "$remote" "$local" && info "seeded $name from Drive"
            continue
        fi
        rt="$(mtime "$remote")"; lt="$(mtime "$local")"
        [ -n "$rt" ] && [ -n "$lt" ] || continue
        if   [ "$rt" -gt "$lt" ]; then cp -p "$remote" "$local" && info "updated $name (Drive -> local)"
        elif [ "$lt" -gt "$rt" ]; then cp -p "$local" "$remote" && info "updated $name (local -> Drive)"
        fi
    done
}

# ---- migrate a single path from Drive-symlink to a real local file -----------
migrate_one() {
    local local="$1" name tgt tmp
    name="$(basename "$local")"
    [ -L "$local" ] || return 0
    tgt="$(readlink "$local")"
    case "$tgt" in
        *rc-files-hidden*) ;;      # ours to migrate
        *) return 0 ;;             # unrelated symlink, leave it
    esac
    if [ -e "$local" ]; then       # symlink resolves -> dereference to real file
        tmp="$(mktemp)"
        cp -p "$local" "$tmp" && rm -f "$local" && mv -f "$tmp" "$local" \
            && info "migrated $name (symlink -> local file)"
    else                            # broken symlink -> just drop it, sync reseeds
        rm -f "$local" && warn "removed broken symlink $name (will reseed from Drive)"
    fi
}

# ---- wire the login-time sync into a startup file (idempotent) ---------------
hook_block() {
    cat <<'EOF'
# >>> rc-sync hook >>>  refresh local rc files from Google Drive when available
[ -x "$HOME/.local/bin/rc-sync" ] && "$HOME/.local/bin/rc-sync" sync --quiet
# <<< rc-sync hook <<<
EOF
}

wire_startup() {
    local file="$1" mode="$2" tmp
    if [ -e "$file" ] && grep -q "$HOOK_MARK" "$file" 2>/dev/null; then
        info "hook already present in $(basename "$file")"; return 0
    fi
    if [ ! -e "$file" ]; then
        hook_block > "$file"; info "created $(basename "$file") with rc-sync hook"; return 0
    fi
    if [ "$mode" = prepend ]; then
        tmp="$(mktemp)"
        { hook_block; printf '\n'; cat "$file"; } > "$tmp" && mv -f "$tmp" "$file"
    else
        { printf '\n'; hook_block; } >> "$file"
    fi
    info "wired rc-sync into $(basename "$file")"
}

# ---- one-time install --------------------------------------------------------
do_install() {
    local name f
    info "migrating any Drive-symlinked rc files to local files..."
    for name in "${RC_FILES[@]}"; do migrate_one "$HOME/$name"; done

    # install this script as ~/.local/bin/rc-sync
    mkdir -p "$(dirname "$SELF_DEST")"
    local self; self="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
    if [ "$self" != "$SELF_DEST" ]; then
        cp "$0" "$SELF_DEST" && chmod +x "$SELF_DEST" && info "installed $SELF_DEST"
    else
        info "already running from $SELF_DEST"
    fi

    for f in "${STARTUP_PREPEND[@]}"; do wire_startup "$f" prepend; done
    for f in "${STARTUP_APPEND[@]}";  do [ -e "$f" ] && wire_startup "$f" append; done

    info "running initial sync..."
    do_sync
    info "install complete. New shells and tmux will now use local rc files that"
    info "refresh from Google Drive when it's mounted."
}

# ---- status ------------------------------------------------------------------
do_status() {
    local rc name local remote ls ds
    rc="$(find_rc_hidden)" && info "Drive: $rc" || warn "Drive not mounted"
    printf '%-22s %-12s %-12s\n' "FILE" "LOCAL" "DRIVE"
    for name in "${RC_FILES[@]}"; do
        local="$HOME/$name"; remote="${rc:+$rc/$name}"
        if   [ -L "$local" ]; then ls="symlink!"
        elif [ -f "$local" ]; then ls="$(mtime "$local")"
        else ls="missing"; fi
        if   [ -n "${rc:-}" ] && [ -f "$remote" ]; then ds="$(mtime "$remote")"
        else ds="-"; fi
        printf '%-22s %-12s %-12s\n' "$name" "$ls" "$ds"
    done
}

# ---- arg parsing -------------------------------------------------------------
main() {
    local cmd="sync" a
    [ $# -gt 0 ] && case "$1" in sync|install|status) cmd="$1"; shift;; esac
    for a in "$@"; do
        case "$a" in
            -q|--quiet) QUIET=1 ;;
            -h|--help)  cmd="help" ;;
        esac
    done
    case "$cmd" in
        sync)    do_sync ;;
        install) do_install ;;
        status)  do_status ;;
        help|*)  sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//' ;;
    esac
}

main "$@"
