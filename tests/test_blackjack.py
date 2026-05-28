"""Unit tests for Blackjack game logic."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from blackjack import RANKS, BlackjackGame, card_value, hand_value


class TestCardValue:
    def test_number_cards(self):
        for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
            assert card_value(rank) == int(rank)

    def test_face_cards(self):
        for rank in ['J', 'Q', 'K']:
            assert card_value(rank) == 10

    def test_ace(self):
        assert card_value('A') == 11


class TestHandValue:
    def test_simple_sum(self):
        assert hand_value([('A', 0), ('K', 1)]) == 21

    def test_ace_eleven(self):
        assert hand_value([('A', 0), ('5', 1)]) == 16

    def test_ace_as_one(self):
        assert hand_value([('A', 0), ('7', 1), ('5', 2)]) == 13

    def test_multi_ace(self):
        assert hand_value([('A', 0), ('A', 1), ('9', 2)]) == 21

    def test_bust(self):
        assert hand_value([('K', 0), ('Q', 1), ('5', 2)]) == 25

    def test_two_aces(self):
        assert hand_value([('A', 0), ('A', 1)]) == 12

    def test_three_aces(self):
        assert hand_value([('A', 0), ('A', 1), ('A', 2)]) == 13

    def test_empty_hand(self):
        assert hand_value([]) == 0


class TestBlackjackGame:
    def test_init(self):
        game = BlackjackGame('easy')
        assert game.game_name == 'blackjack'
        assert game.difficulty == 'easy'
        assert game.deck == []
        assert game.player_hand == []
        assert game.dealer_hand == []
        assert game.player_turn is True
        assert game.game_result is None
        assert game.round == 1
        assert game.score == 0

    def test_build_deck_size(self):
        game = BlackjackGame()
        game.build_deck()
        assert len(game.deck) == 52

    def test_build_deck_all_cards(self):
        game = BlackjackGame()
        game.build_deck()
        ranks = [r for r, _ in game.deck]
        suits = [s for _, s in game.deck]
        for rank in RANKS:
            assert ranks.count(rank) == 4
        for suit in range(4):
            assert suits.count(suit) == 13

    def test_deal_card(self):
        game = BlackjackGame()
        game.build_deck()
        card = game.deal_card()
        assert len(card) == 2
        assert card[0] in RANKS
        assert card[1] in range(4)
        assert len(game.deck) == 51

    def test_deal_initial(self):
        game = BlackjackGame()
        game.build_deck()
        game.deal_initial()
        assert len(game.player_hand) == 2
        assert len(game.dealer_hand) == 2
        assert len(game.deck) == 48

    def test_dealer_play_hits_until_17(self):
        game = BlackjackGame()
        game.build_deck()
        game.dealer_hand = [('K', 0), ('5', 1)]
        game.dealer_play()
        from blackjack import hand_value
        game.dealer_hand = game.dealer_hand
        assert hand_value(game.dealer_hand) >= 17

    def test_dealer_stands_on_17(self):
        game = BlackjackGame()
        game.build_deck()
        game.dealer_hand = [('K', 0), ('7', 1)]
        game.dealer_play()
        assert hand_value(game.dealer_hand) >= 17

    def test_resolve_player_bust(self):
        game = BlackjackGame()
        game.build_deck()
        game.player_hand = [('K', 0), ('Q', 1), ('5', 2)]
        game.dealer_hand = [('2', 0), ('2', 1)]
        game.resolve_round()
        assert 'bust' in game.game_result

    def test_resolve_dealer_bust(self):
        game = BlackjackGame()
        game.build_deck()
        game.player_hand = [('K', 0), ('7', 1)]
        game.dealer_hand = [('K', 0), ('Q', 1), ('5', 2)]
        game.resolve_round()
        assert 'bust' in game.game_result

    def test_resolve_player_win(self):
        game = BlackjackGame()
        game.build_deck()
        game.player_hand = [('K', 0), ('9', 1)]
        game.dealer_hand = [('K', 0), ('7', 1)]
        game.resolve_round()
        assert 'win' in game.game_result

    def test_resolve_dealer_win(self):
        game = BlackjackGame()
        game.build_deck()
        game.player_hand = [('K', 0), ('7', 1)]
        game.dealer_hand = [('K', 0), ('9', 1)]
        game.resolve_round()
        assert 'dealer wins' in game.game_result

    def test_resolve_push(self):
        game = BlackjackGame()
        game.build_deck()
        game.player_hand = [('K', 0), ('9', 1)]
        game.dealer_hand = [('K', 0), ('9', 1)]
        game.resolve_round()
        assert 'push' in game.game_result

    def test_difficulty_configs(self):
        for diff in ['easy', 'normal', 'hard']:
            game = BlackjackGame(diff)
            assert game.difficulty == diff
            assert game.xp_system.multiplier in [0.5, 1.0, 2.0]


