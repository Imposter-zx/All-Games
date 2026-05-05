"""
XP earning configuration and system for all games.
Provides consistent XP calculation logic based on game-specific metrics.
"""

from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class GameXPConfig:
    """XP earning configuration per game."""
    name: str
    base_multiplier: float = 1.0
    difficulty_easy: float = 0.5
    difficulty_normal: float = 1.0
    difficulty_hard: float = 2.0


# Define XP rewards for each game
# Formula principles:
# - Snake: points_scored * 0.5 = XP
# - Tetris: lines_cleared * 50 + score * 0.1 = XP
# - Chess: win * 100 + pieces * 5 = XP
# - Dungeon: room_cleared * 75 + enemy_defeated * 25 = XP
XP_CONFIGS = {
    'snake': GameXPConfig(
        name='Snake',
        base_multiplier=0.5  # points_scored * 0.5 = XP
    ),
    'tetris': GameXPConfig(
        name='Tetris',
        base_multiplier=1.0  # lines_cleared * 50 + score * 0.1
    ),
    'chess': GameXPConfig(
        name='Chess',
        base_multiplier=10.0  # win * 100 + pieces * 5
    ),
    'dungeon': GameXPConfig(
        name='Dungeon Crawler',
        base_multiplier=5.0   # room_cleared * 75 + combat * 25
    ),
    'breakout': GameXPConfig(
        name='Breakout',
        base_multiplier=0.8
    ),
    'space_shooter': GameXPConfig(
        name='Space Shooter',
        base_multiplier=0.6
    ),
    'minesweeper': GameXPConfig(
        name='Minesweeper',
        base_multiplier=10.0
    ),
    'sudoku': GameXPConfig(
        name='Sudoku',
        base_multiplier=5.0
    ),
    'pacman': GameXPConfig(
        name='Pac-Man',
        base_multiplier=0.4
    )
}


class XPSystem:
    """Dynamic XP earning system with difficulty multipliers."""
    
    def __init__(self, difficulty='normal'):
        """
        Initialize XP system.
        
        Args:
            difficulty: Game difficulty ('easy', 'normal', 'hard')
        """
        self.difficulty = difficulty.lower()
        self.multiplier = self._get_multiplier(self.difficulty)
    
    def _get_multiplier(self, difficulty: str) -> float:
        """
        Get difficulty multiplier.
        
        Args:
            difficulty: Difficulty string
            
        Returns:
            Multiplier value
        """
        multipliers = {
            'easy': 0.5,
            'normal': 1.0,
            'hard': 2.0
        }
        return multipliers.get(difficulty, 1.0)
    
    def calculate_xp(self, game_name: str, base_value: int) -> int:
        """
        Calculate XP earned for a game action.
        
        Args:
            game_name: Name of the game
            base_value: Base metric value (e.g., points, lines)
            
        Returns:
            XP amount to award
        """
        if game_name in XP_CONFIGS:
            config = XP_CONFIGS[game_name]
            base_xp = int(base_value * config.base_multiplier)
            return int(base_xp * self.multiplier)
        
        logger.warning(f"No XP config for game: {game_name}")
        return base_value


# Global instance
_xp_system = None


def get_xp_system(difficulty: str = 'normal') -> XPSystem:
    """
    Get global XP system instance.
    
    Args:
        difficulty: Difficulty level to use
        
    Returns:
        XPSystem instance
    """
    global _xp_system
    if _xp_system is None or _xp_system.difficulty != difficulty:
        _xp_system = XPSystem(difficulty)
    return _xp_system
