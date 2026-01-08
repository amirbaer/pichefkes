#!/bin/bash
set -e
echo "=== Installing Claude Code ==="
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    if [ -f /etc/redhat-release ]; then
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        sudo dnf install -y nodejs
    elif [ -f /etc/debian_version ]; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
        sudo apt-get install -y nodejs
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install node
    fi
fi
npm install -g @anthropic-ai/claude-code
echo "=== Done! Run: claude auth login --headless ==="
