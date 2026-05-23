# Retro Arcade Online Leaderboard

A lightweight FastAPI server for global high scores.

## Deploy

### Render (free tier)
1. Fork/push this repo to GitHub
2. On Render: New Web Service → connect repo
3. Set:
   - Root Directory: `server`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy — copy the URL to `DEFAULT_SERVER` in `terminal_games/online_leaderboard.py`

### Docker
```bash
docker build -t retro-leaderboard server/
docker run -p 8000:8000 retro-leaderboard
```

### Local
```bash
pip install -r server/requirements.txt
uvicorn server.main:app --reload --port 8000
```

### API
- `GET /health` — health check
- `POST /api/scores` — submit `{"player_name", "game_name", "score", "difficulty"}`
- `GET /api/leaderboard?game_name=snake&limit=10` — global top scores
- `GET /api/my_best?player_name=PLAYER&game_name=snake` — player's best
