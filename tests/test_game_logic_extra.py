"""Unit tests for pure logic in boss_fight, marathon, vs_mode, celebrations,
achievements_config, error_handler, arcade helpers and chess guard paths."""

import os
import sys
import time
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

import arcade
import arcade_utils
import pytest
import stats_manager


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    """Isolate stats DB, silence sound/popups and time for every logic test."""
    stats_manager._manager = None
    monkeypatch.setattr(stats_manager.StatsManager, 'DB_PATH', str(tmp_path / 'player.db'))
    monkeypatch.setattr(arcade_utils, 'play_sound', lambda *a, **k: None)
    monkeypatch.setattr(arcade_utils, 'beep', lambda *a, **k: None)
    monkeypatch.setattr(arcade_utils, 'show_popup', lambda *a, **k: None)
    monkeypatch.setattr(arcade_utils, 'clear_screen', lambda *a, **k: None)
    monkeypatch.setattr(time, 'sleep', lambda *a, **k: None)


class FakeMgr:
    """Records stats manager calls for assertions."""

    def __init__(self):
        self.xp_gained = []
        self.unlocked = []
        self.sessions = []
        self.updates = []
        self.high_scores = {}

    def add_xp(self, amount):
        self.xp_gained.append(amount)

    def unlock_achievement(self, aid):
        self.unlocked.append(aid)

    def record_session(self, game, score, xp, duration, difficulty):
        self.sessions.append((game, score, xp, duration, difficulty))

    def update_game_stats(self, game, data):
        self.updates.append((game, data))

    def get_high_score(self, game):
        return self.high_scores.get(game, 0)


