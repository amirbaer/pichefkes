#!/usr/bin/env bash
#
# claude-top.sh - Monitor Claude processes with live updates (diff highlighting)
#
# Usage: ./claude-top.sh [interval]
#   interval: refresh interval in seconds (default: 2)
#

INTERVAL=${1:-2}

# Colors
BOLD=$'\033[1m'
DIM=$'\033[2m'
GREEN=$'\033[32m'
YELLOW=$'\033[33m'
CYAN=$'\033[36m'
RED=$'\033[31m'
RESET=$'\033[0m'
INVERSE=$'\033[7m'

HIDE_CURSOR=$'\033[?25l'
SHOW_CURSOR=$'\033[?25h'

# Temp file for state
STATE_FILE="/tmp/claude-top-state-$$"

cleanup() {
    echo -e "${SHOW_CURSOR}"
    tput cnorm 2>/dev/null
    rm -f "$STATE_FILE" "$STATE_FILE.new"
    exit 0
}
trap cleanup EXIT INT TERM

format_bytes() {
    local kb=$1
    if (( kb >= 1048576 )); then
        printf "%.1fG" "$(echo "scale=1; $kb / 1048576" | bc)"
    elif (( kb >= 1024 )); then
        printf "%dM" "$((kb / 1024))"
    else
        printf "%dK" "$kb"
    fi
}

get_color() {
    local val=$1 thresh_hi=$2 thresh_lo=$3
    if (( $(echo "$val > $thresh_hi" | bc -l) )); then
        echo "$RED"
    elif (( $(echo "$val > $thresh_lo" | bc -l) )); then
        echo "$YELLOW"
    else
        echo "$GREEN"
    fi
}

# Load previous state
declare -A PREV
load_state() {
    [[ -f "$STATE_FILE" ]] && source "$STATE_FILE"
}

save_state() {
    mv -f "$STATE_FILE.new" "$STATE_FILE" 2>/dev/null
}

echo -e "${HIDE_CURSOR}"
clear

while true; do
    load_state

    # Move cursor to top
    tput cup 0 0

    echo -e "${BOLD}Claude Process Monitor${RESET} ${DIM}(${INTERVAL}s refresh)${RESET}          "
    echo -e "${DIM}$(date '+%H:%M:%S')${RESET}    "
    echo ""

    # Gather data
    mapfile -t LINES < <(ps aux | grep -E '[c]laude' | grep -v 'chrome-native-host' | sort -k3 -rn)

    if (( ${#LINES[@]} == 0 )); then
        echo -e "${YELLOW}No Claude processes found${RESET}"
        tput ed
    else
        # Totals
        TOT_CPU=0 TOT_MEM=0 TOT_RSS=0
        for line in "${LINES[@]}"; do
            read -r _ _ cpu mem _ rss _ <<< "$line"
            TOT_CPU=$(echo "$TOT_CPU + $cpu" | bc)
            TOT_MEM=$(echo "$TOT_MEM + $mem" | bc)
            TOT_RSS=$((TOT_RSS + rss))
        done
        COUNT=${#LINES[@]}

        # Highlight totals if changed
        [[ "${PREV[TOT_CPU]}" != "$TOT_CPU" && -n "${PREV[TOT_CPU]}" ]] && INV_CPU=$INVERSE || INV_CPU=""
        [[ "${PREV[TOT_MEM]}" != "$TOT_MEM" && -n "${PREV[TOT_MEM]}" ]] && INV_MEM=$INVERSE || INV_MEM=""

        printf "${BOLD}%2d procs${RESET} | CPU: ${INV_CPU}${GREEN}%5.1f%%${RESET} | MEM: ${INV_MEM}${GREEN}%5.1f%%${RESET} | RSS: ${CYAN}%s${RESET}          \n" \
            "$COUNT" "$TOT_CPU" "$TOT_MEM" "$(format_bytes $TOT_RSS)"
        echo ""

        # Header
        printf "${DIM}%7s %7s %7s %7s %10s %s${RESET}\n" "PID" "CPU%" "MEM%" "RSS" "TIME" "START"
        echo -e "${DIM}-------------------------------------------------------${RESET}"

        # Save new state
        echo "# State" > "$STATE_FILE.new"
        echo "PREV[TOT_CPU]='$TOT_CPU'" >> "$STATE_FILE.new"
        echo "PREV[TOT_MEM]='$TOT_MEM'" >> "$STATE_FILE.new"

        for line in "${LINES[@]}"; do
            read -r _ pid cpu mem _ rss _ _ start time _ <<< "$line"

            cpu_color=$(get_color "$cpu" 50 20)
            mem_color=$(get_color "$mem" 5 2)

            # Diff highlighting
            [[ "${PREV[CPU_$pid]}" != "$cpu" && -n "${PREV[CPU_$pid]}" ]] && inv_c=$INVERSE || inv_c=""
            [[ "${PREV[MEM_$pid]}" != "$mem" && -n "${PREV[MEM_$pid]}" ]] && inv_m=$INVERSE || inv_m=""
            [[ "${PREV[RSS_$pid]}" != "$rss" && -n "${PREV[RSS_$pid]}" ]] && inv_r=$INVERSE || inv_r=""

            printf "%7s ${inv_c}${cpu_color}%6s%%${RESET} ${inv_m}${mem_color}%6s%%${RESET} ${inv_r}%7s${RESET} %10s ${DIM}%s${RESET}\n" \
                "$pid" "$cpu" "$mem" "$(format_bytes $rss)" "$time" "$start"

            echo "PREV[CPU_$pid]='$cpu'" >> "$STATE_FILE.new"
            echo "PREV[MEM_$pid]='$mem'" >> "$STATE_FILE.new"
            echo "PREV[RSS_$pid]='$rss'" >> "$STATE_FILE.new"
        done

        save_state
        tput ed
    fi

    echo ""
    echo -e "${DIM}q=quit${RESET}    "

    read -t "$INTERVAL" -n 1 key 2>/dev/null && [[ $key == "q" || $key == "Q" ]] && break
done
