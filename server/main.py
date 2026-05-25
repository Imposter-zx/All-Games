"""Retro Arcade Online Leaderboard + Chess + Pong Multiplayer API."""

import json
import random
import secrets
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Retro Arcade", version="1.0.0")

DB_PATH = str(Path(__file__).parent / "leaderboard.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            game_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            difficulty TEXT DEFAULT 'normal',
            submitted_at REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_scores_game
        ON scores (game_name, score DESC)
    """)
    conn.commit()
    return conn


class ScoreSubmission(BaseModel):
    player_name: str
    game_name: str
    score: int
    difficulty: str = 'normal'


class ScoreEntry(BaseModel):
    rank: int
    player_name: str
    score: int
    difficulty: str
    submitted_at: float


@app.on_event("startup")
def startup() -> None:
    get_db().close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "timestamp": time.time()}


@app.post("/api/scores")
def submit_score(submission: ScoreSubmission) -> dict:
    if not submission.player_name.strip():
        raise HTTPException(400, "player_name is required")
    if not submission.game_name.strip():
        raise HTTPException(400, "game_name is required")
    if submission.score < 0:
        raise HTTPException(400, "score must be non-negative")

    conn = get_db()
    conn.execute(
        "INSERT INTO scores (player_name, game_name, score, difficulty, submitted_at) VALUES (?, ?, ?, ?, ?)",
        (submission.player_name.strip(), submission.game_name.strip().lower(),
         submission.score, submission.difficulty, time.time())
    )
    conn.commit()
    conn.close()
    return {"status": "accepted"}


@app.get("/api/leaderboard")
def leaderboard(
    game_name: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
) -> List[dict]:
    conn = get_db()
    if game_name:
        rows = conn.execute(
            "SELECT player_name, score, difficulty, submitted_at FROM scores "
            "WHERE game_name = ? ORDER BY score DESC LIMIT ?",
            (game_name.strip().lower(), limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT player_name, game_name, score, difficulty, submitted_at FROM scores "
            "ORDER BY score DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()

    result = []
    for i, row in enumerate(rows, 1):
        entry = dict(row)
        entry["rank"] = i
        result.append(entry)
    return result


# ── Chess Multiplayer ────────────────────────────────────────────────

@dataclass
class ChessRoom:
    room_id: str
    player_white: Optional[str] = None
    player_black: Optional[str] = None
    board_fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    moves: List[str] = field(default_factory=list)
    status: str = "waiting"       # waiting | playing | finished
    winner: Optional[str] = None
    created_at: float = 0.0


CHESS_ROOMS: Dict[str, ChessRoom] = {}


def _get_chess_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chess_games (
            room_id TEXT PRIMARY KEY,
            player_white TEXT,
            player_black TEXT,
            winner TEXT,
            moves_json TEXT,
            created_at REAL
        )
    """)
    conn.commit()
    return conn


@app.post("/api/chess/create_room")
def chess_create_room(player_name: str = Query(...)) -> dict:
    room_id = secrets.token_hex(4)
    room = ChessRoom(
        room_id=room_id,
        player_white=player_name.strip(),
        created_at=time.time(),
    )
    CHESS_ROOMS[room_id] = room
    return {"room_id": room_id, "color": "white", "status": room.status}


@app.post("/api/chess/join_room")
def chess_join_room(room_id: str = Query(...), player_name: str = Query(...)):
    room = CHESS_ROOMS.get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    if room.status != "waiting":
        raise HTTPException(400, "Game already started or finished")
    if room.player_white == player_name.strip():
        raise HTTPException(400, "Cannot join your own room")
    room.player_black = player_name.strip()
    room.status = "playing"
    return {"room_id": room_id, "color": "black", "status": room.status}


@app.post("/api/chess/move")
def chess_move(
    room_id: str = Query(...),
    player_name: str = Query(...),
    move: str = Query(...),
) -> dict:
    room = CHESS_ROOMS.get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    if room.status != "playing":
        raise HTTPException(400, "Game is not in progress")
    if player_name.strip() not in (room.player_white, room.player_black):
        raise HTTPException(403, "You are not a player in this game")

    # Basic turn validation (alternating moves)
    expected = "white" if len(room.moves) % 2 == 0 else "black"
    if (expected == "white" and player_name.strip() != room.player_white) or \
       (expected == "black" and player_name.strip() != room.player_black):
        raise HTTPException(400, f"Not your turn — waiting for {expected}")

    room.moves.append(move)
    return {"move_number": len(room.moves), "ack": True}


