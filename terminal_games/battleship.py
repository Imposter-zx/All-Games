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

GRID_SIZE = 8
SHIPS = [
    ("Carrier", 4),
    ("Battleship", 3),
    ("Cruiser", 3),
    ("Submarine", 2),
    ("Destroyer", 2),
]

HIT = "X"
MISS = "O"
EMPTY = "."
SHIP = "S"


class BattleshipGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('battleship', difficulty)
        self.input_handler = get_safe_input_handler()
        self.player_grid: List[List[str]] = []
        self.enemy_grid: List[List[str]] = []
        self.enemy_ships: List[List[bool]] = []
        self.player_ship_cells: List[Tuple[int, int]] = []
        self.enemy_ship_cells: List[Tuple[int, int]] = []
        self.ship_sunk: List[bool] = []
        self.cursor_r = 0
        self.cursor_c = 0
        self.turns = 0
        self.player_hits = 0
        self.enemy_hits = 0
        self.phase = "place"
        self.placing_ship = 0
        self.place_horizontal = True
        self._init_grids()

    def _init_grids(self) -> None:
        self.player_grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.enemy_grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.enemy_ships = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.ship_sunk = [False] * len(SHIPS)
        self.player_ship_cells = []
        self.enemy_ship_cells = []

    def place_ship(self, r: int, c: int, horizontal: bool, ship_idx: int) -> bool:
        name, length = SHIPS[ship_idx]
        cells = []
        for i in range(length):
            nr = r + (0 if horizontal else i)
            nc = c + (i if horizontal else 0)
            if nr >= GRID_SIZE or nc >= GRID_SIZE:
                return False
            if self.player_grid[nr][nc] != EMPTY:
                return False
            cells.append((nr, nc))

        for nr, nc in cells:
            self.player_grid[nr][nc] = SHIP
            self.player_ship_cells.append((nr, nc))
        return True

    def place_enemy_ships(self) -> None:
        for idx, (name, length) in enumerate(SHIPS):
            placed = False
            attempts = 0
            while not placed and attempts < 1000:
                r = random.randint(0, GRID_SIZE - 1)
                c = random.randint(0, GRID_SIZE - 1)
                horizontal = random.choice([True, False])
                cells = []
                ok = True
                for i in range(length):
                    nr = r + (0 if horizontal else i)
                    nc = c + (i if horizontal else 0)
                    if nr >= GRID_SIZE or nc >= GRID_SIZE:
                        ok = False
                        break
                    if self.enemy_ships[nr][nc]:
                        ok = False
                        break
                    cells.append((nr, nc))
                if ok:
                    for nr, nc in cells:
                        self.enemy_ships[nr][nc] = True
                        self.enemy_ship_cells.append((nr, nc))
                    placed = True
                attempts += 1

    def fire(self, r: int, c: int, target_grid: List[List[str]],
             target_ships: List[List[bool]]) -> bool:
        if target_grid[r][c] != EMPTY:
            return False
        if target_ships[r][c]:
            target_grid[r][c] = HIT
            return True
        target_grid[r][c] = MISS
        return False

    def check_ship_sunk(self, r: int, c: int, grid: List[List[str]],
                        ships: List[List[bool]]) -> Optional[str]:
        """Check if the ship at (r,c) on the given grid is now fully sunk."""
        checked: List[Tuple[int, int]] = []
        queue: List[Tuple[int, int]] = [(r, c)]
        ship_cells: List[Tuple[int, int]] = []

        while queue:
            cr, cc = queue.pop()
            if (cr, cc) in checked:
                continue
            checked.append((cr, cc))
            if not ships[cr][cc]:
                continue
            ship_cells.append((cr, cc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and ships[nr][nc]:
                    queue.append((nr, nc))

        for sr, sc in ship_cells:
            if grid[sr][sc] != HIT:
                return None

        for ship_idx, (name, length) in enumerate(SHIPS):
            if len(ship_cells) == length:
                return name
        return None

    def check_all_sunk(self, grid: List[List[str]],
                       ships: List[List[bool]]) -> bool:
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if ships[r][c] and grid[r][c] != HIT:
                    return False
        return True

    def ai_fire(self) -> Tuple[int, int]:
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.player_grid[r][c] == HIT:
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                            if self.player_grid[nr][nc] == EMPTY:
                                return nr, nc
        r, c = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        while self.player_grid[r][c] != EMPTY:
            r, c = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        return r, c

    def render_placement(self) -> None:
        clear_screen()
        print("\n" * 1)

        name, length = SHIPS[self.placing_ship]
        direction = "H" if self.place_horizontal else "V"
        lines = [
            f"{C_YELLOW}Place your ships on the grid!{C_RESET}",
            "",
            f"{C_WHITE}Placing: {C_CYAN}{name}{C_RESET}  "
            f"Length: {length}  Dir: {direction}",
            f"{C_YELLOW}Press R to rotate{C_RESET}",
            "",
        ]

        header = "   " + " ".join(f"{C_CYAN}{c+1}{C_RESET}" for c in range(GRID_SIZE))
        lines.append(header)

        for r in range(GRID_SIZE):
            row = [f"{C_CYAN}{r+1:2}{C_RESET}"]
            for c in range(GRID_SIZE):
                if self.player_grid[r][c] == SHIP:
                    row.append(f" {C_GREEN}{SHIP}{C_RESET} ")
                elif (r, c) == (self.cursor_r, self.cursor_c):
                    can_place = self._can_preview(r, c, self.place_horizontal)
                    preview = "." if can_place else "!"
                    row.append(f"[{C_WHITE}{preview}{C_RESET}]")
                else:
                    row.append(f" {C_MAGENTA}{EMPTY}{C_RESET} ")
            lines.append(" ".join(row))

        remaining = [f"{SHIPS[i][0]}({SHIPS[i][1]})" for i in range(self.placing_ship, len(SHIPS))]
        lines += [
            "",
            f"{C_WHITE}Remaining: {', '.join(remaining)}{C_RESET}",
            "",
            f"{C_YELLOW}ARROWS Move  SPACE Place  R Rotate  Q Auto-place{C_RESET}",
        ]

        draw_retro_box(GRID_SIZE * 4 + 8, "BATTLESHIP", lines, color=C_CYAN)

    def _can_preview(self, r: int, c: int, horizontal: bool) -> bool:
        _, length = SHIPS[self.placing_ship]
        for i in range(length):
            nr = r + (0 if horizontal else i)
            nc = c + (i if horizontal else 0)
            if nr >= GRID_SIZE or nc >= GRID_SIZE:
                return False
            if self.player_grid[nr][nc] != EMPTY:
                return False
        return True

    def auto_place_ships(self) -> None:
        self.player_grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.player_ship_cells = []
        for idx in range(len(SHIPS)):
            placed = False
            attempts = 0
            while not placed and attempts < 500:
                r = random.randint(0, GRID_SIZE - 1)
                c = random.randint(0, GRID_SIZE - 1)
                h = random.choice([True, False])
                if self.place_ship(r, c, h, idx):
                    placed = True
                attempts += 1

    def render_battle(self) -> None:
        clear_screen()
        print("\n" * 1)

        lines = [
            f"{C_CYAN}Your Board{C_RESET}           "
            f"{C_CYAN}Target Board{C_RESET}",
        ]

        header = "   " + " ".join(f"{C_WHITE}{c+1}{C_RESET}"
                                   for c in range(GRID_SIZE))
        header2 = "   " + " ".join(f"{C_WHITE}{c+1}{C_RESET}"
                                    for c in range(GRID_SIZE))
        lines.append(f"   {header}      {header2}")

        for r in range(GRID_SIZE):
            prow = [f"{C_WHITE}{r+1:2}{C_RESET}"]
            for c in range(GRID_SIZE):
                val = self.player_grid[r][c]
                if val == HIT:
                    prow.append(f" {C_RED}{HIT}{C_RESET} ")
                elif val == MISS:
                    prow.append(f" {C_WHITE}{MISS}{C_RESET} ")
                elif val == SHIP:
                    prow.append(f" {C_GREEN}{SHIP}{C_RESET} ")
                else:
                    prow.append(f" {C_MAGENTA}{EMPTY}{C_RESET} ")

            erow = [f"{C_WHITE}{r+1:2}{C_RESET}"]
            for c in range(GRID_SIZE):
                if (r, c) == (self.cursor_r, self.cursor_c):
                    val = self.enemy_grid[r][c]
                    if val == HIT:
                        erow.append(f"[{C_RED}{HIT}{C_RESET}]")
                    elif val == MISS:
                        erow.append(f"[{C_WHITE}{MISS}{C_RESET}]")
                    else:
                        erow.append(f"[{C_YELLOW}?{C_RESET}]")
                else:
                    val = self.enemy_grid[r][c]
                    if val == HIT:
                        erow.append(f" {C_RED}{HIT}{C_RESET} ")
                    elif val == MISS:
                        erow.append(f" {C_WHITE}{MISS}{C_RESET} ")
                    else:
                        erow.append(f" {C_MAGENTA}?{C_RESET} ")

            lines.append(" ".join(prow) + "   " + " ".join(erow))

        lines += [
            "",
            f"{C_YELLOW}Turns:{C_RESET} {self.turns}  "
            f"{C_GREEN}Sunk:{C_RESET} {self._count_sunk()}  "
            f"{C_RED}Hits Taken:{C_RESET} {self.enemy_hits}",
            "",
            f"{C_YELLOW}ARROWS Move  SPACE Fire  Q Quit{C_RESET}",
        ]

        draw_retro_box(GRID_SIZE * 8 + 12, "BATTLESHIP", lines, color=C_CYAN)

    def _count_sunk(self) -> int:
        return self.ship_sunk.count(True)

    def _fire_and_check(self, r: int, c: int) -> Tuple[bool, Optional[str]]:
        hit = self.fire(r, c, self.enemy_grid, self.enemy_ships)
        if hit:
            self.player_hits += 1
            sunk = self.check_ship_sunk(r, c, self.enemy_grid, self.enemy_ships)
            return True, sunk
        return False, None

    def enemy_turn(self) -> Tuple[bool, Optional[str]]:
        r, c = self.ai_fire()
        hit = self.fire(r, c, self.player_grid, self.player_ship_cells)
        if hit:
            self.enemy_hits += 1
            sunk = None
            for (sr, sc) in self.player_ship_cells:
                if r == sr and c == sc and self.player_grid[r][c] == HIT:
                    sunk = self.check_ship_sunk(
                        r, c, self.player_grid, self.player_ship_cells)
                    break
            return True, sunk
        return False, None

    def show_result_popup(self, hit: bool, sunk: Optional[str],
                          is_player: bool) -> None:
        if sunk:
            msg = f"{'You' if is_player else 'Enemy'} sank my {C_GREEN}{sunk}{C_RESET}!"
            show_popup(msg, delay=1.5)
        elif hit:
            beep("correct")
            show_popup(f"{'HIT!' if is_player else 'ENEMY HIT!'}", delay=0.6)
        else:
            beep("wrong")
            show_popup(f"{'Miss...' if is_player else 'Enemy missed!'}", delay=0.6)

    def show_game_over(self, player_won: bool) -> None:
        clear_screen()
        print("\n" * 3)
        if player_won:
            lines = [
                f"{C_GREEN}VICTORY!{C_RESET}",
                "",
                f"{C_WHITE}Turns:{C_RESET}   {self.turns}",
                f"{C_WHITE}Hits:{C_RESET}    {self.player_hits}",
                f"{C_WHITE}Score:{C_RESET}   {C_YELLOW}{self.score}{C_RESET}",
                f"{C_WHITE}XP Earned:{C_RESET} {C_MAGENTA}{self.xp_earned}{C_RESET}",
            ]
            draw_retro_box(30, "YOU WIN!", lines, color=C_GREEN)
        else:
            lines = [
                f"{C_RED}Defeated!{C_RESET}",
                "",
                f"{C_WHITE}Turns:{C_RESET}   {self.turns}",
                f"{C_WHITE}Enemy hits:{C_RESET} {self.enemy_hits}",
            ]
            draw_retro_box(30, "GAME OVER", lines, color=C_RED)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()

    def play(self) -> dict:
        self.start_timer()
        self.renderer.hide_cursor()
        self.place_enemy_ships()

        try:
            while self.phase == "place" and not self.game_over:
                self.render_placement()
                key = self.input_handler.get_safe_key()

                if key and self._save_and_quit(key.lower()):
                    break
                if key == '?':
                    self._show_help()
                    continue

                handled = False
                if key == 'up' or key == 'w':
                    self.cursor_r = (self.cursor_r - 1) % GRID_SIZE
                    handled = True
                elif key == 'down' or key == 's':
                    self.cursor_r = (self.cursor_r + 1) % GRID_SIZE
                    handled = True
                elif key == 'left' or key == 'a':
                    self.cursor_c = (self.cursor_c - 1) % GRID_SIZE
                    handled = True
                elif key == 'right' or key == 'd':
                    self.cursor_c = (self.cursor_c + 1) % GRID_SIZE
                    handled = True

                if handled:
                    beep("move")
                    time.sleep(0.05)
                    continue

                if key in ['\r', '\n', ' ']:
                    placed = self.place_ship(
                        self.cursor_r, self.cursor_c,
                        self.place_horizontal, self.placing_ship)
                    if placed:
                        beep("correct")
                        self.placing_ship += 1
                        if self.placing_ship >= len(SHIPS):
                            self.phase = "battle"
                            self.cursor_r = 0
                            self.cursor_c = 0
                    else:
                        beep("wrong")
                elif key and key.lower() == 'r':
                    self.place_horizontal = not self.place_horizontal
                    beep("move")
                elif key and key.lower() == 'q':
                    self.auto_place_ships()
                    self.phase = "battle"
                    self.cursor_r = 0
                    self.cursor_c = 0

                time.sleep(0.05)

            while self.phase == "battle" and not self.game_over:
                self.render_battle()
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
                    self.cursor_r = (self.cursor_r - 1) % GRID_SIZE
                    handled = True
                elif key == 'down' or key == 's':
                    self.cursor_r = (self.cursor_r + 1) % GRID_SIZE
                    handled = True
                elif key == 'left' or key == 'a':
                    self.cursor_c = (self.cursor_c - 1) % GRID_SIZE
                    handled = True
                elif key == 'right' or key == 'd':
                    self.cursor_c = (self.cursor_c + 1) % GRID_SIZE
                    handled = True

                if handled:
                    beep("move")
                    time.sleep(0.05)
                    continue

                if key in ['\r', '\n', ' ']:
                    if self.enemy_grid[self.cursor_r][self.cursor_c] != EMPTY:
                        continue

                    self.turns += 1
                    hit, sunk = self._fire_and_check(self.cursor_r, self.cursor_c)
                    self.render_battle()
                    self.show_result_popup(hit, sunk, is_player=True)
                    if sunk:
                        for i, (name, _) in enumerate(SHIPS):
                            if name == sunk:
                                self.ship_sunk[i] = True
                                break

                    if self.check_all_sunk(self.enemy_grid, self.enemy_ships):
                        self.score = max(0, (GRID_SIZE * GRID_SIZE - self.turns) * 5)
                        self.award_xp_for_action(100)
                        self.end_timer()
                        self.show_game_over(player_won=True)
                        break

                    e_hit, e_sunk = self.enemy_turn()
                    self.show_result_popup(e_hit, e_sunk, is_player=False)

                    if self.check_all_sunk(self.player_grid, self.player_ship_cells):
                        self.end_timer()
                        self.show_game_over(player_won=False)
                        break

                time.sleep(0.05)

            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
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
            "Sink all enemy ships to win!",
            "",
            f"{C_CYAN}Ships:{C_RESET}",
            "  Carrier(4)  Battleship(3)  Cruiser(3)",
            "  Submarine(2)  Destroyer(2)",
            "",
            f"{C_CYAN}Placement:{C_RESET}",
            "  ARROWS  Move cursor",
            "  SPACE   Place ship",
            "  R       Rotate ship",
            "  Q       Auto-place all ships",
            "",
            f"{C_CYAN}Battle:{C_RESET}",
            "  ARROWS  Move cursor on target grid",
            "  SPACE   Fire at selected cell",
            "  Q       Quit",
        ]
        draw_retro_box(36, "BATTLESHIP HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_battleship(difficulty: str = 'normal') -> dict:
    game = BattleshipGame(difficulty)
    return game.play()
