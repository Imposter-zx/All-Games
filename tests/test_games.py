import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add terminal_games to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from snake import SnakeGame
from breakout import BreakoutGame
from tetris import TetrisGame
from space_shooter import SpaceShooterGame
from pacman import PacmanGame
from minesweeper import MinesweeperGame
from sudoku import SudokuGame
from dungeon import DungeonGame
from chess_game import ChessGame, CHESS_AVAILABLE

class TestGamesIntegration(unittest.TestCase):
    """Integration tests to ensure all games follow the BaseGame interface."""

    def setUp(self):
        # Mocking StatsManager and arcade_utils to avoid side effects
        self.patchers = [
            patch('arcade_utils.load_stats', return_value={}),
            patch('arcade_utils.update_stats'),
            patch('arcade_utils.clear_screen'),
            patch('arcade_utils.beep'),
            patch('arcade_utils.get_key', return_value='q'), # Force quit on first input
            patch('msvcrt.kbhit', return_value=False) if os.name == 'nt' else patch('select.select', return_value=([False], [], []))
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    def test_snake_instantiation(self):
        game = SnakeGame()
        self.assertEqual(game.game_name, "snake")
        # Ensure it has required methods
        self.assertTrue(callable(getattr(game, "play")))
        self.assertTrue(callable(getattr(game, "_render")))

    def test_breakout_instantiation(self):
        game = BreakoutGame()
        self.assertEqual(game.game_name, "breakout")
        self.assertTrue(callable(getattr(game, "play")))

    def test_tetris_instantiation(self):
        game = TetrisGame()
        self.assertEqual(game.game_name, "tetris")
        self.assertTrue(callable(getattr(game, "play")))

    def test_space_shooter_instantiation(self):
        game = SpaceShooterGame()
        self.assertEqual(game.game_name, "space_shooter")
        self.assertTrue(callable(getattr(game, "play")))

    def test_pacman_instantiation(self):
        game = PacmanGame()
        self.assertEqual(game.game_name, "pacman")
        self.assertTrue(callable(getattr(game, "play")))

    def test_minesweeper_instantiation(self):
        game = MinesweeperGame()
        self.assertEqual(game.game_name, "minesweeper")
        self.assertTrue(callable(getattr(game, "play")))

    def test_sudoku_instantiation(self):
        game = SudokuGame()
        self.assertEqual(game.game_name, "sudoku")
        self.assertTrue(callable(getattr(game, "play")))

    def test_dungeon_instantiation(self):
        game = DungeonGame()
        self.assertEqual(game.game_name, "dungeon")
        self.assertTrue(callable(getattr(game, "play")))

    def test_chess_instantiation(self):
        if CHESS_AVAILABLE:
            game = ChessGame()
            self.assertEqual(game.game_name, "chess")
            self.assertTrue(callable(getattr(game, "play")))
        else:
            self.skipTest("python-chess not installed")

if __name__ == '__main__':
    unittest.main()
