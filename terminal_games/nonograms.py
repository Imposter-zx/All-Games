import logging
import time
from typing import Dict, List, Tuple

from arcade_utils import (
    C_CYAN,
    C_GREEN,
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

PUZZLES = [
    {
        "name": "Heart",
        "size": 5,
        "data": [
            [0, 1, 0, 1, 0],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0],
        ],
    },
    {
        "name": "Star",
        "size": 7,
        "data": [
            [0, 0, 1, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 1, 0],
            [1, 1, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0],
        ],
    },
    {
        "name": "Cat",
        "size": 10,
        "data": [
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
    },
    {
        "name": "House",
        "size": 10,
        "data": [
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
    },
]


def get_clues(data: List[List[int]]) -> Tuple[List[List[int]], List[List[int]]]:
    rows = []
    for row in data:
        clues = []
        count = 0
        for cell in row:
            if cell:
                count += 1
            else:
                if count:
                    clues.append(count)
                    count = 0
        if count:
            clues.append(count)
        rows.append(clues if clues else [0])
    cols = []
    for c in range(len(data[0])):
        clues = []
        count = 0
        for r in range(len(data)):
            if data[r][c]:
                count += 1
            else:
                if count:
                    clues.append(count)
                    count = 0
        if count:
            clues.append(count)
        cols.append(clues if clues else [0])
    return rows, cols


class NonogramsGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('nonograms', difficulty)
        if difficulty == 'easy':
            self.puzzle = PUZZLES[0]
        elif difficulty == 'hard':
            self.puzzle = PUZZLES[3]
        else:
            self.puzzle = PUZZLES[1]
        self.size = self.puzzle['size']
        self.solution = self.puzzle['data']
        self.player: List[List[int]] = [[0] * self.size for _ in range(self.size)]
        self.row_clues, self.col_clues = get_clues(self.solution)
        self.cursor_row = 0
        self.cursor_col = 0
        self.mistakes = 0
        self.solved = False
        self.high_score = 0

    def _is_solved(self) -> bool:
        return self.player == self.solution

    def _render(self) -> None:
        lines = [
            f"{C_CYAN}{self.puzzle['name']} ({self.size}x{self.size})  "
            f"DIFFICULTY: {self.difficulty.upper()}  Mistakes: {self.mistakes}{C_RESET}",
        ]
        draw_retro_box(40, "\u25A0 NONOGRAMS \u25A0", lines, color=C_CYAN)

        max_clue_len = max(len(c) for c in self.col_clues)
        print()
        for i in range(max_clue_len):
            print("     ", end="")
            for c in range(self.size):
                clue_idx = i - (max_clue_len - len(self.col_clues[c]))
                if 0 <= clue_idx < len(self.col_clues[c]):
                    print(f"{self.col_clues[c][clue_idx]:>2}", end="")
                else:
                    print("  ", end="")
            print()

        print("     ", end="")
        for c in range(self.size):
            print(f"{c + 1:>2}", end="")
        print()

        for r in range(self.size):
            clue_str = " ".join(str(x) for x in self.row_clues[r])
            print(f" {clue_str:>5} ", end="")
            for c in range(self.size):
                if r == self.cursor_row and c == self.cursor_col:
                    bg = "\033[47m"
                    fg = "\033[30m"
                else:
                    bg = ""
                    fg = C_WHITE
                if self.player[r][c]:
                    print(f"{bg}{fg}\u2588\u2588{C_RESET}", end="")
                else:
                    print(f"{bg}{C_WHITE}\u00B7\u00B7{C_RESET}", end="")
            print(f" {clue_str:>5}")

        print("     ", end="")
        for c in range(self.size):
            print(f"{c + 1:>2}", end="")
        print()

        if self.solved:
            print(f"\n{C_GREEN}SOLVED!{C_RESET}")
        else:
            print(f"\n{C_WHITE}[Arrows] Move  [Space] Fill  [X] Mark  [V] Verify  [Q] Quit  [?] Help{C_RESET}")

    def _show_help(self) -> None:
        show_popup(
            "NONOGRAMS: Fill cells to reveal a hidden picture! "
            "Numbers at edges show consecutive filled blocks per row/column. "
            "Use arrow keys to move, SPACE to fill, X to mark empty. "
            "Press V to verify your solution.",
            C_CYAN, delay=2.5
        )

    def play(self) -> Dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 1)
                self._render()

                if self.solved:
                    self.score = max(100 - self.mistakes * 5, 10) * (self.size // 2)
                    if self.score > self.high_score:
                        self.high_score = self.score
                    self.award_xp_for_action(self.score)
                    if self.mistakes == 0:
                        self.unlock_achievement("nonograms_perfect", "Perfect Picross")
                    self.end_timer()
                    final_stats = self.get_final_stats()
                    final_stats['high_score'] = self.high_score
                    self.save_stats(final_stats)
                    print(f"\n{C_WHITE}[Any Key] Next Puzzle  [Q] Quit{C_RESET}")
                    key = input_handler.get_safe_key()
                    if key and self._save_and_quit(key.lower()):
                        break
                    if key:
                        puzzle_idx = (PUZZLES.index(self.puzzle) + 1) % len(PUZZLES)
                        self.puzzle = PUZZLES[puzzle_idx]
                        self.size = self.puzzle['size']
                        self.solution = self.puzzle['data']
                        self.player = [[0] * self.size for _ in range(self.size)]
                        self.row_clues, self.col_clues = get_clues(self.solution)
                        self.cursor_row = 0
                        self.cursor_col = 0
                        self.mistakes = 0
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
                if key == 'up':
                    self.cursor_row = max(0, self.cursor_row - 1)
                    beep("move")
                elif key == 'down':
                    self.cursor_row = min(self.size - 1, self.cursor_row + 1)
                    beep("move")
                elif key == 'left':
                    self.cursor_col = max(0, self.cursor_col - 1)
                    beep("move")
                elif key == 'right':
                    self.cursor_col = min(self.size - 1, self.cursor_col + 1)
                    beep("move")
                elif key == ' ':
                    self.player[self.cursor_row][self.cursor_col] = 1
                    if self.solution[self.cursor_row][self.cursor_col] != 1:
                        self.mistakes += 1
                        beep("lose")
                    else:
                        beep("correct")
                        if self._is_solved():
                            self.solved = True
                            beep("win")
                elif key.lower() == 'x':
                    self.player[self.cursor_row][self.cursor_col] = 0
                    beep("correct")
                elif key.lower() == 'v':
                    if self._is_solved():
                        self.solved = True
                        beep("win")
                    else:
                        self.mistakes += 1
                        beep("lose")
                        show_popup("Not correct yet — keep trying!", C_YELLOW, delay=1.0)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            stats = self.get_final_stats()
            stats['high_score'] = self.high_score
            return stats


def play_nonograms(difficulty: str = 'normal') -> dict:
    game = NonogramsGame(difficulty)
    return game.play()
