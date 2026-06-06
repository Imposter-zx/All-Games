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

SUITS = ["H", "D", "C", "S"]
SUIT_SYMS = ["♥", "♦", "♣", "♠"]
SUIT_COLORS = [C_RED, C_RED, C_WHITE, C_WHITE]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

Card = Tuple[str, int]


def card_str(card: Optional[Card], hidden: bool = False) -> str:
    if card is None:
        return "   "
    rank, suit_idx = card
    color = SUIT_COLORS[suit_idx]
    if hidden:
        return f"{C_MAGENTA}[?]{C_RESET}"
    sym = SUIT_SYMS[suit_idx] if SUIT_SYMS[suit_idx] else ["H", "D", "C", "S"][suit_idx]
    return f"{color}{rank:>2}{sym}{C_RESET}"


def card_red(card: Card) -> bool:
    return card[1] in (0, 1)


def card_rank_val(rank: str) -> int:
    return RANKS.index(rank)


class SolitaireGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('solitaire', difficulty)
        self.stock: List[Card] = []
        self.waste: List[Card] = []
        self.foundations: List[List[Card]] = [[] for _ in range(4)]
        self.tableau: List[List[Card]] = [[] for _ in range(7)]
        self.selected: Optional[str] = None
        self.selected_idx: Optional[int] = None
        self.moves = 0
        self.input_handler = get_safe_input_handler()
        self._deal()

    def _build_deck(self) -> List[Card]:
        deck = [(rank, si) for si in range(4) for rank in RANKS]
        random.shuffle(deck)
        return deck

    def _deal(self) -> None:
        deck = self._build_deck()
        idx = 0
        for col in range(7):
            for row in range(col + 1):
                self.tableau[col].append(deck[idx])
                idx += 1
        self.stock = deck[idx:]

    def is_tableau_face_up(self, col: int, row: int) -> bool:
        return row == len(self.tableau[col]) - 1

    def can_place_on_tableau(self, card: Card, col: int) -> bool:
        if not self.tableau[col]:
            return card_rank_val(card[0]) == card_rank_val("K")
        top = self.tableau[col][-1]
        diff = card_rank_val(top[0]) - card_rank_val(card[0])
        if diff != 1:
            return False
        return card_red(card) != card_red(top)

    def can_place_on_foundation(self, card: Card, col: int) -> bool:
        if not self.foundations[col]:
            return card[0] == "A"
        top = self.foundations[col][-1]
        if top[1] != card[1]:
            return False
        return card_rank_val(card[0]) - card_rank_val(top[0]) == 1

    def auto_foundation(self) -> bool:
        for fi in range(4):
            for ci in range(7):
                if not self.tableau[ci]:
                    continue
                card = self.tableau[ci][-1]
                if self.can_place_on_foundation(card, fi):
                    self.foundations[fi].append(self.tableau[ci].pop())
                    self.moves += 1
                    self.award_xp_for_action(5)
                    return True
        if self.waste:
            card = self.waste[-1]
            for fi in range(4):
                if self.can_place_on_foundation(card, fi):
                    self.foundations[fi].append(self.waste.pop())
                    self.moves += 1
                    self.award_xp_for_action(5)
                    return True
        return False

    def draw_stock(self) -> None:
        if not self.stock:
            self.stock = self.waste[::-1]
            self.waste = []
            if not self.stock:
                return
        self.waste.append(self.stock.pop())

    def move_tableau_to_tableau(self, src: int, dst: int, count: int = 1) -> bool:
        if not self.tableau[src]:
            return False
        if count > len(self.tableau[src]):
            return False
        cards = self.tableau[src][-count:]
        if not self.can_place_on_tableau(cards[0], dst):
            if not self.tableau[dst] and card_rank_val(cards[0][0]) == card_rank_val("K"):
                pass
            else:
                return False
        if not self.is_tableau_face_up(src, len(self.tableau[src]) - count):
            return False
        for card in cards:
            self.tableau[dst].append(card)
        self.tableau[src] = self.tableau[src][:-count]
        self.moves += 1
        self.award_xp_for_action(5)
        return True

    def check_win(self) -> bool:
        for fi in range(4):
            if len(self.foundations[fi]) != 13:
                return False
        return True

    def get_tableau_display(self, col: int) -> List[str]:
        result = []
        for i, card in enumerate(self.tableau[col]):
            if i == len(self.tableau[col]) - 1:
                s = card_str(card)
            else:
                s = card_str(card, hidden=True)
            result.append(s)
        return result

    def render_game(self) -> None:
        clear_screen()
        print("\n" * 1)

        stock_str = card_str(self.stock[-1] if self.stock else None,
                             hidden=bool(self.stock))
        waste_str = card_str(self.waste[-1] if self.waste else None)

        found_strs = []
        for fi in range(4):
            if self.foundations[fi]:
                found_strs.append(card_str(self.foundations[fi][-1]))
            else:
                found_strs.append(f" {C_CYAN}[ ]{C_RESET}")

        max_rows = max((len(t) for t in self.tableau), default=0)

        lines = [
            f"{C_YELLOW}Moves:{C_RESET} {self.moves}  "
            f"{C_CYAN}Stock:{C_RESET} {len(self.stock)}",
            "",
            f"  {C_WHITE}STOCK:{C_RESET} {stock_str}   "
            f"{C_WHITE}WASTE:{C_RESET} {waste_str}   "
            f"  {'  '.join(found_strs)}",
            "",
            f"  {C_CYAN}1{C_RESET}    {C_CYAN}2{C_RESET}    {C_CYAN}3{C_RESET}    "
            f"{C_CYAN}4{C_RESET}    {C_CYAN}5{C_RESET}    {C_CYAN}6{C_RESET}    {C_CYAN}7{C_RESET}",
        ]

        for row in range(max_rows):
            row_parts = []
            for col in range(7):
                t_len = len(self.tableau[col])
                if row < t_len:
                    card = self.tableau[col][row]
                    if row == t_len - 1:
                        s = card_str(card)
                    else:
                        s = card_str(card, hidden=True)
                else:
                    s = "    "
                row_parts.append(s)
            lines.append("  " + "  ".join(row_parts))

        if self.selected == "tableau":
            lines += [
                "",
                f"{C_YELLOW}Source: Tableau {self.selected_idx + 1}  "
                f"Select destination (1-7=F,T=F,F1-4={C_RESET}"
            ]
        elif self.selected == "waste":
            lines += [
                "",
                f"{C_YELLOW}Source: Waste  "
                f"Select destination (1-7=F,T=F,F1-4={C_RESET}",
            ]

        footer = f"{C_YELLOW}D=Draw  "
        if self.waste:
            footer += "W+1-7=Waste  "
        footer += f"1-7=Select  F=Foundation  Q=Quit{C_RESET}"

        draw_retro_box(46, "SOLITAIRE", lines, color=C_CYAN)
        print(f"\n  {footer}")

    def _handle_tableau_select(self, col: int) -> None:
        if self.selected is None:
            if self.tableau[col]:
                self.selected = "tableau"
                self.selected_idx = col
                beep("correct")
        elif self.selected == "tableau":
            src = self.selected_idx
            if src is not None and src != col:
                if self.move_tableau_to_tableau(src, col):
                    beep("win")
                else:
                    beep("wrong")
            self.selected = None
            self.selected_idx = None
        elif self.selected == "waste":
            self.selected = None
            self.selected_idx = None
            if self.waste:
                card = self.waste[-1]
                if self.can_place_on_tableau(card, col):
                    self.tableau[col].append(self.waste.pop())
                    self.moves += 1
                    self.award_xp_for_action(5)
                    beep("win")
                else:
                    beep("wrong")

    def _send_to_foundation(self, src: str, idx: Optional[int] = None) -> None:
        if src == "tableau" and idx is not None:
            if self.tableau[idx]:
                card = self.tableau[idx][-1]
                for fi in range(4):
                    if self.can_place_on_foundation(card, fi):
                        self.foundations[fi].append(self.tableau[idx].pop())
                        self.moves += 1
                        self.award_xp_for_action(10)
                        beep("win")
                        return
        elif src == "waste":
            if self.waste:
                card = self.waste[-1]
                for fi in range(4):
                    if self.can_place_on_foundation(card, fi):
                        self.foundations[fi].append(self.waste.pop())
                        self.moves += 1
                        self.award_xp_for_action(10)
                        beep("win")
                        return
        beep("wrong")

    def play(self) -> dict:
        self.start_timer()
        self.renderer.hide_cursor()

        try:
            while not self.game_over:
                while self.auto_foundation():
                    pass
                if self.check_win():
                    self.award_xp_for_action(200)
                    self.end_timer()
                    clear_screen()
                    show_popup(f"{C_GREEN}YOU WIN! ALL FOUNDATIONS COMPLETE!{C_RESET}",
                               delay=2.0)
                    break

                self.render_game()
                key = self.input_handler.get_safe_key()

                if key and self._save_and_quit(key.lower()):
                    break
                if key == '?':
                    self._show_help()
                    continue
                if key == 'p':
                    self._pause_game()
                    continue

                if key and key.lower() == 'd':
                    self.draw_stock()
                    beep("move")
                    self.selected = None
                    self.selected_idx = None

                elif key and key.lower() == 'w':
                    if self.waste:
                        if self.selected is None:
                            self.selected = "waste"
                            beep("correct")
                        elif self.selected == "waste":
                            self.selected = None
                    else:
                        beep("wrong")

                elif key == 'f':
                    if self.selected == "tableau" and self.selected_idx is not None:
                        self._send_to_foundation("tableau", self.selected_idx)
                    elif self.selected == "waste":
                        self._send_to_foundation("waste")
                    self.selected = None
                    self.selected_idx = None

                elif key in ('1', '2', '3', '4', '5', '6', '7'):
                    col = int(key) - 1
                    self._handle_tableau_select(col)

                time.sleep(0.05)

            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.moves
            self.save_stats(final_stats)
            return final_stats

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            self.renderer.show_cursor()
            return self.get_final_stats()

    def _show_help(self) -> None:
        lines = [
            "Build all 4 foundations by suit",
            "from Ace to King to win!",
            "",
            f"{C_CYAN}Tableau rules:{C_RESET}",
            "  Build DOWN alternating colors",
            "  Move sequences of face-up cards",
            "  Empty column = place any King",
            "",
            f"{C_CYAN}Controls:{C_RESET}",
            "  D          Draw from stock",
            "  1-7        Select/deselect tableau",
            "  W          Select waste as source",
            "  F          Send to foundation",
            "  Q          Quit",
            "  P          Pause",
        ]
        draw_retro_box(36, "SOLITAIRE HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_solitaire(difficulty: str = 'normal') -> dict:
    game = SolitaireGame(difficulty)
    return game.play()
