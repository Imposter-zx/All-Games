"""Validate XP configs and achievements cover all 18 games."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from xp_config import XP_CONFIGS
from achievements_config import ACHIEVEMENTS


ALL_GAMES = [
    "snake", "breakout", "space_shooter", "tetris", "pacman",
    "dungeon", "minesweeper", "chess", "sudoku", "2048",
    "pong", "asteroids", "frogger", "flappy", "racing", "blackjack",
    "connect_four", "hangman",
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
