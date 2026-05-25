"""Retro Arcade Online Leaderboard + Chess Multiplayer API — FastAPI server."""

import json
import secrets
import sqlite3
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
