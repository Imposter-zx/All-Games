"""
Centralized player statistics manager.
Handles loading, saving, and updating player stats with validation.
"""

import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StatsManager:
    """Centralized player statistics manager."""
    
    STATS_FILE = "terminal_games/player_stats.json"
    
    DEFAULT_STATS = {
        "player_name": "RETRO_MASTER",
        "total_xp": 0,
        "level": 1,
        "games_played": 0,
        "total_playtime": 0,
        "games": {}
    }
    
    def __init__(self):
        """Initialize StatsManager and load existing stats."""
        self.stats = self._load_stats()
        # Ensure required fields are present
        if 'level' not in self.stats:
            self.stats['level'] = 1
        if 'total_xp' not in self.stats:
            self.stats['total_xp'] = 0
        if 'games' not in self.stats:
            self.stats['games'] = {}
        if 'games_played' not in self.stats:
            self.stats['games_played'] = 0
        logger.info(f"StatsManager initialized. Level: {self.stats.get('level', 1)}, XP: {self.stats.get('total_xp', 0)}")
    
    def _load_stats(self) -> dict:
        """
        Load stats from JSON file.
        
        Returns:
            Dictionary containing player statistics
        """
        if os.path.exists(self.STATS_FILE):
            try:
                with open(self.STATS_FILE, 'r') as f:
                    data = json.load(f)
                    # Validate required fields
                    if not isinstance(data, dict):
                        logger.warning("Stats file format invalid, using defaults")
                        return self.DEFAULT_STATS.copy()
                    logger.info(f"Loaded stats from {self.STATS_FILE}")
                    return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse stats JSON: {e}")
                return self.DEFAULT_STATS.copy()
            except IOError as e:
                logger.error(f"Failed to read stats file: {e}")
                return self.DEFAULT_STATS.copy()
        else:
            logger.info("No existing stats file, creating new")
            return self.DEFAULT_STATS.copy()
    
    def save(self) -> bool:
        """
        Save stats to JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(self.STATS_FILE), exist_ok=True)
            with open(self.STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
            logger.debug(f"Saved stats to {self.STATS_FILE}")
            return True
        except IOError as e:
            logger.error(f"Failed to save stats: {e}")
            return False
    
    def update_game_stats(self, game_name: str, stats_dict: dict) -> None:
        """
        Update stats for a specific game.
        
        Args:
            game_name: Name of the game
            stats_dict: Dictionary of stats to update
        """
        try:
            if game_name not in self.stats['games']:
                self.stats['games'][game_name] = {}
            
            self.stats['games'][game_name].update(stats_dict)
            self.stats['games_played'] += 1
            self.save()
            logger.info(f"Updated stats for {game_name}")
        except Exception as e:
            logger.error(f"Failed to update game stats: {e}")
    
    def add_xp(self, amount: int) -> int:
        """
        Add XP to player and update level.
        
        Args:
            amount: Amount of XP to add
            
        Returns:
            New level after XP addition
        """
        try:
            if amount < 0:
                logger.warning(f"Negative XP amount: {amount}")
                return self.stats['level']
            
            self.stats['total_xp'] += amount
            old_level = self.stats['level']
            self._update_level()
            new_level = self.stats['level']
            
            if new_level > old_level:
                logger.info(f"Level up! New level: {new_level}")
            
            self.save()
            return new_level
        except Exception as e:
            logger.error(f"Failed to add XP: {e}")
            return self.stats['level']
    
    def _update_level(self) -> None:
        """
        Calculate current level based on XP.
        Uses formula: level = 1 + (total_xp // 500)
        """
        self.stats['level'] = 1 + (self.stats['total_xp'] // 500)
    
    def get_stats(self, game_name: str = None) -> dict:
        """
        Get stats for a game or overall stats.
        
        Args:
            game_name: Optional game name. If None, returns overall stats.
            
        Returns:
            Dictionary of stats
        """
        try:
            if game_name:
                return self.stats['games'].get(game_name, {})
            return self.stats
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {} if game_name else self.DEFAULT_STATS.copy()
    
    def get_level_and_xp(self) -> tuple:
        """
        Get current level and XP.
        
        Returns:
            Tuple of (level, xp, progress_percentage)
        """
        level = self.stats['level']
        current_xp = self.stats['total_xp']
        xp_for_level = (level - 1) * 500
        xp_for_next = level * 500
        progress = (current_xp - xp_for_level) / (xp_for_next - xp_for_level) if xp_for_next > xp_for_level else 0
        progress = min(1.0, max(0.0, progress))  # Clamp to 0-1
        
        return level, current_xp, progress
    
    def get_high_score(self, game_name: str) -> int:
        """
        Get high score for a specific game.
        
        Args:
            game_name: Name of the game
            
        Returns:
            High score, or 0 if game not found
        """
        try:
            game_stats = self.stats['games'].get(game_name, {})
            # Try both 'high_score' and 'best_score' for compatibility
            return game_stats.get('high_score', game_stats.get('best_score', 0))
        except Exception as e:
            logger.error(f"Failed to get high score for {game_name}: {e}")
            return 0


# Global instance
_manager = None


def get_stats_manager() -> StatsManager:
    """
    Get global stats manager instance (singleton pattern).
    
    Returns:
        The global StatsManager instance
    """
    global _manager
    if _manager is None:
        _manager = StatsManager()
    return _manager
