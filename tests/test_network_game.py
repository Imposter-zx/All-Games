"""Tests for the network game client module."""

import os
import sys
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

import network_game as ng


class TestCreateChessRoom:
    @patch.object(ng, '_post')
    def test_create_success(self, mock_post):
        mock_post.return_value = {'room_id': 'abc123', 'color': 'white', 'status': 'waiting'}
        result = ng.create_chess_room('Player1')
        assert result['room_id'] == 'abc123'
        assert result['color'] == 'white'
        mock_post.assert_called_once()

    @patch.object(ng, '_post')
    def test_create_failure(self, mock_post):
        mock_post.return_value = None
        result = ng.create_chess_room('Player1')
        assert result is None


class TestJoinChessRoom:
    @patch.object(ng, '_post')
    def test_join_success(self, mock_post):
        mock_post.return_value = {'room_id': 'abc123', 'color': 'black', 'status': 'playing'}
        result = ng.join_chess_room('abc123', 'Player2')
        assert result['color'] == 'black'
        assert result['status'] == 'playing'

    @patch.object(ng, '_post')
    def test_join_not_found(self, mock_post):
        mock_post.return_value = None
        result = ng.join_chess_room('invalid', 'Player2')
        assert result is None


class TestSubmitChessMove:
    @patch.object(ng, '_post')
    def test_submit_move(self, mock_post):
        mock_post.return_value = {'move_number': 1, 'ack': True}
        result = ng.submit_chess_move('abc123', 'Player1', 'e4')
        assert result['ack'] is True
        assert result['move_number'] == 1


class TestGetChessGameState:
    @patch.object(ng, '_get')
    def test_get_state(self, mock_get):
        mock_get.return_value = {
            'room_id': 'abc123', 'status': 'playing',
            'moves': ['e4', 'e5'], 'turn': 'black',
        }
        result = ng.get_chess_game_state('abc123', 'Player1')
        assert result['status'] == 'playing'
        assert len(result['moves']) == 2


class TestResignChess:
    @patch.object(ng, '_post')
    def test_resign(self, mock_post):
        mock_post.return_value = {'status': 'finished', 'winner': 'black'}
        result = ng.resign_chess('abc123', 'Player1')
        assert result['status'] == 'finished'
        assert result['winner'] == 'black'
