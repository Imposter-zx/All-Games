"""
Error handling and safe game execution wrapper.
Provides consistent error handling across all games.
"""

import logging
import traceback

logger = logging.getLogger(__name__)


def safe_game_call(game_func, game_name: str) -> dict:
    """
    Safely execute a game function with comprehensive error handling.
    
    Args:
        game_func: The game function to execute
        game_name: Name of the game (for logging)
        
    Returns:
        Dictionary with game results or empty dict on error
    """
    try:
        logger.info(f"Starting game: {game_name}")
        result = game_func()
        logger.info(f"Completed game: {game_name}")
        return result if isinstance(result, dict) else {}
    
    except KeyboardInterrupt:
        logger.info(f"Player quit {game_name}")
        return {}
    
    except ImportError as e:
        logger.error(f"Missing dependency for {game_name}: {e}")
        from arcade_utils import draw_retro_box, C_RED
        draw_retro_box(
            60,
            "MISSING DEPENDENCY",
            [
                f"Error: {str(e)}",
                "",
                "Install required packages:",
                "  pip install -r requirements.txt"
            ],
            color=C_RED
        )
        return {}
    
    except Exception as e:
        logger.error(f"Error in {game_name}: {e}", exc_info=True)
        from arcade_utils import draw_retro_box, C_RED
        
        error_lines = [
            f"Game Error: {game_name}",
            "",
            f"Error: {str(e)[:60]}",
            "",
            "Check terminal_games/debug.log for details"
        ]
        
        draw_retro_box(
            70,
            "GAME ERROR",
            error_lines,
            color=C_RED
        )
        
        return {}


class GameException(Exception):
    """Base exception for game-related errors."""
    pass


class InvalidInputError(GameException):
    """Raised when invalid input is provided."""
    pass


class GameStateError(GameException):
    """Raised when game state is invalid."""
    pass


class StatsSaveError(GameException):
    """Raised when stats cannot be saved."""
    pass
