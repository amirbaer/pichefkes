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
#   -r, --required       Mark argument as required
#   -t, --type TYPE      Type validation: string (default), int
#   -a, --action ACTION  Action: store (default), store_true
#
# For boolean flags (store_true):
#   add_argument -s v -l verbose -a store_true -h 'Enable verbose mode'
#
# For value flags (store):
#   add_argument -s o -l output -d '/tmp/out' -h 'Output file'
#   add_argument -l config -r -h 'Config file path (required)'
#
# For integer arguments:
#   add_argument -l port -t int -d '8080' -h 'Port number'
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
    local required=0
    local type="string"
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
            -r|--required)
                required=1
                shift 1
                ;;
            -t|--type)
                type="$2"
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

    # Validate type option
    if [[ "$type" != "string" && "$type" != "int" ]]; then
        echo "add_argument: invalid type '$type' (must be 'string' or 'int')" >&2
        return 1
    fi

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

    # Validate: type validation doesn't make sense for store_true
    if [[ "$type" == "int" && "$action" == "store_true" ]]; then
        echo "add_argument: type 'int' cannot be used with 'store_true' action" >&2
        return 1
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
    _ARGPARSE_REQUIRED[$idx]="$required"
    _ARGPARSE_TYPE[$idx]="$type"
    _ARGPARSE_CHOICES[$idx]=""
    _ARGPARSE_ACTION[$idx]="$action"
    _ARGPARSE_NARGS[$idx]=""
    _ARGPARSE_DEST[$idx]="$dest"

    # Track positional arguments in order for parsing
    if [[ -n "$positional" ]]; then
        _ARGPARSE_POSITIONAL_ORDER+=("$idx")
    fi

    # Increment argument count
    _ARGPARSE_ARG_COUNT=$((_ARGPARSE_ARG_COUNT + 1))
}

# Validate that a value is an integer
# Usage: _argparse_is_int value
# Returns: 0 if value is an integer, 1 otherwise
_argparse_is_int() {
    local value="$1"
    # Match optional leading minus/plus sign followed by one or more digits
    [[ "$value" =~ ^[+-]?[0-9]+$ ]]
}

# Print short usage line (for error messages)
# Usage: _argparse_usage
_argparse_usage() {
    local prog="$_ARGPARSE_PROG"
    local usage="usage: $prog [options]"
    for idx in "${_ARGPARSE_POSITIONAL_ORDER[@]}"; do
        local pos_name="${_ARGPARSE_POSITIONAL[$idx]}"
        usage="$usage $pos_name"
    done
    echo "$usage" >&2
}

