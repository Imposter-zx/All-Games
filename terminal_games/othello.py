import logging
import random
import time
from typing import Dict, List, Optional, Tuple

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

BOARD_SIZE = 8
EMPTY = '.'
BLACK = 'B'
WHITE = 'W'

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

POSITION_WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   1,   1,   1,   1,  -2,  10],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [ 10,  -2,   1,   1,   1,   1,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]


def opponent(piece: str) -> str:
    return BLACK if piece == WHITE else WHITE


class OthelloGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('othello', difficulty)
        self.board: List[List[str]] = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.board[3][3] = WHITE
        self.board[3][4] = BLACK
        self.board[4][3] = BLACK
        self.board[4][4] = WHITE
        self.current_player = BLACK
        self.wins = 0
        self.streak = 0
        self.high_score = 0
        self.human_piece = BLACK
        self.ai_piece = WHITE

    def _is_valid(self, row: int, col: int, piece: str) -> bool:
        if self.board[row][col] != EMPTY:
            return False
        opp = opponent(piece)
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == opp:
                r += dr
                c += dc
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == opp:
                    r += dr
                    c += dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == piece:
                    return True
        return False

    def _get_valid_moves(self, piece: str) -> List[Tuple[int, int]]:
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self._is_valid(r, c, piece):
                    moves.append((r, c))
        return moves

    def _flip(self, row: int, col: int, piece: str) -> None:
        self.board[row][col] = piece
        opp = opponent(piece)
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            to_flip = []
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == opp:
                to_flip.append((r, c))
                r += dr
                c += dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == piece:
                for fr, fc in to_flip:
                    self.board[fr][fc] = piece

    def _count(self, piece: str) -> int:
        return sum(row.count(piece) for row in self.board)

    def _score_board(self, piece: str) -> int:
        opp = opponent(piece)
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == piece:
                    score += POSITION_WEIGHTS[r][c]
                elif self.board[r][c] == opp:
                    score -= POSITION_WEIGHTS[r][c]
        moves = len(self._get_valid_moves(piece))
        opp_moves = len(self._get_valid_moves(opp))
        score += moves * 5
        score -= opp_moves * 5
        return score

    def _ai_move(self) -> Optional[Tuple[int, int]]:
        moves = self._get_valid_moves(self.ai_piece)
        if not moves:
            return None
        if self.difficulty == 'easy':
            return random.choice(moves)
        best_score = -999999
        best_moves = []
        for r, c in moves:
            saved = [list(row) for row in self.board]
            self._flip(r, c, self.ai_piece)
            score = self._score_board(self.ai_piece)
            if self.difficulty == 'hard':
                opp_moves2 = self._get_valid_moves(opponent(self.ai_piece))
                score2 = 0
                for r2, c2 in opp_moves2:
                    saved2 = [list(row) for row in self.board]
                    self._flip(r2, c2, opponent(self.ai_piece))
                    score2 += self._score_board(self.ai_piece)
                    self.board = [list(row) for row in saved2]
                score -= score2 / max(1, len(opp_moves2))
            self.board = [list(row) for row in saved]
            if score > best_score:
                best_score = score
                best_moves = [(r, c)]
            elif score == best_score:
                best_moves.append((r, c))
        return random.choice(best_moves) if best_moves else None

    def _is_game_over(self) -> bool:
        return not self._get_valid_moves(BLACK) and not self._get_valid_moves(WHITE)

    def _render(self) -> None:
        lines = [
            f"{C_CYAN}DIFFICULTY: {self.difficulty.upper()}{C_RESET}",
            f"{C_GREEN}● You ({'B' if self.human_piece == BLACK else 'W'}){C_RESET}  "
            f"{C_RED}○ AI ({'W' if self.ai_piece == WHITE else 'B'}){C_RESET}  "
            f"{C_WHITE}Wins: {self.wins}  Streak: {self.streak}{C_RESET}",
        ]
        draw_retro_box(40, "\u25CB OTHELLO \u25CF", lines, color=C_GREEN)

        print(f"\n  {C_YELLOW}  ", end="")
        for c in range(BOARD_SIZE):
            print(f" {chr(97 + c)}", end="")
        print(f"{C_RESET}")
        for r in range(BOARD_SIZE):
            print(f"  {C_YELLOW}{r + 1}{C_RESET} ", end="")
            for c in range(BOARD_SIZE):
                cell = self.board[r][c]
                if cell == BLACK:
                    print(f" {C_GREEN}\u25CF{C_RESET}", end="")
                elif cell == WHITE:
                    print(f" {C_RED}\u25CB{C_RESET}", end="")
                else:
                    print(f" {C_WHITE}.{C_RESET}", end="")
            print(f"  {C_YELLOW}{r + 1}{C_RESET}")
        print(f"  {C_YELLOW}  ", end="")
        for c in range(BOARD_SIZE):
            print(f" {chr(97 + c)}", end="")
        print(f"{C_RESET}")
        print(f"\n  {C_WHITE}● {self._count(BLACK)}  ○ {self._count(WHITE)}{C_RESET}")

        if self._is_game_over():
            b = self._count(BLACK)
            w = self._count(WHITE)
            if b > w:
                print(f"\n{C_GREEN}YOU WIN! {b}-{w}{C_RESET}")
            elif w > b:
                print(f"\n{C_RED}AI WINS! {w}-{b}{C_RESET}")
            else:
                print(f"\n{C_YELLOW}DRAW! {b}-{w}{C_RESET}")
            print(f"\n{C_WHITE}[Any Key] Play Again  [Q] Quit{C_RESET}")
        elif self.current_player == self.ai_piece:
            print(f"\n{C_WHITE}AI is thinking...{C_RESET}")
        else:
            moves = self._get_valid_moves(self.human_piece)
            if not moves:
                print(f"\n{C_YELLOW}No valid moves — passing.{C_RESET}")
            else:
                valid_str = ", ".join(f"{chr(97 + c)}{r + 1}" for r, c in moves[:8])
                if len(moves) > 8:
                    valid_str += f"... +{len(moves) - 8} more"
                print(f"\n{C_WHITE}Enter move (e.g. d3)  [Q] Quit  [?] Help{C_RESET}")
                print(f"  {C_CYAN}Valid: {valid_str}{C_RESET}")

    def _show_help(self) -> None:
        show_popup(
            "OTHELLO: Place pieces to outflank your opponent. "
            "You must sandwich opponent pieces between your new piece "
            "and an existing piece. All sandwiched pieces flip to your color. "
            "Enter moves as letter+number (e.g. e3). "
            "The player with the most pieces at the end wins!",
            C_GREEN, delay=3.0
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

                if self._is_game_over():
                    b = self._count(BLACK)
                    w = self._count(WHITE)
                    if b > w:
                        self.score += 100
                        self.wins += 1
                        self.streak += 1
                        if self.streak >= 3:
                            self.unlock_achievement("othello_streak_3", "Othello Streak")
                        if self.score > self.high_score:
                            self.high_score = self.score
                        self.award_xp_for_action(50)
                    elif w > b:
                        self.streak = 0
                    else:
                        self.award_xp_for_action(20)
                    self.end_timer()
                    final_stats = self.get_final_stats()
                    final_stats['high_score'] = self.high_score
                    final_stats['wins'] = self.wins
                    self.save_stats(final_stats)
                    key = input_handler.get_safe_key()
                    if key and self._save_and_quit(key.lower()):
                        break
                    if key:
                        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
                        self.board[3][3] = WHITE
                        self.board[3][4] = BLACK
                        self.board[4][3] = BLACK
                        self.board[4][4] = WHITE
                        self.current_player = BLACK
                        self.start_timer()
                    continue

                if self.current_player == self.ai_piece:
                    moves = self._get_valid_moves(self.ai_piece)
                    if not moves:
                        self.current_player = self.human_piece
                        continue
                    time.sleep(0.5)
                    move = self._ai_move()
                    if move:
                        self._flip(move[0], move[1], self.ai_piece)
                        beep("correct")
                    self.current_player = self.human_piece
                    continue

                moves = self._get_valid_moves(self.human_piece)
                if not moves:
                    self.current_player = self.ai_piece
                    beep("lose")
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
                if move and self._is_valid(move[0], move[1], self.human_piece):
                    self._flip(move[0], move[1], self.human_piece)
                    beep("correct")
                    self.current_player = self.ai_piece
                elif move:
                    beep("lose")

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            stats = self.get_final_stats()
            stats['high_score'] = self.high_score
            return stats


def play_othello(difficulty: str = 'normal') -> dict:
    game = OthelloGame(difficulty)
    return game.play()
