#!/bin/bash
# bashargparse - A simple bash implementation of Python's argparse
#
# Usage: source bashargparse.sh
#
# Provides functions:
#   argparse_init     - Initialize the parser
#   add_argument      - Define arguments (flags, options, positionals)
#   argparse_parse    - Parse command line arguments

# Prevent multiple sourcing
[[ -n "$_BASHARGPARSE_LOADED" ]] && return 0
_BASHARGPARSE_LOADED=1

# Version
BASHARGPARSE_VERSION="0.1.0"

# =============================================================================
# Internal State Variables
# =============================================================================

# Parser metadata
_ARGPARSE_PROG=""
_ARGPARSE_DESCRIPTION=""

# Argument storage (indexed arrays)
# Each argument is stored with an index, and properties are stored in parallel arrays
_ARGPARSE_ARG_COUNT=0

# Argument properties (parallel arrays indexed by argument number)
declare -a _ARGPARSE_SHORT       # Short flag (-v)
declare -a _ARGPARSE_LONG        # Long flag (--verbose)
declare -a _ARGPARSE_POSITIONAL  # Positional name (for positional args)
declare -a _ARGPARSE_HELP        # Help text
declare -a _ARGPARSE_DEFAULT     # Default value
declare -a _ARGPARSE_REQUIRED    # Required flag (0/1)
declare -a _ARGPARSE_TYPE        # Type (string, int)
declare -a _ARGPARSE_CHOICES     # Comma-separated choices
declare -a _ARGPARSE_ACTION      # Action (store, store_true, count)
declare -a _ARGPARSE_NARGS       # nargs value (number, +, *)
declare -a _ARGPARSE_DEST        # Destination variable name

# Track positional arguments order
declare -a _ARGPARSE_POSITIONAL_ORDER

# =============================================================================
# Internal Helper Functions
# =============================================================================

# Convert flag name to variable name: --my-flag -> MY_FLAG
_argparse_to_varname() {
    local name="$1"
    # Remove leading dashes, convert to uppercase, replace - with _
    echo "$name" | sed 's/^-*//; s/-/_/g' | tr '[:lower:]' '[:upper:]'
}

# Reset all internal state
_argparse_reset() {
    _ARGPARSE_PROG=""
    _ARGPARSE_DESCRIPTION=""
    _ARGPARSE_ARG_COUNT=0
    _ARGPARSE_SHORT=()
    _ARGPARSE_LONG=()
    _ARGPARSE_POSITIONAL=()
    _ARGPARSE_HELP=()
    _ARGPARSE_DEFAULT=()
    _ARGPARSE_REQUIRED=()
    _ARGPARSE_TYPE=()
    _ARGPARSE_CHOICES=()
    _ARGPARSE_ACTION=()
    _ARGPARSE_NARGS=()
    _ARGPARSE_DEST=()
    _ARGPARSE_POSITIONAL_ORDER=()
}

# Initialize state on first load
_argparse_reset

# =============================================================================
# Public API Functions
# =============================================================================

# Initialize the argument parser
# Usage: argparse_init [program_name] [description]
#
# Arguments:
#   program_name  - Name of the program (default: script name)
#   description   - Description shown in help (default: empty)
#
# Example:
#   argparse_init 'myprogram' 'A tool for processing files'
#
argparse_init() {
    local prog="${1:-}"
    local desc="${2:-}"

    # Reset all state to allow re-initialization
    _argparse_reset

    # Set program name (default to script name if not provided)
    if [[ -n "$prog" ]]; then
        _ARGPARSE_PROG="$prog"
    else
        _ARGPARSE_PROG="$(basename "${BASH_SOURCE[-1]:-$0}")"
    fi

    # Set description
    _ARGPARSE_DESCRIPTION="$desc"
}

