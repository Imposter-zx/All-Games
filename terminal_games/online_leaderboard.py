"""Online leaderboard client — submits/fetches scores via REST API."""

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_SERVER = "https://retro-arcade-leaderboard.onrender.com"
TIMEOUT = 5


def submit_score(
    player_name: str,
    game_name: str,
    score: int,
    difficulty: str = "normal",
    server: str = DEFAULT_SERVER,
) -> bool:
    """Submit a score to the online leaderboard. Returns True on success."""
    try:
        data = json.dumps({
            "player_name": player_name,
            "game_name": game_name,
            "score": score,
            "difficulty": difficulty,
        }).encode()
        req = urllib.request.Request(
            f"{server}/api/scores",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=TIMEOUT)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        logger.debug(f"Online leaderboard unavailable: {e}")
        return False


def fetch_leaderboard(
    game_name: Optional[str] = None,
    limit: int = 10,
    server: str = DEFAULT_SERVER,
) -> List[Dict[str, Any]]:
    """Fetch global leaderboard from the server."""
    try:
        url = f"{server}/api/leaderboard?limit={limit}"
        if game_name:
            url += f"&game_name={game_name}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError) as e:
        logger.debug(f"Online leaderboard fetch failed: {e}")
        return []


def health_check(server: str = DEFAULT_SERVER) -> bool:
    """Check if the leaderboard server is reachable."""
    try:
        req = urllib.request.Request(f"{server}/health")
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False
