import logging
import time
from typing import List, Optional

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

DISK_CONFIGS = {"easy": 3, "normal": 4, "hard": 5}

LABEL = {0: "A", 1: "B", 2: "C"}

SYMBOLS = ["@", "#", "$", "%", "&"]
COLORS = [C_RED, C_YELLOW, C_GREEN, C_CYAN, C_MAGENTA]


class HanoiGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('hanoi', difficulty)
        self.num_disks = DISK_CONFIGS.get(difficulty, 4)
        self.pegs: List[List[int]] = [
            list(range(self.num_disks, 0, -1)),
            [],
            [],
        ]
        self.moves = 0
        self.min_moves = (1 << self.num_disks) - 1
        self.source: Optional[int] = None
        self.input_handler = get_safe_input_handler()

    def render_game(self) -> None:
        clear_screen()
        print("\n" * 1)

        lines = [
            f"{C_YELLOW}Moves:{C_RESET} {self.moves}  "
            f"{C_CYAN}Min:{C_RESET} {self.min_moves}  "
            f"{C_GREEN}Disks:{C_RESET} {self.num_disks}",
            "",
        ]

        max_h = self.num_disks
        for row in range(max_h - 1, -1, -1):
            row_parts = []
            for p in range(3):
                if row < len(self.pegs[p]):
                    d = self.pegs[p][row]
                    sym = SYMBOLS[(d - 1) % len(SYMBOLS)]
                    color = COLORS[(d - 1) % len(COLORS)]
                    label = sym * d
                    row_parts.append(f"{color}{label:^{self.num_disks + 3}}{C_RESET}")
                else:
                    row_parts.append(f"{'|':^{self.num_disks + 3}}")
            lines.append("".join(f"  {p}" for p in row_parts))

        lines.append("  " + "  ".join(
            f"{C_CYAN}═══{'═' * self.num_disks}═══{C_RESET}" for _ in range(3)))
        lines.append("  " + "  ".join(
            f"{C_WHITE}  {LABEL[i]}  {C_RESET}" for i in range(3)))

        if self.source is not None:
            lines += [
                "",
                f"{C_YELLOW}Source: {LABEL[self.source]}  "
                f"Select destination (1-3) or Q to cancel{C_RESET}",
            ]
        else:
            lines += [
                "",
                f"{C_YELLOW}Select source peg (1-3)  Q Quit  H Help{C_RESET}",
            ]

        draw_retro_box(self.num_disks * 3 + 22, "TOWER OF HANOI", lines, color=C_CYAN)

    def is_valid_move(self, src: int, dst: int) -> bool:
        if not self.pegs[src]:
            return False
        if not self.pegs[dst]:
            return True
        return self.pegs[src][-1] < self.pegs[dst][-1]

    def move_disk(self, src: int, dst: int) -> bool:
        if not self.is_valid_move(src, dst):
            return False
        disk = self.pegs[src].pop()
        self.pegs[dst].append(disk)
        self.moves += 1
        return True

    def check_win(self) -> bool:
        return len(self.pegs[2]) == self.num_disks

    def show_summary(self) -> None:
        clear_screen()
        print("\n" * 2)
        efficiency = int((self.min_moves / max(self.moves, 1)) * 100)
        lines = [
            f"{C_GREEN}Puzzle Solved!{C_RESET}",
            "",
            f"{C_WHITE}Disks:{C_RESET}     {self.num_disks}",
            f"{C_WHITE}Moves:{C_RESET}     {self.moves}",
            f"{C_WHITE}Minimum:{C_RESET}   {self.min_moves}",
            f"{C_WHITE}Efficiency:{C_RESET} {C_YELLOW}{efficiency}%{C_RESET}",
            f"{C_WHITE}XP Earned:{C_RESET} {C_MAGENTA}{self.xp_earned}{C_RESET}",
        ]
        draw_retro_box(34, "CONGRATULATIONS!", lines, color=C_GREEN)
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

                if self.source is None:
                    if key in ('1', '2', '3'):
                        src = int(key) - 1
                        if self.pegs[src]:
                            self.source = src
                            beep("correct")
                        else:
                            show_popup(f"{C_RED}Peg {LABEL[src]} is empty!{C_RESET}", delay=0.8)
                else:
                    if key in ('1', '2', '3'):
                        dst = int(key) - 1
                        if dst == self.source:
                            show_popup("Same peg!", delay=0.6)
                        elif self.is_valid_move(self.source, dst):
                            self.move_disk(self.source, dst)
                            beep("win")
                            if self.check_win():
                                eff = self.min_moves / max(self.moves, 1)
                                base_xp = int(self.min_moves * 5 * eff)
                                self.award_xp_for_action(max(base_xp, 10))
                                self.end_timer()
                                self.render_game()
                                self.show_summary()
                                break
                        else:
                            beep("wrong")
                            show_popup(f"{C_RED}Invalid move! Larger disk on smaller.{C_RESET}",
                                       delay=1.0)
                        self.source = None
                    elif key and key.lower() == 'q':
                        self.source = None

                time.sleep(0.05)

            final_stats = self.get_final_stats()
            final_stats['high_score'] = max(0, self.min_moves * 10 - self.moves)
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
            "Move all disks from peg A to peg C!",
            "",
            f"{C_CYAN}Rules:{C_RESET}",
            "  1. Move one disk at a time",
            "  2. Only top disk can be moved",
            "  3. No larger disk on smaller",
            "",
            f"{C_CYAN}Controls:{C_RESET}",
            "  1/2/3     Select peg",
            "  First: choose source peg",
            "  Then:  choose destination",
            "  Q        Cancel source / Quit",
            "  P        Pause",
            "",
            f"{C_CYAN}Minimum moves:{C_RESET}",
            "  3 disks = 7    4 disks = 15",
            "  5 disks = 31",
        ]
        draw_retro_box(36, "HANOI HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_hanoi(difficulty: str = 'normal') -> dict:
    game = HanoiGame(difficulty)
    return game.play()
