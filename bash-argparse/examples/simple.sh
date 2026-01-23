#!/usr/bin/env bash
# =============================================================================
# Simple bashargparse Example
# =============================================================================
#
# This script shows the most basic usage of bashargparse.
# In just a few lines, you get argument parsing with automatic --help!
#
# Try it:
#   ./simple.sh --help
#   ./simple.sh hello
#   ./simple.sh -v hello
#   ./simple.sh --name World hello
#
# =============================================================================

# Source the library (adjust path as needed)
source "$(dirname "${BASH_SOURCE[0]}")/../bashargparse.sh"

# Initialize with program name and description
argparse_init 'simple' 'A simple greeting program'

# Define a boolean flag
add_argument -s v -l verbose -a store_true -h 'Enable verbose output'

# Define a value flag with default
add_argument -s n -l name -d 'User' -h 'Name to greet'

# Define a positional argument
add_argument -p message -h 'Message to display'

# Parse the arguments
argparse_parse "$@"

# Use the parsed values
if [[ $ARG_VERBOSE -eq 1 ]]; then
    echo "Verbose mode enabled"
    echo "Name: $ARG_NAME"
    echo "Message: $ARG_MESSAGE"
    echo "---"
fi

echo "Hello, $ARG_NAME! $ARG_MESSAGE"
