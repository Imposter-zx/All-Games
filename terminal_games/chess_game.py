import logging
import random
import subprocess
import time
from typing import Optional

from arcade_utils import (
    BG_CUR,
    BG_DARK,
    BG_LIGHT,
    BG_RED,
    BG_SEL,
    C_BLACK,
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    beep,
    clear_screen,
    draw_retro_box,
    particle_effect,
    print_big_title,
    screen_shake,
    show_popup,
    u_safe,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

try:
    import chess
    import chess.engine
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False


def _find_stockfish() -> Optional[str]:
    """Search common paths for a Stockfish executable."""
    candidates = [
        "stockfish", "stockfish.exe",
        r"C:\Program Files\Stockfish\stockfish.exe",
        "/usr/games/stockfish",
        "/usr/local/bin/stockfish",
    ]
    for path in candidates:
        try:
            result = subprocess.run([path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
            if result.returncode == 0 or "Stockfish" in result.stdout.decode('utf-8', errors='ignore'):
                return path
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            continue
    return None


_STOCKFISH_PATH: Optional[str] = _find_stockfish()


class ChessGame(BaseGame):
    """Chess game implementation using BaseGame and python-chess."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("chess", difficulty)
        self.board = chess.Board() if CHESS_AVAILABLE else None
        self.selected_square: Optional[int] = None
        self.cursor_x = 0
        self.cursor_y = 0
        self.u_white = True
        self.input_handler = get_safe_input_handler()
        self.engine: Optional[chess.engine.SimpleEngine] = None

        # Init Stockfish engine if available
        if _STOCKFISH_PATH and CHESS_AVAILABLE:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(_STOCKFISH_PATH)
                # Set skill level based on difficulty
                skill_map = {'easy': 2, 'normal': 8, 'hard': 18}
                skill = skill_map.get(difficulty, 8)
                self.engine.configure({"Skill Level": skill})
                logger.info(f"Stockfish loaded at skill level {skill}")
            except Exception as e:
                logger.warning(f"Could not load Stockfish: {e}")
                self.engine = None

    def save_state_json(self) -> dict:
        if not self.board:
            return {}
        return {
            'fen': self.board.fen(),
            'selected_square': self.selected_square,
            'u_white': self.u_white,
            'score': self.score,
            'moves': [m.uci() for m in self.board.move_stack],
        }

    def load_state_json(self, state: dict) -> None:
        if not CHESS_AVAILABLE:
            return
        fen = state.get('fen', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.board = chess.Board(fen)
        self.selected_square = state.get('selected_square')
        self.u_white = state.get('u_white', True)
        self.score = state.get('score', 0)

    def __del__(self) -> None:
        if self.engine:
            try:
                self.engine.quit()
            except Exception:
                pass

    def play(self) -> dict:
        """Main Chess game loop."""
        if not CHESS_AVAILABLE:
            show_popup("python-chess NOT INSTALLED!", C_RED)
            return self.get_final_stats()

        if not self._select_side():
            return self.get_final_stats()

        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("CHESS", color=C_WHITE)
        time.sleep(1)

        while not self.game_over:
            is_p_turn = self.board.turn == (chess.WHITE if self.u_white else chess.BLACK)
            self.renderer.render_frame(self._render)

            if is_p_turn:
                self._handle_input()
            else:
                self._make_ai_move()

            if self.board.is_game_over():
                self._handle_game_end()

            time.sleep(0.01)

        self.end_timer()

        stats = self.stats_manager.get_stats('chess')
        res = self.board.result()
        won = (res == "1-0" and self.u_white) or (res == "0-1" and not self.u_white)

        is_stalemate = self.board.is_stalemate()
        is_draw = is_stalemate or self.board.is_insufficient_material()
        self.save_stats({
            'wins': stats.get('wins', 0) + (1 if won else 0),
            'draws': stats.get('draws', 0) + (1 if is_draw else 0),
            'losses': stats.get('losses', 0) + (1 if not won and not is_stalemate else 0),
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })

        return self.get_final_stats()

    def _select_side(self) -> bool:
        clear_screen()
        draw_retro_box(40, "CHESS ARCADE", ["SELECT YOUR SIDE", "(W) WHITE", "(B) BLACK", "(Q) QUIT"], color=C_MAGENTA)
        while True:
            choice = self.input_handler.get_safe_key()
            if not choice:
                continue
            if choice in ['q', 'Q']:
                return False
            if choice in ['w', 'W', '\r', '\n', 'enter']:
                self.u_white = True
                return True
            if choice in ['b', 'B']:
                self.u_white = False
                return True

    def _render(self) -> None:
        turn_color = f"{C_WHITE}WHITE" if self.board.turn == chess.WHITE else f"{C_MAGENTA}BLACK"
        engine_status = f" {C_GREEN}[Stockfish]{C_RESET}" if self.engine else f" {C_RED}[Random AI]{C_RESET}"
        print(f" {C_WHITE}CHESS ARCADE {C_RESET}| Turn: {turn_color}{C_RESET}{engine_status}")
        print("  a b c d e f g h")

        for r in range(7, -1, -1):
            line = f"{r+1} "
            for f in range(8):
                square = chess.square(f, r)
                piece = self.board.piece_at(square)
                bg = BG_LIGHT if (r + f) % 2 == 1 else BG_DARK
                if (f, r) == (self.cursor_x, self.cursor_y):
                    bg = BG_CUR
                if square == self.selected_square:
                    bg = BG_SEL
                is_check = self.board.is_check() and piece.color == self.board.turn
                if piece and piece.piece_type == chess.KING and is_check:
                    bg = BG_RED
                symbol = " "
                if piece:
                    symbol = u_safe(piece.unicode_symbol(), piece.symbol())
                fg = C_WHITE if piece and piece.color == chess.WHITE else C_MAGENTA
                if (f, r) == (self.cursor_x, self.cursor_y):
                    fg = C_BLACK
                line += f"{bg}{fg}{symbol} {C_RESET}"
            print(line + f" {r+1}")
        print("  a b c d e f g h")
        print(f"\n{C_WHITE}ARROWS/WASD: Move | SPACE/ENTER: Select | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        elif k == 'h':
            show_popup("CHESS: Select piece, then target square. Promotions auto-queen.", C_CYAN, delay=1.5)
        elif k in [' ', '\r', '\n', 'enter']:
            self._handle_selection()
        else:
            direction = self.input_handler.validator.validate_direction(k)
            if direction == 'up':
                self.cursor_y = min(7, self.cursor_y + 1)
            elif direction == 'down':
                self.cursor_y = max(0, self.cursor_y - 1)
            elif direction == 'left':
                self.cursor_x = max(0, self.cursor_x - 1)
            elif direction == 'right':
                self.cursor_x = min(7, self.cursor_x + 1)

    def _handle_selection(self) -> None:
        square = chess.square(self.cursor_x, self.cursor_y)
        player_color = chess.WHITE if self.u_white else chess.BLACK

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == player_color:
                self.selected_square = square
                beep("correct")
        else:
            move = chess.Move(self.selected_square, square)
            piece = self.board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN:
                rank = chess.square_rank(square)
                is_promotion = (self.u_white and rank == 7) or (not self.u_white and rank == 0)
                if is_promotion:
                    move.promotion = chess.QUEEN

            if move in self.board.legal_moves:
                if self.board.is_capture(move):
                    screen_shake(0.1, 1)
                    particle_effect(char="*", color=C_RED, count=5)
                    beep("eat")
                self.board.push(move)
                self.score += 10
                self.award_xp_for_action(5)
                beep("correct")
                self.selected_square = None
            elif square == self.selected_square:
                self.selected_square = None
            else:
                piece = self.board.piece_at(square)
                if piece and piece.color == player_color:
                    self.selected_square = square
                else:
                    beep("invalid")
                    self.selected_square = None

    def _make_ai_move(self) -> None:
        """Make an AI move using Stockfish or random fallback."""
        time.sleep(0.3)
        if not self.board.is_game_over():
            move = self._get_ai_move()
            if move:
                if self.board.is_capture(move):
                    screen_shake(0.1, 1)
                self.board.push(move)
                beep("lose")

    def _get_ai_move(self) -> Optional[chess.Move]:
        """Generate AI move. Prefer Stockfish, fallback to random."""
        if self.engine:
            try:
                time_limit = {'easy': 0.05, 'normal': 0.2, 'hard': 1.0}
                limit = time_limit.get(self.difficulty, 0.2)
                result = self.engine.play(self.board, chess.engine.Limit(time=limit))
                return result.move
            except Exception as e:
                logger.warning(f"Stockfish error: {e}")

        # Fallback: random with basic heuristics
        try:
            legal = list(self.board.legal_moves)
            if not legal:
                return None
            # Prefer captures and checks for a slightly better random AI
            capture_moves = [m for m in legal if self.board.is_capture(m)]
            if capture_moves and random.random() < 0.6:
                return random.choice(capture_moves)
            return random.choice(legal)
        except Exception:
            return None

    def _handle_game_end(self) -> None:
        result = self.board.result()
        won = (result == "1-0" and self.u_white) or (result == "0-1" and not self.u_white)

        if won:
            self.unlock_achievement("chess_win", "Grandmaster")
            show_popup("VICTORY! YOU WON!", C_GREEN)
            self.award_xp_for_action(100)
        elif result == "1/2-1/2":
            show_popup("DRAW!", C_WHITE)
            self.award_xp_for_action(50)
        else:
            show_popup("DEFEAT!", C_RED)

        self.game_over = True


def play_chess(difficulty: str = 'normal') -> Optional[dict]:
    """Wrapper function for arcade.py compatibility."""
    if not CHESS_AVAILABLE:
        show_popup("python-chess missing!", C_RED)
        return None
    game = ChessGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_chess()
