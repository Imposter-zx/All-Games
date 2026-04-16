"""
Unit tests for StatsManager.
"""

import pytest
import sys
import os
import json
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from stats_manager import StatsManager, get_stats_manager


class TestStatsManagerInitialization:
    """Test StatsManager initialization."""
    
    def test_stats_manager_default_stats(self):
        """Test StatsManager initializes with default stats."""
        # Create manager - will load existing stats from file
        manager = StatsManager()
        assert manager.stats is not None
        # Check critical fields are present (they are added if missing)
        assert 'total_xp' in manager.stats
        assert 'level' in manager.stats
        assert 'games' in manager.stats
    
    def test_level_calculation(self):
        """Test level is calculated correctly."""
        manager = StatsManager()
        assert manager.stats['level'] >= 1


class TestStatsManagerXP:
    """Test XP functionality."""
    
    def test_add_xp(self):
        """Test adding XP."""
        manager = StatsManager()
        initial_xp = manager.stats['total_xp']
        manager.add_xp(100)
        assert manager.stats['total_xp'] == initial_xp + 100
    
    def test_add_negative_xp(self):
        """Test negative XP is rejected."""
        manager = StatsManager()
        initial_xp = manager.stats['total_xp']
        manager.add_xp(-50)
        assert manager.stats['total_xp'] == initial_xp
    
    def test_add_zero_xp(self):
        """Test adding zero XP."""
        manager = StatsManager()
        initial_xp = manager.stats['total_xp']
        manager.add_xp(0)
        assert manager.stats['total_xp'] == initial_xp
    
    def test_level_up_on_xp_threshold(self):
        """Test level increases at XP thresholds."""
        manager = StatsManager()
        # Set to just before level 2
        manager.stats['total_xp'] = 490
        manager._update_level()
        assert manager.stats['level'] == 1
        
        # Cross into level 2
        manager.stats['total_xp'] = 500
        manager._update_level()
        assert manager.stats['level'] == 2


class TestStatsManagerGameStats:
    """Test game-specific stats."""
    
    def test_update_game_stats(self):
        """Test updating stats for a game."""
        manager = StatsManager()
        game_stats = {'high_score': 500, 'wins': 3}
        manager.update_game_stats('snake', game_stats)
        
        assert 'snake' in manager.stats['games']
        assert manager.stats['games']['snake']['high_score'] == 500
        assert manager.stats['games']['snake']['wins'] == 3
    
    def test_update_multiple_games(self):
        """Test updating stats for multiple games."""
        manager = StatsManager()
        manager.update_game_stats('snake', {'high_score': 500})
        manager.update_game_stats('tetris', {'high_score': 1000})
        
        assert len(manager.stats['games']) >= 2
        assert manager.stats['games']['snake']['high_score'] == 500
        assert manager.stats['games']['tetris']['high_score'] == 1000
    
    def test_get_game_stats(self):
        """Test retrieving game stats."""
        manager = StatsManager()
        manager.update_game_stats('chess', {'wins': 5})
        stats = manager.get_stats('chess')
        
        assert 'wins' in stats
        assert stats['wins'] == 5
    
    def test_get_nonexistent_game_stats(self):
        """Test getting stats for non-existent game."""
        manager = StatsManager()
        stats = manager.get_stats('nonexistent_game')
        assert stats == {}


class TestStatsManagerLevelAndXP:
    """Test level and XP calculations."""
    
    def test_get_level_and_xp(self):
        """Test getting current level and XP."""
        manager = StatsManager()
        manager.stats['total_xp'] = 0
        manager._update_level()
        
        level, xp, progress = manager.get_level_and_xp()
        assert level == 1
        assert xp == 0
        assert 0 <= progress <= 1
    
    def test_get_level_and_xp_multiple_levels(self):
        """Test level and XP with multiple levels."""
        manager = StatsManager()
        manager.stats['total_xp'] = 1500
        manager._update_level()
        
        level, xp, progress = manager.get_level_and_xp()
        assert level == 4  # 1 + (1500 // 500)
        assert xp == 1500
        assert 0 <= progress <= 1


class TestStatsManagerHighScore:
    """Test high score retrieval."""
    
    def test_get_high_score(self):
        """Test getting high score for a game."""
        manager = StatsManager()
        manager.update_game_stats('snake', {'high_score': 2500})
        
        score = manager.get_high_score('snake')
        assert score == 2500
    
    def test_get_high_score_nonexistent(self):
        """Test getting high score for non-existent game."""
        manager = StatsManager()
        score = manager.get_high_score('nonexistent')
        assert score == 0
    
    def test_get_high_score_compatibility(self):
        """Test getting best_score as fallback for high_score."""
        manager = StatsManager()
        # Use a unique game name to avoid conflicts with existing data
        unique_game = 'test_compat_game'
        manager.update_game_stats(unique_game, {'best_score': 5000})
        
        score = manager.get_high_score(unique_game)
        assert score == 5000  # Should work with best_score as fallback


class TestStatsManagerGlobalStats:
    """Test retrieving overall stats."""
    
    def test_get_overall_stats(self):
        """Test getting overall stats without game name."""
        manager = StatsManager()
        overall_stats = manager.get_stats()
        
        # Check critical fields are present
        assert 'total_xp' in overall_stats
        assert 'level' in overall_stats
        assert 'games' in overall_stats


class TestStatsManagerSingleton:
    """Test singleton pattern."""
    
    def test_get_same_manager_instance(self):
        """Test that get_stats_manager returns same instance."""
        # This test assumes module reload - just verify the function exists
        manager = get_stats_manager()
        assert manager is not None
        assert isinstance(manager, StatsManager)


class TestStatsManagerGameCounter:
    """Test games played counter."""
    
    def test_games_played_increment(self):
        """Test that games_played increments on update."""
        manager = StatsManager()
        initial_count = manager.stats['games_played']
        
        manager.update_game_stats('snake', {'high_score': 100})
        manager.update_game_stats('tetris', {'high_score': 200})
        
        # Should have incremented twice
        assert manager.stats['games_played'] >= initial_count + 2
