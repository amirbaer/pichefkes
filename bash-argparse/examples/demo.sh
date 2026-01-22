#!/usr/bin/env bash
# =============================================================================
# bashargparse Demo Script
# =============================================================================
# NOTE: Requires bash 4.2+ for declare -g support. macOS ships with bash 3.2,
# so you may need to install a newer bash via Homebrew: brew install bash
#
# This script demonstrates all features of the bashargparse library.
# Run with --help to see the generated help message, or with various
# combinations of arguments to see how parsing works.
#
# Examples:
#   ./demo.sh --help
#   ./demo.sh input.txt
#   ./demo.sh -v input.txt
#   ./demo.sh -vvv --output result.txt input.txt
#   ./demo.sh --level info --port 8080 input.txt
#   ./demo.sh --files a.txt b.txt c.txt -- input.txt
#
# =============================================================================

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the bashargparse library (adjust path as needed)
source "${SCRIPT_DIR}/../bashargparse.sh"

# =============================================================================
# FEATURE 1: Initialize the parser
# =============================================================================
# argparse_init takes two optional arguments:
#   - program name (defaults to script name)
#   - description (shown in help)

argparse_init 'demo' 'A comprehensive demo of bashargparse features.

This script showcases all the argument parsing capabilities:
boolean flags, value flags, positional arguments, type validation,
choices, count actions, and nargs for multiple values.'

# =============================================================================
# FEATURE 2: Boolean flags (store_true)
# =============================================================================
# Boolean flags are set to 1 when present, 0 when absent.
# Use -a store_true to create a boolean flag.

add_argument -s d -l debug -a store_true -h 'Enable debug mode'
add_argument -l dry-run -a store_true -h 'Perform a dry run without making changes'

# =============================================================================
# FEATURE 3: Count action (-vvv = 3)
# =============================================================================
# Count flags increment each time they appear.
# Supports combined short form: -vvv equals -v -v -v

add_argument -s v -l verbose -a count -h 'Increase verbosity (can be repeated: -vvv)'

# =============================================================================
# FEATURE 4: Value flags with defaults
# =============================================================================
# Value flags take an argument. Use -d to specify a default value.

add_argument -s o -l output -d './output.txt' -h 'Output file path'
add_argument -l config -d '/etc/demo.conf' -h 'Configuration file'

# =============================================================================
# FEATURE 5: Required flags
# =============================================================================
# Use -r to mark a flag as required. Parsing fails if not provided.

# Commenting this out so the demo runs without errors:
# add_argument -l api-key -r -h 'API key (required)'

# =============================================================================
# FEATURE 6: Type validation (int)
# =============================================================================
# Use -t int to validate that the value is an integer.
# Supports positive, negative, and zero values.

add_argument -s p -l port -t int -d '8080' -h 'Port number (must be integer)'
add_argument -l retries -t int -d '3' -h 'Number of retries'

# =============================================================================
# FEATURE 7: Choices validation
# =============================================================================
# Use -c to specify a comma-separated list of valid choices.
# Parsing fails if the value is not in the list.

add_argument -s l -l level -c 'debug,info,warn,error' -d 'info' -h 'Log level'
add_argument -l format -c 'json,xml,csv,text' -d 'text' -h 'Output format'

# =============================================================================
# FEATURE 8: nargs - Multiple values
# =============================================================================
# Use -n to collect multiple values:
#   '+' = one or more (at least one required)
#   '*' = zero or more (optional)
#   N   = exactly N values

add_argument -l files -n '+' -h 'Files to process (one or more)'
add_argument -l tags -n '*' -h 'Optional tags'
add_argument -l coords -n 3 -t int -h 'Exactly 3 coordinates (x y z)'

# =============================================================================
# FEATURE 9: Positional arguments
# =============================================================================
# Positional arguments are specified with -p instead of -s/-l.
# They are consumed in order after all flags are processed.

add_argument -p input -h 'Input file to process'

# =============================================================================
# FEATURE 10: Positional with nargs
# =============================================================================
# Positional arguments can also use nargs for multiple values.
# Note: nargs '*' or '+' on positional consumes all remaining args.

# Uncomment to demo positional nargs (will consume all positional args):
# add_argument -p extras -n '*' -h 'Additional files (optional)'

# =============================================================================
# Parse the command line arguments
# =============================================================================
# argparse_parse processes "$@" and sets ARG_* variables.
# Exits with error if:
#   - Required arguments are missing
#   - Type validation fails
#   - Choice validation fails
#   - Unknown flags are encountered

argparse_parse "$@"

# =============================================================================
# Display parsed results
# =============================================================================

echo "=========================================="
echo "Parsed Arguments"
echo "=========================================="
echo

echo "--- Boolean Flags (store_true) ---"
echo "  ARG_DEBUG    = $ARG_DEBUG"
echo "  ARG_DRY_RUN  = $ARG_DRY_RUN"
echo

echo "--- Count Flag ---"
echo "  ARG_VERBOSE  = $ARG_VERBOSE"
echo

echo "--- Value Flags with Defaults ---"
echo "  ARG_OUTPUT   = $ARG_OUTPUT"
echo "  ARG_CONFIG   = $ARG_CONFIG"
echo

echo "--- Integer Flags (type validation) ---"
echo "  ARG_PORT     = $ARG_PORT"
echo "  ARG_RETRIES  = $ARG_RETRIES"
echo

echo "--- Choice Flags ---"
echo "  ARG_LEVEL    = $ARG_LEVEL"
echo "  ARG_FORMAT   = $ARG_FORMAT"
echo

echo "--- nargs Flags (multiple values) ---"
echo "  ARG_FILES    = '$ARG_FILES'"
echo "  ARG_TAGS     = '$ARG_TAGS'"
echo "  ARG_COORDS   = '$ARG_COORDS'"
echo

echo "--- Positional Arguments ---"
echo "  ARG_INPUT    = $ARG_INPUT"
echo

# =============================================================================
# Example: Using the parsed values
# =============================================================================

echo "=========================================="
echo "Example Usage"
echo "=========================================="
echo

# Example: verbosity levels
if [[ $ARG_VERBOSE -ge 3 ]]; then
    echo "[TRACE] Very verbose output enabled"
fi
if [[ $ARG_VERBOSE -ge 2 ]]; then
    echo "[DEBUG] Debug output enabled"
fi
if [[ $ARG_VERBOSE -ge 1 ]]; then
    echo "[INFO] Verbose output enabled"
fi

# Example: boolean flag check
if [[ $ARG_DEBUG -eq 1 ]]; then
    echo "[DEBUG] Debug mode is ON"
fi

if [[ $ARG_DRY_RUN -eq 1 ]]; then
    echo "[DRY-RUN] Would process: $ARG_INPUT"
else
    echo "Processing: $ARG_INPUT"
fi

# Example: iterating over nargs values
if [[ -n "$ARG_FILES" ]]; then
    echo
    echo "Files to process:"
    for file in $ARG_FILES; do
        echo "  - $file"
    done
fi

if [[ -n "$ARG_TAGS" ]]; then
    echo
    echo "Tags:"
    for tag in $ARG_TAGS; do
        echo "  - $tag"
    done
fi

if [[ -n "$ARG_COORDS" ]]; then
    echo
    echo "Coordinates:"
    # Split into x, y, z
    read -r x y z <<< "$ARG_COORDS"
    echo "  X=$x, Y=$y, Z=$z"
fi

echo
echo "Done!"
