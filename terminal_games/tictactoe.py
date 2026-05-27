import logging
import random
import time
from typing import List, Optional, Tuple

from arcade_utils import (
    C_BLUE,
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

BOARD_SIZE = 3
EMPTY = "."
PLAYER_X = "X"
PLAYER_O = "O"


def _print_board(board: List[List[str]], highlight: Optional[List[Tuple[int, int]]] = None) -> None:
    highlight = highlight or []
    print(f"\n  {C_YELLOW}   A   B   C{C_RESET}")
    for r in range(BOARD_SIZE):
        row_str = f"  {C_YELLOW}{r + 1}{C_RESET} "
        for c in range(BOARD_SIZE):
            cell = board[r][c]
            if (r, c) in highlight:
                color = C_GREEN
            elif cell == PLAYER_X:
                color = C_BLUE
            elif cell == PLAYER_O:
                color = C_RED
            else:
                color = C_WHITE
            row_str += f" {color}{cell}{C_RESET} "
            if c < BOARD_SIZE - 1:
                row_str += f"{C_YELLOW}|{C_RESET}"
        print(row_str)
        if r < BOARD_SIZE - 1:
            print(f"     {C_YELLOW}---+---+---{C_RESET}")


def _check_winner(board: List[List[str]]) -> Optional[str]:
    for r in range(BOARD_SIZE):
        if board[r][0] != EMPTY and board[r][0] == board[r][1] == board[r][2]:
            return board[r][0]
    for c in range(BOARD_SIZE):
        if board[0][c] != EMPTY and board[0][c] == board[1][c] == board[2][c]:
            return board[0][c]
    if board[0][0] != EMPTY and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] != EMPTY and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    return None


def _is_full(board: List[List[str]]) -> bool:
    return all(cell != EMPTY for row in board for cell in row)


def _get_winner_line(board: List[List[str]], winner: str) -> List[Tuple[int, int]]:
    for r in range(BOARD_SIZE):
        if board[r][0] == board[r][1] == board[r][2] == winner:
            return [(r, 0), (r, 1), (r, 2)]
    for c in range(BOARD_SIZE):
        if board[0][c] == board[1][c] == board[2][c] == winner:
            return [(0, c), (1, c), (2, c)]
    if board[0][0] == board[1][1] == board[2][2] == winner:
        return [(0, 0), (1, 1), (2, 2)]
    if board[0][2] == board[1][1] == board[2][0] == winner:
        return [(0, 2), (1, 1), (2, 0)]
    return []


def _parse_move(text: str) -> Optional[Tuple[int, int]]:
    text = text.strip().upper()
    if len(text) < 2:
        return None
    col = ord(text[0]) - ord("A")
    row = int(text[1]) - 1
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return (row, col)
    return None


def _get_empty_cells(board: List[List[str]]) -> List[Tuple[int, int]]:
    return [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == EMPTY]


def _minimax(board: List[List[str]], depth: int, is_max: bool, ai_piece: str, human_piece: str) -> int:
    winner = _check_winner(board)
    if winner == ai_piece:
        return 10 - depth
    if winner == human_piece:
        return depth - 10
    if _is_full(board):
        return 0

    if is_max:
        best = -1000
        for r, c in _get_empty_cells(board):
            board[r][c] = ai_piece
            score = _minimax(board, depth + 1, False, ai_piece, human_piece)
            board[r][c] = EMPTY
            best = max(best, score)
        return best
    else:
        best = 1000
        for r, c in _get_empty_cells(board):
            board[r][c] = human_piece
            score = _minimax(board, depth + 1, True, ai_piece, human_piece)
            board[r][c] = EMPTY
            best = min(best, score)
        return best


def _ai_move(board: List[List[str]], ai_piece: str, difficulty: str) -> Tuple[int, int]:
    human_piece = PLAYER_O if ai_piece == PLAYER_X else PLAYER_X
    empty = _get_empty_cells(board)

    if difficulty == "easy":
        return random.choice(empty)

    best_score = -1000
    best_move = empty[0]
    for r, c in empty:
        board[r][c] = ai_piece
        score = _minimax(board, 0, False, ai_piece, human_piece)
        board[r][c] = EMPTY
        if score > best_score:
            best_score = score
            best_move = (r, c)

    if difficulty == "hard":
        return best_move
    if random.random() < 0.3:
        return random.choice(empty)
    return best_move


