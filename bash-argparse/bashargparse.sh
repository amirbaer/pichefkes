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
#   -c, --choices LIST   Comma-separated list of valid choices
#   -a, --action ACTION  Action: store (default), store_true, count
#   -n, --nargs VALUE    Number of args: + (one or more), * (zero or more), or a number
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
# For choices validation:
#   add_argument -l level -c 'debug,info,warn,error' -h 'Log level'
#
# For count action (flag can be repeated: -vvv = 3):
#   add_argument -s v -l verbose -a count -h 'Verbosity level'
#
# For multiple values (nargs):
#   add_argument -l files -n '+' -h 'One or more files'
#   add_argument -l items -n '*' -h 'Zero or more items'
#   add_argument -l coords -n 3 -h 'Exactly 3 coordinates'
#   add_argument -p inputs -n '+' -h 'One or more input files'
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
    local choices=""
    local action=""
    local nargs=""
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
            -c|--choices)
                choices="$2"
                shift 2
                ;;
            -a|--action)
                action="$2"
                shift 2
                ;;
            -n|--nargs)
                nargs="$2"
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

    # Validate: type validation doesn't make sense for store_true or count
    if [[ "$type" == "int" && ( "$action" == "store_true" || "$action" == "count" ) ]]; then
        echo "add_argument: type 'int' cannot be used with '$action' action" >&2
        return 1
    fi

    # Validate: choices validation doesn't make sense for store_true or count
    if [[ -n "$choices" && ( "$action" == "store_true" || "$action" == "count" ) ]]; then
        echo "add_argument: choices cannot be used with '$action' action" >&2
        return 1
    fi

    # Validate nargs option: must be +, *, or a positive integer
    if [[ -n "$nargs" ]]; then
        if [[ "$nargs" != "+" && "$nargs" != "*" ]]; then
            # Must be a positive integer
            if ! [[ "$nargs" =~ ^[1-9][0-9]*$ ]]; then
                echo "add_argument: invalid nargs value '$nargs' (must be '+', '*', or a positive integer)" >&2
                return 1
            fi
        fi
    fi

    # Validate: nargs doesn't make sense for store_true or count
    if [[ -n "$nargs" && ( "$action" == "store_true" || "$action" == "count" ) ]]; then
        echo "add_argument: nargs cannot be used with '$action' action" >&2
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
            count)
                default="0"
                ;;
            store)
                # For nargs, default is empty (will be space-separated list)
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
    _ARGPARSE_CHOICES[$idx]="$choices"
    _ARGPARSE_ACTION[$idx]="$action"
    _ARGPARSE_NARGS[$idx]="$nargs"
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

