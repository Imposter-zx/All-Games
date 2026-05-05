import os
import time
import logging
import random
from arcade_utils import (
    clear_screen, get_key, draw_retro_box, beep, show_popup, 
    update_stats, load_stats, animated_flash, print_big_title, 
    add_xp, screen_shake, particle_effect, 
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK,
    BG_DARK, BG_LIGHT, BG_CUR, BG_SEL, BG_RED
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

class ChessGame(BaseGame):
    """Chess game implementation using BaseGame and python-chess."""
    
    def __init__(self, difficulty='normal'):
        super().__init__("chess", difficulty)
        self.board = chess.Board() if CHESS_AVAILABLE else None
        self.selected_square = None
        self.cursor_x = 0
        self.cursor_y = 0
        self.u_white = True
        self.input_handler = get_safe_input_handler()
        
    def play(self) -> dict:
        """Main Chess game loop."""
        if not CHESS_AVAILABLE:
            show_popup("python-chess NOT INSTALLED!", C_RED)
            return self.get_final_stats()
            
        if not self._select_side():
            return self.get_final_stats()
            
        self.start_timer()
        clear_screen()
        print_big_title("CHESS", color=C_WHITE)
        time.sleep(1)
        
        while not self.game_over:
            is_p_turn = self.board.turn == (chess.WHITE if self.u_white else chess.BLACK)
            self._render()
            
            if is_p_turn:
                self._handle_input()
            else:
                self._make_ai_move()
                
            if self.board.is_game_over():
                self._handle_game_end()
                
        self.end_timer()
        
        # Save stats
        stats = self.stats_manager.get_stats('chess')
        res = self.board.result()
        won = (res == "1-0" and self.u_white) or (res == "0-1" and not self.u_white)
        
        self.save_stats({
            'wins': stats.get('wins', 0) + (1 if won else 0),
            'draws': stats.get('draws', 0) + (1 if self.board.is_stalemate() or self.board.is_insufficient_material() else 0),
            'losses': stats.get('losses', 0) + (1 if not won and not self.board.is_stalemate() else 0),
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })
        
        return self.get_final_stats()

    def _select_side(self) -> bool:
        """Let player choose color."""
        clear_screen()
        draw_retro_box(40, "CHESS ARCADE", ["SELECT YOUR SIDE", "(W) WHITE", "(B) BLACK", "(Q) QUIT"], color=C_MAGENTA)
        while True:
            choice = self.input_handler.get_safe_key()
            if not choice: continue
            if choice in ['q', 'Q']: return False
            if choice in ['w', 'W', '\r', '\n', 'enter']:
                self.u_white = True
                return True
            if choice in ['b', 'B']:
                self.u_white = False
                return True

    def _render(self):
        """Render the chess board."""
        clear_screen()
        turn_color = f"{C_WHITE}WHITE" if self.board.turn == chess.WHITE else f"{C_MAGENTA}BLACK"
        print(f" {C_WHITE}CHESS ARCADE {C_RESET}| Turn: {turn_color}{C_RESET}")
        print("  a b c d e f g h")
        
        for r in range(7, -1, -1):
            line = f"{r+1} "
            for f in range(8):
                square = chess.square(f, r)
                piece = self.board.piece_at(square)
                
                # Background
                bg = BG_LIGHT if (r + f) % 2 == 1 else BG_DARK
                if (f, r) == (self.cursor_x, self.cursor_y): bg = BG_CUR
                if square == self.selected_square: bg = BG_SEL
                
                # Check flash
                if piece and piece.piece_type == chess.KING and self.board.is_check() and piece.color == self.board.turn:
                    bg = BG_RED
                
                symbol = " "
                if piece:
                    symbol = piece.unicode_symbol()
                
                # Piece color
                fg = C_WHITE if piece and piece.color == chess.WHITE else C_MAGENTA
                if (f, r) == (self.cursor_x, self.cursor_y): fg = C_BLACK
                
                line += f"{bg}{fg}{symbol} {C_RESET}"
            print(line + f" {r+1}")
        print("  a b c d e f g h")
        print(f"\n{C_WHITE}ARROWS/WASD: Move | SPACE/ENTER: Select | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle movement and selection using SafeInputHandler."""
        k = self.input_handler.get_safe_key()
        if not k:
            return
            
        if k == 'q':
            self.game_over = True
        elif k in [' ', '\r', '\n', 'enter']:
            self._handle_selection()
        else:
            direction = self.input_handler.validator.validate_direction(k)
            if direction == 'up': self.cursor_y = min(7, self.cursor_y + 1)
            elif direction == 'down': self.cursor_y = max(0, self.cursor_y - 1)
            elif direction == 'left': self.cursor_x = max(0, self.cursor_x - 1)
            elif direction == 'right': self.cursor_x = min(7, self.cursor_x + 1)

    def _handle_selection(self):
        """Handle piece selection and movement."""
        square = chess.square(self.cursor_x, self.cursor_y)
        player_color = chess.WHITE if self.u_white else chess.BLACK
        
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == player_color:
                self.selected_square = square
                beep("correct")
        else:
            # Try to move
            move = chess.Move(self.selected_square, square)
            # Check for promotion
            piece = self.board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN:
                if (self.u_white and chess.square_rank(square) == 7) or (not self.u_white and chess.square_rank(square) == 0):
                    move.promotion = chess.QUEEN
                
            if move in self.board.legal_moves:
                if self.board.is_capture(move):
                    screen_shake(0.1, 1)
                    particle_effect(char="*", color=C_RED, count=5)
                    beep("eat")
                
                self.board.push(move)
                self.score += 10
                self.award_xp_for_action(5) # 5 base XP per move
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

    def _make_ai_move(self):
        """Simple AI that makes a move using Stockfish or random."""
        time.sleep(0.5)
        if not self.board.is_game_over():
            move = self._get_ai_move()
            if self.board.is_capture(move):
                screen_shake(0.1, 1)
            self.board.push(move)
            beep("lose")

    def _get_ai_move(self):
        """Generate AI move."""
        try:
            # Try stockfish if available
            # engine = chess.engine.SimpleEngine.popen_uci("stockfish")
            # res = engine.play(self.board, chess.engine.Limit(time=0.1))
            # engine.quit()
            # return res.move
            return random.choice(list(self.board.legal_moves))
        except:
            return random.choice(list(self.board.legal_moves))

    def _handle_game_end(self):
        """Handle game termination."""
        result = self.board.result()
        won = (result == "1-0" and self.u_white) or (result == "0-1" and not self.u_white)
        
        if won:
            show_popup("VICTORY! YOU WON!", C_GREEN)
            self.award_xp_for_action(100) # 100 base XP for win
        elif result == "1/2-1/2":
            show_popup("DRAW!", C_WHITE)
            self.award_xp_for_action(50)
        else:
            show_popup("DEFEAT!", C_RED)
            
        self.game_over = True

def play_chess(difficulty='normal'):
    """Wrapper function for arcade.py compatibility."""
    if not CHESS_AVAILABLE:
        show_popup("python-chess missing!", C_RED)
        return None
    game = ChessGame(difficulty)
    return game.play()

if __name__ == "__main__":
    play_chess()