@app.get("/api/chess/game_state")
def chess_game_state(room_id: str = Query(...), player_name: str = Query(...)):
    room = CHESS_ROOMS.get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    last_move = room.moves[-1] if room.moves else None
    return {
        "room_id": room.room_id,
        "status": room.status,
        "player_white": room.player_white,
        "player_black": room.player_black,
        "your_color": "white" if room.player_white == player_name.strip() else "black",
        "moves": room.moves,
        "last_move": last_move,
        "turn": "white" if len(room.moves) % 2 == 0 else "black",
        "winner": room.winner,
    }


@app.post("/api/chess/resign")
def chess_resign(room_id: str = Query(...), player_name: str = Query(...)) -> dict:
    room = CHESS_ROOMS.get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    if room.status != "playing":
        raise HTTPException(400, "Game is not in progress")

    resigner_color = "white" if room.player_white == player_name.strip() else "black"
    room.status = "finished"
    room.winner = "black" if resigner_color == "white" else "white"

    # Persist to DB
    conn = _get_chess_db()
    conn.execute(
        "INSERT OR REPLACE INTO chess_games VALUES (?, ?, ?, ?, ?, ?)",
        (room.room_id, room.player_white, room.player_black, room.winner,
         json.dumps(room.moves), room.created_at),
    )
    conn.commit()
    conn.close()
    return {"status": "finished", "winner": room.winner}


# ── Leaderboard ──────────────────────────────────────────────────────

@app.get("/api/my_best")
def my_best(player_name: str = Query(...), game_name: Optional[str] = Query(None)) -> dict:
    conn = get_db()
    if game_name:
        row = conn.execute(
            "SELECT MAX(score) as best FROM scores WHERE player_name = ? AND game_name = ?",
            (player_name.strip(), game_name.strip().lower())
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT MAX(score) as best FROM scores WHERE player_name = ?",
            (player_name.strip(),)
        ).fetchone()
    conn.close()
    return {"best": row["best"] if row and row["best"] else 0}


# ── Pong Multiplayer ───────────────────────────────────────────────────

PONG_WIDTH = 80
PONG_HEIGHT = 30
PONG_TICK = 0.033  # ~30 fps
WIN_SCORE = 10


@dataclass
class PongRoom:
    room_id: str
    player_left: str = ""
    player_right: str = ""
    ball_x: float = PONG_WIDTH / 2
    ball_y: float = PONG_HEIGHT / 2
    ball_dx: float = 2.0
    ball_dy: float = 1.0
    paddle_left: float = PONG_HEIGHT / 2 - 2
    paddle_right: float = PONG_HEIGHT / 2 - 2
    paddle_dir_left: str = "stop"     # up / down / stop
    paddle_dir_right: str = "stop"
    paddle_size: int = 4
    score_left: int = 0
    score_right: int = 0
    status: str = "waiting"
    winner: str = ""
    last_tick: float = 0.0
    seed: int = 0


PONG_ROOMS: Dict[str, PongRoom] = {}
_PONG_LOCK = threading.Lock()


def _init_pong_room(room: PongRoom) -> None:
    room.seed = random.randint(0, 2 ** 31)
    rng = random.Random(room.seed)
    room.ball_x = PONG_WIDTH / 2
    room.ball_y = PONG_HEIGHT / 2
    angle = rng.uniform(-0.6, 0.6)
    room.ball_dx = 2.0 * (1 if rng.choice([True, False]) else -1)
    room.ball_dy = angle * 2.0
    room.score_left = 0
    room.score_right = 0
    room.paddle_left = PONG_HEIGHT / 2 - 2
    room.paddle_right = PONG_HEIGHT / 2 - 2
    room.paddle_dir_left = "stop"
    room.paddle_dir_right = "stop"
    room.status = "playing"
    room.winner = ""
    room.last_tick = time.time()


