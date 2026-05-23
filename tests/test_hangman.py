"""Unit tests for Hangman game logic."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from hangman import HangmanGame, WORDS, HANGMAN_STAGES


class TestHangmanInit:
    def test_init(self):
        game = HangmanGame('normal')
        assert game.game_name == 'hangman'
        assert game.word in WORDS or game.word.upper() in [w.upper() for w in WORDS]
        assert game.guessed == []
        assert game.wrong_guesses == []
        assert game.max_wrong == 6
        assert game.round == 1
        assert game.streak == 0

    def test_init_with_difficulty(self):
        for diff in ['easy', 'normal', 'hard']:
            game = HangmanGame(diff)
            assert game.difficulty == diff


class TestDisplayWord:
    def test_all_hidden_at_start(self):
        game = HangmanGame()
        display = game.display_word()
        assert "_" in display
        assert len(display.replace(" ", "")) == len(game.word)

    def test_revealed_letters(self):
        game = HangmanGame()
        game.word = "TEST"
        game.guessed = ["T"]
        display = game.display_word()
        assert "T" in display
        assert "_" in display

    def test_all_revealed(self):
        game = HangmanGame()
        game.word = "AB"
        game.guessed = ["A", "B"]
        assert game.display_word() == "A B"
        assert game.is_won() is True


class TestWinLose:
    def test_is_won(self):
        game = HangmanGame()
        game.word = "HI"
        game.guessed = ["H", "I"]
        assert game.is_won() is True

    def test_not_won(self):
        game = HangmanGame()
        game.word = "HI"
        game.guessed = ["H"]
        assert game.is_won() is False

    def test_game_over_at_max_wrong(self):
        game = HangmanGame()
        game.max_wrong = 6
        assert len(game.wrong_guesses) < 6
        assert not game.game_over


class TestHangmanStages:
    def test_stage_count(self):
        assert len(HANGMAN_STAGES) == 7  # 0 through 6 wrong guesses

    def test_stage_0_empty(self):
        assert HANGMAN_STAGES[0] == ""

    def test_stage_6_complete(self):
        assert "O" in HANGMAN_STAGES[6]
        assert "/" in HANGMAN_STAGES[6]
        assert "\\" in HANGMAN_STAGES[6]


class TestWordList:
    def test_word_list_has_words(self):
        assert len(WORDS) >= 40

    def test_all_words_are_alpha(self):
        for word in WORDS:
            assert word.isalpha(), f"'{word}' contains non-alpha characters"
