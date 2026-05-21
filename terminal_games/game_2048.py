"""
2048 Game implementation for the Retro Arcade.
Merge tiles with the same numbers to reach 2048.
"""

import logging
import random
import time
from typing import List, Dict, Any

from arcade_utils import (
    C_WHITE, C_YELLOW, C_CYAN, C_GREEN, C_MAGENTA, C_RED, C_BLUE,
    C_BOLD, C_RESET, draw_retro_box, beep, u_safe
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)


class Game2048(BaseGame):
    """2048 Game logic and rendering."""

    TILE_COLORS: Dict[int, str] = {
        0: C_WHITE, 2: C_WHITE, 4: C_YELLOW, 8: C_CYAN, 16: C_MAGENTA,
        32: C_RED, 64: C_GREEN, 128: C_BLUE, 256: C_YELLOW + C_BOLD,
        512: C_CYAN + C_BOLD, 1024: C_MAGENTA + C_BOLD,
        2048: C_GREEN + C_BOLD, 4096: C_RED + C_BOLD,
    }

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('2048', difficulty)
        self.grid: List[List[int]] = [[0] * 4 for _ in range(4)]
        self.grid_size = 4
        self.four_chance = 0.1

        if difficulty == 'easy':
            self.four_chance = 0.05
        elif difficulty == 'hard':
            self.four_chance = 0.25

        self.spawn_tile()
        self.spawn_tile()
        self.high_tile = 2
        self.moves = 0

    def spawn_tile(self) -> bool:
        empty_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if self.grid[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.grid[r][c] = 4 if random.random() < self.four_chance else 2
            return True
        return False

    def compress(self, row: List[int]) -> List[int]:
        new_row = [i for i in row if i != 0]
        new_row += [0] * (len(row) - len(new_row))
        return new_row

    def merge(self, row: List[int]) -> tuple:
        score_gain = 0
        for i in range(len(row) - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                row[i + 1] = 0
                score_gain += row[i]
                if row[i] > self.high_tile:
                    self.high_tile = row[i]
        return row, score_gain

    def move_left(self) -> tuple:
        moved = False
        total_score_gain = 0
        for i in range(self.grid_size):
            old_row = list(self.grid[i])
            row = self.compress(self.grid[i])
            row, gain = self.merge(row)
            row = self.compress(row)
            self.grid[i] = row
            if old_row != self.grid[i]:
                moved = True
                total_score_gain += gain
        return moved, total_score_gain

    def rotate_grid(self) -> None:
        self.grid = [list(row) for row in zip(*self.grid[::-1])]

    def move(self, direction: str) -> bool:
        rotations_map = {'left': 0, 'up': 3, 'right': 2, 'down': 1}
        for _ in range(rotations_map[direction]):
            self.rotate_grid()

        moved, gain = self.move_left()

        for _ in range((4 - rotations_map[direction]) % 4):
            self.rotate_grid()

        if moved:
            self.score += gain
            self.award_xp_for_action(gain)
            self.spawn_tile()
            self.moves += 1
            beep("move")

            if self.high_tile >= 2048:
                self.unlock_achievement("2048_master", "2048 Master")
            elif self.high_tile >= 1024:
                self.unlock_achievement("2048_expert", "1024 Expert")
            elif self.high_tile >= 512:
                self.unlock_achievement("2048_rookie", "512 Rookie")

        return moved

    def is_game_over(self) -> bool:
        if any(0 in row for row in self.grid):
            return False
        for r in range(self.grid_size):
            for c in range(self.grid_size - 1):
                if self.grid[r][c] == self.grid[r][c + 1]:
                    return False
        for r in range(self.grid_size - 1):
            for c in range(self.grid_size):
                if self.grid[r][c] == self.grid[r + 1][c]:
                    return False
        return True

    def render(self) -> None:
        lines: list[str] = []
        lines.append(f" SCORE: {C_YELLOW}{self.score}{C_RESET}  |  BEST TILE: {C_GREEN}{self.high_tile}{C_RESET}")
        lines.append(f" MOVES: {self.moves}  |  DIFFICULTY: {self.difficulty.upper()}")
        lines.append("─" * 30)

        for row in self.grid:
            row_str = " "
            for val in row:
                color = self.TILE_COLORS.get(val, C_WHITE)
                if val == 0:
                    row_str += f"{C_WHITE}[      ]{C_RESET} "
                else:
                    row_str += f"{color}[{val:^6}]{C_RESET} "
            lines.append(row_str)
            lines.append("")

        draw_retro_box(40, f"{u_safe('🔢', '#')} 2048 ARCADE", lines, color=C_CYAN)
        print(f"\n{C_WHITE}   [ARROWS] Move  [Q] Quit  [H] Help{C_RESET}")

    def _show_help(self) -> None:
        show_popup("2048: Use ARROWS to slide tiles. Same tiles merge. Reach 2048 to win!", C_CYAN, delay=1.5)

    def play(self) -> dict:
        self.start_timer()
        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                self.renderer.render_frame(self.render)

                direction = input_handler.get_direction()
                if direction:
                    self.move(direction)
                    if self.is_game_over():
                        self.game_over = True
                        beep("lose")
                        time.sleep(1)

                key = input_handler.get_safe_key()
                if key and key.lower() == 'q':
                    break
                if key and key.lower() == 'h':
                    self._show_help()

                time.sleep(0.01)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            self.save_stats(final_stats)
            return final_stats


def play_2048(difficulty: str = 'normal') -> dict:
    """Entry point for the 2048 game."""
    game = Game2048(difficulty)
    return game.play()


if __name__ == "__main__":
    play_2048()
