import logging
import random
import time
from typing import List, Tuple

from arcade_utils import (
    C_BLUE,
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

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER = 1
AI = 2


class ConnectFourGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('connect_four', difficulty)
        self.board: List[List[int]] = [[EMPTY] * COLS for _ in range(ROWS)]
        self.current_player = PLAYER
        self.input_handler = get_safe_input_handler()
        self.move_count = 0
        self.ai_depth = {'easy': 3, 'normal': 5, 'hard': 7}.get(difficulty, 5)

    def drop_piece(self, col: int, player: int) -> bool:
        if col < 0 or col >= COLS or self.board[0][col] != EMPTY:
            return False
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                self.board[row][col] = player
                self.move_count += 1
                return True
        return False

    def check_win(self, player: int) -> bool:
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(self.board[r][c + i] == player for i in range(4)):
                    return True
        for r in range(ROWS - 3):
            for c in range(COLS):
                if all(self.board[r + i][c] == player for i in range(4)):
                    return True
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if all(self.board[r + i][c + i] == player for i in range(4)):
                    return True
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if all(self.board[r - i][c + i] == player for i in range(4)):
                    return True
        return False

    def is_draw(self) -> bool:
        return all(self.board[0][c] != EMPTY for c in range(COLS))

    def get_valid_cols(self) -> List[int]:
        return [c for c in range(COLS) if self.board[0][c] == EMPTY]

    def evaluate(self, player: int) -> int:
        opponent = AI if player == PLAYER else PLAYER
        score = 0
        for r in range(ROWS):
            for c in range(COLS):
                for dr, dc in [(0, 1), (1, 0), (1, 1), (-1, 1)]:
                    if 0 <= r + 3 * dr < ROWS and 0 <= c + 3 * dc < COLS:
                        player_count = 0
                        for i in range(4):
                            val = self.board[r + i * dr][c + i * dc]
                            if val == player:
                                player_count += 1
                            elif val == opponent:
                                player_count -= 2
                        score += player_count
        return score

    def minimax(self, depth: int, alpha: int, beta: int, maximizing: bool) -> Tuple[int, int]:
        valid = self.get_valid_cols()
        if self.check_win(PLAYER):
            return -1000 + (self.ai_depth - depth), -1
        if self.check_win(AI):
            return 1000 - (self.ai_depth - depth), -1
        if not valid or depth == 0:
            return self.evaluate(AI), -1

        if maximizing:
            value = -10**9
            col = valid[0]
            for c in valid:
                row = self.get_next_row(c)
                if row < 0:
                    continue
                self.board[row][c] = AI
                new_score, _ = self.minimax(depth - 1, alpha, beta, False)
                self.board[row][c] = EMPTY
                if new_score > value:
                    value = new_score
                    col = c
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, col
        else:
            value = 10**9
            col = valid[0]
            for c in valid:
                row = self.get_next_row(c)
                if row < 0:
                    continue
                self.board[row][c] = PLAYER
                new_score, _ = self.minimax(depth - 1, alpha, beta, True)
                self.board[row][c] = EMPTY
                if new_score < value:
                    value = new_score
                    col = c
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value, col

    def get_next_row(self, col: int) -> int:
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                return row
        return -1

    def ai_move(self) -> int:
        _, col = self.minimax(self.ai_depth, -10**9, 10**9, True)
        if col < 0:
            valid = self.get_valid_cols()
            col = random.choice(valid) if valid else 0
        return col

    def render_board(self) -> None:
        lines: list[str] = []
        header = " " + "   ".join(str(i + 1) for i in range(COLS))
        lines.append(f"  {C_CYAN}{header}{C_RESET}")
        for r in range(ROWS):
            row_parts = []
            for c in range(COLS):
                val = self.board[r][c]
                if val == PLAYER:
                    row_parts.append(f"{C_YELLOW}\u25CF{C_RESET}")
                elif val == AI:
                    row_parts.append(f"{C_RED}\u25CF{C_RESET}")
                else:
                    row_parts.append(f"{C_WHITE}\u25CB{C_RESET}")
            lines.append("  " + "   ".join(row_parts))
        draw_retro_box(COLS * 4 + 4, "\u25CF CONNECT FOUR \u25CB", lines, color=C_BLUE)
        print(f"\n{C_WHITE}[1-7] Drop  [Q] Quit  [?] Help{C_RESET}")

    def save_state_json(self) -> dict:
        return {
            'board': [row[:] for row in self.board],
            'current_player': self.current_player,
            'move_count': self.move_count,
            'score': self.score,
        }

    def load_state_json(self, state: dict) -> None:
        self.board = [list(row) for row in state.get('board', [[EMPTY] * COLS for _ in range(ROWS)])]
        self.current_player = state.get('current_player', PLAYER)
        self.move_count = state.get('move_count', 0)
        self.score = state.get('score', 0)

    def _show_help(self) -> None:
        show_popup(
            "CONNECT FOUR: Drop pieces into columns (1-7). "
            "First to get 4 in a row (horizontal, vertical, diagonal) wins. "
            "You are Yellow, AI is Red.",
            C_BLUE, delay=2.0
        )

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 1)
                self.render_board()
                turn_text = 'YOUR TURN' if self.current_player == PLAYER else 'AI THINKING...'
                turn_color = C_YELLOW if self.current_player == PLAYER else C_RED
                print(f"\n{C_WHITE}Turn: {turn_color}{turn_text}{C_RESET}")

                if self.current_player == PLAYER:
                    key = self.input_handler.get_safe_key()
                    if key and self._save_and_quit(key.lower()):
                        break
                    if key == '?':
                        self._show_help()
                        continue
                    if key in [str(i) for i in range(1, 8)]:
                        col = int(key) - 1
                        if self.drop_piece(col, PLAYER):
                            beep("correct")
                            if self.check_win(PLAYER):
                                self.score += 200
                                self.award_xp_for_action(100)
                                clear_screen()
                                self.render_board()
                                show_popup("YOU WIN!", C_GREEN, delay=1.5)
                                self.unlock_achievement("connect_four_win", "Connect Four Champion")
                                break
                            if self.is_draw():
                                show_popup("DRAW!", C_YELLOW, delay=1.5)
                                break
                            self.current_player = AI
                else:
                    time.sleep(0.3)
                    col = self.ai_move()
                    self.drop_piece(col, AI)
                    beep("correct")
                    if self.check_win(AI):
                        clear_screen()
                        self.render_board()
                        show_popup("AI WINS!", C_RED, delay=1.5)
                        self.award_xp_for_action(20)
                        break
                    if self.is_draw():
                        show_popup("DRAW!", C_YELLOW, delay=1.5)
                        break
                    self.current_player = PLAYER

                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats


def play_connect_four(difficulty: str = 'normal') -> dict:
    game = ConnectFourGame(difficulty)
    return game.play()
