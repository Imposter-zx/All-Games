"""Unit tests for online leaderboard client module."""

import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

import online_leaderboard as olb


SERVER = "https://test-server.example.com"


class TestSubmitScore:
    @patch('urllib.request.urlopen')
    def test_submit_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value = mock_response
        result = olb.submit_score("PLAYER", "snake", 500, "normal", SERVER)
        assert result is True
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen', side_effect=OSError("Connection failed"))
    def test_submit_server_down(self, mock_urlopen):
        result = olb.submit_score("PLAYER", "snake", 500, "normal", SERVER)
        assert result is False


class TestFetchLeaderboard:
    @patch('urllib.request.urlopen')
    def test_fetch_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"rank": 1, "player_name": "PLAYER", "score": 500, "game_name": "snake", "difficulty": "normal", "submitted_at": 1000.0}
        ]).encode()
        mock_urlopen.return_value = mock_response
        result = olb.fetch_leaderboard("snake", 10, SERVER)
        assert len(result) == 1
        assert result[0]["rank"] == 1
        assert result[0]["player_name"] == "PLAYER"
        assert result[0]["score"] == 500

    @patch('urllib.request.urlopen', side_effect=OSError("Connection failed"))
    def test_fetch_server_down(self, mock_urlopen):
        result = olb.fetch_leaderboard("snake", 10, SERVER)
        assert result == []

    @patch('urllib.request.urlopen', side_effect=OSError("Connection failed"))
    def test_fetch_all_games_server_down(self, mock_urlopen):
        result = olb.fetch_leaderboard(None, 10, SERVER)
        assert result == []


class TestHealthCheck:
    @patch('urllib.request.urlopen')
    def test_health_ok(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value = mock_response
        result = olb.health_check(SERVER)
        assert result is True

    @patch('urllib.request.urlopen', side_effect=OSError("Connection failed"))
    def test_health_fail(self, mock_urlopen):
        result = olb.health_check(SERVER)
        assert result is False

    @patch('urllib.request.urlopen')
    def test_health_non_200(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 503
        mock_urlopen.return_value.__enter__.return_value = mock_response
        result = olb.health_check(SERVER)
        assert result is False


class TestConstants:
    def test_default_server(self):
        assert olb.DEFAULT_SERVER == "https://retro-arcade-leaderboard.onrender.com"

    def test_timeout(self):
        assert olb.TIMEOUT == 5
