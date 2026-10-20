"""
Unit tests for StatsManager (SQLite-backed).
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from stats_manager import StatsManager, get_stats_manager


class TestStatsManagerInitialization:
    """Test StatsManager initialization."""

    def test_stats_manager_default_stats(self):
        manager = StatsManager()
        stats = manager.get_stats()
        assert stats is not None
        assert 'total_xp' in stats
        assert 'level' in stats
        assert 'games' in stats

    def test_level_calculation(self):
        manager = StatsManager()
        level, xp, progress = manager.get_level_and_xp()
        assert level >= 1


class TestStatsManagerXP:
    """Test XP functionality."""

    def test_add_xp(self):
        manager = StatsManager()
        before, _, _ = manager.get_level_and_xp()
        total_before = manager._get_profile_int('total_xp', 0)
        manager.add_xp(100)
        total_after = manager._get_profile_int('total_xp', 0)
        assert total_after == total_before + 100

    def test_add_negative_xp(self):
        manager = StatsManager()
        before, total_before, _ = manager.get_level_and_xp()
        manager.add_xp(-50)
        total_after = manager._get_profile_int('total_xp', 0)
        assert total_after == total_before  # Should not change

    def test_add_zero_xp(self):
        manager = StatsManager()
        before, total_before, _ = manager.get_level_and_xp()
        manager.add_xp(0)
        total_after = manager._get_profile_int('total_xp', 0)
        assert total_after == total_before

    def test_level_up_on_xp_threshold(self):
        manager = StatsManager()
        # Directly set total_xp to 490 and level to 1 using SQL
        conn = manager.conn
        conn.execute("INSERT OR REPLACE INTO profile (key, value) VALUES ('total_xp', '490')")
        conn.execute("INSERT OR REPLACE INTO profile (key, value) VALUES ('level', '1')")
        conn.commit()

        level, xp, _ = manager.get_level_and_xp()
        assert level == 1
        assert xp >= 490

        # Add 10 more to trigger level up (500 threshold)
        new_level = manager.add_xp(10)
        assert new_level >= 2
        level, xp, _ = manager.get_level_and_xp()
        assert level == 2


class TestStatsManagerGameStats:
    """Test game-specific stats."""

    def test_update_game_stats(self):
        manager = StatsManager()
        game_stats = {'high_score': 500, 'wins': 3}
        manager.update_game_stats('snake', game_stats)

        stats = manager.get_stats('snake')
        assert stats.get('high_score') == 500
        assert stats.get('wins') == 3

    def test_update_multiple_games(self):
        manager = StatsManager()
        manager.update_game_stats('snake', {'high_score': 500})
        manager.update_game_stats('tetris', {'high_score': 1000})

        snake_stats = manager.get_stats('snake')
        tetris_stats = manager.get_stats('tetris')
        assert snake_stats.get('high_score') == 500
        assert tetris_stats.get('high_score') == 1000

    def test_get_game_stats(self):
        manager = StatsManager()
        manager.update_game_stats('chess', {'wins': 5})
        stats = manager.get_stats('chess')
        assert 'wins' in stats
        assert stats['wins'] == 5

    def test_get_nonexistent_game_stats(self):
        manager = StatsManager()
        stats = manager.get_stats('nonexistent_game')
        assert stats == {}


class TestStatsManagerLevelAndXP:
    """Test level and XP calculations."""

    def test_get_level_and_xp(self):
        manager = StatsManager()
        manager._set_profile_int('total_xp', 0)
        manager._set_profile_int('level', 1)

        level, xp, progress = manager.get_level_and_xp()
        assert level == 1
        assert xp == 0
        assert 0 <= progress <= 1

    def test_get_level_and_xp_multiple_levels(self):
        manager = StatsManager()
        manager._set_profile_int('total_xp', 1500)
        manager._set_profile_int('level', 1 + 1500 // 500)

        level, xp, progress = manager.get_level_and_xp()
        assert level == 4
        assert xp == 1500
        assert 0 <= progress <= 1


class TestStatsManagerHighScore:
    """Test high score retrieval."""

    def test_get_high_score(self):
        manager = StatsManager()
        manager.update_game_stats('snake', {'high_score': 2500})

        score = manager.get_high_score('snake')
        assert score == 2500

    def test_get_high_score_nonexistent(self):
        manager = StatsManager()
        score = manager.get_high_score('nonexistent')
        assert score == 0

    def test_get_high_score_compatibility(self):
        manager = StatsManager()
        unique_game = 'test_compat_game'
        manager.update_game_stats(unique_game, {'best_score': 5000})
        score = manager.get_high_score(unique_game)
        assert score == 5000


class TestStatsManagerGlobalStats:
    """Test retrieving overall stats."""

    def test_get_overall_stats(self):
        manager = StatsManager()
        overall_stats = manager.get_stats()
        assert 'total_xp' in overall_stats
        assert 'level' in overall_stats
        assert 'games' in overall_stats


class TestStatsManagerSingleton:
    """Test singleton pattern."""

    def test_get_same_manager_instance(self):
        manager = get_stats_manager()
        assert manager is not None
        assert isinstance(manager, StatsManager)


class TestStatsManagerGameCounter:
    """Test games played counter."""

    def test_games_played_increment(self):
        manager = StatsManager()
        initial_count = manager._get_profile_int('games_played', 0)

        manager.update_game_stats('snake', {'high_score': 100})
        manager.update_game_stats('tetris', {'high_score': 200})

        final_count = manager._get_profile_int('games_played', 0)
        assert final_count >= initial_count + 2


class TestStatsManagerGameState:
    """Test save/load game state roundtrips."""

    def test_save_and_load_state_roundtrip(self):
        manager = StatsManager()
        manager.delete_game_state('breakout')
        state = {'score': 50, 'lives': 2}
        manager.save_game_state('breakout', state)
        loaded = manager.load_game_state('breakout')
        assert loaded == state

    def test_save_state_with_color_objects_serializes(self):
        from arcade_utils import Color
        manager = StatsManager()
        manager.delete_game_state('tetris')
        manager.save_game_state('tetris', {
            'piece': {'color': Color('\033[36m'), 'x': 3},
            'bricks': [{'active': True, 'color': Color('\033[31m')}],
        })
        loaded = manager.load_game_state('tetris')
        assert loaded['piece']['color'] == '\033[36m'
        assert loaded['bricks'][0]['color'] == '\033[31m'

    def test_load_missing_state_returns_none(self):
        manager = StatsManager()
        manager.delete_game_state('nonexistent_xyz')
        assert manager.load_game_state('nonexistent_xyz') is None


class TestStatsManagerAchievements:
    """Test achievement unlocking, XP integration, and transactional consistency."""

    def test_unlock_achievement_awards_configured_xp(self):
        from achievements_config import ACHIEVEMENTS
        manager = StatsManager()
        ach_id = next(iter(ACHIEVEMENTS.keys()))
        ach_xp = ACHIEVEMENTS[ach_id]['xp']
        xp_before = manager._get_profile_int('total_xp', 0)

        unlocked = manager.unlock_achievement(ach_id)
        assert unlocked is True
        xp_after = manager._get_profile_int('total_xp', 0)
        assert xp_after == xp_before + ach_xp
        assert ach_id in manager.get_unlocked_achievements()

    def test_unlock_duplicate_achievement_never_repeats_xp(self):
        from achievements_config import ACHIEVEMENTS
        manager = StatsManager()
        ach_id = next(iter(ACHIEVEMENTS.keys()))

        assert manager.unlock_achievement(ach_id) is True
        xp_after_first = manager._get_profile_int('total_xp', 0)

        # Second attempt must return False and never award XP again
        assert manager.unlock_achievement(ach_id) is False
        assert manager._get_profile_int('total_xp', 0) == xp_after_first

    def test_unlock_unknown_achievement_without_config(self):
        manager = StatsManager()
        xp_before = manager._get_profile_int('total_xp', 0)

        # Unknown achievement not in config
        unlocked = manager.unlock_achievement('completely_unknown_achievement_xyz')
        assert unlocked is True
        # Achievement is tracked, but 0 XP is added
        assert manager._get_profile_int('total_xp', 0) == xp_before
        assert 'completely_unknown_achievement_xyz' in manager.get_unlocked_achievements()

    def test_unlock_achievement_rollback_on_failure(self):
        manager = StatsManager()
        from achievements_config import ACHIEVEMENTS
        ach_id = next(iter(ACHIEVEMENTS.keys()))

        # Create a trigger on profile that aborts any write to profile
        manager.conn.execute("""
            CREATE TRIGGER abort_profile_write
            BEFORE INSERT ON profile
            BEGIN
                SELECT RAISE(ABORT, 'Simulated write failure');
            END;
        """)

        # When unlock_achievement tries to update profile XP, the trigger aborts the transaction
        res = manager.unlock_achievement(ach_id)
        assert res is False

        # Ensure that because of transaction rollback, the achievement was NOT recorded
        assert ach_id not in manager.get_unlocked_achievements()


class TestStatsManagerDatabaseIsolation:
    """Test database isolation, custom paths, and cleanup."""

    def test_custom_db_path_initialization(self, tmp_path):
        custom_db = str(tmp_path / 'custom_player.db')
        mgr = StatsManager(db_path=custom_db)
        assert mgr.db_path == custom_db
        assert os.path.exists(custom_db)
        mgr.close()

    def test_env_var_db_path_override(self, tmp_path, monkeypatch):
        env_db = str(tmp_path / 'env_player.db')
        monkeypatch.setenv("RETRO_ARCADE_DB_PATH", env_db)
        mgr = StatsManager()
        assert mgr.db_path == env_db
        assert os.path.exists(env_db)
        mgr.close()

    def test_independent_temporary_databases(self, tmp_path):
        db1_path = str(tmp_path / 'db1.db')
        db2_path = str(tmp_path / 'db2.db')
        mgr1 = StatsManager(db_path=db1_path)
        mgr2 = StatsManager(db_path=db2_path)

        mgr1.add_xp(500)
        assert mgr1._get_profile_int('total_xp', 0) == 500
        assert mgr2._get_profile_int('total_xp', 0) == 0

        mgr1.close()
        mgr2.close()

    def test_real_db_never_touched_during_tests(self):
        # Verify that active test manager is NOT using the user's home player.db
        mgr = get_stats_manager()
        assert mgr.db_path != StatsManager.DB_PATH
        assert "test_player.db" in mgr.db_path or "tmp" in mgr.db_path.lower()

    def test_connection_close_cleanup(self, tmp_path):
        db_path = str(tmp_path / 'cleanup.db')
        mgr = StatsManager(db_path=db_path)
        mgr.close()
        # Ensure connection is closed by checking that execute raises ProgrammingError
        import sqlite3
        with pytest.raises(sqlite3.ProgrammingError):
            mgr.conn.execute("SELECT 1")


