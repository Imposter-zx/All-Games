"""Smoke tests: every game must instantiate, run, and quit cleanly on synthetic input."""

import itertools
import msvcrt
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

import arcade
import arcade_utils
import pytest
import stats_manager


@pytest.fixture(autouse=True)
def quit_env(monkeypatch, tmp_path):
    """Simulate keys: a few ENTERs to start, then Q to quit. Fresh stats DB per test."""
    keys = itertools.chain(['\r'] * 5, itertools.repeat('q'))
    monkeypatch.setattr(msvcrt, 'getch', lambda: next(keys).encode())
    monkeypatch.setattr(msvcrt, 'kbhit', lambda: True)
    monkeypatch.setattr(time, 'sleep', lambda *a, **k: None)
    monkeypatch.setattr(arcade_utils, 'play_sound', lambda *a, **k: None)

    stats_manager._manager = None
    monkeypatch.setattr(stats_manager.StatsManager, 'DB_PATH', str(tmp_path / 'player.db'))
    yield


class TestAllGames:
    def test_all_games_play_and_quit_cleanly(self):
        game_map = arcade._build_game_map()
        assert len(game_map) == len(arcade.GAMES)
        for key, func in game_map.items():
            if func is None:
                continue
            result = func('easy')
            assert result is None or isinstance(result, dict)

    def test_every_game_has_menu_and_xp_and_score_entries(self):
        for g in arcade.GAMES:
            assert g in arcade._build_game_map(), f"{g} missing from game map"
            assert g in arcade.GAME_ICONS
            assert g in arcade.GAME_ICON_FALLBACK
            assert g in arcade.COMPACT_GAME_SHORT_NAMES

    def test_chess_entry_exports_function_or_none(self):
        func = arcade._build_game_map()['chess']
        assert func is None or callable(func)

    def test_play_functions_accept_difficulty(self):
        import inspect
        game_map = arcade._build_game_map()
        for key, func in game_map.items():
            if func is None:
                continue
            sig = inspect.signature(func)
            assert 'difficulty' in sig.parameters, f"{key} play function lacks difficulty param"


class TestSpecialModes:
    def test_special_mode_modules_import_and_export(self):
        import boss_fight
        import celebrations
        import chaos_mutator
        import daily_challenge
        import marathon
        import rhythm
        import secret_menu
        import vs_mode

        assert callable(marathon.run_marathon)
        assert callable(boss_fight.play_boss_fight)
        assert callable(rhythm.play_rhythm)
        assert callable(vs_mode.run_vs_mode)
        assert callable(secret_menu.show_secret_menu)
        assert callable(secret_menu.feed_key)
        assert callable(secret_menu.reset)
        assert callable(chaos_mutator.is_chaos)
        assert callable(chaos_mutator.chaos_mutate_input)
        assert callable(chaos_mutator.chaos_start_game)
        assert callable(daily_challenge.show_daily_challenge_menu)
        assert callable(daily_challenge.mark_daily_played)
        assert callable(celebrations.celebrate_level_up)
        assert callable(celebrations.check_and_celebrate)

    def test_secret_menu_konami_sequence(self):
        import secret_menu
        secret_menu.reset()
        for key in ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', 'b']:
            assert secret_menu.feed_key(key) is False
        assert secret_menu.feed_key('a') is True
        secret_menu.reset()
        assert secret_menu.feed_key('up') is False

    def test_chaos_mutate_input_passthrough_when_off(self):
        import chaos_mutator
        if not chaos_mutator.is_chaos():
            assert chaos_mutator.chaos_mutate_input('left') == 'left'


class TestDailyChallenge:
    def test_daily_high_score_and_played(self, tmp_path):
        import daily_challenge
        daily_challenge.set_daily_high_score('snake', 42)
        assert daily_challenge.get_daily_high_score('snake') == 42
        daily_challenge.set_daily_high_score('snake', 10)
        assert daily_challenge.get_daily_high_score('snake') == 42
        assert daily_challenge.has_daily_played('snake') is False
        daily_challenge.mark_daily_played('snake')
        assert daily_challenge.has_daily_played('snake') is True
        assert daily_challenge.daily_seed() == daily_challenge.daily_seed()
