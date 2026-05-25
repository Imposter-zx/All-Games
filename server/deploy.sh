#!/usr/bin/env bash
# Deploy the Retro Arcade leaderboard server.
# Options: render (default), docker, local

set -euo pipefail

MODE="${1:-render}"

case "$MODE" in
  render)
    echo "=== Deploying to Render ==="
    echo ""
    echo "Steps:"
    echo "  1. Push this repo to GitHub"
    echo "  2. Go to https://dashboard.render.com/select-repo"
    echo "  3. Connect your repo"
    echo "  4. Set:"
    echo "     - Root Directory: server"
    echo "     - Build Command: pip install -r requirements.txt"
    echo "     - Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo "  5. Deploy"
    echo ""
    echo "After deploy, update DEFAULT_SERVER in:"
    echo "    terminal_games/online_leaderboard.py"
    echo "  with your Render URL (e.g. https://retro-arcade-leaderboard.onrender.com)"
    ;;
  docker)
    echo "=== Building & running with Docker ==="
    cd "$(dirname "$0")"
    docker build -t retro-leaderboard .
    docker run -d -p 8000:8000 --name retro-leaderboard retro-leaderboard
    echo "Server running at http://localhost:8000"
    echo "Health check: curl http://localhost:8000/health"
    ;;
  local)
    echo "=== Running locally with uvicorn ==="
    cd "$(dirname "$0")"
    pip install -r requirements.txt
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ;;
  *)
    echo "Usage: $0 {render|docker|local}"
    exit 1
    ;;
esac
