import logging
import random
import time
from typing import Dict, List, Optional, Set, Tuple

from arcade_utils import (
    C_BLACK,
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

BOARD_SIZE = 15
EMPTY = '.'
PLAYER = 'X'
AI_PIECE = 'O'

DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]


class GomokuGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('gomoku', difficulty)
        self.board: List[List[str]] = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER
        self.winner: Optional[str] = None
        self.round = 1
        self.wins = 0
        self.streak = 0
        self.high_score = 0
        self.last_move: Optional[Tuple[int, int]] = None
        self.ai_think_time = 0.5 if difficulty == 'hard' else 0.2
        self.ai_depth = 2 if difficulty == 'hard' else 1

    def _reset_board(self) -> None:
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER
        self.winner = None
        self.last_move = None

    def _is_full(self) -> bool:
        return all(cell != EMPTY for row in self.board for cell in row)

    def _check_win_at(self, row: int, col: int) -> Optional[str]:
        piece = self.board[row][col]
        if piece == EMPTY:
            return None
        for dr, dc in DIRECTIONS:
            count = 1
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == piece:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == piece:
                    count += 1
                else:
                    break
            if count >= 5:
                return piece
        return None

    def _evaluate_line(self, row: int, col: int, dr: int, dc: int, piece: str) -> int:
        count = 0
        open_ends = 0
        for i in range(1, 5):
            r, c = row + dr * i, col + dc * i
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if self.board[r][c] == piece:
                    count += 1
                elif self.board[r][c] == EMPTY:
                    open_ends += 1
                    break
                else:
                    break
            else:
                break
        for i in range(1, 5):
            r, c = row - dr * i, col - dc * i
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if self.board[r][c] == piece:
                    count += 1
                elif self.board[r][c] == EMPTY:
                    open_ends += 1
                    break
                else:
                    break
            else:
                break
        if count >= 4:
            return 100000
        scores = {0: 0, 1: 10, 2: 100, 3: 1000, 4: 10000}
        multiplier = 2 if open_ends >= 2 else 1
        return scores.get(count, 0) * multiplier

    def _score_cell(self, row: int, col: int, for_piece: str) -> int:
        score = 0
        for dr, dc in DIRECTIONS:
            score += self._evaluate_line(row, col, dr, dc, for_piece)
        return score

    def _ai_move(self) -> Tuple[int, int]:
        best_score = -1
        best_moves: List[Tuple[int, int]] = []
        candidates = self._get_candidates()

        for row, col in candidates:
            attack = self._score_cell(row, col, AI_PIECE)
            defense = self._score_cell(row, col, PLAYER)
            score = attack * 1.1 + defense
            if random.random() < 0.1 and self.difficulty == 'easy':
                score += random.randint(-50, 50)
            if score > best_score:
                best_score = score
                best_moves = [(row, col)]
            elif score == best_score:
                best_moves.append((row, col))

        return random.choice(best_moves)

    def _get_candidates(self) -> List[Tuple[int, int]]:
        candidates: Set[Tuple[int, int]] = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == EMPTY:
                                candidates.add((nr, nc))
        if not candidates:
            return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
        return list(candidates)

    def _render(self) -> None:
        lines = [
            f"{C_CYAN}ROUND {self.round}  DIFFICULTY: {self.difficulty.upper()}{C_RESET}",
            f"{C_WHITE}You: {C_GREEN}X{C_RESET}  AI: {C_RED}O{C_RESET}  Streak: {self.streak}{C_RESET}",
        ]
        draw_retro_box(40, "\u2B1C GOMOKU \u2B1B", lines, color=C_CYAN)

        print(f"\n  {C_YELLOW}   ", end="")
        for c in range(BOARD_SIZE):
            print(f"{chr(97 + c):>2}", end="")
        print(f"{C_RESET}")

        for r in range(BOARD_SIZE):
            print(f"  {C_YELLOW}{r + 1:>2}{C_RESET} ", end="")
            for c in range(BOARD_SIZE):
                cell = self.board[r][c]
                if cell == PLAYER:
                    print(f" {C_GREEN}X{C_RESET}", end="")
                elif cell == AI_PIECE:
                    print(f" {C_RED}O{C_RESET}", end="")
                else:
                    print(f" {C_BLACK}.{C_RESET}", end="")
            print(f"  {C_YELLOW}{r + 1}{C_RESET}")

        print(f"  {C_YELLOW}   ", end="")
        for c in range(BOARD_SIZE):
            print(f"{chr(97 + c):>2}", end="")
        print(f"{C_RESET}")

        if self.winner:
            if self.winner == PLAYER:
                print(f"\n{C_GREEN}YOU WIN!{C_RESET}")
            elif self.winner == AI_PIECE:
                print(f"\n{C_RED}AI WINS!{C_RESET}")
            print(f"\n{C_WHITE}[Any Key] Continue  [Q] Quit{C_RESET}")
        elif self._is_full():
            print(f"\n{C_YELLOW}DRAW!{C_RESET}")
            print(f"\n{C_WHITE}[Any Key] Continue  [Q] Quit{C_RESET}")
        else:
            print(f"\n{C_WHITE}Enter move (e.g. h8 or a1)  [Q] Quit  [?] Help{C_RESET}")

    def _show_help(self) -> None:
        show_popup(
            "GOMOKU: Get 5 in a row on the 15x15 board! "
            "Enter moves as letter+number (e.g. h8 for center). "
            "Black (X) goes first. Line up 5 horizontally, "
            "vertically, or diagonally to win.",
            C_CYAN, delay=2.5
        )

    def _parse_move(self, text: str) -> Optional[Tuple[int, int]]:
        text = text.strip().lower()
        if len(text) < 2:
            return None
        col = ord(text[0]) - ord('a')
        if not text[1:].isdigit():
            return None
        row = int(text[1:]) - 1
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return (row, col)
        return None

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

                if self.winner or self._is_full():
                    if self.winner == PLAYER:
                        self.score += 100
                        self.wins += 1
                        self.streak += 1
                        if self.score > self.high_score:
                            self.high_score = self.score
                        self.award_xp_for_action(50)
                        if self.streak >= 3:
                            self.unlock_achievement("gomoku_streak_3", "Gomoku Streak")
                    elif self.winner == AI_PIECE:
                        self.streak = 0
                    else:
                        self.award_xp_for_action(10)
                    self.end_timer()
                    final_stats = self.get_final_stats()
                    final_stats['high_score'] = self.high_score
                    final_stats['wins'] = self.wins
                    final_stats['streak'] = self.streak
                    self.save_stats(final_stats)

                    key = input_handler.get_safe_key()
                    if key and self._save_and_quit(key.lower()):
                        break
                    if key:
                        self.round += 1
                        self._reset_board()
                        self.start_timer()
                    continue

                if self.current_player == AI_PIECE:
                    time.sleep(self.ai_think_time)
                    row, col = self._ai_move()
                    self.board[row][col] = AI_PIECE
                    self.last_move = (row, col)
                    self.winner = self._check_win_at(row, col)
                    self.current_player = PLAYER
                    beep("correct")
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

                move = self._parse_move(key)
                if move:
                    row, col = move
                    if self.board[row][col] == EMPTY:
                        self.board[row][col] = PLAYER
                        self.last_move = (row, col)
                        self.winner = self._check_win_at(row, col)
                        if not self.winner:
                            self.current_player = AI_PIECE
                        beep("correct")
                    else:
                        beep("lose")

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            stats = self.get_final_stats()
            stats['high_score'] = self.high_score
            stats['wins'] = self.wins
            self.save_stats(stats)
            return stats


def play_gomoku(difficulty: str = 'normal') -> dict:
    game = GomokuGame(difficulty)
    return game.play()
