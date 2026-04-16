"""
Unit tests for BaseGame abstract class and its functionality.
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from base_game import BaseGame


class ConcreteGame(BaseGame):
    """Concrete implementation of BaseGame for testing."""
    
    def play(self) -> dict:
        """Simple test implementation."""
        self.score = 100
        self.add_xp(50)
        return {
            'score': self.score,
            'xp_earned': self.xp_earned
        }


class TestBaseGameInitialization:
    """Test BaseGame initialization."""
    
    def test_base_game_init(self):
        """Test BaseGame initializes correctly."""
        game = ConcreteGame("test_game")
        assert game.game_name == "test_game"
        assert game.score == 0
        assert game.xp_earned == 0
        assert game.start_time is None
        assert game.end_time is None
        assert game.game_over is False
    
    def test_base_game_different_names(self):
        """Test BaseGame with different game names."""
        games = ["snake", "tetris", "chess"]
        for game_name in games:
            game = ConcreteGame(game_name)
            assert game.game_name == game_name


class TestBaseGameXP:
    """Test XP functionality."""
    
    def test_add_xp(self):
        """Test adding XP."""
        game = ConcreteGame("test")
        game.add_xp(100)
        assert game.xp_earned == 100
    
    def test_add_negative_xp(self):
        """Test that negative XP is rejected."""
        game = ConcreteGame("test")
        initial_xp = game.xp_earned
        game.add_xp(-50)
        assert game.xp_earned == initial_xp  # Should not change
    
    def test_add_multiple_xp(self):
        """Test adding XP multiple times."""
        game = ConcreteGame("test")
        game.add_xp(50)
        game.add_xp(30)
        game.add_xp(20)
        assert game.xp_earned == 100
    
    def test_add_zero_xp(self):
        """Test adding zero XP."""
        game = ConcreteGame("test")
        game.add_xp(0)
        assert game.xp_earned == 0


class TestBaseGameScore:
    """Test score validation."""
    
    def test_validate_valid_score(self):
        """Test validation of valid score."""
        game = ConcreteGame("test")
        assert game.validate_score(100) is True
        assert game.validate_score(0) is True
        assert game.validate_score(999999) is True
    
    def test_validate_negative_score(self):
        """Test validation rejects negative score."""
        game = ConcreteGame("test")
        assert game.validate_score(-100) is False
    
    def test_validate_non_integer_score(self):
        """Test validation rejects non-integer score."""
        game = ConcreteGame("test")
        assert game.validate_score(100.5) is False
        assert game.validate_score("100") is False
        assert game.validate_score(None) is False


class TestBaseGameTimer:
    """Test game timing functionality."""
    
    def test_timer_start_and_end(self):
        """Test starting and ending game timer."""
        import time
        game = ConcreteGame("test")
        game.start_timer()
        assert game.start_time is not None
        time.sleep(0.1)
        game.end_timer()
        assert game.end_time is not None
        duration = game.get_duration_seconds()
        assert duration >= 0
    
    def test_timer_without_start(self):
        """Test duration when timer not properly started."""
        game = ConcreteGame("test")
        duration = game.get_duration_seconds()
        assert duration == 0


class TestBaseGamePlay:
    """Test play method."""
    
    def test_play_returns_dict(self):
        """Test that play returns a dictionary."""
        game = ConcreteGame("test")
        result = game.play()
        assert isinstance(result, dict)
        assert result['score'] == 100
        assert result['xp_earned'] == 50
    
    def test_final_stats(self):
        """Test getting final stats."""
        game = ConcreteGame("test")
        game.score = 250
        game.xp_earned = 100
        stats = game.get_final_stats()
        
        assert stats['score'] == 250
        assert stats['xp_earned'] == 100
        assert 'duration_seconds' in stats


class TestBaseGameAbstractMethods:
    """Test abstract method enforcement."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseGame cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseGame("test")
