#!/bin/bash
# Ralph Loop Runner (wrapper)
# Calls the Python implementation for better argument handling
#
# Usage:
#   ./bin/ralph.sh              # Run with confirmation prompt
#   ./bin/ralph.sh -y           # Skip confirmation
#   ./bin/ralph.sh -y 10        # Skip confirmation, max 10 iterations
#   ./bin/ralph.sh 20           # Max 20 iterations (with confirmation)
#   ./bin/ralph.sh -i           # Show current cycle status
#   ./bin/ralph.sh -iH          # Show status with history
#   ./bin/ralph.sh -a "desc"    # Add bug/feature (processed by Claude)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/ralph.py" "$@"