def _tick_pong(room: PongRoom, dt: float) -> None:
    dt = min(dt, 0.1)
    # Paddle movement
    speed = 12.0
    for side, pos, direction in [
        ("left", "paddle_left", "paddle_dir_left"),
        ("right", "paddle_right", "paddle_dir_right"),
    ]:
        d = getattr(room, direction)
        if d == "up":
            setattr(room, pos, max(0, getattr(room, pos) - speed * dt))
        elif d == "down":
            setattr(room, pos, min(PONG_HEIGHT - room.paddle_size, getattr(room, pos) + speed * dt))

    # Ball movement
    room.ball_x += room.ball_dx * dt * 30
    room.ball_y += room.ball_dy * dt * 30

    # Wall bounce
    if room.ball_y <= 0 or room.ball_y >= PONG_HEIGHT - 1:
        room.ball_dy *= -0.95
        room.ball_y = max(0.1, min(PONG_HEIGHT - 1.1, room.ball_y))

    # Left paddle collision
    if room.ball_x <= 2.0:
        top = room.paddle_left
        bot = top + room.paddle_size
        if top <= room.ball_y < bot:
            room.ball_dx = abs(room.ball_dx) * 1.01
            hit = (room.ball_y - top) / room.paddle_size - 0.5
            room.ball_dy = hit * 3.0
            room.ball_x = 2.0
        else:
            room.score_right += 1
            room.ball_x = PONG_WIDTH / 2
            room.ball_y = PONG_HEIGHT / 2
            room.ball_dx = 2.0
            room.ball_dy = random.uniform(-1, 1)

    # Right paddle collision
    if room.ball_x >= PONG_WIDTH - 3.0:
        top = room.paddle_right
        bot = top + room.paddle_size
        if top <= room.ball_y < bot:
            room.ball_dx = -abs(room.ball_dx) * 1.01
            hit = (room.ball_y - top) / room.paddle_size - 0.5
            room.ball_dy = hit * 3.0
            room.ball_x = PONG_WIDTH - 3.0
        else:
            room.score_left += 1
            room.ball_x = PONG_WIDTH / 2
            room.ball_y = PONG_HEIGHT / 2
            room.ball_dx = -2.0
            room.ball_dy = random.uniform(-1, 1)

    # Win check
    if room.score_left >= WIN_SCORE:
        room.status = "finished"
        room.winner = room.player_left
    elif room.score_right >= WIN_SCORE:
        room.status = "finished"
        room.winner = room.player_right


def _pong_background_loop() -> None:
    while True:
        now = time.time()
        with _PONG_LOCK:
            for room in PONG_ROOMS.values():
                if room.status == "playing":
                    dt = now - room.last_tick
                    _tick_pong(room, dt)
                    room.last_tick = now
        time.sleep(PONG_TICK)


_pong_thread = threading.Thread(target=_pong_background_loop, daemon=True)
_pong_thread.start()


@app.post("/api/pong/create_room")
def pong_create_room(player_name: str = Query(...)) -> dict:
    room_id = secrets.token_hex(4)
    room = PongRoom(room_id=room_id, player_left=player_name.strip())
    with _PONG_LOCK:
        PONG_ROOMS[room_id] = room
    return {"room_id": room_id, "side": "left", "status": "waiting"}


@app.post("/api/pong/join_room")
def pong_join_room(room_id: str = Query(...), player_name: str = Query(...)):
    room = PONG_ROOMS.get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    if room.status != "waiting":
        raise HTTPException(400, "Game already started")
    if room.player_left == player_name.strip():
        raise HTTPException(400, "Cannot join your own room")
    room.player_right = player_name.strip()
    _init_pong_room(room)
    return {"room_id": room_id, "side": "right", "status": "playing"}


@app.post("/api/pong/paddle")
def pong_paddle(room_id: str = Query(...), player_name: str = Query(...), direction: str = Query("stop")):
    room = PONG_ROOMS.get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    if direction not in ("up", "down", "stop"):
        raise HTTPException(400, "Invalid direction")

    with _PONG_LOCK:
        if room.player_left == player_name.strip():
            room.paddle_dir_left = direction
        elif room.player_right == player_name.strip():
            room.paddle_dir_right = direction
        else:
            raise HTTPException(403, "Not a player in this game")
    return {"ack": True}


@app.get("/api/pong/state")
def pong_state(room_id: str = Query(...), player_name: str = Query(...)):
    room = PONG_ROOMS.get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")

    if player_name.strip() == room.player_left:
        side = "left"
        opponent_paddle = room.paddle_right
        my_paddle = room.paddle_left
    elif room.player_right and player_name.strip() == room.player_right:
        side = "right"
        opponent_paddle = room.paddle_left
        my_paddle = room.paddle_right
    else:
        raise HTTPException(403, "Not a player")

    return {
        "side": side,
        "ball_x": room.ball_x,
        "ball_y": room.ball_y,
        "my_paddle_y": my_paddle,
        "opponent_paddle_y": opponent_paddle,
        "my_score": room.score_left if side == "left" else room.score_right,
        "opponent_score": room.score_right if side == "left" else room.score_left,
        "status": room.status,
        "winner": room.winner,
        "paddle_size": room.paddle_size,
        "width": PONG_WIDTH,
        "height": PONG_HEIGHT,
    }


@app.post("/api/pong/forfeit")
def pong_forfeit(room_id: str = Query(...), player_name: str = Query(...)):
    room = PONG_ROOMS.get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    if room.status != "playing":
        raise HTTPException(400, "Game not in progress")

    with _PONG_LOCK:
        if room.player_left == player_name.strip():
            room.status = "finished"
            room.winner = room.player_right
        elif room.player_right == player_name.strip():
            room.status = "finished"
            room.winner = room.player_left
        else:
            raise HTTPException(403, "Not a player")
    return {"status": "finished", "winner": room.winner}
