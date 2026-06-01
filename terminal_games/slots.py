import logging
import random
import time
from typing import List, Tuple

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

SYMBOLS: List[str] = ["CHR", "LEM", "BEL", "STA", "DIA", "SEV"]
SYMBOL_DISPLAY: List[str] = ["Cherry", "Lemon", "Bell", "Star", "Diamond", "Seven"]

PAYOUTS: List[int] = [2, 3, 10, 25, 50, 100]

SYMBOL_COLORS: List[str] = [C_RED, C_YELLOW, C_CYAN, C_GREEN, C_MAGENTA, C_WHITE]

STARTING_COINS = 100
BET_OPTIONS = [1, 5, 10, 25]


class SlotsGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('slots', difficulty)
        self.coins = STARTING_COINS
        self.bet_index = 0
        self.spins = 0
        self.wins = 0
        self.biggest_win = 0
        self.reels: List[str] = ["", "", ""]
        self.input_handler = get_safe_input_handler()

    @property
    def bet(self) -> int:
        return BET_OPTIONS[self.bet_index]

    def spin(self) -> Tuple[int, str]:
        if self.coins < self.bet:
            return 0, ""

        self.coins -= self.bet
        self.spins += 1

        self.reels = [random.choice(SYMBOLS) for _ in range(3)]

        if self.reels[0] == self.reels[1] == self.reels[2]:
            idx = SYMBOLS.index(self.reels[0])
            multiplier = PAYOUTS[idx]
            winnings = self.bet * multiplier
            self.coins += winnings
            self.wins += 1
            if winnings > self.biggest_win:
                self.biggest_win = winnings

            xp_base = multiplier * 2
            self.award_xp_for_action(xp_base)

            if multiplier >= 100:
                beep("win")
                return winnings, "JACKPOT"
            return winnings, "WIN"

        return 0, "LOSE"

    def render_reel(self, symbol: str) -> str:
        if not symbol:
            return "???"
        idx = SYMBOLS.index(symbol)
        color = SYMBOL_COLORS[idx]
        return f"{color}{symbol}{C_RESET}"

    def render_game(self) -> None:
        clear_screen()
        print("\n" * 1)

        reel_line = " | ".join(self.render_reel(s) for s in self.reels)
        lines = [
            f"{C_YELLOW}Coins:{C_RESET}  {C_WHITE}{self.coins}{C_RESET}",
            f"{C_YELLOW}Bet:{C_RESET}    {self.bet}",
            "",
            f"  {C_CYAN}+---+---+---+{C_RESET}",
            f"  {C_CYAN}|{C_RESET} {reel_line} {C_CYAN}|{C_RESET}",
            f"  {C_CYAN}+---+---+---+{C_RESET}",
            "",
            f"{C_CYAN}Spins:{C_RESET} {self.spins}  {C_GREEN}Wins:{C_RESET} {self.wins}  "
            f"{C_MAGENTA}Biggest:{C_RESET} {self.biggest_win}",
            "",
            f"{C_YELLOW}[SPACE/ENTER] Spin  [B] Bet  [Q] Quit{C_RESET}",
        ]

        draw_retro_box(38, "SLOT MACHINE", lines, color=C_MAGENTA)

    def show_paytable(self) -> None:
        lines = []
        for i, sym in enumerate(SYMBOL_DISPLAY):
            color = SYMBOL_COLORS[i]
            lines.append(f"  {color}{sym}{C_RESET}  x{PAYOUTS[i]}")
        lines.append("")
        lines.append(f"{C_YELLOW}3 matching symbols = payout x bet{C_RESET}")
        draw_retro_box(36, "PAY TABLE", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()

    def show_result(self, winnings: int, result: str) -> None:
        if result == "JACKPOT":
            show_popup(f"{C_YELLOW}*** JACKPOT! ***{C_RESET}  +{winnings} coins!",
                       delay=1.5)
        elif result == "WIN":
            show_popup(f"{C_GREEN}YOU WIN!{C_RESET}  +{winnings} coins", delay=0.8)
        else:
            show_popup(f"{C_RED}No luck!{C_RESET}", delay=0.5)

    def select_bet(self) -> bool:
        selection = self.bet_index
        while True:
            clear_screen()
            print("\n" * 2)
            lines = [f"{C_WHITE}Current coins: {C_YELLOW}{self.coins}{C_RESET}", ""]
            for i, b in enumerate(BET_OPTIONS):
                if i == selection:
                    lines.append(f"  {C_GREEN}> {b}{C_RESET}")
                else:
                    lines.append(f"    {b}")
            lines += [
                "",
                f"{C_YELLOW}↑↓ Change  ENTER Select  Q Back{C_RESET}",
            ]
            draw_retro_box(28, "BET AMOUNT", lines, color=C_CYAN)

            key = self.input_handler.get_safe_key()
            if key == 'up':
                selection = (selection - 1) % len(BET_OPTIONS)
                beep("move")
            elif key == 'down':
                selection = (selection + 1) % len(BET_OPTIONS)
                beep("move")
            elif key in ['\r', '\n', ' ']:
                self.bet_index = selection
                beep("correct")
                return True
            elif key and key.lower() == 'q':
                return False
            time.sleep(0.05)

    def play(self) -> dict:
        self.start_timer()
        self.renderer.hide_cursor()

        try:
            while not self.game_over:
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

                if key in ['\r', '\n', ' ']:
                    if self.coins < self.bet:
                        if self.coins > 0:
                            self.bet_index = 0
                        if self.coins < BET_OPTIONS[0]:
                            show_popup(f"{C_RED}OUT OF COINS!{C_RESET}  Game over.",
                                       delay=2.0)
                            self.game_over = True
                            break
                        continue

                    winnings, result = self.spin()
                    self.render_game()
                    self.show_result(winnings, result)

                elif key and key.lower() == 'b':
                    self.select_bet()

                time.sleep(0.05)

            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.coins
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
            "Classic 3-reel slot machine.",
            "",
            f"{C_CYAN}Controls:{C_RESET}",
            "  SPACE/ENTER   Spin the reels",
            "  B             Change bet amount",
            "  Q             Quit",
            "  P             Pause",
            "  ?             Show this help",
            "",
            f"{C_CYAN}Rules:{C_RESET}",
            "  Match 3 symbols to win!",
            "  Higher bets = higher payouts.",
            "  Run out of coins = game over.",
        ]
        draw_retro_box(36, "SLOTS HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_slots(difficulty: str = 'normal') -> dict:
    game = SlotsGame(difficulty)
    return game.play()
