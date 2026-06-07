"""XP earning configuration and system for all games."""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class GameXPConfig:
    """XP earning configuration per game."""
    name: str
    base_multiplier: float = 1.0
    difficulty_easy: float = 0.5
    difficulty_normal: float = 1.0
    difficulty_hard: float = 2.0


XP_CONFIGS: Dict[str, GameXPConfig] = {
    'snake': GameXPConfig(name='Snake', base_multiplier=0.5),
    'tetris': GameXPConfig(name='Tetris', base_multiplier=1.0),
    'chess': GameXPConfig(name='Chess', base_multiplier=10.0),
    'dungeon': GameXPConfig(name='Dungeon Crawler', base_multiplier=5.0),
    'breakout': GameXPConfig(name='Breakout', base_multiplier=0.8),
    'space_shooter': GameXPConfig(name='Space Shooter', base_multiplier=0.6),
    'minesweeper': GameXPConfig(name='Minesweeper', base_multiplier=10.0),
    'sudoku': GameXPConfig(name='Sudoku', base_multiplier=5.0),
    'pacman': GameXPConfig(name='Pac-Man', base_multiplier=0.4),
    '2048': GameXPConfig(name='2048', base_multiplier=0.2),
    'frogger': GameXPConfig(name='Frogger', base_multiplier=1.0),
    'asteroids': GameXPConfig(name='Asteroids', base_multiplier=0.5),
    'pong': GameXPConfig(name='Pong', base_multiplier=10.0),
    'flappy': GameXPConfig(name='Flappy Bird', base_multiplier=50.0),
    'racing': GameXPConfig(name='Racing', base_multiplier=1.0),
    'blackjack': GameXPConfig(name='Blackjack', base_multiplier=2.0),
    'connect_four': GameXPConfig(name='Connect Four', base_multiplier=3.0),
    'hangman': GameXPConfig(name='Hangman', base_multiplier=1.0),
    'wordle': GameXPConfig(name='Wordle', base_multiplier=2.0),
    'tictactoe': GameXPConfig(name='Tic-Tac-Toe', base_multiplier=1.5),
    'simon': GameXPConfig(name='Simon Says', base_multiplier=2.0),
    'trivia': GameXPConfig(name='Trivia', base_multiplier=1.0),
    'slots': GameXPConfig(name='Slots', base_multiplier=2.0),
    'memory': GameXPConfig(name='Memory', base_multiplier=1.5),
    'battleship': GameXPConfig(name='Battleship', base_multiplier=2.0),
    'crossword': GameXPConfig(name='Crossword', base_multiplier=2.0),
    'hanoi': GameXPConfig(name='Tower of Hanoi', base_multiplier=1.5),
    'typer': GameXPConfig(name='Typer', base_multiplier=2.0),
    'solitaire': GameXPConfig(name='Solitaire', base_multiplier=1.5),
    'rpsls': GameXPConfig(name='RPSLS', base_multiplier=1.0),
}


class XPSystem:
    """Dynamic XP earning system with difficulty multipliers."""

    def __init__(self, difficulty: str = 'normal') -> None:
        self.difficulty = difficulty.lower()
        self.multiplier = self._get_multiplier(self.difficulty)

    def _get_multiplier(self, difficulty: str) -> float:
        multipliers = {'easy': 0.5, 'normal': 1.0, 'hard': 2.0}
        return multipliers.get(difficulty, 1.0)

    def calculate_xp(self, game_name: str, base_value: int) -> int:
        if game_name in XP_CONFIGS:
            config = XP_CONFIGS[game_name]
            base_xp = int(base_value * config.base_multiplier)
            return int(base_xp * self.multiplier)

        logger.warning(f"No XP config for game: {game_name}")
        return base_value


# Global instance
_xp_system: Optional[XPSystem] = None


def get_xp_system(difficulty: str = 'normal') -> XPSystem:
    global _xp_system
    if _xp_system is None or _xp_system.difficulty != difficulty:
        _xp_system = XPSystem(difficulty)
    return _xp_system
