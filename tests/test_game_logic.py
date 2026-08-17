"""Unit tests for pure game logic across the arcade (no terminal interaction)."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

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


class TestPoker:
    def test_all_hand_types(self):
        from poker import evaluate_hand
        H = 0  # hearts
        assert evaluate_hand([('A', H), ('K', H), ('Q', H), ('J', H), ('10', H)]) == 'royal_flush'
        assert evaluate_hand([('9', H), ('K', H), ('Q', H), ('J', H), ('10', H)]) == 'straight_flush'
        assert evaluate_hand([('7', 0), ('7', 1), ('7', 2), ('7', 3), ('2', 0)]) == 'four_of_a_kind'
        assert evaluate_hand([('7', 0), ('7', 1), ('7', 2), ('2', 0), ('2', 1)]) == 'full_house'
        assert evaluate_hand([('2', H), ('5', H), ('9', H), ('J', H), ('K', H)]) == 'flush'
        assert evaluate_hand([('A', 0), ('2', 1), ('3', 2), ('4', 3), ('5', 0)]) == 'straight'
        assert evaluate_hand([('7', 0), ('7', 1), ('7', 2), ('2', 0), ('9', 1)]) == 'three_of_a_kind'
        assert evaluate_hand([('7', 0), ('7', 1), ('2', 0), ('2', 1), ('9', 3)]) == 'two_pair'
        assert evaluate_hand([('J', 0), ('J', 1), ('2', 0), ('5', 1), ('9', 0)]) == 'jacks_or_better'
        assert evaluate_hand([('10', 0), ('10', 1), ('2', 0), ('5', 1), ('9', 0)]) == 'nothing'

    def test_ace_low_straight_edges(self):
        from poker import evaluate_hand
        assert evaluate_hand([('A', 0), ('2', 0), ('3', 0), ('4', 0), ('5', 1)]) == 'straight'
        assert evaluate_hand([('A', 0), ('2', 1), ('3', 2), ('4', 3), ('6', 0)]) != 'straight'

    def test_deck_has_52_unique_cards(self):
        from poker import build_deck
        deck = build_deck()
        assert len(deck) == 52
        assert len(set(deck)) == 52

    def test_payouts_ordered_by_strength(self):
        from poker import PAYOUT_ORDER, PAYOUTS
        values = [PAYOUTS[h] for h in PAYOUT_ORDER]
        assert values == sorted(values, reverse=True)
        assert PAYOUTS['royal_flush'] == 250
        assert PAYOUTS['nothing'] == 0

    def test_hand_name_mapping(self):
        from poker import hand_name
        assert hand_name('full_house') == 'Full House'
        assert hand_name('nothing') == 'Nothing'


class TestMastermind:
    def test_evaluate_guess_cases(self):
        from mastermind import MastermindGame
        game = MastermindGame('normal')
        game.secret = [0, 1, 2, 3]
        assert game.evaluate_guess([0, 1, 2, 4]) == (3, 0)
        assert game.evaluate_guess([0, 2, 1, 3]) == (2, 2)
        assert game.evaluate_guess([3, 2, 1, 0]) == (0, 4)
        assert game.evaluate_guess([0, 1, 2, 3]) == (4, 0)
        assert game.evaluate_guess([4, 5, 6, 7]) == (0, 0)

    def test_difficulty_config(self):
        from mastermind import MastermindGame
        assert (MastermindGame('easy').num_colors, MastermindGame('easy').max_tries) == (6, 12)
        assert (MastermindGame('normal').num_colors, MastermindGame('normal').max_tries) == (6, 10)
        assert (MastermindGame('hard').num_colors, MastermindGame('hard').max_tries) == (8, 8)
        for d in ('easy', 'normal', 'hard'):
            assert MastermindGame(d).code_length == 4


class Test2048:
    def test_compress(self):
        from game_2048 import Game2048
        game = Game2048('normal')
        assert game.compress([2, 0, 2, 4]) == [2, 2, 4, 0]
        assert game.compress([0, 0, 0, 0]) == [0, 0, 0, 0]
        assert game.compress([8, 4, 2, 1]) == [8, 4, 2, 1]

    def test_merge_once_per_turn(self):
        from game_2048 import Game2048
        game = Game2048('normal')
        row, gain = game.merge([2, 2, 2, 2])
        assert row == [4, 0, 4, 0]
        assert gain == 8

    def test_move_left(self):
        from game_2048 import Game2048
        game = Game2048('normal')
        game.grid = [[2, 2, 2, 2], [0, 2, 0, 2], [4, 0, 0, 0], [0, 0, 0, 0]]
        moved, gain = game.move_left()
        assert moved is True
        assert gain == 8 + 4
        assert game.grid[0] == [4, 4, 0, 0]

    def test_no_move_when_stuck(self):
        from game_2048 import Game2048
        game = Game2048('normal')
        game.grid = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]]
        moved, gain = game.move_left()
        assert moved is False
        assert gain == 0

    def test_rotate_grid(self):
        from game_2048 import Game2048
        game = Game2048('normal')
        game.grid = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
        game.rotate_grid()
        assert game.grid == [
            [13, 9, 5, 1],
            [14, 10, 6, 2],
            [15, 11, 7, 3],
            [16, 12, 8, 4],
        ]

    def test_is_game_over(self):
        from game_2048 import Game2048
        game = Game2048('normal')
        game.grid = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]]
        assert game.is_game_over() is True
        game.grid[0][0] = 0
        assert game.is_game_over() is False

    def test_state_roundtrip(self):
        from game_2048 import Game2048
        game = Game2048('normal')
        game.grid = [[2, 4, 2, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        game.score = 77
        game.high_tile = 64
        game.moves = 5
        loaded = Game2048('normal')
        loaded.load_state_json(game.save_state_json())
        assert loaded.grid == game.grid
        assert loaded.score == 77
        assert loaded.high_tile == 64
        assert loaded.moves == 5


class TestRPSLS:
    def test_resolve(self):
        from rpsls import RPSLSGame
        game = RPSLSGame()
        assert game.resolve("Rock", "Scissors") == 'win'
        assert game.resolve("Scissors", "Spock") == 'lose'
        assert game.resolve("Paper", "Paper") == 'draw'

    def test_winner_map_complete(self):
        from rpsls import WINNERS
        assert set(WINNERS.keys()) == {"Rock", "Paper", "Scissors", "Lizard", "Spock"}
        for move, beats in WINNERS.items():
            assert len(beats) == 2

    def test_verbs(self):
        from rpsls import RPSLSGame
        game = RPSLSGame()
        assert game.get_verb("Scissors", "Paper") == 'cuts'
        assert game.get_verb("Spock", "Rock") == 'vaporizes'
        assert game.get_verb("Rock", "Rock") == 'beats'


class TestHanoi:
    def test_valid_move_rules(self):
        from hanoi import HanoiGame
        game = HanoiGame('normal')
        assert game.pegs[0] == [4, 3, 2, 1]
        assert game.is_valid_move(0, 1) is True
        game.move_disk(0, 1)
        assert game.pegs[1] == [1]
        assert game.is_valid_move(0, 1) is False  # 2 on 1

    def test_invalid_move_rejected(self):
        from hanoi import HanoiGame
        game = HanoiGame('normal')
        game.pegs = [[2], [1], []]
        assert game.move_disk(0, 1) is False
        assert game.moves == 0

    def test_win_condition(self):
        from hanoi import HanoiGame
        game = HanoiGame('easy')
        assert game.check_win() is False
        game.pegs = [[], [], [3, 2, 1]]
        assert game.check_win() is True

    def test_difficulty_configs(self):
        from hanoi import HanoiGame
        for diff, disks in (('easy', 3), ('normal', 4), ('hard', 5)):
            game = HanoiGame(diff)
            assert game.num_disks == disks
            assert game.min_moves == 2 ** disks - 1
            assert game.pegs[0] == list(range(disks, 0, -1))


class TestSimon:
    def test_add_step_grows_sequence(self):
        from simon import SimonGame
        game = SimonGame('normal')
        game.sequence = [0, 1]
        game.player_index = 3
        game._add_step()
        assert len(game.sequence) == 3
        assert game.player_index == 0

    def test_state_roundtrip(self):
        from simon import SimonGame
        game = SimonGame('normal')
        game.sequence = [0, 2, 1, 3]
        game.player_index = 2
        game.score = 30
        game.round = 3
        game.streak = 2
        game.high_round = 5
        loaded = SimonGame('normal')
        loaded.load_state_json(game.save_state_json())
        assert loaded.sequence == [0, 2, 1, 3]
        assert loaded.round == 3
        assert loaded.high_round == 5


class TestSlots:
    def test_bet_property(self):
        from slots import SlotsGame
        game = SlotsGame()
        assert game.bet == 1
        game.bet_index = 2
        assert game.bet == 10

    def test_spin_jackpot(self, monkeypatch):
        from slots import SlotsGame
        game = SlotsGame()
        game.coins = 100
        monkeypatch.setattr('slots.random.choice', lambda seq: "SEV")
        payout, label = game.spin()
        assert payout == 100
        assert label == "JACKPOT"

    def test_spin_loss(self, monkeypatch):
        from slots import SlotsGame
        game = SlotsGame()
        game.coins = 100
        choices = iter(["CHR", "LEM", "BEL"])
        monkeypatch.setattr('slots.random.choice', lambda seq: next(choices))
        payout, label = game.spin()
        assert payout == 0
        assert label == "LOSE"

    def test_spin_insufficient_coins(self):
        from slots import SlotsGame
        game = SlotsGame()
        game.coins = 0
        payout, label = game.spin()
        assert (payout, label) == (0, "")


class TestOthello:
    def test_opponent(self):
        from othello import opponent
        assert opponent('B') == 'W'
        assert opponent('W') == 'B'

    def test_init_board(self):
        from othello import OthelloGame
        game = OthelloGame()
        assert game.board[3][3] == 'W'
        assert game.board[3][4] == 'B'
        assert game.board[4][3] == 'B'
        assert game.board[4][4] == 'W'
        assert game._count('B') == 2

    def test_valid_moves_from_init(self):
        from othello import OthelloGame
        game = OthelloGame()
        moves = sorted(game._get_valid_moves('B'))
        assert moves == [(2, 3), (3, 2), (4, 5), (5, 4)]
        assert game._is_valid(3, 2, 'B') is True
        assert game._is_valid(3, 3, 'B') is False

    def test_flip_sandwich(self):
        from othello import OthelloGame
        game = OthelloGame()
        game._flip(3, 2, 'B')
        assert game.board[3][2] == 'B'
        assert game.board[3][3] == 'B'
        assert game._count('B') == 4

    def test_parse_move(self):
        from othello import OthelloGame
        game = OthelloGame()
        assert game._parse_move('d3') == (2, 3)
        assert game._parse_move('a1') == (0, 0)
        assert game._parse_move('z9') is None
        assert game._parse_move('3d') is None

    def test_score_weights_bias_corners(self):
        from othello import POSITION_WEIGHTS
        assert POSITION_WEIGHTS[0][0] == 100
        assert POSITION_WEIGHTS[4][4] == 0


class TestGomoku:
    def test_win_detection_lines(self):
        from gomoku import GomokuGame
        game = GomokuGame()
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            game._reset_board()
            for i in range(5):
                game.board[7 + dr * i][7 + dc * i] = 'X'
            assert game._check_win_at(7, 7) == 'X'
        assert game._check_win_at(0, 0) is None

    def test_no_win_with_four(self):
        from gomoku import GomokuGame
        game = GomokuGame()
        for c in range(4):
            game.board[7][c] = 'X'
        assert game._check_win_at(7, 0) is None

    def test_parse_move(self):
        from gomoku import GomokuGame
        game = GomokuGame()
        assert game._parse_move('h8') == (7, 7)
        assert game._parse_move('a1') == (0, 0)
        assert game._parse_move('x16') is None

    def test_candidates_around_stone(self):
        from gomoku import GomokuGame
        game = GomokuGame()
        game.board[7][7] = 'X'
        candidates = set(game._get_candidates())
        assert (7, 7) not in candidates
        assert (7, 8) in candidates


class TestNonograms:
    def test_get_clues(self):
        from nonograms import get_clues
        data = [[1, 1, 0, 1, 0]]
        rows, cols = get_clues(data)
        assert rows == [[2, 1]]
        data = [[0, 1, 0], [0, 1, 0], [1, 1, 1]]
        rows, cols = get_clues(data)
        assert cols == [[1], [3], [1]]

    def test_puzzles_solvable_clues(self):
        from nonograms import PUZZLES, get_clues
        for puzzle in PUZZLES:
            size = puzzle['size']
            data = puzzle['data']
            assert len(data) == size
            rows, cols = get_clues(data)
            assert len(rows) == size
            assert len(cols) == size


class TestSokoban:
    def test_parse_map(self):
        from sokoban import LEVELS, parse_map
        grid, player_pos, targets = parse_map(LEVELS[0]['map'])
        assert targets == 2
        assert grid[player_pos[0]][player_pos[1]] != '#'

    def test_push_blocked_by_wall(self):
        from sokoban import SokobanGame
        game = SokobanGame()
        game.grid = [['#', '#', '#'], ['#', ' ', '#'], ['#', '$', '#']]
        game.player_pos = (2, 1)
        assert game._push(1, 0) is False

    def test_check_solved(self):
        from sokoban import SokobanGame
        game = SokobanGame()
        game.grid = [['*']]
        assert game._check_solved() is True
        game.grid = [['$']]
        assert game._check_solved() is False


class TestInvaders:
    def test_wave_layout(self):
        from invaders import InvadersGame
        game = InvadersGame('normal')
        game._init_wave()
        assert len(game.enemies) == 3 * 6
        assert game.enemies[0]['type'] == 'basic'
        assert game.enemies[2 * game.enemy_cols]['type'] == 'elite'

    def test_wave_speeds_up(self):
        from invaders import InvadersGame
        game = InvadersGame('normal')
        game.wave = 1
        game._init_wave()
        delay_1 = game.move_delay
        game.wave = 5
        game._init_wave()
        assert game.move_delay < delay_1

    def test_difficulty_sizes(self):
        from invaders import InvadersGame
        easy = InvadersGame('easy')
        easy._init_wave()
        hard = InvadersGame('hard')
        hard._init_wave()
        assert len(easy.enemies) == 3 * 4
        assert len(hard.enemies) == 3 * 9


class TestMinesweeper:
    def test_board_invariants(self):
        from minesweeper import MinesweeperGame
        game = MinesweeperGame()
        mines = sum(row.count(-1) for row in game.board)
        assert mines == 15
        for r in range(10):
            for c in range(10):
                if game.board[r][c] == -1:
                    continue
                expected = sum(
                    1 for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                    if 0 <= r + dr < 10 and 0 <= c + dc < 10 and game.board[r + dr][c + dc] == -1
                )
                assert game.board[r][c] == expected

    def test_flood_reveal(self):
        from minesweeper import MinesweeperGame
        game = MinesweeperGame()
        game.width = 5
        game.height = 5
        game.board = [
            [0, 0, 0, 1, -1],
            [0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [-1, 1, 0, 0, 0],
        ]
        game.revealed = [[False] * 5 for _ in range(5)]
        game.flags = [[False] * 5 for _ in range(5)]
        game._reveal(0, 0)
        assert game.revealed[0][0] is True
        assert game.revealed[0][3] is True
        assert game.revealed[4][0] is False  # mine never revealed
        assert game.revealed[3][1] is True

    def test_win_requires_all_safe_revealed(self):
        from minesweeper import MinesweeperGame
        game = MinesweeperGame()
        game.width = 2
        game.height = 2
        game.board = [[-1, 0], [0, 0]]
        game.revealed = [[False, True], [True, True]]
        assert game._check_win() is True
        game.revealed = [[False, False], [True, True]]
        assert game._check_win() is False

    def test_state_roundtrip(self):
        from minesweeper import MinesweeperGame
        game = MinesweeperGame()
        state = game.save_state_json()
        loaded = MinesweeperGame()
        loaded.load_state_json(state)
        assert loaded.board == game.board
        assert loaded.first_move == game.first_move


class TestSudoku:
    def test_generated_board_invariants(self):
        import random

        from sudoku import SudokuGame
        for diff, remove in (('easy', 30), ('normal', 45), ('hard', 55)):
            random.seed(42)
            game = SudokuGame(diff)
            blanks = sum(row.count(0) for row in game.board)
            assert blanks == remove
            assert game.original == game.board

    def test_check_win(self):
        from sudoku import SudokuGame
        game = SudokuGame('normal')
        game.board = [[0] * 9 for _ in range(9)]
        assert game._check_win() is False
        valid = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        game.board = [row[:] for row in valid]
        assert game._check_win() is True
        bad = [row[:] for row in valid]
        bad[0][1] = bad[0][0]
        game.board = bad
        assert game._check_win() is False


class TestSoundEngine:
    def test_build_wav_header(self):
        from sound_engine import _build_wav
        wav = _build_wav(b'\x00' * 100)
        assert wav[:4] == b'RIFF'
        assert wav[8:12] == b'WAVE'
        assert wav[36:40] == b'data'
        assert len(wav) == 44 + 100
        assert wav[20:22] == b'\x01\x00'  # PCM
        assert wav[22:24] == b'\x01\x00'  # mono

    def test_sine_wave_length(self):
        from sound_engine import SAMPLE_RATE, _generate_sine_wave
        data = _generate_sine_wave(440, 0.1)
        assert len(data) == int(SAMPLE_RATE * 0.1) * 2
        assert data[0:2] == b'\x00\x00'  # fade-in starts at silence

    def test_wav_cache_consistent(self):
        import sound_engine
        sound_engine._wave_cache.clear()
        first = sound_engine._get_wav('win')
        second = sound_engine._get_wav('win')
        assert first == second
        assert first is not None


class TestChaosMutator:
    def test_inactive_by_default(self):
        import chaos_mutator
        chaos_mutator.set_chaos(False)
        chaos_mutator.clear_effects()
        assert chaos_mutator.is_chaos() is False
        assert chaos_mutator.chaos_mutate_input('left') == 'left'
        assert chaos_mutator.chaos_time_multiplier() == 1.0

    def test_mirror_input(self):
        import chaos_mutator
        chaos_mutator.set_chaos(True)
        chaos_mutator.clear_effects()
        chaos_mutator.apply_chaos(['mirror_input'])
        assert chaos_mutator.chaos_mutate_input('up') == 'down'
        assert chaos_mutator.chaos_mutate_input('left') == 'right'
        assert chaos_mutator.chaos_mutate_input('w') == 's'
        assert chaos_mutator.chaos_mutate_input('x') == 'x'
        chaos_mutator.set_chaos(False)
        chaos_mutator.clear_effects()

    def test_effect_params(self):
        import chaos_mutator
        params = chaos_mutator._effect_params('mirror_input')
        assert params['active'] is True
        assert 'axis' in params

    def test_time_multiplier_with_slow(self):
        import chaos_mutator
        chaos_mutator.set_chaos(True)
        chaos_mutator.clear_effects()
        chaos_mutator.apply_chaos(['speed_slow'])
        for effect in chaos_mutator.get_active_effects().values():
            effect['multiplier'] = 0.25
        assert chaos_mutator.chaos_time_multiplier() < 0.5
        chaos_mutator.set_chaos(False)
        chaos_mutator.clear_effects()


class TestDailyChallenge:
    def test_daily_seed_deterministic(self, monkeypatch):
        import datetime

        import daily_challenge

        class FakeDate(datetime.date):
            @classmethod
            def today(cls):
                return cls(2026, 8, 17)

        monkeypatch.setattr(daily_challenge.datetime, 'date', FakeDate)
        first = daily_challenge.daily_seed()
        assert first == daily_challenge.daily_seed()
        assert len(first) == 8
        import hashlib
        expected = hashlib.md5(b'2026-08-17').hexdigest()[:8]
        assert first == expected

    def test_high_score_only_improves(self):
        import daily_challenge
        daily_challenge.set_daily_high_score('snake', 42)
        assert daily_challenge.get_daily_high_score('snake') == 42
        daily_challenge.set_daily_high_score('snake', 10)
        assert daily_challenge.get_daily_high_score('snake') == 42

    def test_daily_played_flag(self):
        import daily_challenge
        assert daily_challenge.has_daily_played('tetris') is False
        daily_challenge.mark_daily_played('tetris')
        assert daily_challenge.has_daily_played('tetris') is True


class TestTyper:
    def test_word_generation(self):
        import random

        from typer import WORD_POOLS, TyperGame
        random.seed(7)
        game = TyperGame('normal')
        assert len(game.word_list) >= 100
        assert game.current_word == game.word_list[0]
        pool = set(WORD_POOLS['easy'] + WORD_POOLS['normal'] + WORD_POOLS['hard'])
        assert all(w in pool for w in game.word_list)

    def test_submit_word_correct(self):
        from typer import TyperGame
        game = TyperGame('normal')
        game.word_list = ['apple', 'banana']
        game.word_index = 0
        game.current_word = 'apple'
        game.current_input = 'apple'
        game.submit_word()
        assert game.correct_words == 1
        assert game.total_words == 1
        assert game.correct_chars == 5

    def test_submit_word_wrong(self):
        from typer import TyperGame
        game = TyperGame('normal')
        game.word_list = ['apple', 'banana']
        game.word_index = 0
        game.current_word = 'apple'
        game.current_input = 'aple'
        game.submit_word()
        assert game.correct_words == 0
        assert game.total_words == 1


class TestTrivia:
    def test_question_pool_bounded(self):
        import random

        from trivia import QUESTIONS_PER_GAME, TriviaGame
        random.seed(3)
        game = TriviaGame('normal')
        game.category = 'Science'
        game.build_question_pool()
        assert 0 < len(game.questions) <= QUESTIONS_PER_GAME
        assert all(q['difficulty'] in ('easy', 'medium', 'hard') for q in game.questions)
        assert all(len(q['options']) == 4 for q in game.questions)
        assert all(0 <= q['answer'] < 4 for q in game.questions)

    def test_difficulty_points(self):
        from trivia import DIFFICULTY_POINTS
        assert DIFFICULTY_POINTS == {'easy': 10, 'medium': 25, 'hard': 50}


class TestCrossword:
    def test_numbered_cells_built(self):
        from crossword import CrosswordGame
        game = CrosswordGame('easy')
        assert (0, 1) in game.numbered
        assert (4, 1) in game.numbered

    def test_get_word_at(self):
        from crossword import CrosswordGame
        game = CrosswordGame('easy')
        game.player_grid[0][1] = 'C'
        game.player_grid[0][2] = 'A'
        game.player_grid[0][3] = 'T'
        word = game._get_word_at(0, 1)
        assert word is not None
        assert word[0] == 'CAT'

    def test_all_complete(self):
        from crossword import CrosswordGame
        game = CrosswordGame('easy')
        assert game._all_complete() is False
        for r in range(len(game.player_grid)):
            for c in range(len(game.player_grid[r])):
                if game.solution[r][c] is not None:
                    game.player_grid[r][c] = game.solution[r][c]
        assert game._all_complete() is True