# Validate that a value is one of the allowed choices
# Usage: _argparse_in_choices value choices_csv
# Returns: 0 if value is in choices, 1 otherwise
_argparse_in_choices() {
    local value="$1"
    local choices_csv="$2"
    local IFS=','
    local choice
    for choice in $choices_csv; do
        if [[ "$value" == "$choice" ]]; then
            return 0
        fi
    done
    return 1
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
        local pos_nargs="${_ARGPARSE_NARGS[$idx]}"
        local pos_required="${_ARGPARSE_REQUIRED[$idx]}"

        if [[ "$pos_nargs" == "+" ]]; then
            usage="$usage $pos_name [${pos_name}...]"
        elif [[ "$pos_nargs" == "*" ]]; then
            usage="$usage [${pos_name}...]"
        elif [[ -n "$pos_nargs" ]]; then
            # Specific number
            for ((n=0; n < pos_nargs; n++)); do
                usage="$usage $pos_name"
            done
        else
            usage="$usage $pos_name"
        fi
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
            local choices="${_ARGPARSE_CHOICES[$idx]}"

            # Format: "  name          help text"
            printf "  %-28s" "$pos_name"
            if [[ -n "$help_text" ]]; then
                printf " %s" "$help_text"
            fi
            # Show choices if defined
            if [[ -n "$choices" ]]; then
                printf " (choices: %s)" "$choices"
            elif [[ "$required" == "1" ]]; then
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
    printf "  %-28s %s\n" "-h, --help" "show this help message and exit"

    for ((idx=0; idx < _ARGPARSE_ARG_COUNT; idx++)); do
        local short="${_ARGPARSE_SHORT[$idx]}"
        local long="${_ARGPARSE_LONG[$idx]}"
        local help_text="${_ARGPARSE_HELP[$idx]}"
        local default="${_ARGPARSE_DEFAULT[$idx]}"
        local action="${_ARGPARSE_ACTION[$idx]}"
        local choices="${_ARGPARSE_CHOICES[$idx]}"
        local arg_nargs="${_ARGPARSE_NARGS[$idx]}"

        # Skip positional arguments
        if [[ -n "${_ARGPARSE_POSITIONAL[$idx]}" ]]; then
            continue
        fi

        # Build VALUE indicator based on nargs
        local value_indicator=""
        if [[ "$action" == "store" ]]; then
            if [[ "$arg_nargs" == "+" ]]; then
                value_indicator=" VALUE [VALUE...]"
            elif [[ "$arg_nargs" == "*" ]]; then
                value_indicator=" [VALUE...]"
            elif [[ -n "$arg_nargs" ]]; then
                # Specific number
                for ((n=0; n < arg_nargs; n++)); do
                    value_indicator="$value_indicator VALUE"
                done
            else
                value_indicator=" VALUE"
            fi
        fi

        # Build the flag string
        local flag_str=""
        if [[ -n "$short" && -n "$long" ]]; then
            flag_str="-$short, --$long${value_indicator}"
        elif [[ -n "$short" ]]; then
            flag_str="-$short${value_indicator}"
        else
            flag_str="--$long${value_indicator}"
        fi

        # Format output
        printf "  %-28s" "$flag_str"
        if [[ -n "$help_text" ]]; then
            printf " %s" "$help_text"
        fi
        # Show choices if defined
        if [[ -n "$choices" ]]; then
            printf " (choices: %s)" "$choices"
        # Show required indicator
        elif [[ "${_ARGPARSE_REQUIRED[$idx]}" == "1" ]]; then
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
            # Handle combined short flags like -vvv (multiple same flags combined)
            # This only applies to single-dash flags with more than one character after the dash
            # and only if all characters are the same (e.g., -vvv but not -vxy)
            if [[ "$arg" =~ ^-([a-zA-Z]+)$ && ${#arg} -gt 2 ]]; then
                local flag_chars="${BASH_REMATCH[1]}"
                local first_char="${flag_chars:0:1}"
                local all_same=1
                local char_count=${#flag_chars}

                # Check if all characters are the same
                for ((c=1; c < char_count; c++)); do
                    if [[ "${flag_chars:$c:1}" != "$first_char" ]]; then
                        all_same=0
                        break
                    fi
                done

                if [[ $all_same -eq 1 ]]; then
                    # Find if this is a valid count or store_true flag
                    local found_idx=-1
                    for ((idx=0; idx < _ARGPARSE_ARG_COUNT; idx++)); do
                        local short="${_ARGPARSE_SHORT[$idx]}"
                        if [[ "$short" == "$first_char" ]]; then
                            local action="${_ARGPARSE_ACTION[$idx]}"
                            if [[ "$action" == "count" || "$action" == "store_true" ]]; then
                                found_idx=$idx
                                break
                            fi
                        fi
                    done

                    if [[ $found_idx -ge 0 ]]; then
                        local action="${_ARGPARSE_ACTION[$found_idx]}"
                        local dest="${_ARGPARSE_DEST[$found_idx]}"
                        _arg_was_provided[$found_idx]=1

                        if [[ "$action" == "count" ]]; then
                            # Add the count
                            local current_val
                            eval "current_val=\$ARG_${dest}"
                            declare -g "ARG_${dest}=$((current_val + char_count))"
                        else
                            # store_true - just set to 1
                            declare -g "ARG_${dest}=1"
                        fi
                        i=$((i + 1))
                        continue
                    fi
                fi
                # If not found or not a count/store_true flag, fall through to regular processing
            fi

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
                        count)
                            # Increment the counter
                            local current_val
                            eval "current_val=\$ARG_${dest}"
                            declare -g "ARG_${dest}=$((current_val + 1))"
                            ;;
                        store)
                            local arg_nargs="${_ARGPARSE_NARGS[$idx]}"
                            local arg_type="${_ARGPARSE_TYPE[$idx]}"
                            local arg_choices="${_ARGPARSE_CHOICES[$idx]}"
                            local collected_values=()
                            local num_to_collect=1

                            # Determine how many values to collect based on nargs
                            if [[ -n "$arg_nargs" ]]; then
                                if [[ "$arg_nargs" == "+" || "$arg_nargs" == "*" ]]; then
                                    # Collect all following non-flag arguments
                                    num_to_collect=-1  # Special value meaning "until next flag"
                                else
                                    # Specific number
                                    num_to_collect="$arg_nargs"
                                fi
                            fi

                            if [[ $num_to_collect -eq -1 ]]; then
                                # Collect values until next flag or end of args
                                while [[ $((i + 1)) -lt ${#args[@]} ]]; do
                                    local next_arg="${args[$((i + 1))]}"
                                    # Stop if we hit a flag (starts with -)
                                    if [[ "$next_arg" == -* ]]; then
                                        break
                                    fi
                                    i=$((i + 1))
                                    local value="${args[$i]}"
                                    # Type validation
                                    if [[ "$arg_type" == "int" ]]; then
                                        if ! _argparse_is_int "$value"; then
                                            _argparse_usage
                                            echo "$_ARGPARSE_PROG: error: argument $arg: invalid int value: '$value'" >&2
                                            return 1
                                        fi
                                    fi
                                    # Choices validation
                                    if [[ -n "$arg_choices" ]]; then
                                        if ! _argparse_in_choices "$value" "$arg_choices"; then
                                            _argparse_usage
                                            echo "$_ARGPARSE_PROG: error: argument $arg: invalid choice: '$value' (choose from: $arg_choices)" >&2
                                            return 1
                                        fi
                                    fi
                                    collected_values+=("$value")
                                done

                                # Validate we got at least one for '+'
                                if [[ "$arg_nargs" == "+" && ${#collected_values[@]} -eq 0 ]]; then
                                    _argparse_usage
                                    echo "$_ARGPARSE_PROG: error: argument $arg: expected at least one argument" >&2
                                    return 1
                                fi

                                # Store as space-separated string
                                declare -g "ARG_${dest}=${collected_values[*]}"
                            else
                                # Collect exactly num_to_collect values
                                for ((n=0; n < num_to_collect; n++)); do
                                    i=$((i + 1))
                                    if [[ $i -ge ${#args[@]} ]]; then
                                        if [[ $num_to_collect -eq 1 ]]; then
                                            echo "Error: $arg requires a value" >&2
                                        else
                                            _argparse_usage
                                            echo "$_ARGPARSE_PROG: error: argument $arg: expected $num_to_collect argument(s)" >&2
                                        fi
                                        return 1
                                    fi
                                    local value="${args[$i]}"
                                    # Type validation
                                    if [[ "$arg_type" == "int" ]]; then
                                        if ! _argparse_is_int "$value"; then
                                            _argparse_usage
                                            echo "$_ARGPARSE_PROG: error: argument $arg: invalid int value: '$value'" >&2
                                            return 1
                                        fi
                                    fi
                                    # Choices validation
                                    if [[ -n "$arg_choices" ]]; then
                                        if ! _argparse_in_choices "$value" "$arg_choices"; then
                                            _argparse_usage
                                            echo "$_ARGPARSE_PROG: error: argument $arg: invalid choice: '$value' (choose from: $arg_choices)" >&2
                                            return 1
                                        fi
                                    fi
                                    collected_values+=("$value")
                                done

                                # Store result: single value for nargs=1, space-separated for others
                                if [[ $num_to_collect -eq 1 ]]; then
                                    declare -g "ARG_${dest}=${collected_values[0]}"
                                else
                                    declare -g "ARG_${dest}=${collected_values[*]}"
                                fi
                            fi
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
    # This is complex because nargs can consume multiple values
    local pos_count=${#_ARGPARSE_POSITIONAL_ORDER[@]}
    local val_count=${#positional_values[@]}
    local val_idx=0  # Current index into positional_values

    for ((p=0; p < pos_count; p++)); do
        local idx="${_ARGPARSE_POSITIONAL_ORDER[$p]}"
        local dest="${_ARGPARSE_DEST[$idx]}"
        local pos_name="${_ARGPARSE_POSITIONAL[$idx]}"
        local arg_type="${_ARGPARSE_TYPE[$idx]}"
        local arg_choices="${_ARGPARSE_CHOICES[$idx]}"
        local arg_nargs="${_ARGPARSE_NARGS[$idx]}"

        if [[ -z "$arg_nargs" ]]; then
            # Single value positional
            if [[ $val_idx -lt $val_count ]]; then
                local value="${positional_values[$val_idx]}"
                # Type validation
                if [[ "$arg_type" == "int" ]]; then
                    if ! _argparse_is_int "$value"; then
                        _argparse_usage
                        echo "$_ARGPARSE_PROG: error: argument $pos_name: invalid int value: '$value'" >&2
                        return 1
                    fi
                fi
                # Choices validation
                if [[ -n "$arg_choices" ]]; then
                    if ! _argparse_in_choices "$value" "$arg_choices"; then
                        _argparse_usage
                        echo "$_ARGPARSE_PROG: error: argument $pos_name: invalid choice: '$value' (choose from: $arg_choices)" >&2
                        return 1
                    fi
                fi
                declare -g "ARG_${dest}=${value}"
                _arg_was_provided[$idx]=1
                val_idx=$((val_idx + 1))
            fi
        elif [[ "$arg_nargs" == "+" || "$arg_nargs" == "*" ]]; then
            # Consume all remaining values
            local collected_values=()
            while [[ $val_idx -lt $val_count ]]; do
                local value="${positional_values[$val_idx]}"
                # Type validation
                if [[ "$arg_type" == "int" ]]; then
                    if ! _argparse_is_int "$value"; then
                        _argparse_usage
                        echo "$_ARGPARSE_PROG: error: argument $pos_name: invalid int value: '$value'" >&2
                        return 1
                    fi
                fi
                # Choices validation
                if [[ -n "$arg_choices" ]]; then
                    if ! _argparse_in_choices "$value" "$arg_choices"; then
                        _argparse_usage
                        echo "$_ARGPARSE_PROG: error: argument $pos_name: invalid choice: '$value' (choose from: $arg_choices)" >&2
                        return 1
                    fi
                fi
                collected_values+=("$value")
                val_idx=$((val_idx + 1))
            done

            # Validate we got at least one for '+'
            if [[ "$arg_nargs" == "+" && ${#collected_values[@]} -eq 0 ]]; then
                # Will be caught by required validation if arg is required
                :
            else
                _arg_was_provided[$idx]=1
            fi

            # For '+', require at least one if marked as provided
            if [[ "$arg_nargs" == "+" && ${#collected_values[@]} -gt 0 ]]; then
                _arg_was_provided[$idx]=1
            elif [[ "$arg_nargs" == "*" ]]; then
                # '*' is always considered provided (empty is valid)
                _arg_was_provided[$idx]=1
            fi

            # Store as space-separated string
            declare -g "ARG_${dest}=${collected_values[*]}"
        else
            # Specific number of values (nargs is a positive integer)
            local num_to_collect="$arg_nargs"
            local collected_values=()

            for ((n=0; n < num_to_collect; n++)); do
                if [[ $val_idx -ge $val_count ]]; then
                    # Not enough values - will be handled by required check or is optional
                    break
                fi
                local value="${positional_values[$val_idx]}"
                # Type validation
                if [[ "$arg_type" == "int" ]]; then
                    if ! _argparse_is_int "$value"; then
                        _argparse_usage
                        echo "$_ARGPARSE_PROG: error: argument $pos_name: invalid int value: '$value'" >&2
                        return 1
                    fi
                fi
                # Choices validation
                if [[ -n "$arg_choices" ]]; then
                    if ! _argparse_in_choices "$value" "$arg_choices"; then
                        _argparse_usage
                        echo "$_ARGPARSE_PROG: error: argument $pos_name: invalid choice: '$value' (choose from: $arg_choices)" >&2
                        return 1
                    fi
                fi
                collected_values+=("$value")
                val_idx=$((val_idx + 1))
            done

            # Only mark as provided if we got all the required values
            if [[ ${#collected_values[@]} -eq $num_to_collect ]]; then
                _arg_was_provided[$idx]=1
                # Store as space-separated string
                declare -g "ARG_${dest}=${collected_values[*]}"
            fi
        fi
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
