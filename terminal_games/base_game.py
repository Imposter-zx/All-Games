"""
Abstract base class for all terminal games.
Provides consistent interface and common functionality.
"""

from abc import ABC, abstractmethod
import time
import logging

logger = logging.getLogger(__name__)


class BaseGame(ABC):
    """Abstract base class for all terminal games."""
    
    def __init__(self, game_name: str):
        """
        Initialize base game.
        
        Args:
            game_name: Name of the game (e.g., 'snake', 'tetris')
        """
        self.game_name = game_name
        self.score = 0
        self.xp_earned = 0
        self.start_time = None
        self.end_time = None
        self.game_over = False
    
    @abstractmethod
    def play(self) -> dict:
        """
        Main game loop. Must be implemented by subclasses.
        
        Returns:
            Dictionary with final game stats (score, xp_earned, etc.)
        """
        pass
    
    def add_xp(self, amount: int) -> None:
        """
        Award XP to player.
        
        Args:
            amount: Amount of XP to award
        """
        if amount < 0:
            logger.warning(f"Negative XP amount: {amount}")
            return
        self.xp_earned += amount
        # XP will be added to global stats in arcade.py
    
    def save_stats(self, stats_dict: dict) -> None:
        """
        Save game stats to persistent storage.
        
        Args:
            stats_dict: Dictionary containing game statistics to save
        """
        from arcade_utils import update_stats
        try:
            update_stats(self.game_name, stats_dict)
            logger.debug(f"Saved stats for {self.game_name}: {stats_dict}")
        except Exception as e:
            logger.error(f"Failed to save stats for {self.game_name}: {e}")
    
    def get_duration_seconds(self) -> int:
        """
        Get game duration in seconds.
        
        Returns:
            Duration in seconds, or 0 if not properly timed
        """
        if self.start_time and self.end_time:
            return int(self.end_time - self.start_time)
        return 0
    
    def get_final_stats(self) -> dict:
        """
        Get final game statistics.
        
        Returns:
            Dictionary with score, xp_earned, and duration
        """
        return {
            'score': self.score,
            'xp_earned': self.xp_earned,
            'duration_seconds': self.get_duration_seconds()
        }
    
    def start_timer(self) -> None:
        """Start the game timer."""
        self.start_time = time.time()
    
    def end_timer(self) -> None:
        """End the game timer."""
        self.end_time = time.time()
    
    def validate_score(self, score: int) -> bool:
        """
        Validate that score is reasonable.
        
        Args:
            score: Score to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(score, int) or score < 0:
            logger.warning(f"Invalid score: {score}")
            return False
        return True