class TestBossFight:
    def test_init_state(self):
        from boss_fight import BossFight
        game = BossFight()
        assert game.phase == 0
        assert game.boss_hp == 100
        assert game.player_hp == 100
        assert game.score == 0
        assert len(game.phase_names) == 4
        assert game.phase_names[0].startswith('QUICKSHOT')

    def test_run_phase_dispatches_by_phase(self, monkeypatch):
        from boss_fight import BossFight
        game = BossFight()
        seen = []
        monkeypatch.setattr(game, '_phase_quickshot', lambda: seen.append(0) or True)
        monkeypatch.setattr(game, '_phase_memory', lambda: seen.append(1) or True)
        monkeypatch.setattr(game, '_phase_reflex', lambda: seen.append(2) or True)
        monkeypatch.setattr(game, '_phase_final', lambda: seen.append(3) or True)
        for phase in range(4):
            game.phase = phase
            assert game._run_phase() is True
        assert seen == [0, 1, 2, 3]
        game.phase = 99
        assert game._run_phase() is True
        assert seen == [0, 1, 2, 3]

    def test_hp_bars(self, monkeypatch, capsys):
        import boss_fight
        from boss_fight import BossFight
        game = BossFight()
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        game.boss_hp = 35
        game.player_hp = 100
        game._show_hp()
        out = capsys.readouterr().out
        assert 'BOSS: [███░░░░░░░] 35%' in out
        assert 'YOU:  [██████████] 100%' in out

    def test_game_result_scoring(self, monkeypatch):
        import boss_fight
        from boss_fight import BossFight
        mgr = FakeMgr()
        monkeypatch.setattr(boss_fight, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(boss_fight, 'get_key', lambda: '\r')
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(boss_fight.time, 'time', lambda: 1000.0)
        game = BossFight()
        game._start_time = 990.0
        game.score = 7
        result = game._game_result()
        assert result['score'] == 7
        assert result['xp_earned'] == 700
        assert result['high_score'] == 7
        assert result['duration_seconds'] == 10
        assert result['boss_defeated'] is False
        assert mgr.xp_gained == [700]
        assert mgr.sessions == [('boss_fight', 7, 700, 10, 'hard')]
        assert mgr.updates[0][0] == 'boss_fight'
        assert mgr.updates[0][1]['high_score'] == 7
        assert 'boss_defeat' not in mgr.unlocked

    def test_game_result_boss_defeat(self, monkeypatch):
        import boss_fight
        from boss_fight import BossFight
        mgr = FakeMgr()
        monkeypatch.setattr(boss_fight, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(boss_fight, 'get_key', lambda: '\r')
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(boss_fight.time, 'time', lambda: 1000.0)
        game = BossFight()
        game._start_time = 990.0
        game.boss_hp = 0
        result = game._game_result()
        assert result['boss_defeated'] is True
        assert 'boss_defeat' in mgr.unlocked

    def test_quickshot_all_correct(self, monkeypatch):
        import boss_fight
        from boss_fight import BossFight
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(boss_fight.random, 'choice', lambda seq: 'w')
        monkeypatch.setattr(boss_fight, 'get_key', lambda: 'w')
        game = BossFight()
        assert game._phase_quickshot() is True
        assert game.score == 1000
        assert game.boss_hp == 85
        assert game.player_hp == 100

    def test_quickshot_all_wrong(self, monkeypatch):
        import boss_fight
        from boss_fight import BossFight
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(boss_fight.random, 'choice', lambda seq: 'w')
        monkeypatch.setattr(boss_fight, 'get_key', lambda: 'a')
        game = BossFight()
        assert game._phase_quickshot() is True
        assert game.score == 0
        assert game.player_hp == 55
        assert game.boss_hp == 85

    def test_memory_perfect_sequence(self, monkeypatch):
        import boss_fight
        from boss_fight import BossFight
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(boss_fight.random, 'randint', lambda a, b: 1)
        monkeypatch.setattr(boss_fight, 'get_key', lambda: '2')
        game = BossFight()
        assert game._phase_memory() is True
        assert game.score == 750
        assert game.boss_hp == 50
        assert game.player_hp == 100

    def test_memory_wrong_key_damages(self, monkeypatch):
        import boss_fight
        from boss_fight import BossFight
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(boss_fight.random, 'randint', lambda a, b: 1)
        monkeypatch.setattr(boss_fight, 'get_key', lambda: '3')
        game = BossFight()
        assert game._phase_memory() is True
        assert game.score == 0
        assert game.player_hp == 90
        assert game.boss_hp == 100

    def test_final_phase_strike_kills_boss(self, monkeypatch):
        import boss_fight
        from boss_fight import BossFight
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(boss_fight.random, 'choice', lambda seq: ('strike', 'w'))
        monkeypatch.setattr(boss_fight, 'get_key', lambda: 'w')
        game = BossFight()
        assert game._phase_final() is True
        assert game.score == 1350
        assert game.boss_hp == 0
        assert game.player_hp == 100

    def test_final_phase_miss_damages_player(self, monkeypatch):
        import boss_fight
        from boss_fight import BossFight
        monkeypatch.setattr(boss_fight, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(boss_fight.random, 'choice', lambda seq: ('dodge', 'up'))
        monkeypatch.setattr(boss_fight, 'get_key', lambda: 'z')
        game = BossFight()
        assert game._phase_final() is False
        assert game.score == 0
        assert game.player_hp == 0
        assert game.boss_hp == 100

    def test_play_boss_fight_delegates(self, monkeypatch):
        import boss_fight

        class Dummy:
            def play(self):
                return {'score': 5}

        monkeypatch.setattr(boss_fight, 'BossFight', Dummy)
        assert boss_fight.play_boss_fight('hard') == {'score': 5}


class TestMarathon:
    def test_game_names_order_and_count(self):
        import marathon
        assert len(marathon.GAME_NAMES) == 37
        ids = [gid for gid, _ in marathon.GAME_NAMES]
        assert len(set(ids)) == 37
        assert ids[0] == 'snake'
        assert ids[-1] == 'invaders'
        assert set(ids) == set(arcade.GAMES)

    def test_register_funcs_populates_map(self):
        import marathon
        marathon.GAME_PLAY_FUNCS.clear()
        marathon._register_funcs()
        assert len(marathon.GAME_PLAY_FUNCS) >= 36
        assert 'snake' in marathon.GAME_PLAY_FUNCS
        assert 'tetris' in marathon.GAME_PLAY_FUNCS
        assert 'invaders' in marathon.GAME_PLAY_FUNCS

    def test_full_run_accounting(self, monkeypatch):
        import marathon
        captured = {}
        mgr = FakeMgr()
        calls = []

        def fake_func(diff):
            calls.append(diff)
            val = {'easy': 1, 'normal': 2, 'hard': 3}[diff]
            return {'score': val, 'high_score': val, 'xp_earned': 10}

        monkeypatch.setattr(marathon, 'GAME_PLAY_FUNCS',
                            dict((gid, fake_func) for gid, _ in marathon.GAME_NAMES))
        monkeypatch.setattr(marathon, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(marathon, 'get_key', lambda: '\r')
        monkeypatch.setattr(marathon, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(marathon, '_show_marathon_progress', lambda *a, **k: None)
        monkeypatch.setattr(marathon, '_show_marathon_summary',
                            lambda *a, **k: captured.update({'args': a}))
        marathon.run_marathon()
        assert calls.count('easy') == 12
        assert calls.count('normal') == 12
        assert calls.count('hard') == 13
        assert captured['args'][2] == 37
        assert captured['args'][3] == 0
        assert captured['args'][0] == 75
        assert captured['args'][1] == 370
        assert len(captured['args'][5]) == 37
        assert captured['args'][6] is True
        assert mgr.xp_gained == [1850]
        assert set(mgr.unlocked) == {'marathon_first', 'marathon_half', 'marathon_full'}

    def test_run_with_failures_loses_lives(self, monkeypatch):
        import marathon
        captured = {}
        mgr = FakeMgr()

        def failing_func(diff):
            return {}

        monkeypatch.setattr(marathon, 'GAME_PLAY_FUNCS',
                            dict((gid, failing_func) for gid, _ in marathon.GAME_NAMES))
        monkeypatch.setattr(marathon, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(marathon, 'get_key', lambda: '\r')
        monkeypatch.setattr(marathon, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(marathon, '_show_marathon_progress', lambda *a, **k: None)
        monkeypatch.setattr(marathon, '_show_marathon_summary',
                            lambda *a, **k: captured.update({'args': a}))
        marathon.run_marathon()
        assert captured['args'][2] == 0
        assert captured['args'][3] == 3
        assert captured['args'][6] is False
        assert len(captured['args'][5]) == 3
        assert all(r['failed'] for r in captured['args'][5])
        assert mgr.xp_gained == [0]
        assert mgr.unlocked == ['marathon_first']

    def test_abort_returns_before_summary_unlocks(self, monkeypatch):
        import marathon
        captured = []
        mgr = FakeMgr()
        monkeypatch.setattr(marathon, 'GAME_PLAY_FUNCS',
                            dict((gid, lambda d: {'score': 1}) for gid, _ in marathon.GAME_NAMES))
        monkeypatch.setattr(marathon, 'get_stats_manager', lambda: mgr)
        keys = iter(['\r', 'q'])
        monkeypatch.setattr(marathon, 'get_key', lambda: next(keys))
        monkeypatch.setattr(marathon, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(marathon, '_show_marathon_progress', lambda *a, **k: None)
        monkeypatch.setattr(marathon, '_show_marathon_summary', lambda *a, **k: captured.append(a))
        marathon.run_marathon()
        assert len(captured) == 1
        assert captured[0][6] is False
        assert len(captured[0][5]) == 0
        assert mgr.unlocked == []
        assert mgr.xp_gained == []

    def test_quit_at_start(self, monkeypatch):
        import marathon
        captured = []
        mgr = FakeMgr()
        monkeypatch.setattr(marathon, 'GAME_PLAY_FUNCS', {})
        monkeypatch.setattr(marathon, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(marathon, 'get_key', lambda: 'q')
        monkeypatch.setattr(marathon, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        monkeypatch.setattr(marathon, '_show_marathon_summary', lambda *a, **k: captured.append(a))
        marathon.run_marathon()
        assert captured == []
        assert mgr.unlocked == []

    def test_summary_time_format(self, monkeypatch, capsys):
        import marathon
        from arcade_utils import strip_ansi
        monkeypatch.setattr(marathon, 'clear_screen', lambda: None)
        monkeypatch.setattr(marathon, 'get_key', lambda: '\r')
        marathon._show_marathon_summary(0, 0, 0, 0, 3661, [], True)
        clean = strip_ansi(capsys.readouterr().out)
        assert '1h1m1s' in clean
        assert 'MARATHON MASTER! +0 BONUS XP' in clean
        marathon._show_marathon_summary(0, 0, 0, 0, 59, [{'game': 'Snake', 'score': 5, 'xp': 1}], False)
        clean = strip_ansi(capsys.readouterr().out)
        assert '59s' in clean
        assert 'MARATHON FAILED' in clean
        assert 'Snake' in clean


class TestVSMode:
    def test_init_state(self):
        from vs_mode import VSMode
        game = VSMode()
        assert game.scores == {'Player 1': 0, 'Player 2': 0}
        assert game.round == 0
        assert game.max_rounds == 3

    def test_pick_game_routes(self, monkeypatch):
        import vs_mode
        from vs_mode import VSMode
        game = VSMode()
        monkeypatch.setattr(vs_mode.random, 'choice', lambda seq: seq[1])
        monkeypatch.setattr(game, '_vs_tapper', lambda: {'score': 1})
        monkeypatch.setattr(game, '_vs_reflex', lambda: {'score': 2})
        monkeypatch.setattr(game, '_vs_countdown', lambda: {'score': 3})
        assert game._pick_game() == {'score': 2}

    def test_tapper_scoring(self, monkeypatch):
        import vs_mode
        from vs_mode import VSMode
        game = VSMode()
        state = {'v': 0.0}

        def fake_time():
            state['v'] = min(6.0, state['v'] + 0.05)
            return state['v']

        keys = iter([' ', ' ', ' ', ' ', ' ', ' ', ' ', 'q'])
        monkeypatch.setattr(vs_mode.time, 'time', fake_time)
        monkeypatch.setattr(vs_mode, 'get_key', lambda: next(keys))
        monkeypatch.setattr(vs_mode, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        result = game._vs_tapper()
        assert result == {'score': 70, 'high_score': 70, 'xp_earned': 14, 'duration_seconds': 5}

    def test_reflex_all_hits(self, monkeypatch):
        import vs_mode
        from vs_mode import VSMode
        game = VSMode()
        monkeypatch.setattr(vs_mode.random, 'choice', lambda seq: ('W', 'w'))
        monkeypatch.setattr(vs_mode, 'get_key', lambda: 'w')
        monkeypatch.setattr(vs_mode, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        result = game._vs_reflex()
        assert result == {'score': 200, 'high_score': 200, 'xp_earned': 40, 'duration_seconds': 0}

    def test_countdown_perfect_timing(self, monkeypatch):
        import vs_mode
        from vs_mode import VSMode
        game = VSMode()
        times = iter([0.0, 2.9, 2.94, 2.95,
                      3.0, 5.9, 5.94, 5.95,
                      6.0, 8.9, 8.94, 8.95,
                      9.0, 11.9, 11.94, 11.95,
                      12.0, 14.9, 14.94, 14.95])
        monkeypatch.setattr(vs_mode.time, 'time', lambda: next(times))
        monkeypatch.setattr(vs_mode.random, 'uniform', lambda a, b: 3.0)
        monkeypatch.setattr(vs_mode, 'get_key', lambda: '\r')
        monkeypatch.setattr(vs_mode, 'clear_screen', lambda: None)
        monkeypatch.setattr('builtins.print', lambda *a, **k: None)
        result = game._vs_countdown()
        assert result == {'score': 500, 'high_score': 500, 'xp_earned': 100, 'duration_seconds': 0}

    def test_show_results_winner(self, monkeypatch, capsys):
        import vs_mode
        from vs_mode import VSMode
        game = VSMode()
        mgr = FakeMgr()
        monkeypatch.setattr(vs_mode, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(vs_mode, 'get_key', lambda: '\r')
        monkeypatch.setattr(vs_mode, 'clear_screen', lambda: None)
        monkeypatch.setattr(vs_mode.time, 'time', lambda: 1000.0)
        game._vs_start = 990.0
        game.scores = {'Player 1': 150, 'Player 2': 50}
        game._show_results()
        out = capsys.readouterr().out
        assert 'Player 1 WINS!' in out
        assert mgr.unlocked == ['vs_first', 'vs_win']
        assert mgr.xp_gained == [200]
        assert mgr.sessions == [('VS Mode', 200, 200, 10, 'normal')]

    def test_show_results_tie(self, monkeypatch, capsys):
        import vs_mode
        from vs_mode import VSMode
        game = VSMode()
        mgr = FakeMgr()
        monkeypatch.setattr(vs_mode, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(vs_mode, 'get_key', lambda: '\r')
        monkeypatch.setattr(vs_mode, 'clear_screen', lambda: None)
        monkeypatch.setattr(vs_mode.time, 'time', lambda: 1000.0)
        game._vs_start = 990.0
        game.scores = {'Player 1': 80, 'Player 2': 80}
        game._show_results()
        out = capsys.readouterr().out
        assert 'TIE!' in out
        assert mgr.unlocked == ['vs_first']
        assert mgr.xp_gained == [0]
        assert mgr.sessions == [('VS Mode', 160, 0, 10, 'normal')]

    def test_run_vs_mode_delegates(self, monkeypatch):
        import vs_mode

        class Dummy:
            def __init__(self):
                self.ran = False

            def run(self):
                self.ran = True

        dummy = Dummy()
        monkeypatch.setattr(vs_mode, 'VSMode', lambda: dummy)
        vs_mode.run_vs_mode()
        assert dummy.ran is True


class TestCelebrations:
    def test_check_new_high_score(self, monkeypatch):
        import celebrations

        class Mgr:
            def __init__(self):
                self.keys = []

            def get_high_score(self, key):
                self.keys.append(key)
                return 50

        mgr = Mgr()
        called = []
        monkeypatch.setattr(celebrations, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(celebrations, 'celebrate_high_score',
                            lambda *a: called.append(a))
        celebrations.check_and_celebrate('Space Shooter', 100)
        assert mgr.keys == ['space_shooter']
        assert called == [('Space Shooter', 100, 50)]

    def test_check_no_celebration_when_not_beaten(self, monkeypatch):
        import celebrations

        class Mgr:
            def get_high_score(self, key):
                return 100

        mgr = Mgr()
        called = []
        monkeypatch.setattr(celebrations, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(celebrations, 'celebrate_high_score',
                            lambda *a: called.append(a))
        celebrations.check_and_celebrate('Pac-Man', 100)
        celebrations.check_and_celebrate('Snake', 0)
        celebrations.check_and_celebrate('Snake', -5)
        assert mgr.get_high_score('pacman') == 100
        assert called == []

    def test_check_uses_kwarg_key(self, monkeypatch):
        import celebrations

        class Mgr:
            def __init__(self):
                self.keys = []

            def get_high_score(self, key):
                self.keys.append(key)
                return 0

        mgr = Mgr()
        monkeypatch.setattr(celebrations, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(celebrations, 'celebrate_high_score', lambda *a: None)
        celebrations.check_and_celebrate('Pac-Man', 10, game_key='pacman')
        assert mgr.keys == ['pacman']

    def test_guard_returns_without_celebration(self, monkeypatch):
        import celebrations

        def fail_print(*a, **k):
            raise AssertionError('print was called')

        monkeypatch.setattr('builtins.print', fail_print)
        monkeypatch.setattr(celebrations.time, 'sleep', lambda *a: None)
        monkeypatch.setattr(celebrations, 'clear_screen', lambda: None)
        celebrations.celebrate_high_score('Snake', 100, 200)


class TestAchievementsConfig:
    def test_inventory_invariants(self):
        from achievements_config import ACHIEVEMENTS
        assert len(ACHIEVEMENTS) == 113
        assert len(set(ACHIEVEMENTS)) == 113
        for aid, entry in ACHIEVEMENTS.items():
            assert set(entry) == {'name', 'description', 'xp'}
            assert isinstance(entry['xp'], int)
            assert entry['xp'] > 0

    def test_get_achievement(self):
        from achievements_config import get_achievement
        assert get_achievement('first_game')['name'] == 'First Steps'
        assert get_achievement('first_game')['xp'] == 100
        assert get_achievement('marathon_full')['xp'] == 5000
        assert get_achievement('boss_defeat')['xp'] == 2000
        assert get_achievement('invaders_first')['xp'] == 300
        assert get_achievement('does_not_exist') is None


class TestErrorHandler:
    def test_passthrough_result(self):
        from error_handler import safe_game_call
        assert safe_game_call(lambda: {'score': 10}, 'Snake') == {'score': 10}

    def test_non_dict_result_becomes_empty(self):
        from error_handler import safe_game_call
        assert safe_game_call(lambda: None, 'Snake') == {}
        assert safe_game_call(lambda: 'x', 'Snake') == {}

    def test_kwargs_forwarded(self):
        from error_handler import safe_game_call
        assert safe_game_call(lambda **kw: {'got': kw}, 'Snake', difficulty='hard') == \
            {'got': {'difficulty': 'hard'}}

    def test_keyboard_interrupt(self):
        from error_handler import safe_game_call

        def boom():
            raise KeyboardInterrupt()

        assert safe_game_call(boom, 'Snake') == {}

    def test_import_error_branch(self, monkeypatch):
        from error_handler import safe_game_call
        drawn = []

        def fake_draw(*a, **k):
            drawn.append(a)

        monkeypatch.setattr('arcade_utils.draw_retro_box', fake_draw)

        def boom():
            raise ImportError('numpy missing')

        assert safe_game_call(boom, 'Snake') == {}
        assert drawn and drawn[0][1] == 'MISSING DEPENDENCY'

    def test_generic_exception_branch(self, monkeypatch):
        from error_handler import safe_game_call
        drawn = []

        def fake_draw(*a, **k):
            drawn.append(a)

        monkeypatch.setattr('arcade_utils.draw_retro_box', fake_draw)

        def boom():
            raise ValueError('boom')

        assert safe_game_call(boom, 'Snake') == {}
        assert drawn and drawn[0][1] == 'GAME ERROR'

    def test_exception_hierarchy(self):
        from error_handler import (
            GameException,
            GameStateError,
            InvalidInputError,
            StatsSaveError,
        )
        assert issubclass(GameException, Exception)
        assert issubclass(InvalidInputError, GameException)
        assert issubclass(GameStateError, GameException)
        assert issubclass(StatsSaveError, GameException)


class TestArcadeHelpers:
    def test_games_and_display_names(self):
        assert len(arcade.GAMES) == 37
        assert arcade.GAMES[0] == 'snake'
        assert arcade.GAMES[-1] == 'invaders'
        assert len(arcade.GAME_DISPLAY_NAMES) == 37
        assert len(arcade.NAME_TO_KEY) == 37
        assert arcade.NAME_TO_KEY['Pac-Man'] == 'pacman'
        assert arcade.NAME_TO_KEY['2048'] == '2048'
        assert arcade.NAME_TO_KEY['Tower of Hanoi'] == 'hanoi'

    def test_icon_maps_cover_all_games(self):
        assert set(arcade.GAME_ICONS) == set(arcade.GAMES)
        assert set(arcade.GAME_ICON_FALLBACK) == set(arcade.GAMES)
        assert set(arcade.COMPACT_GAME_SHORT_NAMES) == set(arcade.GAMES)
        assert all(len(f) == 1 for f in arcade.GAME_ICON_FALLBACK.values())

    def test_menu_viewport(self):
        assert arcade.MENU_VIEWPORT == 14

    def test_format_time(self):
        cases = {
            0: '0s', 7: '7s', 59: '59s', 60: '1m0s', 61: '1m1s',
            90: '1m30s', 3599: '59m59s', 3600: '1h0m', 3661: '1h1m', 7200: '2h0m',
        }
        for seconds, expected in cases.items():
            assert arcade._format_time(seconds) == expected

    def test_build_menu_options_compact(self, monkeypatch):
        class FakeStdout:
            encoding = 'utf-8'

        monkeypatch.setattr(sys, 'stdout', FakeStdout())
        options = arcade._build_menu_options(True)
        assert len(options) == 41
        assert options[0] == '1.Snake'
        assert options[6] == '7.Mineswp'
        assert options[19] == '20.TTT'
        assert options[36] == '37.Invaders'
        assert options[37:] == ['L. 🏆 Leaderboard', 'S. ⚙️ Settings',
                                'H. 📖 Tutorial', 'Q. 🚪 Quit']

    def test_build_menu_options_full(self, monkeypatch):
        class FakeStdout:
            encoding = 'utf-8'

        monkeypatch.setattr(sys, 'stdout', FakeStdout())
        options = arcade._build_menu_options(False)
        assert len(options) == 41
        assert options[0] == '1. 🐍 Snake'
        assert options[36] == '37. 👾 Invaders'
        assert options[37].startswith('L. ')

    def test_build_menu_options_locked_invaders(self, monkeypatch):
        class FakeStdout:
            encoding = 'utf-8'

        monkeypatch.setattr(sys, 'stdout', FakeStdout())
        options = arcade._build_menu_options(True, invaders_locked=True)
        assert options[36] == '37.Invaders 🔒'
        full = arcade._build_menu_options(False, invaders_locked=True)
        assert '🔒' in full[36]

    def test_is_game_locked(self, monkeypatch):
        assert arcade._is_game_locked('snake') is False
        assert arcade._is_game_locked('tetris') is False
        fake = types.SimpleNamespace(is_invaders_unlocked=lambda: False)
        monkeypatch.setitem(sys.modules, 'invaders', fake)
        assert arcade._is_game_locked('invaders') is True
        fake2 = types.SimpleNamespace(is_invaders_unlocked=lambda: True)
        monkeypatch.setitem(sys.modules, 'invaders', fake2)
        assert arcade._is_game_locked('invaders') is False

    def test_build_game_map(self):
        game_map = arcade._build_game_map()
        assert set(game_map) == set(arcade.GAMES)
        assert callable(game_map['snake'])
        assert game_map['invaders'] is not None


class TestChessGuard:
    @pytest.fixture(autouse=True)
    def only_without_lib(self):
        import chess_game
        if chess_game.CHESS_AVAILABLE:
            pytest.skip('requires python-chess NOT installed')

    def test_no_lib_board_is_none(self):
        import chess_game
        game = chess_game.ChessGame('normal')
        assert game.board is None
        assert game.game_name == 'chess'

    def test_no_lib_state_roundtrip_noop(self):
        import chess_game
        game = chess_game.ChessGame('normal')
        assert game.save_state_json() == {}
        game.load_state_json({'fen': 'bad fen'})
        assert game.board is None

    def test_ai_move_returns_none_without_engine(self):
        import chess_game
        game = chess_game.ChessGame('normal')
        game.engine = None
        assert game._get_ai_move() is None

    def test_play_returns_empty_stats(self, monkeypatch):
        import chess_game
        popups = []
        monkeypatch.setattr(chess_game, 'show_popup', lambda *a, **k: popups.append(a))
        monkeypatch.setattr(chess_game.ChessGame, 'get_final_stats',
                            lambda self: {'score': 0, 'xp_earned': 0, 'duration_seconds': 0})
        game = chess_game.ChessGame('normal')
        result = game.play()
        assert len(popups) == 1
        assert 'NOT INSTALLED' in popups[0][0]
        assert result == {'score': 0, 'xp_earned': 0, 'duration_seconds': 0}

    def test_play_chess_returns_none_without_lib(self, monkeypatch):
        import chess_game
        monkeypatch.setattr(chess_game, 'show_popup', lambda *a, **k: None)
        assert chess_game.play_chess('easy') is None

    def test_find_stockfish_first_candidate(self, monkeypatch):
        import chess_game
        calls = []

        class FakeResult:
            returncode = 0
            stdout = b''

        def fake_run(cmd, **kw):
            calls.append(cmd[0])
            return FakeResult()

        monkeypatch.setattr('subprocess.run', fake_run)
        assert chess_game._find_stockfish() == 'stockfish'
        assert calls[0] == 'stockfish'

    def test_find_stockfish_skips_missing(self, monkeypatch):
        import chess_game

        def fake_run(cmd, **kw):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr('subprocess.run', fake_run)
        assert chess_game._find_stockfish() is None

    def test_find_stockfish_stdout_match(self, monkeypatch):
        import chess_game

        class FakeResult:
            returncode = 1
            stdout = b'Stockfish 16.1 by the Stockfish developers'

        def fake_run(cmd, **kw):
            return FakeResult()

        monkeypatch.setattr('subprocess.run', fake_run)
        assert chess_game._find_stockfish() == 'stockfish'

    def test_find_stockfish_timeout_skipped(self, monkeypatch):
        import chess_game

        def fake_run(cmd, **kw):
            raise subprocess.TimeoutExpired(cmd, 1)

        import subprocess
        monkeypatch.setattr('subprocess.run', fake_run)
        assert chess_game._find_stockfish() is None


class TestChessEngine:
    @pytest.fixture(autouse=True)
    def requires_lib(self):
        import chess_game
        if not chess_game.CHESS_AVAILABLE:
            pytest.skip('requires python-chess installed')

    def test_initial_board_is_standard(self):
        import chess
        import chess_game
        game = chess_game.ChessGame('normal')
        assert game.board is not None
        assert game.board.fen().split()[0] == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        assert game.board.turn == chess.WHITE
        assert len(list(game.board.legal_moves)) == 20

    def test_state_roundtrip(self):
        import chess
        import chess_game
        game = chess_game.ChessGame('normal')
        game.board.push(chess.Move.from_uci('e2e4'))
        game.board.push(chess.Move.from_uci('e7e5'))
        game.score = 30
        game.selected_square = chess.E2
        state = game.save_state_json()
        assert state['fen'].startswith('rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR')
        assert state['score'] == 30
        assert state['moves'] == ['e2e4', 'e7e5']
        loaded = chess_game.ChessGame('normal')
        loaded.load_state_json(state)
        assert loaded.board.fen() == game.board.fen()
        assert loaded.score == 30
        assert loaded.selected_square == chess.E2

    def test_load_state_with_custom_fen(self):
        import chess_game
        game = chess_game.ChessGame('normal')
        game.load_state_json({'fen': '4k3/8/8/8/8/8/8/4K3 w - - 0 1'})
        assert game.board.piece_at(chess_game.chess.E4) is None

    def test_ai_move_returns_legal(self):
        import chess_game
        game = chess_game.ChessGame('normal')
        game.engine = None
        import random
        random.seed(42)
        move = game._get_ai_move()
        assert move is not None
        assert move in list(game.board.legal_moves)
        game.board.push(move)
        assert game.board.move_stack

    def test_ai_move_none_when_checkmated(self):
        import chess_game
        game = chess_game.ChessGame('normal')
        game.engine = None
        game.board = chess_game.chess.Board(
            'rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3')
        assert game.board.is_checkmate()
        assert game._get_ai_move() is None

    def test_ai_move_prefers_captures(self, monkeypatch):
        import chess_game
        game = chess_game.ChessGame('normal')
        game.engine = None
        game.board = chess_game.chess.Board(
            'rnbqkbnr/1p1ppppp/2p5/2PQ4/8/8/1PPP1PPP/RNB1KBNR b KQkq - 0 2')
        capture_moves = [m for m in game.board.legal_moves if game.board.is_capture(m)]
        assert capture_moves
        monkeypatch.setattr('chess_game.random.random', lambda: 0.0)
        monkeypatch.setattr('chess_game.random.choice', lambda seq: seq[0])
        move = game._get_ai_move()
        assert move in capture_moves

    def test_handle_game_end_win(self, monkeypatch):
        import chess_game
        popups = []
        unlocked = []
        xp_gained = []
        monkeypatch.setattr(chess_game, 'show_popup', lambda *a, **k: popups.append(a[0]))
        monkeypatch.setattr(chess_game.ChessGame, 'unlock_achievement',
                            lambda self, *a: unlocked.append(a))
        monkeypatch.setattr(chess_game.ChessGame, 'award_xp_for_action',
                            lambda self, n: xp_gained.append(n))
        game = chess_game.ChessGame('normal')
        game.u_white = True
        game.board = chess_game.chess.Board()
        for mv in ('e2e4', 'e7e5', 'f1c4', 'b8c6', 'd1h5', 'g8f6', 'h5f7'):
            game.board.push_uci(mv)
        assert game.board.is_checkmate()
        game._handle_game_end()
        assert game.game_over is True
        assert unlocked == [('chess_win', 'Grandmaster')]
        assert xp_gained == [100]
        assert popups == ['VICTORY! YOU WON!']

    def test_handle_game_end_draw(self, monkeypatch):
        import chess_game
        popups = []
        xp_gained = []
        monkeypatch.setattr(chess_game, 'show_popup', lambda *a, **k: popups.append(a[0]))
        monkeypatch.setattr(chess_game.ChessGame, 'award_xp_for_action',
                            lambda self, n: xp_gained.append(n))
        game = chess_game.ChessGame('normal')
        game.board = chess_game.chess.Board('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1')
        assert game.board.is_stalemate()
        game._handle_game_end()
        assert popups == ['DRAW!']
        assert xp_gained == [50]

    def test_handle_game_end_loss(self, monkeypatch):
        import chess_game
        popups = []
        monkeypatch.setattr(chess_game, 'show_popup', lambda *a, **k: popups.append(a[0]))
        monkeypatch.setattr(chess_game.ChessGame, 'unlock_achievement', lambda *a, **k: None)
        monkeypatch.setattr(chess_game.ChessGame, 'award_xp_for_action', lambda *a, **k: None)
        game = chess_game.ChessGame('normal')
        game.u_white = False
        game.board = chess_game.chess.Board()
        for mv in ('e2e4', 'e7e5', 'f1c4', 'b8c6', 'd1h5', 'g8f6', 'h5f7'):
            game.board.push_uci(mv)
        assert game.board.is_checkmate()
        game._handle_game_end()
        assert popups == ['DEFEAT!']
        assert game.game_over is True


class TestWordle:
    def test_guess_all_green(self):
        from wordle import WordleGame
        game = WordleGame('normal')
        game.target = 'APPLE'
        assert game._check_guess('APPLE') == [('A', 'green'), ('P', 'green'), ('P', 'green'),
                                              ('L', 'green'), ('E', 'green')]

    def test_guess_mixed_feedback(self):
        from wordle import WordleGame
        game = WordleGame('normal')
        game.target = 'ABIDE'
        result = game._check_guess('AEFIG')
        assert result == [('A', 'green'), ('E', 'yellow'), ('F', 'gray'),
                          ('I', 'yellow'), ('G', 'gray')]

    def test_duplicate_letters_only_count_once(self):
        from wordle import WordleGame
        game = WordleGame('normal')
        game.target = 'ABBA'
        result = game._check_guess('AAAA')
        assert result == [('A', 'green'), ('A', 'gray'), ('A', 'gray'), ('A', 'green')]

    def test_daily_word_deterministic(self):
        from wordle import WordleGame
        assert WordleGame('normal', daily=True).target == \
            WordleGame('normal', daily=True).target
        assert len(WordleGame('normal', daily=True).target) == 5

    def test_state_roundtrip(self):
        from wordle import WordleGame
        game = WordleGame('normal')
        game.target = 'STARE'
        game.attempts = ['SLATE', 'STARE']
        game.round = 3
        state = game.save_state_json()
        loaded = WordleGame('normal')
        loaded.load_state_json(state)
        assert loaded.target == 'STARE'
        assert loaded.attempts == ['SLATE', 'STARE']
        assert loaded.round == 3


class TestTicTacToe:
    def test_check_winner_lines(self):
        from tictactoe import _check_winner
        X, Oh, E = 'X', 'O', '.'
        assert _check_winner([[X, X, X], [Oh, Oh, E], [E, E, E]]) == 'X'
        assert _check_winner([[Oh, X, E], [Oh, X, E], [Oh, E, E]]) == 'O'
        assert _check_winner([[X, Oh, E], [E, X, Oh], [E, E, X]]) == 'X'
        assert _check_winner([[E, Oh, X], [E, X, Oh], [X, Oh, E]]) == 'X'
        assert _check_winner([[X, Oh, E], [E, Oh, E], [E, X, Oh]]) is None

    def test_is_full(self):
        from tictactoe import _is_full
        assert _is_full([['X', 'O', 'X'], ['O', 'X', 'O'], ['O', 'X', 'O']]) is True
        assert _is_full([['X', 'O', '.'], ['O', 'X', 'O'], ['O', 'X', 'O']]) is False

    def test_winner_line_coordinates(self):
        from tictactoe import _get_winner_line
        assert _get_winner_line([['X', 'X', 'X'], ['O', 'O', '.'], ['.', '.', '.']], 'X') == \
            [(0, 0), (0, 1), (0, 2)]
        assert _get_winner_line([['O', 'X', '.'], ['O', 'X', '.'], ['O', '.', '.']], 'O') == \
            [(0, 0), (1, 0), (2, 0)]

    def test_parse_move(self):
        from tictactoe import _parse_move
        assert _parse_move('a1') == (0, 0)
        assert _parse_move('C3') == (2, 2)
        assert _parse_move('b2') == (1, 1)
        assert _parse_move('d4') is None
        assert _parse_move('x') is None
        assert _parse_move('a4') is None

    def test_empty_cells(self):
        from tictactoe import _get_empty_cells
        board = [['X', '.', '.'], ['.', 'O', '.'], ['.', '.', '.']]
        assert len(_get_empty_cells(board)) == 7
        assert (0, 0) not in _get_empty_cells(board)

    def test_minimax_scores(self):
        from tictactoe import _minimax
        X, Oh, E = 'X', 'O', '.'
        assert _minimax([[X, X, X], [Oh, Oh, E], [E, E, E]], 0, True, X, Oh) == 10
        assert _minimax([[Oh, Oh, Oh], [X, X, E], [E, E, E]], 0, True, X, Oh) == -10
        assert _minimax([[X, Oh, X], [X, Oh, Oh], [Oh, X, E]], 0, True, X, Oh) == 0

    def test_ai_move_takes_win(self):
        from tictactoe import _ai_move
        board = [['X', 'X', '.'], ['O', 'O', '.'], ['.', '.', '.']]
        assert _ai_move(board, 'X', 'hard') == (0, 2)

    def test_ai_move_blocks_human(self):
        from tictactoe import _ai_move
        board = [['O', 'O', '.'], ['X', '.', '.'], ['.', '.', '.']]
        assert _ai_move(board, 'X', 'normal') == (0, 2)

    def test_ai_move_easy_random(self, monkeypatch):
        import tictactoe
        from tictactoe import _ai_move
        board = [['X', '.', '.'], ['.', '.', '.'], ['.', '.', '.']]
        monkeypatch.setattr(tictactoe.random, 'choice', lambda seq: (1, 1))
        assert _ai_move(board, 'O', 'easy') == (1, 1)

    def test_ai_move_first_play_corner(self):
        from tictactoe import _ai_move
        board = [['.', '.', '.'], ['.', '.', '.'], ['.', '.', '.']]
        assert _ai_move(board, 'X', 'hard') == (0, 0)


class TestArcadeDifficulty:
    def test_default_normal(self, monkeypatch):
        import arcade
        monkeypatch.setattr(arcade_utils, 'get_key', lambda: '\r')
        monkeypatch.setattr(arcade_utils, 'draw_retro_box', lambda *a, **k: None)
        monkeypatch.setattr(arcade, 'beep', lambda *a, **k: None)
        assert arcade.select_game_difficulty() == 'normal'

    def test_down_then_enter(self, monkeypatch):
        import arcade
        keys = iter(['down', '\r'])
        monkeypatch.setattr(arcade_utils, 'get_key', lambda: next(keys))
        monkeypatch.setattr(arcade_utils, 'draw_retro_box', lambda *a, **k: None)
        monkeypatch.setattr(arcade, 'beep', lambda *a, **k: None)
        assert arcade.select_game_difficulty() == 'hard'

    def test_up_then_enter(self, monkeypatch):
        import arcade
        keys = iter(['up', '\r'])
        monkeypatch.setattr(arcade_utils, 'get_key', lambda: next(keys))
        monkeypatch.setattr(arcade_utils, 'draw_retro_box', lambda *a, **k: None)
        monkeypatch.setattr(arcade, 'beep', lambda *a, **k: None)
        assert arcade.select_game_difficulty() == 'easy'

    def test_quit_returns_none(self, monkeypatch):
        import arcade
        monkeypatch.setattr(arcade_utils, 'get_key', lambda: 'q')
        monkeypatch.setattr(arcade_utils, 'draw_retro_box', lambda *a, **k: None)
        monkeypatch.setattr(arcade, 'beep', lambda *a, **k: None)
        assert arcade.select_game_difficulty() is None


class TestArcadeMenuViewport:
    def _capture_menu(self, monkeypatch, selection):
        import arcade
        boxes = []

        def fake_box(width, title, content, **kw):
            boxes.append(content)

        class FakeStdout:
            encoding = 'utf-8'

            def write(self, s):
                pass

            def flush(self):
                pass

        monkeypatch.setattr(sys, 'stdout', FakeStdout())
        monkeypatch.setattr(arcade, 'get_terminal_size', lambda: (120, 30))
        monkeypatch.setattr(arcade, 'draw_profile', lambda: None)
        monkeypatch.setattr(arcade, '_is_game_locked', lambda key: False)
        monkeypatch.setattr(arcade, 'draw_retro_box', fake_box)
        monkeypatch.setattr(arcade_utils, 'clear_screen', lambda: None)
        from arcade import Renderer
        arcade.print_menu(selection, Renderer())
        return boxes[0]

    def test_top_viewport(self, monkeypatch):
        import arcade
        from arcade_utils import strip_ansi
        content = self._capture_menu(monkeypatch, 0)
        opts = arcade._build_menu_options(False)
        assert strip_ansi(opts[0]) in strip_ansi(content[0])
        assert not any('more above' in line for line in content)
        assert '27 more below' in ''.join(content)

    def test_bottom_viewport(self, monkeypatch):
        import arcade
        from arcade_utils import strip_ansi
        content = self._capture_menu(monkeypatch, 40)
        opts = arcade._build_menu_options(False)
        assert '27 more above' in ''.join(content)
        assert strip_ansi(opts[40]) in strip_ansi(content[-1])

    def test_middle_viewport(self, monkeypatch):
        import arcade
        from arcade_utils import strip_ansi
        content = self._capture_menu(monkeypatch, 20)
        opts = arcade._build_menu_options(False)
        text = ''.join(content)
        assert '13 more above' in text
        assert '14 more below' in text
        assert strip_ansi(opts[20]) in strip_ansi(content[8])

    def test_selection_marker(self, monkeypatch):
        content = self._capture_menu(monkeypatch, 0)
        assert '►' in content[0]


class TestCelebrationOutput:
    def test_high_score_output(self, monkeypatch, capsys):
        import random

        import celebrations
        monkeypatch.setattr(celebrations, 'clear_screen', lambda: None)
        monkeypatch.setattr(celebrations.time, 'sleep', lambda *a: None)
        random.seed(1)
        celebrations.celebrate_high_score('Snake', 1500, 1000)
        from arcade_utils import strip_ansi
        out = strip_ansi(capsys.readouterr().out)
        assert 'Snake' in out
        assert '1500' in out
        assert '+500' in out
        assert '+50%' in out

    def test_level_up_output(self, monkeypatch, capsys):
        import celebrations
        monkeypatch.setattr(celebrations, 'clear_screen', lambda: None)
        monkeypatch.setattr(celebrations.time, 'sleep', lambda *a: None)
        celebrations.celebrate_level_up(3)
        from arcade_utils import strip_ansi
        out = strip_ansi(capsys.readouterr().out)
        assert 'LEVEL 3' in out


class TestArcadePlayAndSubmit:
    def test_submit_flow(self, monkeypatch):
        import arcade

        class Mgr:
            def __init__(self):
                self.unlocked = []

            def get_level_and_xp(self):
                return (7, 500)

            def unlock_achievement(self, aid):
                self.unlocked.append(aid)

            def get_settings(self):
                return {'player_name': 'TESTER'}

        mgr = Mgr()
        celebrated = []
        summaries = []
        submitted = []
        monkeypatch.setattr(arcade, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(arcade, '_check_saved_state', lambda *a: None)
        monkeypatch.setattr(arcade, 'safe_game_call',
                            lambda func, name, **kw: {'high_score': 42, 'score': 42})
        monkeypatch.setattr(arcade, '_show_game_summary', lambda *a: summaries.append(a))
        monkeypatch.setattr(arcade, 'check_and_celebrate', lambda *a: celebrated.append(a))
        monkeypatch.setattr(arcade, 'celebrate_level_up', lambda *a: None)
        monkeypatch.setattr(arcade.olb, 'submit_score', lambda *a: submitted.append(a))
        arcade._play_and_submit(lambda: None, 'Snake', 'normal')
        assert 'first_game' in mgr.unlocked
        assert 'level_5' in mgr.unlocked
        assert celebrated == [('Snake', 42, 'snake')]
        assert submitted == [('TESTER', 'snake', 42, 'normal')]
        assert len(summaries) == 1

    def test_no_submit_without_score(self, monkeypatch):
        import arcade

        class Mgr:
            def __init__(self):
                self.unlocked = []

            def get_level_and_xp(self):
                return (2, 100)

            def unlock_achievement(self, aid):
                self.unlocked.append(aid)

            def get_settings(self):
                return {'player_name': 'TESTER'}

        mgr = Mgr()
        submitted = []
        celebrated = []
        monkeypatch.setattr(arcade, 'get_stats_manager', lambda: mgr)
        monkeypatch.setattr(arcade, '_check_saved_state', lambda *a: None)
        monkeypatch.setattr(arcade, 'safe_game_call', lambda func, name, **kw: {})
        monkeypatch.setattr(arcade, 'check_and_celebrate', lambda *a: celebrated.append(a))
        monkeypatch.setattr(arcade.olb, 'submit_score', lambda *a: submitted.append(a))
        arcade._play_and_submit(lambda: None, 'Snake', 'hard')
        assert 'first_game' in mgr.unlocked
        assert celebrated == []
        assert submitted == []
        assert 'level_5' not in mgr.unlocked


class _FakeStatsMgr:
    def __init__(self):
        self.unlocked = []
        self.sessions = []
        self.xp_added = 0
        self.updated = None

    def unlock_achievement(self, aid):
        self.unlocked.append(aid)

    def add_xp(self, xp):
        self.xp_added += xp

    def record_session(self, *args):
        self.sessions.append(args)

    def get_high_score(self, game):
        return 0

    def update_game_stats(self, *args):
        self.updated = args


class TestPong:
    def _make(self, monkeypatch, difficulty='normal', **kw):
        import pong
        monkeypatch.setattr(pong, 'get_terminal_size', lambda: (120, 28))
        monkeypatch.setattr(pong.random, 'choice', lambda seq: seq[0])
        monkeypatch.setattr(pong, 'beep', lambda *a: None)
        return pong.PongGame(difficulty, **kw)

    def test_default_properties(self, monkeypatch):
        game = self._make(monkeypatch)
        assert game.paddle_size == 3
        assert game.ai_paddle_size == 3
        assert game.ball_speed == 1.0
        assert game.ai_reaction_delay == 0.15
        assert (game.player_score, game.ai_score) == (0, 0)
        assert game.hits == 0
        assert game.game_over is False
        assert (game.width, game.height) == (80, 20)
        assert (game.ball_x, game.ball_y) == (40.0, 10.0)
        assert game.ball_dx == -1
        assert game.ball_dy == -0.8

    def test_easy_config(self, monkeypatch):
        game = self._make(monkeypatch, 'easy')
        assert (game.paddle_size, game.ai_paddle_size, game.ball_speed, game.ai_reaction_delay) \
            == (4, 3, 0.9, 0.3)

    def test_hard_config(self, monkeypatch):
        game = self._make(monkeypatch, 'hard')
        assert (game.paddle_size, game.ai_paddle_size, game.ball_speed, game.ai_reaction_delay) \
            == (2, 4, 1.3, 0.05)

    def test_unknown_difficulty_defaults_to_normal(self, monkeypatch):
        game = self._make(monkeypatch, 'insane')
        assert game.paddle_size == 3

    def test_move_paddle_up(self, monkeypatch):
        game = self._make(monkeypatch)
        game.paddle_pos = 3
        game.move_paddle('up')
        assert game.paddle_pos == 2
        game.paddle_pos = 0
        game.move_paddle('up')
        assert game.paddle_pos == 0

    def test_move_paddle_down(self, monkeypatch):
        game = self._make(monkeypatch)
        assert game.paddle_pos == 9
        game.move_paddle('down')
        assert game.paddle_pos == 10
        game.paddle_pos = 17
        game.move_paddle('down')
        assert game.paddle_pos == 17

    def test_state_roundtrip(self, monkeypatch):
        game = self._make(monkeypatch)
        game.ball_x, game.ball_y = 12.5, 7.25
        game.ball_dx, game.ball_dy = 1.0, -0.5
        game.ball_speed = 1.7
        game.paddle_pos, game.ai_paddle_pos = 4, 11
        game.player_score, game.ai_score = 20, 30
        game.hits = 5
        other = self._make(monkeypatch)
        other.load_state_json(game.save_state_json())
        assert other.ball_x == 12.5
        assert other.ball_dy == -0.5
        assert (other.player_score, other.ai_score) == (20, 30)
        assert other.hits == 5
        assert (other.paddle_pos, other.ai_paddle_pos) == (4, 11)
        assert other.ball_speed == 1.7

    def test_load_state_defaults(self, monkeypatch):
        game = self._make(monkeypatch)
        game.load_state_json({})
        assert game.ball_dx == 1.0
        assert game.ball_dy == 0.5
        assert game.player_score == 0

    def test_update_ai_tracks_incoming_ball(self, monkeypatch):
        game = self._make(monkeypatch, 'hard')
        game.ball_dx = 1.0
        game.ball_y = 12.0
        game.ai_paddle_pos = 5
        game._update_ai()
        assert game.ai_paddle_pos == 6

    def test_update_ai_recenters_when_ball_away(self, monkeypatch):
        game = self._make(monkeypatch, 'hard')
        game.ball_dx = -1.0
        game.ball_y = 3.0
        game.ai_paddle_pos = 0
        game._update_ai()
        assert game.ai_paddle_pos == 1

    def test_update_ai_respects_reaction_delay(self, monkeypatch):
        game = self._make(monkeypatch, 'hard')
        game.ai_miss_timer = 2
        pos = game.ai_paddle_pos
        game._update_ai()
        assert game.ai_paddle_pos == pos
        assert game.ai_miss_timer == 1

    def test_update_ai_clamped_to_board(self, monkeypatch):
        game = self._make(monkeypatch, 'hard')
        game.ball_dx = 1.0
        game.ball_y = 0.0
        game.ai_paddle_pos = 0
        game._update_ai()
        assert game.ai_paddle_pos == 0
        game.ball_y = 19.0
        game.ai_paddle_pos = 0
        game._update_ai()
        assert game.ai_paddle_pos == 1
        game.ai_paddle_pos = 17
        game._update_ai()
        assert game.ai_paddle_pos == 16

    def test_update_ai_easy_randomness(self, monkeypatch):
        import pong
        monkeypatch.setattr(pong.random, 'uniform', lambda a, b: 0.25)
        game = self._make(monkeypatch, 'easy')
        game.ball_dx = 1.0
        game.ball_y = 10.0
        game.ai_paddle_pos = 8
        game._update_ai()
        assert game.ai_paddle_pos == 9

    def test_update_ball_wall_bounce(self, monkeypatch):
        game = self._make(monkeypatch)
        game.ball_x = 40.0
        game.ball_y = 0.05
        game.ball_dy = -0.5
        game.ball_dx = 1.0
        game.update_ball()
        assert game.ball_dy > 0
        assert game.ball_y == 0.1

    def test_update_ball_player_paddle_hit(self, monkeypatch):
        import pong
        xp = []
        unlocks = []
        monkeypatch.setattr(pong.PongGame, 'award_xp_for_action',
                            lambda self, v: xp.append(v))
        monkeypatch.setattr(pong.PongGame, 'unlock_achievement',
                            lambda self, *a: unlocks.append(a))
        game = self._make(monkeypatch)
        game.ball_x = 1.5
        game.ball_dx = -1.0
        game.ball_y = 6.0
        game.paddle_pos = 5
        game.update_ball()
        assert game.ball_dx > 0
        assert game.ball_x == 1.5
        assert game.score == 10
        assert game.hits == 1
        assert game.ball_speed == 1.05
        assert xp == [10]
        assert unlocks == []

    def test_update_ball_player_paddle_miss(self, monkeypatch):
        game = self._make(monkeypatch)
        game.ball_x = 1.5
        game.ball_dx = -1.0
        game.ball_y = 0.0
        game.paddle_pos = 5
        game.update_ball()
        assert game.ai_score == 1
        assert game.score == 0

    def test_update_ball_ai_paddle_hit(self, monkeypatch):
        game = self._make(monkeypatch)
        game.ball_x = 77.5
        game.ball_dx = 1.0
        game.ball_y = 6.0
        game.ai_paddle_pos = 5
        game.update_ball()
        assert game.ball_dx < 0
        assert game.ball_x == 77.5
        assert game.player_score == 0

    def test_update_ball_ai_paddle_miss(self, monkeypatch):
        game = self._make(monkeypatch)
        game.ball_x = 77.5
        game.ball_dx = 1.0
        game.ball_y = 0.0
        game.ai_paddle_pos = 5
        game.update_ball()
        assert game.player_score == 10
        assert game.score == 10

    def test_win_condition_player(self, monkeypatch):
        game = self._make(monkeypatch)
        game.player_score = 95
        game.ball_x = 77.5
        game.ball_dx = 1.0
        game.ball_y = 0.0
        game.ai_paddle_pos = 5
        game.update_ball()
        assert game.player_score == 105
        assert game.game_over is True

    def test_win_condition_ai(self, monkeypatch):
        game = self._make(monkeypatch)
        game.ai_score = 99
        game.ball_x = 1.5
        game.ball_dx = -1.0
        game.ball_y = 0.0
        game.paddle_pos = 5
        game.update_ball()
        assert game.ai_score == 100
        assert game.game_over is True

    def test_achievement_pong_pro(self, monkeypatch):
        import pong
        unlocks = []
        monkeypatch.setattr(pong.PongGame, 'unlock_achievement',
                            lambda self, *a: unlocks.append(a))
        game = self._make(monkeypatch)
        game.hits = 9
        game.ball_x = 1.5
        game.ball_dx = -1.0
        game.ball_y = 6.0
        game.paddle_pos = 5
        game.update_ball()
        assert unlocks == [('pong_pro', 'Pong Pro')]

    def test_achievement_pong_master(self, monkeypatch):
        import pong
        unlocks = []
        monkeypatch.setattr(pong.PongGame, 'unlock_achievement',
                            lambda self, *a: unlocks.append(a))
        game = self._make(monkeypatch)
        game.hits = 24
        game.ball_x = 1.5
        game.ball_dx = -1.0
        game.ball_y = 6.0
        game.paddle_pos = 5
        game.update_ball()
        assert unlocks == [('pong_master', 'Pong Master')]

    def test_select_mode_play(self, monkeypatch):
        import pong

        class IH:
            def get_safe_key(self):
                return 'p'

        monkeypatch.setattr(pong, 'get_safe_input_handler', lambda: IH())
        monkeypatch.setattr(pong, 'clear_screen', lambda: None)
        monkeypatch.setattr(pong, 'draw_retro_box', lambda *a, **k: None)
        game = self._make(monkeypatch)
        assert game._select_mode() is True
        assert game.online_mode is False

    def test_select_mode_quit(self, monkeypatch):
        import pong

        class IH:
            def get_safe_key(self):
                return 'q'

        monkeypatch.setattr(pong, 'get_safe_input_handler', lambda: IH())
        monkeypatch.setattr(pong, 'clear_screen', lambda: None)
        monkeypatch.setattr(pong, 'draw_retro_box', lambda *a, **k: None)
        game = self._make(monkeypatch)
        assert game._select_mode() is False

    def test_select_mode_online(self, monkeypatch):
        import pong

        class IH:
            def get_safe_key(self):
                return 'o'

        monkeypatch.setattr(pong, 'get_safe_input_handler', lambda: IH())
        monkeypatch.setattr(pong, 'clear_screen', lambda: None)
        monkeypatch.setattr(pong, 'draw_retro_box', lambda *a, **k: None)
        monkeypatch.setattr(pong.PongGame, '_setup_online', lambda self: True)
        game = self._make(monkeypatch)
        assert game._select_mode() is True
        assert game.online_mode is True

    def test_setup_online_quit(self, monkeypatch):
        import pong

        class IH:
            def get_safe_key(self):
                return 'q'

        monkeypatch.setattr(pong, 'get_safe_input_handler', lambda: IH())
        monkeypatch.setattr(pong, 'clear_screen', lambda: None)
        monkeypatch.setattr(pong, 'draw_retro_box', lambda *a, **k: None)
        game = self._make(monkeypatch)
        assert game._setup_online() is False

    def test_play_quits_at_mode_select(self, monkeypatch):
        import pong
        monkeypatch.setattr(pong.PongGame, '_select_mode', lambda self: False)
        game = self._make(monkeypatch)
        result = game.play()
        assert result['score'] == 0
        assert 'duration_seconds' in result
        assert 'xp_earned' in result

    def test_play_full_loop_quit_key(self, monkeypatch):
        import pong

        class IH:
            def get_direction(self):
                return None

            def get_safe_key(self):
                return 'q'

        saved = []
        monkeypatch.setattr(pong, 'get_safe_input_handler', lambda: IH())
        monkeypatch.setattr(pong.PongGame, '_select_mode', lambda self: True)
        monkeypatch.setattr(pong.PongGame, '_save_and_quit', lambda self, k: True)
        monkeypatch.setattr(pong.PongGame, 'render', lambda self: None)
        monkeypatch.setattr(pong.time, 'sleep', lambda *a: None)
        monkeypatch.setattr(pong.PongGame, 'save_stats', lambda self, s: saved.append(s))
        game = self._make(monkeypatch)
        result = game.play()
        assert result['score'] == 0
        assert result['high_score'] == 0
        assert 'duration_seconds' in result
        assert len(saved) == 1

    def test_play_pong_wrapper(self, monkeypatch):
        import pong
        monkeypatch.setattr(pong, 'get_terminal_size', lambda: (120, 28))
        monkeypatch.setattr(pong.PongGame, 'play', lambda self: {'score': 77, 'xp_earned': 5})
        assert pong.play_pong('easy') == {'score': 77, 'xp_earned': 5}

    def test_play_pong_online_wrapper(self, monkeypatch):
        import pong
        monkeypatch.setattr(pong, 'get_terminal_size', lambda: (120, 28))
        monkeypatch.setattr(pong.PongGame, 'play', lambda self: {'online': True})
        assert pong.play_pong_online('Bob', 'ROOM1', 'right', 'hard') == {'online': True}


class TestRoulette:
    def test_pick_prefers_least_played(self, monkeypatch):
        import roulette

        class Mgr:
            def get_game_play_count(self, g):
                return {'snake': 0, 'tetris': 0, 'slots': 9}.get(g, 0)

        monkeypatch.setattr(roulette, 'get_stats_manager', lambda: Mgr())
        monkeypatch.setattr(roulette.random, 'uniform', lambda a, b: 0.0)
        assert roulette.pick_roulette_game(['snake', 'tetris', 'slots']) == 'snake'
        monkeypatch.setattr(roulette.random, 'uniform', lambda a, b: 1.0)
        assert roulette.pick_roulette_game(['snake', 'tetris', 'slots']) == 'snake'
        monkeypatch.setattr(roulette.random, 'uniform', lambda a, b: 1.5)
        assert roulette.pick_roulette_game(['snake', 'tetris', 'slots']) == 'tetris'
        monkeypatch.setattr(roulette.random, 'uniform', lambda a, b: 2.09)
        assert roulette.pick_roulette_game(['snake', 'tetris', 'slots']) == 'slots'

    def test_spin_returns_game_on_enter(self, monkeypatch):
        import roulette
        monkeypatch.setattr(roulette, 'clear_screen', lambda: None)
        monkeypatch.setattr(roulette.time, 'sleep', lambda *a: None)
        monkeypatch.setattr(roulette.random, 'choice', lambda seq: seq[0])
        for key in ['enter', '\r', '\n', ' ']:
            monkeypatch.setattr(roulette, 'get_key', lambda: key)
            assert roulette.show_roulette_spin('snake') == 'snake'
        assert roulette.show_roulette_spin('space_shooter') == 'space_shooter'

    def test_spin_cancel(self, monkeypatch):
        import roulette
        monkeypatch.setattr(roulette, 'clear_screen', lambda: None)
        monkeypatch.setattr(roulette.time, 'sleep', lambda *a: None)
        monkeypatch.setattr(roulette.random, 'choice', lambda seq: seq[0])
        monkeypatch.setattr(roulette, 'get_key', lambda: 'Q')
        assert roulette.show_roulette_spin('snake') is None

    def test_spin_waits_for_valid_key(self, monkeypatch):
        import roulette
        keys = iter([None, 'x', '\r'])
        monkeypatch.setattr(roulette, 'clear_screen', lambda: None)
        monkeypatch.setattr(roulette.time, 'sleep', lambda *a: None)
        monkeypatch.setattr(roulette.random, 'choice', lambda seq: seq[0])
        monkeypatch.setattr(roulette, 'get_key', lambda: next(keys))
        assert roulette.show_roulette_spin('slots') == 'slots'


class TestRhythm:
    def test_config_lookup(self):
        from rhythm import RhythmGame
        assert RhythmGame('easy').config['lane_count'] == 3
        assert RhythmGame('hard').config == RhythmGame.DIFFICULTIES['hard']
        assert RhythmGame('weird').config is RhythmGame.DIFFICULTIES['normal']

    def test_song_selection_wraps(self):
        from rhythm import RhythmGame
        assert RhythmGame('normal', 1).song['name'] == 'Synthwave'
        assert RhythmGame('normal', 5).song['name'] == 'Speed Core'

    def test_generate_notes_base_pattern(self, monkeypatch):
        import rhythm
        monkeypatch.setattr(rhythm.random, 'randint', lambda a, b: 0)
        monkeypatch.setattr(rhythm.random, 'uniform', lambda a, b: 0.0)
        game = rhythm.RhythmGame('normal', 0)
        game._generate_notes()
        assert game.total_notes == 40
        assert all(n['lane'] == 0 for n in game.notes)
        assert [n['beat'] for n in game.notes] == [i * 0.6 for i in range(40)]

    def test_generate_notes_synth_pattern(self, monkeypatch):
        import rhythm
        monkeypatch.setattr(rhythm.random, 'randint', lambda a, b: 1)
        monkeypatch.setattr(rhythm.random, 'uniform', lambda a, b: 0.0)
        game = rhythm.RhythmGame('easy', 1)
        game._generate_notes()
        assert game.total_notes == 30
        assert all(n['lane'] == 1 for n in game.notes)
        assert [n['beat'] for n in game.notes] == [i * 0.8 for i in range(30)]

    def test_generate_notes_speed_pattern(self, monkeypatch):
        import rhythm
        game = rhythm.RhythmGame('hard', 2)
        game._generate_notes()
        assert game.total_notes == 60
        assert [n['lane'] for n in game.notes] == [i % 4 for i in range(60)]
        assert game.notes[0]['beat'] == 0.0
        assert all(game.notes[i + 1]['beat'] > game.notes[i]['beat'] for i in range(59))
        assert game.notes[59]['beat'] < 60 * game.config['interval']

    def _script_play(self, monkeypatch, times, keys, mgr):
        import rhythm
        state = {'i': 0}

        def fake_time():
            i = state['i']
            state['i'] += 1
            return times[min(i, len(times) - 1)]

        it = iter(keys)
        monkeypatch.setattr(rhythm.time, 'time', fake_time)
        monkeypatch.setattr(rhythm.time, 'sleep', lambda *a: None)
        monkeypatch.setattr(rhythm, 'get_key', lambda: next(it))
        monkeypatch.setattr(rhythm, 'clear_screen', lambda: None)
        monkeypatch.setattr(rhythm, 'chaos_start_game', lambda: None)
        monkeypatch.setattr(rhythm.random, 'randint', lambda a, b: 0)
        monkeypatch.setattr(rhythm.random, 'uniform', lambda a, b: 0.0)
        monkeypatch.setattr('stats_manager.get_stats_manager', lambda: mgr)
        return rhythm.RhythmGame('normal', 0)

    def test_play_hit_scoring_and_quit(self, monkeypatch):
        mgr = _FakeStatsMgr()
        times = [0.0, 0.0, 0.4, 0.6, 0.6, 1.2, 0.6, 1.8, 0.6, 2.4, 0.6]
        game = self._script_play(monkeypatch, times, [None, 'd', None, None, 'q', 'x'], mgr)
        result = game.play()
        assert result['score'] == 150
        assert result['duration_seconds'] == 2
        assert game.notes_hit == 1
        assert game.notes_missed == 0
        assert game.max_combo == 1
        from xp_config import get_xp_system
        expected = get_xp_system('normal').calculate_xp('rhythm', 15)
        assert result['xp_earned'] == expected
        assert mgr.xp_added == expected
        assert mgr.unlocked == ['rhythm_first']
        assert mgr.sessions == [('rhythm', 150, expected, 2, 'normal')]
        assert mgr.updated[0] == 'rhythm'
        assert mgr.updated[1]['high_score'] == 150

    def test_play_quit_immediately(self, monkeypatch):
        mgr = _FakeStatsMgr()
        times = [0.0, 0.0, 0.2, 0.2]
        game = self._script_play(monkeypatch, times, ['q', 'x'], mgr)
        result = game.play()
        assert result['score'] == 0
        assert result['duration_seconds'] == 0
        assert game.notes_hit == 0
        assert game.notes_missed == 0
        assert mgr.unlocked == ['rhythm_first']


class TestSecretMenu:
    def test_feed_key_full_sequence(self, monkeypatch):
        import secret_menu
        secret_menu.reset()
        for k in secret_menu.KONAMI_CODE[:-1]:
            assert secret_menu.feed_key(k) is False
        assert secret_menu.is_unlocked() is False
        assert secret_menu.feed_key(secret_menu.KONAMI_CODE[-1]) is True
        assert secret_menu.is_unlocked() is True
        assert secret_menu.feed_key('up') is False
        secret_menu.reset()
        assert secret_menu.is_unlocked() is False

    def test_wrong_key_resets_progress(self, monkeypatch):
        import secret_menu
        secret_menu.reset()
        for k in ['up', 'up', 'x']:
            assert secret_menu.feed_key(k) is False
        assert secret_menu.is_unlocked() is False
        assert secret_menu.feed_key('up') is False

    def test_feed_key_normalizes_and_ignores_empty(self, monkeypatch):
        import secret_menu
        secret_menu.reset()
        assert secret_menu.feed_key('') is False
        assert secret_menu.feed_key(None) is False
        assert secret_menu.feed_key('UP') is False
        assert secret_menu.feed_key('UP') is False
        secret_menu.reset()

    def _run_menu(self, monkeypatch, keys, on_marathon=None, on_boss=None, on_rhythm=None):
        import chaos_mutator
        import secret_menu
        mgr = _FakeStatsMgr()
        calls = {'marathon': [], 'boss': [], 'rhythm': [], 'popups': [], 'chaos': []}
        it = iter(keys)
        monkeypatch.setattr(secret_menu, 'get_key', lambda: next(it))
        monkeypatch.setattr(secret_menu, 'clear_screen', lambda: None)
        monkeypatch.setattr(secret_menu, 'play_sound', lambda *a: None)
        monkeypatch.setattr(secret_menu.random, 'choice', lambda seq: 'X')
        monkeypatch.setattr(secret_menu, 'show_popup',
                            lambda *a, **k: calls['popups'].append(a[0]))
        monkeypatch.setattr(chaos_mutator, 'is_chaos', lambda: False)
        monkeypatch.setattr(chaos_mutator, 'set_chaos',
                            lambda v: calls['chaos'].append(v))
        monkeypatch.setattr('stats_manager.get_stats_manager', lambda: mgr)
        result = secret_menu.show_secret_menu(
            on_marathon=on_marathon and (lambda: calls['marathon'].append(1)),
            on_boss=on_boss and (lambda: calls['boss'].append(1)),
            on_rhythm=on_rhythm and (lambda: calls['rhythm'].append(1)),
        )
        return result, calls, mgr

    def test_marathon_selection(self, monkeypatch):
        result, calls, _ = self._run_menu(monkeypatch, ['\r', 'q'], on_marathon=True)
        assert calls['marathon'] == [1]
        assert calls['boss'] == []
        assert result is False

    def test_chaos_toggle(self, monkeypatch):
        result, calls, mgr = self._run_menu(monkeypatch, ['down', '\r', 'q'])
        assert calls['chaos'] == [True]
        assert calls['popups'] == ['Chaos Mode: ACTIVATED']
        assert mgr.unlocked == ['chaos_first']
        assert result is False

    def test_boss_selection(self, monkeypatch):
        result, calls, _ = self._run_menu(monkeypatch, ['down', 'down', '\r', 'q'], on_boss=True)
        assert calls['boss'] == [1]
        assert calls['marathon'] == []
        assert result is False

    def test_rhythm_selection(self, monkeypatch):
        result, calls, _ = self._run_menu(
            monkeypatch, ['down', 'down', 'down', '\r', 'q'], on_rhythm=True)
        assert calls['rhythm'] == [1]
        assert result is False

    def test_back_selection(self, monkeypatch):
        result, calls, _ = self._run_menu(monkeypatch, ['down'] * 5 + ['\r'])
        assert calls['marathon'] == []
        assert calls['chaos'] == []
        assert result is False

    def test_quit_key(self, monkeypatch):
        result, calls, _ = self._run_menu(monkeypatch, ['q'])
        assert calls['marathon'] == []
        assert result is False

    def test_easter_egg_os(self, monkeypatch, capsys):
        import secret_menu
        keys = iter(['h', 'e', 'l', 'p', '\r', 'l', 's', '\r', 'c', 'd', ' ', '.', '.', '\r', 'q'])
        monkeypatch.setattr(secret_menu, 'get_key', lambda: next(keys))
        monkeypatch.setattr(secret_menu, 'clear_screen', lambda: None)
        secret_menu._show_easter_egg_os()
        out = capsys.readouterr().out
        assert 'Available commands' in out
        assert 'notes.txt' in out
