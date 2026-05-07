#!/usr/bin/env bash
set -euo pipefail

# Auto-start backend and frontend in tmux-like background processes
# Logs go to /tmp so you can `tail -f` from the terminal

echo "==> Starting backend on :5000"
nohup bash -c "cd $(pwd) && python -m backend.app" > /tmp/backend.log 2>&1 &

echo "==> Starting frontend on :3000"
nohup bash -c "cd $(pwd)/frontend && BROWSER=none npm start" > /tmp/frontend.log 2>&1 &

echo "==> Servers starting. Tail logs with: tail -f /tmp/backend.log /tmp/frontend.log"
echo "==> Frontend will open automatically in the Ports tab."
