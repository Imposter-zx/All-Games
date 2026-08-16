"""Validate arcade menu structure: option count matches selection mapping and locks."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

import arcade


class TestMenuOptions:
    def test_menu_has_41_options_both_modes(self):
        assert len(arcade._build_menu_options(compact=False)) == 41
        assert len(arcade._build_menu_options(compact=True)) == 41

    def test_menu_covers_all_games(self):
        wide = arcade._build_menu_options(compact=False)
        for i, g in enumerate(arcade.GAMES):
            assert g in arcade._build_game_map(), f"{g} missing from game map"
            assert str(i + 1) in wide[i], f"menu entry {i} ({g}) missing number shortcut"

    def test_menu_options_match_game_order(self):
        wide = arcade._build_menu_options(compact=False)
        for i, g in enumerate(arcade.GAMES):
            display = arcade.GAME_DISPLAY_NAMES[i]
            assert display in wide[i], f"menu entry {i} does not show {display}"

    def test_trailing_menu_entries_are_utilities(self):
        wide = arcade._build_menu_options(compact=False)
        assert "Leaderboard" in wide[37]
        assert "Settings" in wide[38]
        assert "Tutorial" in wide[39]
        assert "Quit" in wide[40]

    def test_game_icons_cover_all_games(self):
        assert set(arcade.GAME_ICONS.keys()) == set(arcade.GAMES)
        assert set(arcade.GAME_ICON_FALLBACK.keys()) == set(arcade.GAMES)
        assert set(arcade.COMPACT_GAME_SHORT_NAMES.keys()) == set(arcade.GAMES)

    def test_menu_viewport_shows_all_entries_reachable(self):
        total = len(arcade._build_menu_options(compact=False))
        assert total == 41
        for selection in range(total):
            lo = min(max(selection - arcade.MENU_VIEWPORT // 2, 0),
                     max(0, total - arcade.MENU_VIEWPORT))
            assert lo <= selection <= lo + arcade.MENU_VIEWPORT

    def test_marathon_and_boss_keys_are_handled(self):
        import inspect
        src = inspect.getsource(arcade.main)
        assert "key.lower() == 'm'" in src
        assert "key.lower() == 'k'" in src


class TestInvadersLock:
    def test_is_game_locked_returns_false_for_normal_games(self):
        assert not arcade._is_game_locked("snake")
        assert not arcade._is_game_locked("tetris")

    def test_invaders_locked_below_5_achievements(self, monkeypatch, tmp_path):
        from stats_manager import get_stats_manager
        mgr = get_stats_manager()
        assert isinstance(mgr.get_unlocked_achievements(), list)
        locked = arcade._is_game_locked("invaders")
        unlocked_count = len(mgr.get_unlocked_achievements())
        assert locked == (unlocked_count < 5)