# Display help message and exit
# Usage: argparse_help
#
# This function generates and prints a formatted help message based on
# the parser configuration and all defined arguments.
#
argparse_help() {
    local prog="$_ARGPARSE_PROG"
    local desc="$_ARGPARSE_DESCRIPTION"

    # Build usage line
    local usage="usage: $prog"

    # Always add [options] since -h/--help is always available
    usage="$usage [options]"

    # Add positional arguments to usage
    for idx in "${_ARGPARSE_POSITIONAL_ORDER[@]}"; do
        local pos_name="${_ARGPARSE_POSITIONAL[$idx]}"
        usage="$usage $pos_name"
    done

    echo "$usage"
    echo

    # Print description if provided
    if [[ -n "$desc" ]]; then
        echo "$desc"
        echo
    fi

    # Print positional arguments section
    if [[ ${#_ARGPARSE_POSITIONAL_ORDER[@]} -gt 0 ]]; then
        echo "positional arguments:"
        for idx in "${_ARGPARSE_POSITIONAL_ORDER[@]}"; do
            local pos_name="${_ARGPARSE_POSITIONAL[$idx]}"
            local help_text="${_ARGPARSE_HELP[$idx]}"
            local default="${_ARGPARSE_DEFAULT[$idx]}"
            local required="${_ARGPARSE_REQUIRED[$idx]}"

            # Format: "  name          help text"
            printf "  %-20s" "$pos_name"
            if [[ -n "$help_text" ]]; then
                printf "%s" "$help_text"
            fi
            if [[ "$required" == "1" ]]; then
                printf " (required)"
            elif [[ -n "$default" ]]; then
                printf " (default: %s)" "$default"
            fi
            echo
        done
        echo
    fi

    # Print options section (always shown since -h/--help is always available)
    echo "options:"
    # Always show -h, --help first
    printf "  %-20s%s\n" "-h, --help" "show this help message and exit"

    for ((idx=0; idx < _ARGPARSE_ARG_COUNT; idx++)); do
        local short="${_ARGPARSE_SHORT[$idx]}"
        local long="${_ARGPARSE_LONG[$idx]}"
        local help_text="${_ARGPARSE_HELP[$idx]}"
        local default="${_ARGPARSE_DEFAULT[$idx]}"
        local action="${_ARGPARSE_ACTION[$idx]}"

        # Skip positional arguments
        if [[ -n "${_ARGPARSE_POSITIONAL[$idx]}" ]]; then
            continue
        fi

        # Build the flag string
        local flag_str=""
        if [[ -n "$short" && -n "$long" ]]; then
            if [[ "$action" == "store" ]]; then
                flag_str="-$short, --$long VALUE"
            else
                flag_str="-$short, --$long"
            fi
        elif [[ -n "$short" ]]; then
            if [[ "$action" == "store" ]]; then
                flag_str="-$short VALUE"
            else
                flag_str="-$short"
            fi
        else
            if [[ "$action" == "store" ]]; then
                flag_str="--$long VALUE"
            else
                flag_str="--$long"
            fi
        fi

        # Format output
        printf "  %-20s" "$flag_str"
        if [[ -n "$help_text" ]]; then
            printf "%s" "$help_text"
        fi
        # Show required indicator
        if [[ "${_ARGPARSE_REQUIRED[$idx]}" == "1" ]]; then
            printf " (required)"
        # Show default for store actions (not for store_true where default is always 0)
        elif [[ "$action" == "store" && -n "$default" ]]; then
            printf " (default: %s)" "$default"
        fi
        echo
    done
}

# Parse command line arguments
# Usage: argparse_parse "$@"
#
# This function parses the provided arguments and sets result variables.
# Variables are named ARG_<DEST> where DEST is derived from the argument name.
#
# Example:
#   argparse_init 'myprogram' 'A demo program'
#   add_argument -s v -l verbose -a store_true -h 'Verbose mode'
#   add_argument -l output -d '/tmp/out' -h 'Output file'
#   add_argument -p filename -h 'Input file'
#   argparse_parse "$@"
#   # Now available: $ARG_VERBOSE, $ARG_OUTPUT, $ARG_FILENAME
#
argparse_parse() {
    local -a args=("$@")
    local -a positional_values=()
    local -a _arg_was_provided=()  # Track which args were provided (by index)
    local i=0

    # Check for help flags first (before any other processing)
    for arg in "${args[@]}"; do
        if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
            argparse_help
            exit 0
        fi
    done

    # Initialize all arguments with their default values and tracking
    for ((idx=0; idx < _ARGPARSE_ARG_COUNT; idx++)); do
        local dest="${_ARGPARSE_DEST[$idx]}"
        local default="${_ARGPARSE_DEFAULT[$idx]}"
        # Export as ARG_<DEST>
        declare -g "ARG_${dest}=${default}"
        _arg_was_provided[$idx]=0
    done

    # Parse arguments
    while [[ $i -lt ${#args[@]} ]]; do
        local arg="${args[$i]}"
        local matched=0

        # Check if it's a flag (starts with -)
        if [[ "$arg" == -* ]]; then
            # Try to match against defined flags
            for ((idx=0; idx < _ARGPARSE_ARG_COUNT; idx++)); do
                local short="${_ARGPARSE_SHORT[$idx]}"
                local long="${_ARGPARSE_LONG[$idx]}"
                local action="${_ARGPARSE_ACTION[$idx]}"
                local dest="${_ARGPARSE_DEST[$idx]}"

                # Skip positional arguments (they don't have flags)
                if [[ -n "${_ARGPARSE_POSITIONAL[$idx]}" ]]; then
                    continue
                fi

                # Check for match
                local is_match=0
                if [[ -n "$short" && "$arg" == "-$short" ]]; then
                    is_match=1
                elif [[ -n "$long" && "$arg" == "--$long" ]]; then
                    is_match=1
                fi

                if [[ $is_match -eq 1 ]]; then
                    matched=1
                    _arg_was_provided[$idx]=1

                    case "$action" in
                        store_true)
                            # Set to 1
                            declare -g "ARG_${dest}=1"
                            ;;
                        store)
                            # Get the next argument as the value
                            i=$((i + 1))
                            if [[ $i -ge ${#args[@]} ]]; then
                                echo "Error: $arg requires a value" >&2
                                return 1
                            fi
                            local value="${args[$i]}"
                            # Type validation
                            local arg_type="${_ARGPARSE_TYPE[$idx]}"
                            if [[ "$arg_type" == "int" ]]; then
                                if ! _argparse_is_int "$value"; then
                                    _argparse_usage
                                    echo "$_ARGPARSE_PROG: error: argument $arg: invalid int value: '$value'" >&2
                                    return 1
                                fi
                            fi
                            declare -g "ARG_${dest}=${value}"
                            ;;
                    esac
                    break
                fi
            done

            # Check for unknown flag
            if [[ $matched -eq 0 ]]; then
                echo "Error: unknown option: $arg" >&2
                return 1
            fi
        else
            # Not a flag - treat as positional argument
            positional_values+=("$arg")
        fi

        i=$((i + 1))
    done

    # Assign positional values to positional arguments in order
    local pos_count=${#_ARGPARSE_POSITIONAL_ORDER[@]}
    local val_count=${#positional_values[@]}

    for ((p=0; p < pos_count && p < val_count; p++)); do
        local idx="${_ARGPARSE_POSITIONAL_ORDER[$p]}"
        local dest="${_ARGPARSE_DEST[$idx]}"
        local value="${positional_values[$p]}"
        local pos_name="${_ARGPARSE_POSITIONAL[$idx]}"
        # Type validation for positional arguments
        local arg_type="${_ARGPARSE_TYPE[$idx]}"
        if [[ "$arg_type" == "int" ]]; then
            if ! _argparse_is_int "$value"; then
                _argparse_usage
                echo "$_ARGPARSE_PROG: error: argument $pos_name: invalid int value: '$value'" >&2
                return 1
            fi
        fi
        declare -g "ARG_${dest}=${value}"
        _arg_was_provided[$idx]=1
    done

    # Validate required arguments
    local missing_args=()
    for ((idx=0; idx < _ARGPARSE_ARG_COUNT; idx++)); do
        local required="${_ARGPARSE_REQUIRED[$idx]}"
        if [[ "$required" == "1" && "${_arg_was_provided[$idx]}" == "0" ]]; then
            # Build argument name for error message
            local arg_name=""
            if [[ -n "${_ARGPARSE_POSITIONAL[$idx]}" ]]; then
                arg_name="${_ARGPARSE_POSITIONAL[$idx]}"
            elif [[ -n "${_ARGPARSE_LONG[$idx]}" ]]; then
                arg_name="--${_ARGPARSE_LONG[$idx]}"
            else
                arg_name="-${_ARGPARSE_SHORT[$idx]}"
            fi
            missing_args+=("$arg_name")
        fi
    done

    # Report missing required arguments
    if [[ ${#missing_args[@]} -gt 0 ]]; then
        _argparse_usage
        for arg in "${missing_args[@]}"; do
            echo "$_ARGPARSE_PROG: error: the following argument is required: $arg" >&2
        done
        return 1
    fi

    return 0
}
