"""
Centralized player statistics manager using SQLite.
Provides persistent storage, queries, time-series tracking.
"""

import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class StatsManager:
    """Player statistics manager backed by SQLite."""

    DB_PATH = str(Path.home() / ".retro_arcade" / "player.db")

    def __init__(self) -> None:
        """Initialize and ensure schema exists."""
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(self.DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self._ensure_defaults()

    def _init_schema(self) -> None:
        """Create all required tables if they don't exist."""
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS profile (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS games (
                    game_name TEXT NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value INTEGER DEFAULT 0,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (game_name, stat_key)
                );
                CREATE TABLE IF NOT EXISTS achievements (
                    achievement_id TEXT PRIMARY KEY,
                    unlocked_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS play_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_name TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    xp_earned INTEGER DEFAULT 0,
                    duration_seconds REAL DEFAULT 0,
                    difficulty TEXT DEFAULT 'normal',
                    played_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS telemetry_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload TEXT DEFAULT '',
                    created_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS game_states (
                    game_name TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    saved_at REAL NOT NULL
                );
            """)

    def _ensure_defaults(self) -> None:
        """Insert default profile/settings rows if missing."""
        defaults: Dict[str, str] = {
            'player_name': 'RETRO_MASTER',
            'total_xp': '0',
            'level': '1',
            'games_played': '0',
            'total_playtime': '0',
        }
        with self.conn:
            for k, v in defaults.items():
                self.conn.execute(
                    "INSERT OR IGNORE INTO profile (key, value) VALUES (?, ?)",
                    (k, v)
                )
            self.conn.execute(
                "INSERT OR IGNORE INTO settings (setting_key, setting_value) VALUES (?, ?)",
                ('sound_enabled', 'True')
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO settings (setting_key, setting_value) VALUES (?, ?)",
                ('theme', 'classic')
            )

    # --- Profile helpers ---

    def _get_profile_int(self, key: str, default: int = 0) -> int:
        row = self.conn.execute(
            "SELECT value FROM profile WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return default
        try:
            return int(row['value'])
        except (ValueError, TypeError):
            return default

    def _set_profile_int(self, key: str, value: int) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO profile (key, value) VALUES (?, ?)",
                (key, str(value))
            )

    def _get_profile_str(self, key: str, default: str = '') -> str:
        row = self.conn.execute(
            "SELECT value FROM profile WHERE key = ?", (key,)
        ).fetchone()
        return row['value'] if row is not None else default

    def _set_profile_str(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO profile (key, value) VALUES (?, ?)",
                (key, value)
            )

    # --- Public API ---

    def update_game_stats(self, game_name: str, stats_dict: Dict[str, Any]) -> None:
        """Upsert game-specific stats."""
        now = time.time()
        with self.conn:
            for key, value in stats_dict.items():
                if isinstance(value, (int, float)):
                    self.conn.execute(
                        "INSERT OR REPLACE INTO games "
                        "(game_name, stat_key, stat_value, updated_at) VALUES (?, ?, ?, ?)",
                        (game_name.lower(), key, int(value), now)
                    )
            self.conn.execute(
                "UPDATE profile SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT) WHERE key = 'games_played'"
            )

    def add_xp(self, amount: int) -> int:
        """Add XP, recalculate level, return new level."""
        if amount < 0:
            logger.warning(f"Negative XP amount: {amount}")
            return self._get_profile_int('level', 1)

        current = self._get_profile_int('total_xp', 0)
        current += amount
        self._set_profile_int('total_xp', current)

        old_level = self._get_profile_int('level', 1)
        new_level = 1 + (current // 500)
        self._set_profile_int('level', new_level)

        if new_level > old_level:
            logger.info(f"Level up! New level: {new_level}")

        return new_level

    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement. Returns True if newly unlocked."""
        now = time.time()
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT OR IGNORE INTO achievements (achievement_id, unlocked_at) VALUES (?, ?)",
                    (achievement_id, now)
                )
                return self.conn.total_changes > 0
        except sqlite3.IntegrityError:
            return False

    def get_stats(self, game_name: Optional[str] = None) -> Dict[str, Any]:
        """Get overall or game-specific stats."""
        if game_name:
            rows = self.conn.execute(
                "SELECT stat_key, stat_value, updated_at FROM games WHERE game_name = ?",
                (game_name.lower(),)
            ).fetchall()
            result: Dict[str, Any] = {}
            for row in rows:
                result[row['stat_key']] = row['stat_value']
            return result

        result: Dict[str, Any] = {}
        profile_rows = self.conn.execute("SELECT key, value FROM profile").fetchall()
        for row in profile_rows:
            val: Any = row['value']
            try:
                val = int(val)
            except (ValueError, TypeError):
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    pass
            result[row['key']] = val

        result['achievements'] = self.get_unlocked_achievements()
        result['settings'] = self.get_settings()
        result['games'] = {}
        game_rows = self.conn.execute(
            "SELECT game_name, stat_key, stat_value FROM games ORDER BY game_name"
        ).fetchall()
        for row in game_rows:
            gname = row['game_name']
            if gname not in result['games']:
                result['games'][gname] = {}
            result['games'][gname][row['stat_key']] = row['stat_value']
        result['games_played'] = self._get_profile_int('games_played', 0)
        result['total_playtime'] = self._get_profile_int('total_playtime', 0)
        return result

    def get_level_and_xp(self) -> Tuple[int, int, float]:
        """Return (level, total_xp, progress_to_next_level)."""
        level = self._get_profile_int('level', 1)
        total_xp = self._get_profile_int('total_xp', 0)
        xp_for_level = (level - 1) * 500
        xp_for_next = level * 500
        progress = 0.0
        if xp_for_next > xp_for_level:
            progress = (total_xp - xp_for_level) / (xp_for_next - xp_for_level)
        progress = min(1.0, max(0.0, progress))
        return level, total_xp, progress

    def get_high_score(self, game_name: str) -> int:
        """Return the highest score recorded for a game."""
        row = self.conn.execute(
            "SELECT stat_value FROM games WHERE game_name = ? AND stat_key = ? ORDER BY stat_value DESC LIMIT 1",
            (game_name.lower(), 'high_score')
        ).fetchone()
        if row:
            return row['stat_value']
        # Fallback to best_score
        row = self.conn.execute(
            "SELECT stat_value FROM games WHERE game_name = ? AND stat_key = ? ORDER BY stat_value DESC LIMIT 1",
            (game_name.lower(), 'best_score')
        ).fetchone()
        return row['stat_value'] if row else 0

    def get_unlocked_achievements(self) -> List[str]:
        """Return list of unlocked achievement IDs."""
        rows = self.conn.execute(
            "SELECT achievement_id FROM achievements ORDER BY unlocked_at"
        ).fetchall()
        return [r['achievement_id'] for r in rows]

    # --- Settings ---

    def get_settings(self) -> Dict[str, Any]:
        """Return all settings as a dict."""
        rows = self.conn.execute("SELECT setting_key, setting_value FROM settings").fetchall()
        settings: Dict[str, Any] = {
            'sound_enabled': True,
            'player_name': 'RETRO_MASTER',
            'theme': 'classic',
        }
        for row in rows:
            val: Any = row['setting_value']
            if val.lower() in ('true', 'false'):
                val = val.lower() == 'true'
            settings[row['setting_key']] = val
        return settings

    def set_setting(self, key: str, value: Any) -> None:
        """Update a single setting."""
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)",
                (key, str(value))
            )

    def save(self) -> None:
        """Commit any pending writes (no-op with auto-commit)."""
        self.conn.commit()

    # --- Session tracking ---

    def record_session(self, game_name: str, score: int, xp_earned: int,
                       duration: float, difficulty: str = 'normal') -> None:
        """Record a completed play session."""
        now = time.time()
        with self.conn:
            self.conn.execute(
                "INSERT INTO play_sessions (game_name, score, xp_earned, duration_seconds, difficulty, played_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (game_name.lower(), score, xp_earned, duration, difficulty, now)
            )
            total = self._get_profile_int('total_playtime', 0)
            self._set_profile_int('total_playtime', total + int(duration))

    def get_recent_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return recent play sessions."""
        rows = self.conn.execute(
            "SELECT * FROM play_sessions ORDER BY played_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_game_leaderboard(self, game_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Return top scores for a specific game."""
        rows = self.conn.execute(
            "SELECT score, difficulty, played_at FROM play_sessions "
            "WHERE game_name = ? ORDER BY score DESC LIMIT ?",
            (game_name.lower(), limit)
        ).fetchall()
        return [dict(r) for r in rows]

    # --- Telemetry ---

    def record_telemetry(self, event_type: str, payload: str = '') -> None:
        """Record an anonymous telemetry event."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO telemetry_events (event_type, payload, created_at) VALUES (?, ?, ?)",
                (event_type, payload, time.time())
            )

    def get_telemetry_summary(self) -> Dict[str, int]:
        """Return count of each event type."""
        rows = self.conn.execute(
            "SELECT event_type, COUNT(*) as cnt FROM telemetry_events GROUP BY event_type"
        ).fetchall()
        return {r['event_type']: r['cnt'] for r in rows}

    def save_game_state(self, game_name: str, state: Dict[str, Any]) -> None:
        """Save a game's progress state as JSON."""
        import json
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO game_states (game_name, state_json, saved_at) VALUES (?, ?, ?)",
                (game_name.lower(), json.dumps(state), time.time())
            )

    def load_game_state(self, game_name: str) -> Optional[Dict[str, Any]]:
        """Load a saved game state, or None."""
        import json
        row = self.conn.execute(
            "SELECT state_json FROM game_states WHERE game_name = ?",
            (game_name.lower(),)
        ).fetchone()
        if row is None:
            return None
        try:
            return json.loads(row['state_json'])
        except (json.JSONDecodeError, TypeError, ValueError):
            return None

    def delete_game_state(self, game_name: str) -> None:
        """Remove a saved game state (after resume or completion)."""
        with self.conn:
            self.conn.execute(
                "DELETE FROM game_states WHERE game_name = ?",
                (game_name.lower(),)
            )

    def has_game_state(self, game_name: str) -> bool:
        """Check if a saved game state exists."""
        row = self.conn.execute(
            "SELECT 1 FROM game_states WHERE game_name = ?",
            (game_name.lower(),)
        ).fetchone()
        return row is not None


# Global singleton
_manager: Optional[StatsManager] = None


def get_stats_manager() -> StatsManager:
    global _manager
    if _manager is None:
        _manager = StatsManager()
    return _manager
