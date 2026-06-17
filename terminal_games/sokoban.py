import logging
import time
from copy import deepcopy
from typing import Dict, List, Tuple

from arcade_utils import (
    C_CYAN,
    C_GREEN,
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

LEVELS = [
    {
        "name": "Beginner",
        "map": [
            "  ####  ",
            "###  ###",
            "#   $  #",
            "# #  # #",
            "# . .  #",
            "#  $  ##",
            "## @ ## ",
            " ####   ",
        ],
    },
    {
        "name": "Crate",
        "map": [
            "  ####  ",
            "  #  #  ",
            "  #  #  ",
            "###  ###",
            "#  $   #",
            "# .$.  #",
            "## @ ##",
            " ####   ",
        ],
    },
    {
        "name": "Tricky",
        "map": [
            " ##### ",
            "##   ##",
            "# $ $ #",
            "# . . #",
            "#  $  #",
            "## @ ##",
            " ##### ",
        ],
    },
    {
        "name": "Puzzle",
        "map": [
            "  ####  ",
            "  #  #  ",
            "###  ###",
            "#  ..  #",
            "# $$   #",
            "##  # ##",
            " # @ # ",
            "  ###  ",
        ],
    },
    {
        "name": "Expert",
        "map": [
            "  ##### ",
            "###   ##",
            "#  $   #",
            "# . $. #",
            "# .  $ #",
            "##    ##",
            " # @ #  ",
            "  ###   ",
        ],
    },
]

WALL = '#'
FLOOR = ' '
BOX = '$'
TARGET = '.'
PLAYER = '@'
BOX_ON_TARGET = '*'
PLAYER_ON_TARGET = '+'

DIRS = {
    'up': (-1, 0),
    'down': (1, 0),
    'left': (0, -1),
    'right': (0, 1),
}


def parse_map(map_data: List[str]) -> Tuple[List[List[str]], Tuple[int, int], int]:
    grid = [list(row) for row in map_data]
    player_pos = None
    target_count = 0
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            ch = grid[r][c]
            if ch in (PLAYER, PLAYER_ON_TARGET):
                player_pos = (r, c)
                if ch == PLAYER_ON_TARGET:
                    grid[r][c] = TARGET
                else:
                    grid[r][c] = FLOOR
            if ch == TARGET or ch == PLAYER_ON_TARGET or ch == BOX_ON_TARGET:
                target_count += 1
    return grid, player_pos, target_count


class SokobanGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('sokoban', difficulty)
        if difficulty == 'easy':
            start, end = 0, 2
        elif difficulty == 'hard':
            start, end = 2, 5
        else:
            start, end = 0, 5
        self.levels = LEVELS[start:end]
        if not self.levels:
            self.levels = LEVELS[:2]
        self.level_idx = 0
        self.grid: List[List[str]] = []
        self.player_pos: Tuple[int, int] = (0, 0)
        self.target_count = 0
        self.moves = 0
        self.history: List[Tuple[List[List[str]], Tuple[int, int]]] = []
        self.solved = False
        self.high_score = 0

    def _load_level(self, idx: int) -> None:
        level = self.levels[idx]
        self.grid, self.player_pos, self.target_count = parse_map(level['map'])
        self.moves = 0
        self.history = []
        self.solved = False

    def _push(self, dr: int, dc: int) -> bool:
        r, c = self.player_pos
        nr, nc = r + dr, c + dc
        if not (0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[nr])):
            return False
        cell = self.grid[nr][nc]
        if cell == WALL:
            return False
        if cell in (BOX, BOX_ON_TARGET):
            nnr, nnc = nr + dr, nc + dc
            if not (0 <= nnr < len(self.grid) and 0 <= nnc < len(self.grid[nnr])):
                return False
            next_cell = self.grid[nnr][nnc]
            if next_cell in (BOX, BOX_ON_TARGET, WALL):
                return False
            self.history.append((deepcopy(self.grid), self.player_pos))
            self.grid[nnr][nnc] = BOX_ON_TARGET if next_cell == TARGET else BOX
            self.grid[nr][nc] = TARGET if cell == BOX_ON_TARGET else FLOOR
        else:
            self.history.append((deepcopy(self.grid), self.player_pos))
        self.grid[r][c] = TARGET if self.grid[r][c] in (TARGET, PLAYER_ON_TARGET) else FLOOR
        self.player_pos = (nr, nc)
        self.grid[nr][nc] = TARGET if isinstance(self.grid[nr][nc], str) and self.grid[nr][nc] == TARGET else FLOOR
        self.moves += 1
        return True

    def _render(self) -> None:
        level = self.levels[self.level_idx]
        lines = [
            f"{C_CYAN}{level['name']}  M: {self.moves}  "
            f"DIFFICULTY: {self.difficulty.upper()}{C_RESET}",
        ]
        draw_retro_box(40, "\u25A0 SOKOBAN \u25A0", lines, color=C_YELLOW)
        print()
        for r in range(len(self.grid)):
            print("     ", end="")
            for c in range(len(self.grid[r])):
                ch = self.grid[r][c]
                if (r, c) == self.player_pos:
                    is_on_target = self.grid[r][c] == TARGET
                    ch = PLAYER_ON_TARGET if is_on_target else PLAYER
                else:
                    ch = self.grid[r][c]
                if ch == WALL:
                    print(f"{C_WHITE}#{C_RESET}", end="")
                elif ch == PLAYER:
                    print(f"{C_GREEN}@{C_RESET}", end="")
                elif ch == PLAYER_ON_TARGET:
                    print(f"{C_YELLOW}+{C_RESET}", end="")
                elif ch == BOX:
                    print(f"{C_RED}${C_RESET}", end="")
                elif ch == BOX_ON_TARGET:
                    print(f"{C_GREEN}*{C_RESET}", end="")
                elif ch == TARGET:
                    print(f"{C_YELLOW}.{C_RESET}", end="")
                else:
                    print(" ", end="")
            print()

        on_targets = sum(row.count(BOX_ON_TARGET) for row in self.grid)
        remaining = self.target_count - on_targets
        print(f"\n     {C_WHITE}Boxes on target: {on_targets}/{self.target_count}{C_RESET}")

        if self.solved:
            print(f"\n{C_GREEN}LEVEL SOLVED!{C_RESET}")
        elif remaining > 0:
            print(f"\n{C_WHITE}[Arrows] Move  [U] Undo  [R] Reset  [Q] Quit  [?] Help{C_RESET}")

    def _show_help(self) -> None:
        show_popup(
            "SOKOBAN: Push all boxes onto targets! "
            "Use arrow keys to move. You can only PUSH boxes, not pull them. "
            "Plan ahead — you can get stuck if boxes are pushed into corners. "
            "Press U to undo a move, R to reset the level.",
            C_YELLOW, delay=3.0
        )

    def _check_solved(self) -> bool:
        return all(row.count(BOX) == 0 for row in self.grid)

    def play(self) -> Dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        else:
            self._load_level(0)
        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 1)
                self._render()

                if self.solved:
                    self.score += max(100 - self.moves, 10)
                    if self.score > self.high_score:
                        self.high_score = self.score
                    self.award_xp_for_action(self.score)
                    self.end_timer()
                    final_stats = self.get_final_stats()
                    final_stats['high_score'] = self.high_score
                    self.save_stats(final_stats)
                    print(f"\n{C_WHITE}[Any Key] Next Level  [Q] Quit{C_RESET}")
                    key = input_handler.get_safe_key()
                    if key and self._save_and_quit(key.lower()):
                        break
                    if key:
                        self.level_idx = (self.level_idx + 1) % len(self.levels)
                        self._load_level(self.level_idx)
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
                if key in DIRS:
                    dr, dc = DIRS[key]
                    r, c = self.player_pos
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[nr]):
                        cell = self.grid[nr][nc]
                        if cell in (BOX, BOX_ON_TARGET):
                            nnr, nnc = nr + dr, nc + dc
                            if 0 <= nnr < len(self.grid) and 0 <= nnc < len(self.grid[nnr]):
                                next_cell = self.grid[nnr][nnc]
                                if next_cell not in (BOX, BOX_ON_TARGET, WALL):
                                    self.history.append((deepcopy(self.grid), self.player_pos))
                                    self.grid[nnr][nnc] = BOX_ON_TARGET if next_cell == TARGET else BOX
                                    self.grid[nr][nc] = TARGET if cell == BOX_ON_TARGET else FLOOR
                                    self.grid[r][c] = FLOOR
                                    self.player_pos = (nr, nc)
                                    self.moves += 1
                                    if self._check_solved():
                                        self.solved = True
                                        beep("win")
                                    else:
                                        beep("correct")
                                else:
                                    beep("lose")
                            else:
                                beep("lose")
                        elif cell != WALL:
                            self.history.append((deepcopy(self.grid), self.player_pos))
                            self.grid[r][c] = FLOOR
                            self.player_pos = (nr, nc)
                            self.moves += 1
                            beep("correct")
                        else:
                            beep("lose")
                elif key.lower() == 'u' and self.history:
                    self.grid, self.player_pos = self.history.pop()
                    self.moves = max(0, self.moves - 1)
                    beep("correct")
                elif key.lower() == 'r':
                    self._load_level(self.level_idx)
                    beep("correct")

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            stats = self.get_final_stats()
            stats['high_score'] = self.high_score
            return stats


def play_sokoban(difficulty: str = 'normal') -> dict:
    game = SokobanGame(difficulty)
    return game.play()
