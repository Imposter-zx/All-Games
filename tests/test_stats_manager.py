"""
Unit tests for StatsManager (SQLite-backed).
"""

import pytest
import sys
import os
from pathlib import Path

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
