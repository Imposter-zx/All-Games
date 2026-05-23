"""Unit tests for Connect Four game logic."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from connect_four import ConnectFourGame, ROWS, COLS, EMPTY, PLAYER, AI


class TestConnectFourInit:
    def test_init(self):
        game = ConnectFourGame('normal')
        assert game.game_name == 'connect_four'
        assert game.current_player == PLAYER
        assert game.move_count == 0
        assert len(game.board) == ROWS
        assert len(game.board[0]) == COLS
        assert all(game.board[r][c] == EMPTY for r in range(ROWS) for c in range(COLS))

    def test_difficulty_depths(self):
        assert ConnectFourGame('easy').ai_depth == 3
        assert ConnectFourGame('normal').ai_depth == 5
        assert ConnectFourGame('hard').ai_depth == 7


class TestDropPiece:
    def test_drop_in_empty_column(self):
        game = ConnectFourGame()
        assert game.drop_piece(0, PLAYER) is True
        assert game.board[ROWS - 1][0] == PLAYER

    def test_drop_fills_column(self):
        game = ConnectFourGame()
        for i in range(ROWS):
            assert game.drop_piece(0, PLAYER) is True
        assert game.board[0][0] == PLAYER
        assert game.drop_piece(0, PLAYER) is False

    def test_drop_out_of_bounds(self):
        game = ConnectFourGame()
        assert game.drop_piece(-1, PLAYER) is False
        assert game.drop_piece(COLS, PLAYER) is False


class TestWinDetection:
    def test_horizontal_win(self):
        game = ConnectFourGame()
        for c in range(4):
            game.drop_piece(c, PLAYER)
        assert game.check_win(PLAYER) is True

    def test_vertical_win(self):
        game = ConnectFourGame()
        for _ in range(4):
            game.drop_piece(0, PLAYER)
        assert game.check_win(PLAYER) is True

    def test_diagonal_down_win(self):
        game = ConnectFourGame()
        for i in range(4):
            for j in range(i):
                game.drop_piece(i, AI)
            game.drop_piece(i, PLAYER)
        assert game.check_win(PLAYER) is True

    def test_diagonal_up_win(self):
        game = ConnectFourGame()
        for i in range(3, -1, -1):
            for j in range(3 - i):
                game.drop_piece(i, AI)
            game.drop_piece(i, PLAYER)
        assert game.check_win(PLAYER) is True

    def test_no_win(self):
        game = ConnectFourGame()
        game.drop_piece(0, PLAYER)
        game.drop_piece(1, AI)
        assert game.check_win(PLAYER) is False
        assert game.check_win(AI) is False


class TestDraw:
    def test_is_draw(self):
        game = ConnectFourGame()
        for c in range(COLS):
            for r in range(ROWS):
                game.board[r][c] = PLAYER
        assert game.is_draw() is True

    def test_not_draw(self):
        game = ConnectFourGame()
        assert game.is_draw() is False


class TestValidMoves:
    def test_all_valid_at_start(self):
        game = ConnectFourGame()
        assert game.get_valid_cols() == list(range(COLS))

    def test_filled_column_invalid(self):
        game = ConnectFourGame()
        for _ in range(ROWS):
            game.drop_piece(0, PLAYER)
        assert 0 not in game.get_valid_cols()
