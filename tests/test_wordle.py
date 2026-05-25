"""Tests for the Wordle game module."""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from wordle import WordleGame


class TestWordleInit:
    def test_init(self):
        game = WordleGame()
        assert game.game_name == 'wordle'
        assert game.target is not None
        assert len(game.target) == 5
        assert game.attempts == []
        assert game.max_attempts == 6
        assert game.score == 0

    def test_init_with_difficulty(self):
        game = WordleGame('hard')
        assert game.difficulty == 'hard'


class TestCheckGuess:
    def test_all_correct(self):
        game = WordleGame()
        game.target = "APPLE"
        result = game._check_guess("APPLE")
        assert all(c == 'green' for _, c in result)

    def test_some_yellow(self):
        game = WordleGame()
        game.target = "CRANE"
        result = game._check_guess("RAISE")
        # R at pos 0: R is in target (pos 2) -> yellow
        assert result[0][1] == 'yellow'
        # A at pos 1: A is in target (pos 2) -> yellow
        assert result[1][1] == 'yellow'
        # I, S not in target -> gray
        assert result[2][1] == 'gray'
        assert result[3][1] == 'gray'
        # E at pos 4 matches -> green
        assert result[4][1] == 'green'

    def test_no_match(self):
        game = WordleGame()
        game.target = "JUICE"
        result = game._check_guess("BLANK")
        assert all(c == 'gray' for _, c in result)

    def test_mixed_result(self):
        game = WordleGame()
        game.target = "STONE"
        result = game._check_guess("STAIN")
        # S, T match positions 0,1 -> green
        assert result[0][1] == 'green'
        assert result[1][1] == 'green'
        # A not in target -> gray
        assert result[2][1] == 'gray'
        # I not in target -> gray
        # N is in target (pos 3) -> yellow
        assert result[4][1] == 'yellow'

    def test_correct_word_length(self):
        game = WordleGame()
        game.target = "HAPPY"
        result = game._check_guess("HAPPY")
        assert len(result) == 5


class TestSaveLoadState:
    def test_save_state_json(self):
        game = WordleGame()
        game.target = "CLOUD"
        game.attempts = ["CRANE"]
        state = game.save_state_json()
        assert state['target'] == "CLOUD"
        assert state['attempts'] == ["CRANE"]
        assert 'score' in state

    def test_load_state_json(self):
        game = WordleGame()
        game.load_state_json({
            'target': 'BRAIN',
            'attempts': ['CRANE', 'TRAIN'],
            'used_letters': {'C': 'gray', 'T': 'gray'},
            'score': 20,
            'round': 2,
        })
        assert game.target == 'BRAIN'
        assert game.attempts == ['CRANE', 'TRAIN']
        assert game.score == 20
        assert game.round == 2


class TestUsedLetters:
    def test_green_overrides_yellow(self):
        game = WordleGame()
        game.target = "APPLE"
        result = game._check_guess("PAPER")
        # Position 2: P matches target[2] -> green
        assert result[2][1] == 'green'
        # Position 0: P is in target but not at pos 0 -> yellow
        assert result[0][1] == 'yellow'

    def test_yellow_in_result(self):
        game = WordleGame()
        game.target = "STONE"
        result = game._check_guess("TRAIN")
        # T at pos 0: T is in target (pos 1) -> yellow
        assert result[0][1] == 'yellow'
        assert any(c == 'yellow' for _, c in result)
