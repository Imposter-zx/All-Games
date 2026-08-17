"""API tests for the FastAPI leaderboard + chess/pong multiplayer server."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

import main as srv
import pytest
from fastapi.testclient import TestClient

client = TestClient(srv.app)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(srv, 'DB_PATH', str(tmp_path / 'test.db'))
    yield


class TestHealth:
    def test_health_ok(self):
        r = client.get('/health')
        assert r.status_code == 200
        assert r.json()['status'] == 'ok'


class TestScores:
    def test_submit_valid(self):
        r = client.post('/api/scores', json={
            'player_name': ' Alice ', 'game_name': 'Snake', 'score': 1000
        })
        assert r.status_code == 200
        assert r.json()['status'] == 'accepted'

    def test_submit_requires_name(self):
        r = client.post('/api/scores', json={'player_name': '  ', 'game_name': 'snake', 'score': 1})
        assert r.status_code == 400

    def test_submit_requires_game(self):
        r = client.post('/api/scores', json={'player_name': 'Bob', 'game_name': '', 'score': 1})
        assert r.status_code == 400

    def test_submit_rejects_negative_score(self):
        r = client.post('/api/scores', json={'player_name': 'Bob', 'game_name': 'snake', 'score': -5})
        assert r.status_code == 400

    def test_leaderboard_orders_desc_and_ranks(self):
        for name, score in [('bob', 100), ('amy', 500), ('zoe', 250)]:
            client.post('/api/scores', json={
                'player_name': name, 'game_name': 'snake', 'score': score
            })
        entries = client.get('/api/leaderboard?limit=10').json()
        assert entries[0]['player_name'] == 'amy'
        assert entries[0]['rank'] == 1
        assert [e['score'] for e in entries] == [500, 250, 100]

    def test_leaderboard_filters_by_game(self):
        client.post('/api/scores', json={'player_name': 'bob', 'game_name': 'snake', 'score': 100})
        client.post('/api/scores', json={'player_name': 'bob', 'game_name': 'tetris', 'score': 900})
        entries = client.get('/api/leaderboard?game_name=SNAKE&limit=10').json()
        assert len(entries) == 1
        assert entries[0]['game_name'] == 'snake'

    def test_leaderboard_limit_and_validation(self):
        r = client.get('/api/leaderboard?limit=500')
        assert r.status_code == 422

    def test_my_best_global_and_per_game(self):
        client.post('/api/scores', json={'player_name': 'bob', 'game_name': 'snake', 'score': 100})
        client.post('/api/scores', json={'player_name': 'bob', 'game_name': 'snake', 'score': 600})
        client.post('/api/scores', json={'player_name': 'bob', 'game_name': 'tetris', 'score': 300})
        assert client.get('/api/my_best?player_name=bob').json()['best'] == 600
        assert client.get('/api/my_best?player_name=bob&game_name=tetris').json()['best'] == 300
        assert client.get('/api/my_best?player_name=nobody').json()['best'] == 0


class TestChessRooms:
    def test_create_join_move_and_state(self):
        r = client.post('/api/chess/create_room?player_name=Alice')
        assert r.status_code == 200
        room_id = r.json()['room_id']

        r = client.post(f'/api/chess/join_room?room_id={room_id}&player_name=Bob')
        assert r.status_code == 200
        assert r.json()['color'] == 'black'

        state = client.get(f'/api/chess/game_state?room_id={room_id}&player_name=Alice').json()
        assert state['status'] == 'playing'
        assert state['turn'] == 'white'

        bad = client.post(f'/api/chess/move?room_id={room_id}&player_name=Bob&move=e5')
        assert bad.status_code == 400

        ok = client.post(f'/api/chess/move?room_id={room_id}&player_name=Alice&move=e4')
        assert ok.status_code == 200
        assert ok.json()['move_number'] == 1

        state = client.get(f'/api/chess/game_state?room_id={room_id}&player_name=Alice').json()
        assert state['last_move'] == 'e4'
        assert state['turn'] == 'black'

    def test_cannot_join_own_room(self):
        r = client.post('/api/chess/create_room?player_name=Alice')
        room_id = r.json()['room_id']
        r = client.post(f'/api/chess/join_room?room_id={room_id}&player_name=Alice')
        assert r.status_code == 400

    def test_join_full_or_missing_room(self):
        assert client.post('/api/chess/join_room?room_id=nope&player_name=Bob').status_code == 404
        r = client.post('/api/chess/create_room?player_name=Alice')
        room_id = r.json()['room_id']
        client.post(f'/api/chess/join_room?room_id={room_id}&player_name=Bob')
        assert client.post(
            f'/api/chess/join_room?room_id={room_id}&player_name=Carol'
        ).status_code == 400

    def test_resign_declares_winner(self):
        r = client.post('/api/chess/create_room?player_name=Alice')
        room_id = r.json()['room_id']
        client.post(f'/api/chess/join_room?room_id={room_id}&player_name=Bob')
        r = client.post(f'/api/chess/resign?room_id={room_id}&player_name=Alice')
        assert r.status_code == 200
        assert r.json()['winner'] == 'black'
        state = client.get(f'/api/chess/game_state?room_id={room_id}&player_name=Alice').json()
        assert state['status'] == 'finished'


class TestPongRooms:
    def test_create_join_paddle_state_and_forfeit(self):
        r = client.post('/api/pong/create_room?player_name=Alice')
        room_id = r.json()['room_id']

        r = client.post(f'/api/pong/join_room?room_id={room_id}&player_name=Bob')
        assert r.status_code == 200
        assert r.json()['status'] == 'playing'

        assert client.post(
            f'/api/pong/paddle?room_id={room_id}&player_name=Alice&direction=up'
        ).status_code == 200
        assert client.post(
            f'/api/pong/paddle?room_id={room_id}&player_name=Alice&direction=diagonal'
        ).status_code == 400
        assert client.post(
            f'/api/pong/paddle?room_id={room_id}&player_name=Carol&direction=up'
        ).status_code == 403

        state = client.get(f'/api/pong/state?room_id={room_id}&player_name=Alice').json()
        assert state['side'] == 'left'
        assert state['status'] == 'playing'
        assert state['width'] == srv.PONG_WIDTH

        r = client.post(f'/api/pong/forfeit?room_id={room_id}&player_name=Alice')
        assert r.status_code == 200
        assert r.json()['winner'] == 'Bob'

    def test_pong_room_errors(self):
        assert client.get('/api/pong/state?room_id=nope&player_name=Alice').status_code == 404
        r = client.post('/api/pong/create_room?player_name=Alice')
        room_id = r.json()['room_id']
        assert client.post(
            f'/api/pong/join_room?room_id={room_id}&player_name=Alice'
        ).status_code == 400

    def test_pong_forfeit_before_start_rejected(self):
        r = client.post('/api/pong/create_room?player_name=Alice')
        room_id = r.json()['room_id']
        assert client.post(
            f'/api/pong/forfeit?room_id={room_id}&player_name=Alice'
        ).status_code == 400
