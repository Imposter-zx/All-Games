import logging
import random
import time
from typing import List, Tuple

from arcade_utils import (
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    beep,
    clear_screen,
    draw_retro_box,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

SYMBOLS: List[str] = [
    "A", "B", "C", "D", "E", "F", "G", "H",
    "I", "J", "K", "L", "M", "N", "O", "P",
    "Q", "R", "S", "T",
]

GRID_CONFIGS = {
    "easy":   {"rows": 3, "cols": 4},
    "normal": {"rows": 4, "cols": 4},
    "hard":   {"rows": 4, "cols": 5},
}

DIFFICULTY_LABELS = {"easy": "4x3 (6 pairs)", "normal": "4x4 (8 pairs)", "hard": "4x5 (10 pairs)"}


class MemoryGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('memory', difficulty)
        config = GRID_CONFIGS.get(difficulty, GRID_CONFIGS["normal"])
        self.rows = config["rows"]
        self.cols = config["cols"]
        self.total_cards = self.rows * self.cols
        self.num_pairs = self.total_cards // 2

        self.grid: List[List[str]] = []
        self.revealed: List[List[bool]] = []
        self.matched: List[List[bool]] = []
        self._build_grid()

        self.cursor_row = 0
        self.cursor_col = 0
        self.selected: List[Tuple[int, int]] = []
        self.attempts = 0
        self.matches = 0
        self.streak = 0
        self.best_streak = 0
        self.input_handler = get_safe_input_handler()

    def _build_grid(self) -> None:
        pairs_available = SYMBOLS[:self.num_pairs]
        cards = pairs_available * 2
        random.shuffle(cards)

        self.grid = []
        self.revealed = []
        self.matched = []
        idx = 0
        for _ in range(self.rows):
            row_cards = cards[idx:idx + self.cols]
            self.grid.append(row_cards)
            self.revealed.append([False] * self.cols)
            self.matched.append([False] * self.cols)
            idx += self.cols

    def render_game(self) -> None:
        clear_screen()
        print("\n" * 1)

        lines = [
            f"{C_YELLOW}Matches:{C_RESET} {self.matches}/{self.num_pairs}  "
            f"{C_CYAN}Attempts:{C_RESET} {self.attempts}  "
            f"{C_GREEN}Streak:{C_RESET} {self.streak}",
            "",
        ]

        header = "   " + " ".join(f" {C_CYAN}{c+1}{C_RESET} " for c in range(self.cols))
        lines.append(header)

        for r in range(self.rows):
            row_display = [f"{C_CYAN}{r+1}{C_RESET} "]
            for c in range(self.cols):
                if self.matched[r][c]:
                    cell = f" {C_GREEN}{self.grid[r][c]}{C_RESET} "
                elif self.revealed[r][c]:
                    cell = f" {C_YELLOW}{self.grid[r][c]}{C_RESET} "
                else:
                    cell = f" {C_MAGENTA}?{C_RESET} "

                if (r, c) == (self.cursor_row, self.cursor_col):
                    if self.matched[r][c]:
                        cell = f"[{C_GREEN}{self.grid[r][c]}{C_RESET}]"
                    elif self.revealed[r][c]:
                        cell = f"[{C_YELLOW}{self.grid[r][c]}{C_RESET}]"
                    else:
                        cell = f"[{C_WHITE}?{C_RESET}]"

                row_display.append(cell)
            lines.append(" ".join(row_display))

        lines += [
            "",
            f"{C_YELLOW}←↑→↓ Navigate  SPACE Flip  Q Quit{C_RESET}",
        ]

        draw_retro_box(12 + self.cols * 4, "MEMORY", lines, color=C_CYAN)

    def flip_card(self, r: int, c: int) -> None:
        if self.matched[r][c] or self.revealed[r][c]:
            return
        if (r, c) in self.selected:
            return

        self.revealed[r][c] = True
        self.selected.append((r, c))
        beep("correct")

        if len(self.selected) == 2:
            self.attempts += 1
            (r1, c1), (r2, c2) = self.selected

            if self.grid[r1][c1] == self.grid[r2][c2]:
                self.matched[r1][c1] = True
                self.matched[r2][c2] = True
                self.matches += 1
                self.streak += 1
                if self.streak > self.best_streak:
                    self.best_streak = self.streak
                self.award_xp_for_action(20)
                beep("win")

                if self.matches == self.num_pairs:
                    bonus = max(0, self.num_pairs * 10 - self.attempts)
                    if bonus > 0:
                        self.award_xp_for_action(bonus)
                    self.game_over = True
            else:
                self.streak = 0

    def hide_selected(self) -> None:
        for r, c in self.selected:
            if not self.matched[r][c]:
                self.revealed[r][c] = False
        self.selected = []

    def play(self) -> dict:
        self.start_timer()
        self.renderer.hide_cursor()

        try:
            while not self.game_over:
                self.render_game()

                key = self.input_handler.get_safe_key()

                if key and self._save_and_quit(key.lower()):
                    self.hide_selected()
                    break
                if key == '?':
                    self._show_help()
                    continue
                if key == 'p':
                    self._pause_game()
                    continue

                handled = False
                if key == 'up' or key == 'w':
                    self.cursor_row = (self.cursor_row - 1) % self.rows
                    handled = True
                elif key == 'down' or key == 's':
                    self.cursor_row = (self.cursor_row + 1) % self.rows
                    handled = True
                elif key == 'left' or key == 'a':
                    self.cursor_col = (self.cursor_col - 1) % self.cols
                    handled = True
                elif key == 'right' or key == 'd':
                    self.cursor_col = (self.cursor_col + 1) % self.cols
                    handled = True

                if handled:
                    beep("move")
                    time.sleep(0.05)
                    continue

                if key in ['\r', '\n', ' ']:
                    if len(self.selected) >= 2:
                        self.hide_selected()
                    r, c = self.cursor_row, self.cursor_col
                    self.flip_card(r, c)

                if self.matches == self.num_pairs:
                    self.end_timer()
                    self.render_game()
                    self.show_summary()
                    break

                time.sleep(0.05)

            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.matches
            self.save_stats(final_stats)
            return final_stats

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            self.renderer.show_cursor()
            return self.get_final_stats()

    def show_summary(self) -> None:
        clear_screen()
        print("\n" * 2)
        lines = [
            f"{C_GREEN}All pairs matched!{C_RESET}",
            "",
            f"{C_WHITE}Grid:{C_RESET}     {self.rows}x{self.cols} ({self.num_pairs} pairs)",
            f"{C_WHITE}Attempts:{C_RESET}  {self.attempts}",
            f"{C_WHITE}Best Streak:{C_RESET} {self.best_streak}",
            f"{C_WHITE}Score:{C_RESET}     {C_YELLOW}{self.score}{C_RESET}",
            f"{C_WHITE}XP Earned:{C_RESET} {C_MAGENTA}{self.xp_earned}{C_RESET}",
        ]
        draw_retro_box(36, "YOU WIN!", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()

    def _show_help(self) -> None:
        lines = [
            "Flip cards to find matching pairs!",
            "",
            f"{C_CYAN}Controls:{C_RESET}",
            "  ARROWS/WASD  Move cursor",
            "  SPACE/ENTER  Flip selected card",
            "  Q            Quit (saves progress)",
            "  P            Pause",
            "  ?            Show this help",
            "",
            f"{C_CYAN}Grid sizes:{C_RESET}",
            "  Easy:   4x3  (6 pairs)",
            "  Normal: 4x4  (8 pairs)",
            "  Hard:   4x5  (10 pairs)",
            "",
            f"{C_CYAN}Scoring:{C_RESET}",
            "  +20 XP per match",
            "  Bonus XP for finishing with fewer attempts",
            "  Difficulty multiplier applies",
        ]
        draw_retro_box(36, "MEMORY HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_memory(difficulty: str = 'normal') -> dict:
    game = MemoryGame(difficulty)
    return game.play()