# Add an argument definition
# Usage: add_argument [options]
#
# Options:
#   -s, --short FLAG     Short flag (without dash, e.g., 'v' for -v)
#   -l, --long FLAG      Long flag (without dashes, e.g., 'verbose' for --verbose)
#   -p, --positional NAME  Positional argument name (e.g., 'filename')
#   -h, --help TEXT      Help text for this argument
#   -d, --default VALUE  Default value
#   -a, --action ACTION  Action: store (default), store_true
#
# For boolean flags (store_true):
#   add_argument -s v -l verbose -a store_true -h 'Enable verbose mode'
#
# For value flags (store):
#   add_argument -s o -l output -d '/tmp/out' -h 'Output file'
#   add_argument -l config -h 'Config file path'
#
# For positional arguments:
#   add_argument -p filename -h 'Input file to process'
#   add_argument --positional output_dir --help 'Output directory'
#
add_argument() {
    local short=""
    local long=""
    local positional=""
    local help=""
    local default=""
    local default_was_set=0
    local action=""
    local dest=""

    # Parse options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -s|--short)
                short="$2"
                shift 2
                ;;
            -l|--long)
                long="$2"
                shift 2
                ;;
            -p|--positional)
                positional="$2"
                shift 2
                ;;
            -h|--help)
                help="$2"
                shift 2
                ;;
            -d|--default)
                default="$2"
                default_was_set=1
                shift 2
                ;;
            -a|--action)
                action="$2"
                shift 2
                ;;
            *)
                echo "add_argument: unknown option: $1" >&2
                return 1
                ;;
        esac
    done

    # Validate: for positional args, only positional should be set
    # For flags, at least short or long must be provided
    if [[ -n "$positional" ]]; then
        # Positional argument mode
        if [[ -n "$short" || -n "$long" ]]; then
            echo "add_argument: positional arguments cannot have -s/--short or -l/--long flags" >&2
            return 1
        fi
        # Positional arguments use 'store' action and cannot use store_true
        if [[ "$action" == "store_true" ]]; then
            echo "add_argument: positional arguments cannot use 'store_true' action" >&2
            return 1
        fi
    else
        # Flag mode - need at least short or long
        if [[ -z "$short" && -z "$long" ]]; then
            echo "add_argument: must provide at least -s/--short, -l/--long, or -p/--positional" >&2
            return 1
        fi
    fi

    # Determine action if not explicitly set
    if [[ -z "$action" ]]; then
        action="store"
    fi

    # Determine destination variable name
    # Priority: positional name > long flag > short flag
    if [[ -n "$positional" ]]; then
        dest="$(_argparse_to_varname "$positional")"
    elif [[ -n "$long" ]]; then
        dest="$(_argparse_to_varname "$long")"
    else
        dest="$(_argparse_to_varname "$short")"
    fi

    # Set default value based on action if not explicitly provided
    if [[ $default_was_set -eq 0 ]]; then
        case "$action" in
            store_true)
                default="0"
                ;;
            store)
                default=""
                ;;
            *)
                default=""
                ;;
        esac
    fi

    # Store the argument in parallel arrays
    local idx=$_ARGPARSE_ARG_COUNT
    _ARGPARSE_SHORT[$idx]="$short"
    _ARGPARSE_LONG[$idx]="$long"
    _ARGPARSE_POSITIONAL[$idx]="$positional"
    _ARGPARSE_HELP[$idx]="$help"
    _ARGPARSE_DEFAULT[$idx]="$default"
    _ARGPARSE_REQUIRED[$idx]="0"
    _ARGPARSE_TYPE[$idx]="string"
    _ARGPARSE_CHOICES[$idx]=""
    _ARGPARSE_ACTION[$idx]="$action"
    _ARGPARSE_NARGS[$idx]=""
    _ARGPARSE_DEST[$idx]="$dest"

    # Track positional arguments in order for parsing
    if [[ -n "$positional" ]]; then
        _ARGPARSE_POSITIONAL_ORDER+=("$idx")
    fi

    # Increment argument count
    ((_ARGPARSE_ARG_COUNT++))
}
