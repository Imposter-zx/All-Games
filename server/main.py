"""Retro Arcade Online Leaderboard API — FastAPI server."""

import sqlite3
import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Retro Arcade Leaderboard", version="1.0.0")

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
