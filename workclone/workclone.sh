#!/usr/bin/env bash
# workclone - git clone helper with auto-incrementing directories
#
# Source with configuration:
#   export WORKCLONE_ORG=gytpol WORKCLONE_DIR=~/remedio/tmp
#   source <(curl -sL https://raw.githubusercontent.com/amirbaer/pichefkes/main/workclone/workclone.sh)
#
# Or source locally:
#   export WORKCLONE_ORG=gytpol WORKCLONE_DIR=~/remedio/tmp
#   source ~/Home/code/pichefkes/workclone/workclone.sh

WORKCLONE_ORG="${WORKCLONE_ORG:-}"
WORKCLONE_DIR="${WORKCLONE_DIR:-}"

if [[ -z "$WORKCLONE_ORG" || -z "$WORKCLONE_DIR" ]]; then
  echo "workclone.sh: WORKCLONE_ORG and WORKCLONE_DIR must be set before sourcing"
  return 1 2>/dev/null || exit 1
fi

function workclone() {
  local repo="$1"
  if [[ -z "$repo" ]]; then
    echo "Usage: workclone <repo-name>"
    return 1
  fi

  local dir="$repo"
  if [[ -d "$dir" ]]; then
    local i=1
    while [[ -d "${repo}-${i}" ]]; do
      ((i++))
    done
    dir="${repo}-${i}"
  fi

  git clone "git@github.com:${WORKCLONE_ORG}/${repo}.git" "$dir" && cd "$dir"
}

function workalready() {
  [[ $# -eq 0 ]] && { echo "Usage: workalready <repo-name>"; return 1; }
  cd "$WORKCLONE_DIR" && workclone "$@" && tmux
}

# internal helper: builds ordered list of clone dirs
_workclone_dirs() {
  local dirs=()
  for dir in "$WORKCLONE_DIR"/*/; do
    [[ -d "$dir/.git" ]] && dirs+=("$dir")
  done
  printf '%s\n' "${dirs[@]}"
}

function workls() {
  if [[ ! -d "$WORKCLONE_DIR" ]]; then
    echo "No clones directory found at $WORKCLONE_DIR"
    return 1
  fi

  local dim=$'\033[90m' cyan=$'\033[36m' rst=$'\033[0m'
  local green=$'\033[38;5;114m' yellow=$'\033[38;5;216m'

  # collect data first to compute column widths
  local names=() branches=() statuses=() dates=() date_colors=()
  while IFS= read -r dir; do
    names+=("$(basename "$dir")")
    local branch=$(git -C "$dir" branch --show-current 2>/dev/null || echo "detached")
    branches+=("$branch")
    if [[ -n $(git -C "$dir" status --porcelain 2>/dev/null) ]]; then
      statuses+=("dirty")
    else
      statuses+=("clean")
    fi
    local modified="" dcol="$dim"
    if [[ "$(uname)" == "Darwin" ]]; then
      modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$dir" 2>/dev/null)
      local mod_epoch=$(stat -f "%m" "$dir" 2>/dev/null)
    else
      modified=$(stat -c "%y" "$dir" 2>/dev/null | cut -d. -f1)
      local mod_epoch=$(stat -c "%Y" "$dir" 2>/dev/null)
    fi
    if [[ -n "$mod_epoch" ]]; then
      local now_epoch=$(date "+%s")
      local age_hours=$(( (now_epoch - mod_epoch) / 3600 ))
      if (( age_hours < 1 )); then
        dcol=$'\033[38;5;48m'
      elif (( age_hours < 6 )); then
        dcol=$'\033[38;5;114m'
      elif (( age_hours < 24 )); then
        dcol=$'\033[38;5;229m'
      elif (( age_hours < 48 )); then
        dcol=$'\033[38;5;216m'
      elif (( age_hours < 168 )); then
        dcol=$'\033[38;5;249m'
      else
        dcol=$'\033[38;5;242m'
      fi
    fi
    dates+=("$modified")
    date_colors+=("$dcol")
  done < <(_workclone_dirs)

  # compute dynamic column widths
  local wn=4 wb=6 ws=6
  local _n
  for _n in "${names[@]}"; do (( ${#_n} > wn )) && wn=${#_n}; done
  for _n in "${branches[@]}"; do (( ${#_n} > wb )) && wb=${#_n}; done

  # header
  printf "${dim}%-4s  %-${wn}s  %-${wb}s  %-${ws}s  %s${rst}\n" "#" "REPO" "BRANCH" "STATUS" "MODIFIED"

  # rows
  local idx=0
  while [[ $idx -lt ${#names[@]} ]]; do
    local _name="${names[$((idx + ${_WS_ARR_BASE:-0}))]}"
    local _branch="${branches[$((idx + ${_WS_ARR_BASE:-0}))]}"
    local _status="${statuses[$((idx + ${_WS_ARR_BASE:-0}))]}"
    local _date="${dates[$((idx + ${_WS_ARR_BASE:-0}))]}"
    local _dcol="${date_colors[$((idx + ${_WS_ARR_BASE:-0}))]}"
    local scol="$green"
    [[ "$_status" == "dirty" ]] && scol="$yellow"
    printf "${cyan}%-4s${rst}  %-${wn}s  %-${wb}s  ${scol}%-${ws}s${rst}  ${_dcol}%s${rst}\n" "$((idx + 1))" "$_name" "$_branch" "$_status" "$_date"
    idx=$((idx + 1))
  done
}

function workcd() {
  if [[ -z "$1" ]]; then
    echo "Usage: workcd <index>"
    return 1
  fi

  local target_idx="$1"
  local idx=1
  while IFS= read -r dir; do
    if [[ "$idx" -eq "$target_idx" ]]; then
      cd "$dir"
      return 0
    fi
    ((idx++))
  done < <(_workclone_dirs)

  echo "No clone at index $target_idx"
  return 1
}
