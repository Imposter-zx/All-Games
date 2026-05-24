import random
import time
from typing import List

from arcade_utils import (
    BG_DARK,
    BG_LIGHT,
    BG_RED,
    C_BLACK,
    C_BLUE,
    C_CYAN,
    C_GRAY,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    animated_flash,
    beep,
    clear_screen,
    print_big_title,
    screen_shake,
    show_popup,
    u_safe,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler


class MinesweeperGame(BaseGame):
    """Minesweeper game implementation using BaseGame."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("minesweeper", difficulty)
        self.width = 10
        self.height = 10
        self.num_mines = 15
        self._init_board()
        self.cursor_x = 0
        self.cursor_y = 0
        self.first_move = True
        self.input_handler = get_safe_input_handler()

    def _init_board(self) -> None:
        self.board: List[List[int]] = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed: List[List[bool]] = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flags: List[List[bool]] = [[False for _ in range(self.width)] for _ in range(self.height)]

        placed = 0
        while placed < self.num_mines:
            rx, ry = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if self.board[ry][rx] != -1:
                self.board[ry][rx] = -1
                placed += 1

        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] == -1:
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.height and 0 <= nc < self.width:
                            if self.board[nr][nc] == -1:
                                count += 1
                self.board[r][c] = count

    def save_state_json(self) -> dict:
        return {
            'board': self.board,
            'revealed': self.revealed,
            'flags': self.flags,
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
            'score': self.score,
            'first_move': self.first_move,
        }

    def load_state_json(self, state: dict) -> None:
        self.board = state['board']
        self.revealed = state['revealed']
        self.flags = state['flags']
        self.cursor_x = state['cursor_x']
        self.cursor_y = state['cursor_y']
        self.score = state['score']
        self.first_move = state['first_move']

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("MINESWEEPER", color=C_RED)
        time.sleep(1)

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            if self._check_win():
                self._handle_win()
            time.sleep(0.01)

        self.end_timer()

        stats = self.stats_manager.get_stats('minesweeper')
        diff_key = self.difficulty
        wins = stats.get('wins', {})
        if not isinstance(wins, dict):
            wins = {}

        won = self._check_win()
        if won:
            wins[diff_key] = wins.get(diff_key, 0) + 1

        self.save_stats({
            'wins': wins,
            'high_score': max(0, self.score),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })

        return self.get_final_stats()

    def _render(self) -> None:
        flags_count = sum(row.count(True) for row in self.flags)
        print(f" MINES: {C_RED}{self.num_mines}{C_RESET} | FLAGS: {C_YELLOW}{flags_count}{C_RESET}")

        print(f"{C_WHITE}╔{'══' * self.width}╗")
        for r in range(self.height):
            line = "║"
            for c in range(self.width):
                char = "░ "
                color = C_WHITE
                bg = BG_DARK if (r + c) % 2 == 0 else BG_LIGHT
                if (c, r) == (self.cursor_x, self.cursor_y):
                    bg = "\033[48;5;220m"
                if self.revealed[r][c]:
                    val = self.board[r][c]
                    if val == -1:
                        char = u_safe("💣", "X ")
                        bg = BG_RED
                    elif val == 0:
                        char = "  "
                        color = C_GRAY
                        bg = C_RESET
                    else:
                        colors = [C_RESET, C_BLUE, C_GREEN, C_RED, C_CYAN, C_MAGENTA, C_YELLOW, C_WHITE, C_BLACK]
                        char = f"{val} "
                        color = colors[val]
                elif self.flags[r][c]:
                    char = u_safe("🚩", "F ")
                    color = C_YELLOW
                line += f"{bg}{color}{char}{C_RESET}"
            print(line + f"{C_WHITE}║")
        print(f"╚{'══' * self.width}╝{C_RESET}")
        print(f"\n{C_WHITE}ARROWS/WASD: Move | SPACE/ENTER: Reveal | F: Flag | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        elif k == 'h':
            show_popup("MINESWEEPER: Reveal safe cells. F=flag mine. Numbers = adjacent count.", C_RED, delay=1.5)
        elif k in [' ', '\r', '\n', 'enter']:
            self._reveal(self.cursor_x, self.cursor_y)
        elif k in ['f', 'F']:
            self.flags[self.cursor_y][self.cursor_x] = not self.flags[self.cursor_y][self.cursor_x]
            beep("correct")
        else:
            direction = self.input_handler.validator.validate_direction(k)
            if direction == 'up':
                self.cursor_y = max(0, self.cursor_y - 1)
            elif direction == 'down':
                self.cursor_y = min(self.height - 1, self.cursor_y + 1)
            elif direction == 'left':
                self.cursor_x = max(0, self.cursor_x - 1)
            elif direction == 'right':
                self.cursor_x = min(self.width - 1, self.cursor_x + 1)

    def _reveal(self, x: int, y: int) -> None:
        if self.revealed[y][x] or self.flags[y][x]:
            return
        self.revealed[y][x] = True

        if self.board[y][x] == -1:
            self._handle_loss()
            return

        self.score += 10
        self.award_xp_for_action(5)
        beep("correct")

        if self.board[y][x] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nx, ny = x + dc, y + dr
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self._reveal(nx, ny)

    def _check_win(self) -> bool:
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] != -1 and not self.revealed[r][c]:
                    return False
        return True

    def _handle_win(self) -> None:
        beep("win")
        self.award_xp_for_action(200)
        self.unlock_achievement("mines_win", "Demolition Expert")
        show_popup("YOU CLEARED THE MINEFIELD!", C_GREEN)
        self.game_over = True

    def _handle_loss(self) -> None:
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] == -1:
                    self.revealed[r][c] = True
        self._render()
        beep("game_over")
        screen_shake(0.3, 2)
        animated_flash(C_RED)
        show_popup("BOOM! GAME OVER", C_RED)
        self.game_over = True


def play_minesweeper(difficulty: str = 'normal') -> dict:
    game = MinesweeperGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_minesweeper()
