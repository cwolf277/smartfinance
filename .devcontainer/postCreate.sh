#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing backend dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Installing frontend dependencies"
cd frontend
npm install --legacy-peer-deps --no-audit --no-fund
cd ..

echo "==> Setting up .env (sandbox placeholders if no Codespaces secrets present)"
if [ ! -f .env ]; then
  cp .env.example .env
  if [ -n "${PLAID_CLIENT_ID:-}" ]; then
    sed -i "s|^PLAID_CLIENT_ID=.*|PLAID_CLIENT_ID=${PLAID_CLIENT_ID}|" .env
  fi
  if [ -n "${PLAID_SECRET:-}" ]; then
    sed -i "s|^PLAID_SECRET=.*|PLAID_SECRET=${PLAID_SECRET}|" .env
  fi
fi

echo "==> Done. Run '.devcontainer/start.sh' or use the Codespace's 'Run' command."
