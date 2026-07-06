import random
import time
from typing import List

from arcade_utils import (
    C_BLACK,
    C_CYAN,
    C_GREEN,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    beep,
    clear_screen,
    print_big_title,
    show_popup,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler


class SudokuGame(BaseGame):
    """Sudoku game implementation using BaseGame."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("sudoku", difficulty)
        self.board: List[List[int]] = [[0 for _ in range(9)] for _ in range(9)]
        self.original: List[List[int]] = [[0 for _ in range(9)] for _ in range(9)]
        self._generate_board()
        self.cursor_x = 0
        self.cursor_y = 0
        self.input_handler = get_safe_input_handler()

    def save_state_json(self) -> dict:
        return {
            'grid': self.board,
            'original': self.original,
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
            'score': self.score,
        }

    def load_state_json(self, state: dict) -> None:
        self.board = state.get('grid', [[0]*9 for _ in range(9)])
        self.original = state.get('original', [[0]*9 for _ in range(9)])
        self.cursor_x = state.get('cursor_x', 0)
        self.cursor_y = state.get('cursor_y', 0)
        self.score = state.get('score', 0)

    def _generate_board(self) -> None:
        base_board = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]

        self.board = [row[:] for row in base_board]

        to_remove = 30
        if self.difficulty == 'normal':
            to_remove = 45
        elif self.difficulty == 'hard':
            to_remove = 55

        removed = 0
        while removed < to_remove:
            r, c = random.randint(0, 8), random.randint(0, 8)
            if self.board[r][c] != 0:
                self.board[r][c] = 0
                removed += 1

        self.original = [row[:] for row in self.board]

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("SUDOKU", color=C_GREEN)
        time.sleep(1)

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            if self._check_win():
                self._handle_win()
            time.sleep(0.01)

        self.end_timer()

        stats = self.stats_manager.get_stats('sudoku')
        wins = stats.get('wins', 0)

        self.save_stats({
            'wins': wins + (1 if self._check_win() else 0),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })

        return self.get_final_stats()

    def _render(self) -> None:
        print(f" DIFFICULTY: {C_YELLOW}{self.difficulty.upper()}{C_RESET} | SCORE: {C_GREEN}{self.score}{C_RESET}")

        print(f"{C_WHITE}╔═══════╦═══════╦═══════╗")
        for r in range(9):
            if r > 0 and r % 3 == 0:
                print("╠═══════╬═══════╬═══════╣")

            line = "║ "
            for c in range(9):
                if c > 0 and c % 3 == 0:
                    line += "║ "

                val = self.board[r][c]
                char = str(val) if val != 0 else "."

                color = C_WHITE
                if self.original[r][c] != 0:
                    color = C_CYAN
                elif val != 0:
                    color = C_GREEN

                bg = C_RESET
                if (c, r) == (self.cursor_x, self.cursor_y):
                    bg = "\033[48;5;220m"
                    color = C_BLACK

                line += f"{bg}{color}{char}{C_RESET} "
            print(line + "║")
        print(f"╚═══════╩═══════╩═══════╝{C_RESET}")
        print(f"\n{C_WHITE}ARROWS: Move | 1-9: Enter Number | 0/BACKSPACE: Clear | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        if k == 'h':
            show_popup("SUDOKU: Fill grid so each row, col, and 3x3 box has 1-9 without repeats.", C_GREEN, delay=1.5)
            return
        if k in '123456789':
            if self.original[self.cursor_y][self.cursor_x] == 0:
                self.board[self.cursor_y][self.cursor_x] = int(k)
                self.score += 5
                self.award_xp_for_action(2)
                beep("correct")
        elif k in ['0', '\b', 'backspace']:
            if self.original[self.cursor_y][self.cursor_x] == 0:
                self.board[self.cursor_y][self.cursor_x] = 0
                beep("correct")
        else:
            direction = self.input_handler.validator.validate_direction(k)
            if direction == 'up':
                self.cursor_y = max(0, self.cursor_y - 1)
            elif direction == 'down':
                self.cursor_y = min(8, self.cursor_y + 1)
            elif direction == 'left':
                self.cursor_x = max(0, self.cursor_x - 1)
            elif direction == 'right':
                self.cursor_x = min(8, self.cursor_x + 1)

    def _check_win(self) -> bool:
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return False
        for i in range(9):
            if sorted(self.board[i]) != list(range(1, 10)):
                return False
            col = [self.board[r][i] for r in range(9)]
            if sorted(col) != list(range(1, 10)):
                return False
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                box = [self.board[br + r][bc + c] for r in range(3) for c in range(3)]
                if sorted(box) != list(range(1, 10)):
                    return False
        return True

    def _handle_win(self) -> None:
        beep("win")
        self.award_xp_for_action(300)
        self.unlock_achievement("sudoku_win", "Logic Wizard")
        show_popup("SUDOKU COMPLETE! YOU WIN!", C_GREEN)
        self.game_over = True


def play_sudoku(difficulty: str = 'normal') -> dict:
    game = SudokuGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_sudoku()
