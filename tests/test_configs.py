"""Validate XP configs and achievements cover all 20 games."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from achievements_config import ACHIEVEMENTS
from xp_config import XP_CONFIGS

ALL_GAMES = [
    "snake", "breakout", "space_shooter", "tetris", "pacman",
    "dungeon", "minesweeper", "chess", "sudoku", "2048",
    "pong", "asteroids", "frogger", "flappy", "racing", "blackjack",
    "connect_four", "hangman", "wordle", "tictactoe", "simon", "trivia",
    "typer", "slots", "memory", "battleship", "crossword", "hanoi", "solitaire", "rpsls",
]


class TestXPConfigs:
    def test_all_games_have_xp_config(self):
        for game in ALL_GAMES:
            assert game in XP_CONFIGS, f"{game} missing from XP_CONFIGS"

    def test_all_xp_configs_have_valid_multipliers(self):
        for name, config in XP_CONFIGS.items():
            assert config.base_multiplier > 0, f"{name} has non-positive base multiplier"
            assert config.difficulty_easy < config.difficulty_normal < config.difficulty_hard, \
                f"{name} difficulty multipliers not strictly increasing"


class TestAchievements:
    def test_all_achievements_have_required_keys(self):
        required = {'name', 'description', 'xp'}
        for aid, ach in ACHIEVEMENTS.items():
            missing = required - set(ach.keys())
            assert not missing, f"Achievement '{aid}' missing keys: {missing}"

    def test_all_achievement_xp_positive(self):
        for aid, ach in ACHIEVEMENTS.items():
            assert ach.get('xp', 0) > 0, f"Achievement '{aid}' has non-positive XP"

    def test_new_game_achievements_exist(self):
        assert "blackjack_natural" in ACHIEVEMENTS
        assert "blackjack_500" in ACHIEVEMENTS
        assert "connect_four_win" in ACHIEVEMENTS
        assert "hangman_first_win" in ACHIEVEMENTS
        assert "hangman_streak" in ACHIEVEMENTS
        assert "wordle_win" in ACHIEVEMENTS
        assert "tictactoe_win" in ACHIEVEMENTS
        assert "tictactoe_perfect" in ACHIEVEMENTS
        assert "tictactoe_streak" in ACHIEVEMENTS
        assert "snake_1000" in ACHIEVEMENTS
        assert "breakout_500" in ACHIEVEMENTS
        assert "breakout_no_death" in ACHIEVEMENTS
        assert "space_shooter_5000" in ACHIEVEMENTS
        assert "space_shooter_10000" in ACHIEVEMENTS
        assert "dungeon_level_10" in ACHIEVEMENTS
        assert "dungeon_100_kills" in ACHIEVEMENTS
        assert "pacman_10000" in ACHIEVEMENTS
        assert "pacman_no_dot_left" in ACHIEVEMENTS
        assert "simon_first_win" in ACHIEVEMENTS
        assert "simon_streak_3" in ACHIEVEMENTS
        assert "trivia_first_win" in ACHIEVEMENTS
        assert "trivia_perfect" in ACHIEVEMENTS
        assert "trivia_grade_a" in ACHIEVEMENTS
        assert "slots_first_spin" in ACHIEVEMENTS
        assert "slots_jackpot" in ACHIEVEMENTS
        assert "slots_100_spins" in ACHIEVEMENTS
        assert "memory_first_win" in ACHIEVEMENTS
        assert "memory_perfect" in ACHIEVEMENTS
        assert "memory_streak_3" in ACHIEVEMENTS
        assert "battleship_first_win" in ACHIEVEMENTS
        assert "battleship_perfect" in ACHIEVEMENTS
        assert "battleship_fast_win" in ACHIEVEMENTS
        assert "crossword_first_win" in ACHIEVEMENTS
        assert "crossword_no_hints" in ACHIEVEMENTS
        assert "crossword_streak_3" in ACHIEVEMENTS
        assert "hanoi_first_win" in ACHIEVEMENTS
        assert "hanoi_perfect" in ACHIEVEMENTS
        assert "hanoi_5_disks" in ACHIEVEMENTS
        assert "typer_first_game" in ACHIEVEMENTS
        assert "typer_wpm_50" in ACHIEVEMENTS
        assert "typer_accuracy_100" in ACHIEVEMENTS
        assert "solitaire_first_win" in ACHIEVEMENTS
        assert "solitaire_fast_win" in ACHIEVEMENTS
        assert "solitaire_streak_3" in ACHIEVEMENTS
        assert "rpsls_first_win" in ACHIEVEMENTS
        assert "rpsls_perfect" in ACHIEVEMENTS
        assert "rpsls_streak_3" in ACHIEVEMENTS
