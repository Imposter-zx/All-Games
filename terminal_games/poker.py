import logging
import random
import time
from typing import Dict, List, Optional, Tuple

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
RANK_VALUES = {r: i + 2 for i, r in enumerate(RANKS)}

PAYOUTS = {
    'royal_flush': 250,
    'straight_flush': 50,
    'four_of_a_kind': 25,
    'full_house': 9,
    'flush': 6,
    'straight': 4,
    'three_of_a_kind': 3,
    'two_pair': 2,
    'jacks_or_better': 1,
    'nothing': 0,
}

PAYOUT_ORDER = ['royal_flush', 'straight_flush', 'four_of_a_kind', 'full_house',
                'flush', 'straight', 'three_of_a_kind', 'two_pair',
                'jacks_or_better', 'nothing']


def card_str(rank: str, suit_idx: int) -> str:
    suit = SUITS[suit_idx] if SUITS[suit_idx] else SUIT_FALLBACK[suit_idx]
    return f"{C_WHITE}{rank}{suit}{C_RESET}"


def build_deck() -> List[Tuple[str, int]]:
    deck = [(rank, i) for i in range(4) for rank in RANKS]
    random.shuffle(deck)
    return deck


def evaluate_hand(cards: List[Tuple[str, int]]) -> str:
    ranks = [c[0] for c in cards]
    suits = [c[1] for c in cards]
    values = sorted([RANK_VALUES[r] for r in ranks])
    value_counts = {}
    for v in values:
        value_counts[v] = value_counts.get(v, 0) + 1
    counts = sorted(value_counts.values(), reverse=True)
    unique_ranks = sorted(value_counts.keys())

    is_flush = len(set(suits)) == 1
    is_straight = False
    if unique_ranks == list(range(unique_ranks[0], unique_ranks[0] + 5)):
        is_straight = True
    if set(unique_ranks) == {2, 3, 4, 5, 14}:
        is_straight = True

    has_royal = set(unique_ranks) == {10, 11, 12, 13, 14}

    if is_flush and is_straight and has_royal:
        return 'royal_flush'
    if is_flush and is_straight:
        return 'straight_flush'
    if counts == [4, 1]:
        return 'four_of_a_kind'
    if counts == [3, 2]:
        return 'full_house'
    if is_flush:
        return 'flush'
    if is_straight:
        return 'straight'
    if counts == [3, 1, 1]:
        return 'three_of_a_kind'
    if counts == [2, 2, 1]:
        return 'two_pair'
    for r in ranks:
        if r in ('J', 'Q', 'K', 'A') and value_counts[RANK_VALUES[r]] >= 2:
            return 'jacks_or_better'
    return 'nothing'


def hand_name(hand_type: str) -> str:
    names = {
        'royal_flush': 'Royal Flush',
        'straight_flush': 'Straight Flush',
        'four_of_a_kind': 'Four of a Kind',
        'full_house': 'Full House',
        'flush': 'Flush',
        'straight': 'Straight',
        'three_of_a_kind': 'Three of a Kind',
        'two_pair': 'Two Pair',
        'jacks_or_better': 'Jacks or Better',
        'nothing': 'Nothing',
    }
    return names.get(hand_type, hand_type)


class PokerGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('poker', difficulty)
        self.deck: List[Tuple[str, int]] = []
        self.hand: List[Tuple[str, int]] = []
        self.held: List[bool] = [False] * 5
        self.credits = 100
        self.bet = 1
        self.hand_result: Optional[str] = None
        self.payout = 0
        self.round = 0
        self.phase = 'bet'
        self.high_score = 0
        self.total_won = 0

    def setup_round(self) -> None:
        self.deck = build_deck()
        self.hand = []
        self.held = [False] * 5
        self.hand_result = None
        self.payout = 0
        self.phase = 'bet'

    def deal(self) -> None:
        self.hand = [self.deck.pop() for _ in range(5)]
        self.phase = 'hold'

    def draw(self) -> None:
        for i in range(5):
            if not self.held[i]:
                self.hand[i] = self.deck.pop()
        self.hand_result = evaluate_hand(self.hand)
        self.payout = PAYOUTS[self.hand_result] * self.bet
        if self.payout > 0:
            self.credits += self.payout
            self.total_won += self.payout
            beep("win")
        else:
            beep("lose")
        if self.credits > self.high_score:
            self.high_score = self.credits
        xp_base = self.payout if self.payout > 0 else 10
        self.award_xp_for_action(xp_base)
        self.phase = 'result'

    def render_cards(self, show_numbers: bool = False) -> None:
        line1 = "  "
        line2 = "  "
        for i, (rank, suit) in enumerate(self.hand):
            num = f"{i + 1}" if show_numbers else " "
            if self.phase == 'draw' or self.phase == 'result':
                card = card_str(rank, suit)
            elif self.phase == 'hold' and self.held[i]:
                card = card_str(rank, suit)
            else:
                card = f"{C_MAGENTA}[?]{C_RESET}"
            line1 += f"  {num}   "
            line2 += f" {card}  "
        print(f"\n{C_CYAN}  Your Hand:{C_RESET}")
        print(f"  {'':5}1     2     3     4     5")
        if show_numbers or self.phase in ('draw', 'result'):
            cards_line = "  "
            for i, (rank, suit) in enumerate(self.hand):
                cards_line += f" {card_str(rank, suit)}  "
            print(cards_line)
        else:
            print(f"  {C_MAGENTA}[?]  [?]  [?]  [?]  [?]{C_RESET}")
        held_line = "  "
        for i in range(5):
            held_line += f"  {C_GREEN}[H]{C_RESET} " if self.held[i] else "     "
        print(held_line)

    def show_table(self) -> None:
        lines = [
            f"{C_YELLOW}CREDITS: {self.credits}  BET: {self.bet}  TOTAL WON: {self.total_won}{C_RESET}",
            f"{C_CYAN}ROUND: {self.round}{C_RESET}",
        ]
        if self.hand_result:
            result_color = C_GREEN if self.payout > 0 else C_RED
            lines.append(
                f"{result_color}{hand_name(self.hand_result)} — "
                f"{'WON ' + str(self.payout) + '!' if self.payout > 0 else 'Nothing'}{C_RESET}"
            )
        draw_retro_box(50, "\u2660 VIDEO POKER \u2665", lines, color=C_YELLOW)

        self.render_cards(show_numbers=(self.phase == 'hold'))

        if self.phase == 'bet':
            print(f"\n{C_WHITE}[1-5] Bet amount  [D] Deal  [Q] Quit  [?] Help{C_RESET}")
        elif self.phase == 'hold':
            print(f"\n{C_WHITE}[1-5] Toggle hold  [D] Draw  [A] Hold All  [N] None  [Q] Quit  [?] Help{C_RESET}")
        elif self.phase == 'result':
            print(f"\n{C_WHITE}[Any Key] Next Hand  [Q] Quit  [?] Help{C_RESET}")
        elif self.phase == 'draw':
            print(f"\n{C_WHITE}[Any Key] Continue  [Q] Quit{C_RESET}")

    def _show_help(self) -> None:
        show_popup(
            "VIDEO POKER: Get the best 5-card hand. "
            "Bet 1-5 credits, then hold/discard cards to improve your hand. "
            "Paytable: Royal Flush 250x, Straight Flush 50x, 4-of-Kind 25x, "
            "Full House 9x, Flush 6x, Straight 4x, 3-of-Kind 3x, "
            "Two Pair 2x, Jacks or Better 1x.",
            C_YELLOW, delay=2.5
        )

    def play(self) -> Dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        else:
            self.setup_round()
            self.bet = 1
        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 2)
                self.show_table()

                if self.credits <= 0 and self.phase == 'bet':
                    print(f"\n{C_RED}OUT OF CREDITS! Game Over.{C_RESET}")
                    self.end_timer()
                    final_stats = self.get_final_stats()
                    final_stats['high_score'] = self.high_score
                    final_stats['credits'] = self.credits
                    self.save_stats(final_stats)
                    time.sleep(2)
                    break

                if self.phase == 'bet':
                    key = input_handler.get_safe_key()
                    if key is None:
                        time.sleep(0.05)
                        continue
                    if key in ('1', '2', '3', '4', '5'):
                        self.bet = int(key)
                        beep("correct")
                    elif key.lower() == 'd':
                        if self.credits >= self.bet:
                            self.credits -= self.bet
                            self.round += 1
                            self.deal()
                            beep("correct")
                        else:
                            show_popup("Not enough credits!", C_RED, delay=1.0)
                    elif key and self._save_and_quit(key.lower()):
                        break
                    elif key == '?':
                        self._show_help()

                elif self.phase == 'hold':
                    key = input_handler.get_safe_key()
                    if key is None:
                        time.sleep(0.05)
                        continue
                    if key in ('1', '2', '3', '4', '5'):
                        idx = int(key) - 1
                        self.held[idx] = not self.held[idx]
                        beep("correct")
                    elif key.lower() == 'a':
                        self.held = [True] * 5
                        beep("correct")
                    elif key.lower() == 'n':
                        self.held = [False] * 5
                        beep("correct")
                    elif key.lower() == 'd':
                        beep("correct")
                        self.draw()
                    elif key and self._save_and_quit(key.lower()):
                        break
                    elif key == '?':
                        self._show_help()

                elif self.phase == 'draw':
                    key = input_handler.get_safe_key()
                    if key:
                        self.hand_result = evaluate_hand(self.hand)
                        self.payout = PAYOUTS[self.hand_result] * self.bet
                        if self.payout > 0:
                            self.credits += self.payout
                            self.total_won += self.payout
                            beep("win")
                        else:
                            beep("lose")
                        if self.credits > self.high_score:
                            self.high_score = self.credits
                        xp_base = self.payout if self.payout > 0 else 10
                        self.award_xp_for_action(xp_base)
                        self.phase = 'result'

                elif self.phase == 'result':
                    key = input_handler.get_safe_key()
                    if key is None:
                        time.sleep(0.05)
                        continue
                    if key and self._save_and_quit(key.lower()):
                        break
                    if key:
                        if self.hand_result == 'royal_flush':
                            self.unlock_achievement("poker_royal", "Royal Flush!")
                        if self.total_won >= 500:
                            self.unlock_achievement("poker_500", "Poker High Roller")
                        if self.credits >= 1000:
                            self.unlock_achievement("poker_1000", "Poker Millionaire")
                        self.end_timer()
                        final_stats = self.get_final_stats()
                        final_stats['high_score'] = self.high_score
                        final_stats['credits'] = self.credits
                        final_stats['total_won'] = self.total_won
                        self.save_stats(final_stats)
                        self.start_timer()
                        if self.credits <= 0:
                            self.credits = 100
                        self.setup_round()
                        self.bet = 1

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            stats = self.get_final_stats()
            stats['high_score'] = self.high_score
            stats['credits'] = self.credits
            self.save_stats(stats)
            return stats


def play_poker(difficulty: str = 'normal') -> dict:
    game = PokerGame(difficulty)
    return game.play()
