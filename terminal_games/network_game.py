"""Network multiplayer client — communicates with the chess relay server."""

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_SERVER = "https://retro-arcade-leaderboard.onrender.com"
TIMEOUT = 5


class NetworkError(Exception):
    """Raised when a network operation fails."""


def _get(url: str, server: str) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        return json.loads(resp.read().decode())
    except Exception as e:
        logger.debug(f"Network GET failed: {e}")
        return None


def _post(url: str, data: str, server: str) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(
            url,
            data=data.encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        return json.loads(resp.read().decode())
    except Exception as e:
        logger.debug(f"Network POST failed: {e}")
        return None


def create_chess_room(
    player_name: str,
    server: str = DEFAULT_SERVER,
) -> Optional[Dict[str, Any]]:
    """Create a new chess room. Returns room info or None."""
    return _post(
        f"{server}/api/chess/create_room?player_name={urllib.request.quote(player_name)}",
        "",
        server,
    )


def join_chess_room(
    room_id: str,
    player_name: str,
    server: str = DEFAULT_SERVER,
) -> Optional[Dict[str, Any]]:
    """Join an existing chess room. Returns room info or None."""
    return _post(
        f"{server}/api/chess/join_room?room_id={room_id}&player_name={urllib.request.quote(player_name)}",
        "",
        server,
    )


def submit_chess_move(
    room_id: str,
    player_name: str,
    move: str,
    server: str = DEFAULT_SERVER,
) -> Optional[Dict[str, Any]]:
    """Submit a chess move to the server. Returns ack info or None."""
    return _post(
        f"{server}/api/chess/move?room_id={room_id}&player_name={urllib.request.quote(player_name)}&move={move}",
        "",
        server,
    )


def get_chess_game_state(
    room_id: str,
    player_name: str,
    server: str = DEFAULT_SERVER,
) -> Optional[Dict[str, Any]]:
    """Get the current chess game state from the server."""
    return _get(
        f"{server}/api/chess/game_state?room_id={room_id}&player_name={urllib.request.quote(player_name)}",
        server,
    )


def resign_chess(
    room_id: str,
    player_name: str,
    server: str = DEFAULT_SERVER,
) -> Optional[Dict[str, Any]]:
    """Resign from a chess game."""
    return _post(
        f"{server}/api/chess/resign?room_id={room_id}&player_name={urllib.request.quote(player_name)}",
        "",
        server,
    )
