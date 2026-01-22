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
