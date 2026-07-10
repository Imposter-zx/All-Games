import logging
import random
import time
from typing import Dict, List, Tuple

from arcade_utils import (
    C_BLUE,
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

COLORS = [
    (C_RED, "\u25CF"),
    (C_GREEN, "\u25CF"),
    (C_BLUE, "\u25CF"),
    (C_YELLOW, "\u25CF"),
    (C_MAGENTA, "\u25CF"),
    (C_CYAN, "\u25CF"),
]
COLOR_NAMES = ["Red", "Green", "Blue", "Yellow", "Magenta", "Cyan"]
COLOR_LETTERS = ['R', 'G', 'B', 'Y', 'M', 'C']


def color_block(color_idx: int) -> str:
    c, sym = COLORS[color_idx]
    return f"{c}{sym}{C_RESET}"


def color_name(color_idx: int) -> str:
    return COLOR_NAMES[color_idx]


class MastermindGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('mastermind', difficulty)
        if difficulty == 'easy':
            self.num_colors = 6
            self.max_tries = 12
        elif difficulty == 'hard':
            self.num_colors = 8
            self.max_tries = 8
        else:
            self.num_colors = 6
            self.max_tries = 10
        self.code_length = 4
        self.secret: List[int] = []
        self.guesses: List[List[int]] = []
        self.feedbacks: List[Tuple[int, int]] = []
        self.try_count = 0
        self.solved = False
        self.high_score = 0

    def generate_secret(self) -> None:
        self.secret = [random.randrange(self.num_colors) for _ in range(self.code_length)]

    def evaluate_guess(self, guess: List[int]) -> Tuple[int, int]:
        exact = sum(1 for i in range(self.code_length) if guess[i] == self.secret[i])
        secret_counts = {}
        guess_counts = {}
        for i in range(self.code_length):
            if guess[i] != self.secret[i]:
                secret_counts[self.secret[i]] = secret_counts.get(self.secret[i], 0) + 1
                guess_counts[guess[i]] = guess_counts.get(guess[i], 0) + 1
        color_only = 0
        for c, cnt in guess_counts.items():
            color_only += min(cnt, secret_counts.get(c, 0))
        return (exact, color_only)

    def show_board(self) -> None:
        lines = [
            f"{C_YELLOW}COLORS:{C_RESET}",
            " ".join(f"{i + 1}={color_block(i)}" for i in range(min(6, self.num_colors))),
            "" if self.num_colors <= 6
            else " ".join(f"{i + 1}={color_name(i)}" for i in range(6, self.num_colors)),
            f"{C_CYAN}TRIES: {self.try_count}/{self.max_tries}{C_RESET}",
        ]
        draw_retro_box(40, "\u25CB MASTERMIND \u25CF", lines, color=C_MAGENTA)

        if self.guesses:
            print(f"\n{C_WHITE}  Guess  | Code    | Exact | Color{C_RESET}")
            print(f"  {'-' * 35}")
            for i, (guess, (exact, color)) in enumerate(zip(self.guesses, self.feedbacks)):
                g_display = " ".join(color_block(c) for c in guess)
                marker = f"{C_GREEN}\u2713{C_RESET}" if exact == self.code_length else ""
                print(f"  #{i + 1:<3}  | {g_display} |  {exact}   |  {color}   {marker}")

        if self.solved:
            print(f"\n{C_GREEN}SOLVED! You cracked the code in {self.try_count} tries!{C_RESET}")
        elif self.try_count >= self.max_tries:
            secret_display = " ".join(color_block(c) for c in self.secret)
            print(f"\n{C_RED}Out of tries! The code was: {secret_display}{C_RESET}")

        if not self.solved and self.try_count < self.max_tries:
            print(f"\n{C_WHITE}Enter 4 colors (e.g. 1234)  [Q] Quit  [?] Help{C_RESET}")

    def _show_help(self) -> None:
        show_popup(
            "MASTERMIND: Guess the secret 4-color code! "
            "Enter 4 numbers (1-6 or 1-8 on hard). "
            "After each guess, Exact = correct color+position, "
            "Color = correct color wrong position. "
            "Crack the code before running out of tries!",
            C_YELLOW, delay=2.5
        )

    def play(self) -> Dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        else:
            self.generate_secret()
        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 2)
                self.show_board()

                if self.solved or self.try_count >= self.max_tries:
                    if self.solved:
                        self.score = (self.max_tries - self.try_count + 1) * 50
                        if self.score > self.high_score:
                            self.high_score = self.score
                        self.award_xp_for_action(self.score)
                        if self.try_count == 1:
                            self.unlock_achievement("mastermind_perfect", "Perfect Mind!")
                        if self.try_count <= 3:
                            self.unlock_achievement("mastermind_quick", "Quick Thinker")
                    self.end_timer()
                    final_stats = self.get_final_stats()
                    final_stats['high_score'] = self.high_score
                    self.save_stats(final_stats)
                    print(f"\n{C_WHITE}[Any Key] Play Again  [Q] Quit{C_RESET}")
                    key = input_handler.get_safe_key()
                    if key and self._save_and_quit(key.lower()):
                        break
                    if key:
                        self.generate_secret()
                        self.guesses = []
                        self.feedbacks = []
                        self.try_count = 0
                        self.solved = False
                        self.start_timer()
                    continue

                key = input_handler.get_safe_key()
                if key is None:
                    time.sleep(0.05)
                    continue

                if key == '?':
                    self._show_help()
                    continue

                if self._save_and_quit(key.lower()):
                    break

                if len(key) == self.code_length and key.isdigit():
                    guess = [int(ch) - 1 for ch in key]
                    if all(0 <= c < self.num_colors for c in guess):
                        self.try_count += 1
                        exact, color = self.evaluate_guess(guess)
                        self.guesses.append(guess)
                        self.feedbacks.append((exact, color))
                        if exact == self.code_length:
                            self.solved = True
                            beep("win")
                        else:
                            beep("correct")
                        if self.try_count % 3 == 0 and not self.solved:
                            self.award_xp_for_action(5)
                    else:
                        beep("lose")

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            stats = self.get_final_stats()
            stats['high_score'] = self.high_score
            self.save_stats(stats)
            return stats


def play_mastermind(difficulty: str = 'normal') -> dict:
    game = MastermindGame(difficulty)
    return game.play()
