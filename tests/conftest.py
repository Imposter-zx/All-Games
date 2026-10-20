import os
import sys

import pytest

# Ensure terminal_games and server are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TERMINAL_GAMES_DIR = os.path.join(BASE_DIR, "terminal_games")
SERVER_DIR = os.path.join(BASE_DIR, "server")

for p in [TERMINAL_GAMES_DIR, SERVER_DIR, BASE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(autouse=True)
def isolate_player_db(tmp_path, monkeypatch):
    """Ensure all tests operate against an isolated temporary SQLite database."""
    test_db = str(tmp_path / "test_player.db")
    monkeypatch.setenv("RETRO_ARCADE_DB_PATH", test_db)
    import stats_manager
    stats_manager.reset_stats_manager()
    yield
    stats_manager.reset_stats_manager()
