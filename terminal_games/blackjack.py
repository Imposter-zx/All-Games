import logging
import random
import time
from typing import List, Optional, Tuple

from arcade_utils import (
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    beep,
    clear_screen,
    draw_retro_box,
    show_popup,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

SUITS = ['\u2665', '\u2666', '\u2663', '\u2660']
SUIT_FALLBACK = ['H', 'D', 'C', 'S']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


def card_value(rank: str) -> int:
    if rank in ('J', 'Q', 'K'):
        return 10
    if rank == 'A':
        return 11
    return int(rank)


def hand_value(cards: List[Tuple[str, int]]) -> int:
    total = sum(card_value(r) for r, _ in cards)
    aces = sum(1 for r, _ in cards if r == 'A')
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def card_str(rank: str, suit_idx: int) -> str:
    suit = SUITS[suit_idx] if SUITS[suit_idx] else SUIT_FALLBACK[suit_idx]
    return f"{C_WHITE}{rank}{suit}{C_RESET}"


def card_back() -> str:
    return f"{C_MAGENTA}[?]{C_RESET}"


class BlackjackGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('blackjack', difficulty)
        self.deck: List[Tuple[str, int]] = []
        self.player_hand: List[Tuple[str, int]] = []
        self.dealer_hand: List[Tuple[str, int]] = []
        self.player_turn = True
        self.game_result: Optional[str] = None
        self.round = 1

    def build_deck(self) -> None:
        self.deck = [(rank, i) for i in range(4) for rank in RANKS]
        random.shuffle(self.deck)

    def deal_card(self) -> Tuple[str, int]:
        return self.deck.pop()

    def deal_initial(self) -> None:
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.dealer_hand = [self.deal_card(), self.deal_card()]

    def render_hand(self, hand: List[Tuple[str, int]], hide_first: bool = False) -> str:
        parts = []
        for i, (rank, suit) in enumerate(hand):
            if hide_first and i == 0:
                parts.append(card_back())
            else:
                parts.append(card_str(rank, suit))
        return " ".join(parts)

    def show_table(self, hide_dealer: bool = True) -> None:
        lines: list[str] = [
            f"{C_CYAN}ROUND {self.round}{C_RESET}   DIFFICULTY: {self.difficulty.upper()}",
            "",
            f"{C_YELLOW}DEALER:{C_RESET}",
            f"  {self.render_hand(self.dealer_hand, hide_dealer)}",
            f"  Value: {'?' if hide_dealer else hand_value(self.dealer_hand)}",
            "",
            f"{C_GREEN}YOU:{C_RESET}",
            f"  {self.render_hand(self.player_hand)}",
            f"  Value: {hand_value(self.player_hand)}",
            "",
        ]
        if self.game_result:
            color = C_GREEN if 'win' in self.game_result or 'blackjack' in self.game_result else C_RED
            lines.append(f"{color}{self.game_result.upper()}{C_RESET}")
            lines.append("")
        draw_retro_box(40, "\u2660 BLACKJACK \u2665", lines, color=C_YELLOW)

        if not self.game_result and self.player_turn:
            print(f"\n{C_WHITE}[H] Hit  [S] Stand  [Q] Quit  [?] Help{C_RESET}")
        elif self.game_result:
            print(f"\n{C_WHITE}[Any Key] Next Round  [Q] Quit{C_RESET}")

    def dealer_play(self) -> None:
        while hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deal_card())
            time.sleep(0.5)

    def resolve_round(self) -> None:
        self.dealer_play()
        p_val = hand_value(self.player_hand)
        d_val = hand_value(self.dealer_hand)

        if p_val > 21:
            self.game_result = "bust! dealer wins"
            beep("lose")
        elif d_val > 21:
            self.game_result = "dealer busts! you win!"
            self.score += 100
            self.award_xp_for_action(50)
            beep("win")
        elif p_val > d_val:
            self.game_result = "you win!"
            self.score += 100
            self.award_xp_for_action(50)
            beep("win")
        elif p_val < d_val:
            self.game_result = "dealer wins"
            beep("lose")
        else:
            self.game_result = "push (tie)"
            beep("correct")

        if hand_value(self.player_hand) == 21 and len(self.player_hand) == 2:
            self.unlock_achievement("blackjack_natural", "Natural Blackjack")

        if self.score >= 500:
            self.unlock_achievement("blackjack_500", "Blackjack Pro")

    def save_state_json(self) -> dict:
        return {
            'deck': list(self.deck),
            'player_hand': list(self.player_hand),
            'dealer_hand': list(self.dealer_hand),
            'player_turn': self.player_turn,
            'score': self.score,
            'round': self.round,
            'game_result': self.game_result,
        }

    def load_state_json(self, state: dict) -> None:
        self.deck = list(state.get('deck', []))
        self.player_hand = [(r, s) for r, s in state.get('player_hand', [])]
        self.dealer_hand = [(r, s) for r, s in state.get('dealer_hand', [])]
        self.player_turn = state.get('player_turn', True)
        self.score = state.get('score', 0)
        self.round = state.get('round', 1)
        self.game_result = state.get('game_result', None)

    def _show_help(self) -> None:
        show_popup(
            "BLACKJACK: Beat the dealer by getting closer to 21 without going over. "
            "H = Hit (take a card), S = Stand (keep hand). "
            "Dealer must hit on 16 and stand on 17. "
            "Blackjack (21 in 2 cards) pays bonus XP!",
            C_YELLOW, delay=2.0
        )

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        else:
            self.build_deck()
            self.deal_initial()
        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 2)
                self.show_table(hide_dealer=self.player_turn)

                if self.game_result:
                    self.round += 1
                    self.end_timer()
                    final_stats = self.get_final_stats()
                    final_stats['high_score'] = self.score
                    self.save_stats(final_stats)

                    self.start_timer()
                    key = input_handler.get_safe_key()
                    if key and self._save_and_quit(key.lower()):
                        break
                    self.game_result = None
                    self.player_turn = True
                    self.player_hand = []
                    self.dealer_hand = []
                    if len(self.deck) < 20:
                        self.build_deck()
                    self.deal_initial()
                    continue

                if self.player_turn:
                    if hand_value(self.player_hand) == 21:
                        self.player_turn = False
                        self.resolve_round()
                        continue

                    key = input_handler.get_safe_key()
                    if key and key.lower() == 'h':
                        beep("correct")
                        self.player_hand.append(self.deal_card())
                        if hand_value(self.player_hand) > 21:
                            self.player_turn = False
                            self.resolve_round()
                    elif key and key.lower() == 's':
                        beep("correct")
                        self.player_turn = False
                        self.resolve_round()
                    elif key and self._save_and_quit(key.lower()):
                        break
                    elif key == '?':
                        self._show_help()
                else:
                    key = input_handler.get_safe_key()
                    if key and self._save_and_quit(key.lower()):
                        break
                    if key:
                        self.player_turn = True
                        self.game_result = None
                        self.player_hand = []
                        self.dealer_hand = []
                        if len(self.deck) < 20:
                            self.build_deck()
                        self.deal_initial()

                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats


def play_blackjack(difficulty: str = 'normal') -> dict:
    game = BlackjackGame(difficulty)
    return game.play()
