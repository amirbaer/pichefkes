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

echo "=== Installing dotfiles ==="
curl -fsSL https://raw.githubusercontent.com/amirbaer/amirbaer.github.io/master/tikunolam/.inputrc -o ~/.inputrc

echo "=== Setting up Claude Code hooks ==="
mkdir -p ~/.claude
if [ -f ~/.claude/settings.json ]; then
    python3 -c "
import json, sys
path = sys.argv[1]
with open(path) as f: s = json.load(f)
s.setdefault('hooks', {})['Notification'] = [{'matcher': 'idle_prompt', 'hooks': [{'type': 'command', 'command': \"printf '\\\\a'\"}]}]
with open(path, 'w') as f: json.dump(s, f, indent=2)
print('Updated', path)
" ~/.claude/settings.json
else
    cat > ~/.claude/settings.json << 'SETTINGS'
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "printf '\\a'"
          }
        ]
      }
    ]
  }
}
SETTINGS
    echo "Created ~/.claude/settings.json"
fi

echo "=== Done! Run: claude auth login --headless ==="
