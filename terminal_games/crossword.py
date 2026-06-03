import logging
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

PuzzleGrid = List[List[Optional[str]]]
Clue = Tuple[int, str, int, int, int]
ClueList = List[Clue]
NumberMap = Dict[Tuple[int, int], int]

PuzzleDef = Dict

PUZZLES: Dict[str, PuzzleDef] = {
    "easy": {
        "rows": 5, "cols": 5,
        "grid": [
            [None, "C",  "A",  "T",  None],
            [None, "A",  None, "O",  None],
            ["D",  "O",  "G",  "O",  "G"],
            [None, "G",  None, "L",  None],
            [None, "Y",  "A",  "R",  "D"],
        ],
        "across": [
            (1, "Feline friend", 0, 1, 3),
            (3, "Pet that barks", 2, 0, 3),
            (6, "Outdoor space", 4, 1, 4),
        ],
        "down": [
            (2, "Orange veggie", 0, 1, 4),
            (4, "Loud bark", 2, 4, 3),
            (5, "Howl at the moon", 3, 3, 3),
        ],
    },
    "normal": {
        "rows": 7, "cols": 7,
        "grid": [
            [None, "P",  "Y",  "T",  "H",  "O",  "N"],
            [None, "Y",  None, None, None, None, None],
            [None, "T",  None, "C",  "O",  "D",  "E"],
            [None, "H",  None, "A",  None, None, None],
            ["J",  "A",  "V",  "A",  None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
        ],
        "across": [
            (1, "Programming language (6)", 0, 1, 6),
            (3, "Secret message system (4)", 2, 3, 4),
            (4, "Coffee or tea language (4)", 4, 0, 4),
        ],
        "down": [
            (2, "Snake relative (4)", 0, 1, 4),
            (5, "Scripting language (4)", 0, 4, 5),
            (6, "Database query lang (3)", 2, 6, 3),
        ],
    },
    "hard": {
        "rows": 7, "cols": 7,
        "grid": [
            ["P",  "Y",  "T",  "H",  "O",  "N",  None],
            [None, None, None, None, "A",  None, None],
            [None, None, None, None, "R",  None, None],
            [None, None, None, None, "R",  None, None],
            [None, "J",  "A",  "V",  "A",  None, None],
            [None, None, None, None, "T",  None, None],
            [None, None, None, None, "E",  None, None],
        ],
        "across": [
            (1, "Snake that squeezes (6)", 0, 0, 6),
            (4, "Coffee or tea lang (4)", 4, 1, 4),
        ],
        "down": [
            (2, "Code script lang (6)", 0, 4, 7),
            (3, "Machine learning lang (4)", 4, 2, 4),
        ],
    },
}


class CrosswordGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('crossword', difficulty)
        puzzle = PUZZLES.get(difficulty, PUZZLES["normal"])
        self.rows = puzzle["rows"]
        self.cols = puzzle["cols"]
        self.solution = puzzle["grid"]
        self.across: ClueList = puzzle["across"]
        self.down: ClueList = puzzle["down"]

        self.player_grid: List[List[Optional[str]]] = [
            [None for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self.numbered: NumberMap = {}
        self._build_numbered()

        self.cursor_r = 0
        self.cursor_c = 0
        self.correct_words = 0
        self.total_words = len(self.across) + len(self.down)
        self.hints_used = 0
        self.input_handler = get_safe_input_handler()

    def _build_numbered(self) -> None:
        for num, clue, r, c, length in self.across:
            self.numbered[(r, c)] = num
        for num, clue, r, c, length in self.down:
            if (r, c) not in self.numbered:
                self.numbered[(r, c)] = num

    def _get_word_at(self, r: int, c: int) -> Optional[Tuple[str, int, int, int, str]]:
        for num, clue, sr, sc, length in self.across:
            if sr == r and sc <= c < sc + length:
                letters = []
                for i in range(length):
                    lr = sr
                    lc = sc + i
                    val = self.player_grid[lr][lc]
                    if val is None:
                        return None
                    letters.append(val)
                word = "".join(letters)
                return (word, num, sr, sc, clue)
        for num, clue, sr, sc, length in self.down:
            if sc == c and sr <= r < sr + length:
                letters = []
                for i in range(length):
                    lr = sr + i
                    lc = sc
                    val = self.player_grid[lr][lc]
                    if val is None:
                        return None
                    letters.append(val)
                word = "".join(letters)
                return (word, num, sr, sc, clue)
        return None

    def _check_and_mark(self) -> None:
        for num, clue, sr, sc, length in self.across:
            completed = True
            for i in range(length):
                val = self.player_grid[sr][sc + i]
                sol = self.solution[sr][sc + i]
                if val != sol:
                    completed = False
            if completed:
                self.award_xp_for_action(15)
                self.correct_words += 1
                beep("win")

        for num, clue, sr, sc, length in self.down:
            completed = True
            for i in range(length):
                val = self.player_grid[sr + i][sc]
                sol = self.solution[sr + i][sc]
                if val != sol:
                    completed = False
            if completed:
                self.award_xp_for_action(15)
                self.correct_words += 1
                beep("win")

    def _all_complete(self) -> bool:
        for r in range(self.rows):
            for c in range(self.cols):
                if self.solution[r][c] is not None:
                    if self.player_grid[r][c] != self.solution[r][c]:
                        return False
        return True

    def _clues_by_type(self, is_across: bool) -> List[str]:
        clues = self.across if is_across else self.down
        label = "Across" if is_across else "Down"
        result = [f"{C_CYAN}{label}:{C_RESET}"]
        for num, clue, sr, sc, length in clues:
            done = True
            for i in range(length):
                r = sr + (0 if is_across else i)
                c = sc + (i if is_across else 0)
                if self.player_grid[r][c] != self.solution[r][c]:
                    done = False
                    break
            prefix = f"{C_GREEN}[{num}]{C_RESET}" if done else f"{C_WHITE}{num}.{C_RESET}"
            result.append(f"  {prefix} {clue} ({length})")
        return result

    def render_game(self) -> None:
        clear_screen()
        print("\n" * 1)

        clues_across = self._clues_by_type(True)
        clues_down = self._clues_by_type(False)
        all_clues = clues_across + [""] + clues_down

        disp_lines: List[str] = [
            f"{C_YELLOW}Completed: {self.correct_words}/{self.total_words}  "
            f"Hints: {self.hints_used}{C_RESET}",
            "",
        ]

        col_header = "    " + " ".join(f"{C_CYAN}{c+1:2}{C_RESET}" for c in range(self.cols))
        disp_lines.append(col_header)

        for r in range(self.rows):
            row = [f"{C_CYAN}{r+1:2}{C_RESET} "]
            for c in range(self.cols):
                if self.solution[r][c] is None:
                    row.append(f"  {C_RED}##{C_RESET}")
                    continue

                val = self.player_grid[r][c]
                sol = self.solution[r][c]
                num = self.numbered.get((r, c))

                if (r, c) == (self.cursor_r, self.cursor_c):
                    if val is None:
                        row.append(f"[{C_WHITE} _{C_RESET}]")
                    elif val == sol:
                        row.append(f"[{C_GREEN}{val}{C_RESET}]")
                    else:
                        row.append(f"[{C_RED}{val}{C_RESET}]")
                elif val is None:
                    if num is not None:
                        row.append(f" {C_YELLOW}{num:2}{C_RESET}")
                    else:
                        row.append("  .")
                elif val == sol:
                    row.append(f" {C_GREEN} {val}{C_RESET}")
                else:
                    row.append(f" {C_RED} {val}{C_RESET}")

            disp_lines.append(" ".join(row))

        disp_lines += [
            "",
            f"{C_YELLOW}←↑→↓ Move  Letter=Fill  BKSP=Clear  "
            f"H=Hint  Q=Quit{C_RESET}",
        ]

        total_width = max(12 + self.cols * 4, 34)

        draw_retro_box(total_width, "CROSSWORD", disp_lines, color=C_CYAN)

        print("\n" * 1)
        for line in all_clues:
            print(f"  {line}")
        print(f"\n  {C_YELLOW}Type a letter to fill, ARROWS to move, H for hint{C_RESET}")

    def use_hint(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                if self.solution[r][c] is not None and self.player_grid[r][c] is None:
                    sol = self.solution[r][c]
                    self.player_grid[r][c] = sol
                    self.hints_used += 1
                    self.cursor_r = r
                    self.cursor_c = c
                    self._check_and_mark()
                    beep("correct")
                    show_popup(f"Hint: {sol} at {r+1},{c+1}", delay=1.0)
                    return
        show_popup("Grid is already full!", delay=1.0)

    def show_summary(self) -> None:
        clear_screen()
        print("\n" * 2)
        lines = [
            f"{C_GREEN}Puzzle Complete!{C_RESET}",
            "",
            f"{C_WHITE}Words completed:{C_RESET}  {self.correct_words}/{self.total_words}",
            f"{C_WHITE}Hints used:{C_RESET}     {self.hints_used}",
            f"{C_WHITE}Score:{C_RESET}          {C_YELLOW}{self.score}{C_RESET}",
            f"{C_WHITE}XP Earned:{C_RESET}      {C_MAGENTA}{self.xp_earned}{C_RESET}",
        ]
        draw_retro_box(34, "WELL DONE!", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()

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

                handled = False
                if key == 'up' or key == 'w':
                    self.cursor_r = (self.cursor_r - 1) % self.rows
                    handled = True
                elif key == 'down' or key == 's':
                    self.cursor_r = (self.cursor_r + 1) % self.rows
                    handled = True
                elif key == 'left' or key == 'a':
                    self.cursor_c = (self.cursor_c - 1) % self.cols
                    handled = True
                elif key == 'right' or key == 'd':
                    self.cursor_c = (self.cursor_c + 1) % self.cols
                    handled = True

                if handled:
                    beep("move")
                    time.sleep(0.05)
                    continue

                if key and key.lower() == 'h':
                    self.use_hint()
                    continue

                if self.solution[self.cursor_r][self.cursor_c] is not None:
                    if key and len(key) == 1 and key.isalpha():
                        self.player_grid[self.cursor_r][self.cursor_c] = key.upper()
                        beep("correct")
                        self._check_and_mark()
                        if self._all_complete():
                            self.end_timer()
                            self.render_game()
                            self.show_summary()
                            break
                        nc = (self.cursor_c + 1) % self.cols
                        if self.solution[self.cursor_r][nc] is None:
                            nr = (self.cursor_r + 1) % self.rows
                            self.cursor_r = nr
                        else:
                            self.cursor_c = nc
                    elif key == '\b' or key == '\x7f':
                        self.player_grid[self.cursor_r][self.cursor_c] = None
                        beep("move")

                time.sleep(0.05)

            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.correct_words
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
            "Complete the crossword by filling in",
            "all the words correctly!",
            "",
            f"{C_CYAN}Controls:{C_RESET}",
            "  ARROWS/WASD   Move cursor",
            "  A-Z           Fill letter at cursor",
            "  BACKSPACE     Clear letter",
            "  H             Hint (fills next empty)",
            "  Q             Quit (saves progress)",
            "  P             Pause",
            "",
            f"{C_CYAN}Tips:{C_RESET}",
            "  Correct letters turn green.",
            "  Wrong letters turn red.",
            "  Words auto-check when complete.",
            "  Hints reduce bonus XP.",
        ]
        draw_retro_box(36, "CROSSWORD HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_crossword(difficulty: str = 'normal') -> dict:
    game = CrosswordGame(difficulty)
    return game.play()