class TicTacToeGame(BaseGame):
    def __init__(self, difficulty: str = "normal") -> None:
        super().__init__("tictactoe", difficulty)
        self.board: List[List[str]] = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_X
        self.mode: str = "ai"
        self.ai_piece = PLAYER_O
        self.human_piece = PLAYER_X
        self.round = 1
        self.streak = 0
        self.wins = 0
        self.perfect_games = 0

    def _reset_board(self) -> None:
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_X

    def _switch_player(self) -> None:
        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X

    def save_state_json(self) -> dict:
        return {
            "board": [list(row) for row in self.board],
            "current_player": self.current_player,
            "mode": self.mode,
            "ai_piece": self.ai_piece,
            "human_piece": self.human_piece,
            "score": self.score,
            "round": self.round,
            "streak": self.streak,
            "wins": self.wins,
            "perfect_games": self.perfect_games,
        }

    def load_state_json(self, state: dict) -> None:
        self.board = [list(row) for row in state.get("board", [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)])]
        self.current_player = state.get("current_player", PLAYER_X)
        self.mode = state.get("mode", "ai")
        self.ai_piece = state.get("ai_piece", PLAYER_O)
        self.human_piece = state.get("human_piece", PLAYER_X)
        self.score = state.get("score", 0)
        self.round = state.get("round", 1)
        self.streak = state.get("streak", 0)
        self.wins = state.get("wins", 0)
        self.perfect_games = state.get("perfect_games", 0)

    def _select_mode(self) -> Optional[str]:
        options = ["1-Player (vs AI)", "2-Player (Local)"]
        selection = 0
        while True:
            clear_screen()
            print("\n" * 2)
            lines: list[str] = []
            for i, opt in enumerate(options):
                marker = f"{C_YELLOW}►{C_RESET} " if i == selection else "  "
                style = f"{C_YELLOW}" if i == selection else f"{C_WHITE}"
                lines.append(f"{marker}{style}{opt}{C_RESET}")
            draw_retro_box(30, "TIC-TAC-TOE MODE", lines, color=C_CYAN)
            print(f"\n  {C_WHITE}[UP/DOWN] Select  [ENTER] Confirm  [Q] Back{C_RESET}")

            key = get_safe_input_handler().get_safe_key()
            if key == "up":
                selection = (selection - 1) % len(options)
                beep("move")
            elif key == "down":
                selection = (selection + 1) % len(options)
                beep("move")
            elif key in ["\r", "\n", " ", "enter"]:
                beep("win")
                return options[selection]
            elif key and key.lower() == "q":
                return None
            time.sleep(0.05)

    def _render(self, highlight: Optional[List[Tuple[int, int]]] = None) -> None:
        mode_label = "1P vs AI" if self.mode == "ai" else "2-Player"
        lines: list[str] = [
            f"{C_CYAN}ROUND {self.round}{C_RESET}   MODE: {mode_label}   DIFFICULTY: {self.difficulty.upper()}",
            "",
        ]
        draw_retro_box(30, "TIC-TAC-TOE", lines, color=C_GREEN)
        _print_board(self.board, highlight)
        print(f"\n  {C_WHITE}Enter move (e.g. A1, B2, C3)  [Q] Quit  [?] Help{C_RESET}")

    def _show_help(self) -> None:
        show_popup(
            "TIC-TAC-TOE: Get 3 in a row to win! "
            f"{C_BLUE}X{C_RESET} goes first. Enter moves as column+row (A1, B2, C3). "
            "vs AI plays against the computer.",
            C_GREEN, delay=2.0,
        )

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        else:
            mode_choice = self._select_mode()
            if mode_choice is None:
                self.end_timer()
                return self.get_final_stats()
            self.mode = "ai" if "AI" in mode_choice else "2p"
            self.ai_piece = PLAYER_O
            self.human_piece = PLAYER_X

        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 1)
                self._render()

                winner = _check_winner(self.board)

                if winner:
                    highlight = _get_winner_line(self.board, winner)
                    clear_screen()
                    print("\n" * 1)
                    self._render(highlight)

                    if (self.mode == "ai" and winner == self.human_piece) or \
                       (self.mode == "2p"):
                        xp = 50 + self.round * 10
                        self.score += 100 + xp
                        self.award_xp_for_action(xp)
                        self.wins += 1
                        self.streak += 1
                        if self.streak >= 3:
                            self.unlock_achievement("tictactoe_streak", "Tic-Tac-Toe Streak")
                        if self.streak >= 5:
                            self.unlock_achievement("tictactoe_streak_5", "Unstoppable")
                        self.unlock_achievement("tictactoe_win", "Tic-Tac-Toe Champion")

                        if self.mode == "ai":
                            ai_moves = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                                           if self.board[r][c] == self.ai_piece)
                            if ai_moves == 0:
                                self.perfect_games += 1
                                self.unlock_achievement("tictactoe_perfect", "Perfect Game")

                        beep("win")
                        show_popup(f"PLAYER {winner} WINS! Round {self.round}", C_GREEN, delay=1.5)
                    else:
                        show_popup(f"AI ({winner}) WINS! Round {self.round}", C_RED, delay=1.5)
                        self.streak = 0

                    self.round += 1
                    self._reset_board()
                    continue

                if _is_full(self.board):
                    show_popup("DRAW! Round {0}".format(self.round), C_YELLOW, delay=1.5)
                    self.streak = 0
                    self.round += 1
                    self._reset_board()
                    continue

                if self.mode == "ai" and self.current_player == self.ai_piece:
                    print(f"\n  {C_MAGENTA}AI thinking...{C_RESET}")
                    time.sleep(0.5)
                    r, c = _ai_move(self.board, self.ai_piece, self.difficulty)
                    self.board[r][c] = self.ai_piece
                    self._switch_player()
                    beep("move")
                    continue

                if self.mode == "2p":
                    turn_label = (
                        f"{C_BLUE}Player X{C_RESET}"
                        if self.current_player == PLAYER_X
                        else f"{C_RED}Player O{C_RESET}"
                    )
                    print(f"\n  {turn_label}{C_WHITE}'s turn{C_RESET}")

                key = input_handler.get_safe_key()
                if not key:
                    time.sleep(0.05)
                    continue

                if self._save_and_quit(key.lower()):
                    break
                if key == "?":
                    self._show_help()
                    continue

                if key in ["\r", "\n", "enter"]:
                    continue

                if key.isalpha():
                    if len(key) > 1:
                        continue
                    col = key.upper()
                    row_input = input_handler.get_safe_key()
                    if row_input and row_input.isdigit():
                        move_text = col + row_input
                        move = _parse_move(move_text)
                        if move and self.board[move[0]][move[1]] == EMPTY:
                            self.board[move[0]][move[1]] = self.current_player
                            self._switch_player()
                            beep("correct")
                        else:
                            beep("lose")
                    continue

                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            final_stats["high_score"] = self.score
            self.save_stats(final_stats)
            return final_stats


def play_tictactoe(difficulty: str = "normal") -> dict:
    game = TicTacToeGame(difficulty)
    return game.play()
