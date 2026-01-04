#!/bin/bash
# Kalembang Development Runner (tmux split panes)
# Runs API and Client side-by-side in vertical tmux panes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if we're in tmux
if [ -z "$TMUX" ]; then
    echo "❌ Not running inside tmux."
    echo "   Start tmux first: tmux new -s kalembang"
    exit 1
fi

echo "🔔 Starting Kalembang development servers..."

# Current pane runs the API
# Split vertically and run client in the new pane
tmux split-window -h -c "$PROJECT_DIR/client" "bun run dev"

# Rename the window
tmux rename-window "kalembang"

# Run API in the current pane
cd "$PROJECT_DIR/api"
export KALEMBANG_MOCK_GPIO=1
pipenv run uvicorn kalembang.main:app --host 0.0.0.0 --port 8088 --reload
