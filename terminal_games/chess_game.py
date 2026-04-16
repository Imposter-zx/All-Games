import time
import os
import random
try:
    import chess
    import chess.engine
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False

from arcade_utils import (
    clear_screen, get_key, draw_retro_box, beep, show_popup, 
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, 
    BG_DARK, BG_LIGHT, BG_CUR, BG_SEL, BG_RED, 
    update_stats, load_stats, add_xp, screen_shake, particle_effect
)
from base_game import BaseGame

# --- PIECE ART ---
PIECE_ART = {
    'P': ["  ♙  ", "  |  ", " / \\ "],
    'N': [" /♘> ", " |   ", " / \\ "],
    'B': ["  ^  ", " /♗\\ ", "  |  "],
    'R': ["|♖♖| ", "  |  ", " | | "],
    'Q': [" \\♕/ ", "  |  ", " / \\ "],
    'K': ["  +  ", " /♔\\ ", "  |  "],
    'p': ["  ♟  ", "  |  ", " / \\ "],
    'n': [" /♞> ", " |   ", " / \\ "],
    'b': ["  ^  ", " /♝\\ ", "  |  "],
    'r': ["|♜♜| ", "  |  ", " | | "],
    'q': [" \\♛/ ", "  |  ", " / \\ "],
    'k': ["  +  ", " /♚\\ ", "  |  "],
    ' ': ["     ", "     ", "     "]
}

class ChessGame(BaseGame):
    """Chess vs AI game implementation using BaseGame."""
    
    def __init__(self):
        super().__init__("chess")
        if CHESS_AVAILABLE:
            self.board = chess.Board()
        else:
            self.board = None
            
        self.cursor = 0 # a1
        self.selected = None
        self.last_move = None
        self.u_white = True
        self.ai_delay = 0.5
        self.flash_check = False

    def play(self) -> dict:
        """Main Chess game loop."""
        if not CHESS_AVAILABLE:
            clear_screen()
            show_popup("Error: python-chess not found!", C_RED)
            return self.get_final_stats()
            
        if not self._select_side():
            return self.get_final_stats()
            
        self.start_timer()
        
        while not self.game_over:
            is_p_turn = self.board.turn == (chess.WHITE if self.u_white else chess.BLACK)
            self.flash_check = self.board.is_check()
            
            self._render()
            
            if is_p_turn:
                self._handle_input()
            else:
                self._ai_turn()
                
            self._update_game_state()
            
        self.end_timer()
        return self.get_final_stats()

    def _select_side(self) -> bool:
        """Let player choose color."""
        clear_screen()
        draw_retro_box(40, "CHESS V5", ["SELECT YOUR SIDE", "(W) WHITE", "(B) BLACK", "(Q) QUIT"], color=C_MAGENTA)
        while True:
            choice = get_key()
            if choice in ['q', 'Q']: return False
            if choice in ['w', 'W', '\r', '\n']:
                self.u_white = True
                return True
            if choice in ['b', 'B']:
                self.u_white = False
                return True

    def _render(self):
        """Render the 2D chessboard and UI."""
        clear_screen()
        term_width = 80
        try: term_width = os.get_terminal_size().columns
        except: pass
        
        draw_retro_box(50, "♟️ CHESS V5", [f"{'WHITE' if self.u_white else 'BLACK'} VS STOCKFISH AI"], color=C_MAGENTA)
        
        padding = (term_width - 46) // 2
        indent = " " * padding
        
        print(indent + "     A     B     C     D     E     F     G     H")
        print(indent + "  ╔" + "═════" * 8 + "╗")
        
        for r in range(8):
            for line_idx in range(3):
                row_str = indent
                if line_idx == 1: row_str += f"{8-r} ║"
                else: row_str += "  ║"
                    
                for c in range(8):
                    sq = chess.square(c, 7-r)
                    p = self.board.piece_at(sq)
                    symbol = p.symbol() if p else ' '
                    art_lines = PIECE_ART.get(symbol, PIECE_ART[' '])
                    
                    # Background
                    bg = BG_LIGHT if (r + c) % 2 == 0 else BG_DARK
                    if sq == self.cursor: bg = BG_CUR
                    if sq == self.selected: bg = BG_SEL
                    if self.last_move and (sq == self.last_move.from_square or sq == self.last_move.to_square):
                        bg = BG_SEL
                    
                    if self.flash_check and p and p.piece_type == chess.KING and p.color == self.board.turn:
                        bg = BG_RED
                    
                    # Foreground
                    fg = C_WHITE if p and p.color == chess.WHITE else C_MAGENTA
                    if sq == self.cursor: fg = "\033[30m"
                    
                    row_str += f"{bg}{fg}{art_lines[line_idx]}{C_RESET}"
                
                row_str += f"║ {8-r}" if line_idx == 1 else "║"
                print(row_str)
                
        print(indent + "  ╚" + "═════" * 8 + "╝")
        print(indent + "     A     B     C     D     E     F     G     H")
        
        if self.board.is_check():
            print("\n" + " " * ((term_width - 8) // 2) + f"{C_RED}{C_BOLD}⚠ CHECK!{C_RESET}")
            
        print("\n" + " " * ((term_width - 48) // 2) + f"{C_YELLOW}ARROWS: Move | ENTER: Select | U: Undo | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle player movement and moves."""
        k = get_key()
        if k == 'q':
            self.game_over = True
        elif k == 'up': self.cursor = min(63, self.cursor + 8) if self.cursor < 56 else self.cursor; beep("correct")
        elif k == 'down': self.cursor = max(0, self.cursor - 8) if self.cursor > 7 else self.cursor; beep("correct")
        elif k == 'left': self.cursor = max(0, self.cursor - 1) if self.cursor % 8 > 0 else self.cursor; beep("correct")
        elif k == 'right': self.cursor = min(63, self.cursor + 1) if self.cursor % 8 < 7 else self.cursor; beep("correct")
        elif k == 'u':
            if len(self.board.move_stack) >= 2:
                self.board.pop(); self.board.pop()
                beep("correct")
        elif k in ['\r', '\n', ' ']:
            self._handle_selection()

    def _handle_selection(self):
        """Logic for selecting a piece and making a move."""
        if self.selected is None:
            piece = self.board.piece_at(self.cursor)
            if piece and piece.color == self.board.turn:
                self.selected = self.cursor
                beep("correct")
            else:
                beep("invalid")
        else:
            move = chess.Move(self.selected, self.cursor)
            # Pawn promotion to Queen
            piece = self.board.piece_at(self.selected)
            if piece and piece.piece_type == chess.PAWN:
                rank = chess.square_rank(self.cursor)
                if (rank == 7 and self.board.turn == chess.WHITE) or (rank == 0 and self.board.turn == chess.BLACK):
                    move.promotion = chess.QUEEN
                    
            if move in self.board.legal_moves:
                self._execute_move(move)
            else:
                self.selected = None
                beep("invalid")

    def _execute_move(self, move):
        """Perform checking for captures and pushes the move."""
        if self.board.is_capture(move):
            screen_shake(0.1, 1)
            particle_effect(char="*", color=C_RED, count=5)
            self.add_xp(20)
            
        self.board.push(move)
        self.last_move = move
        self.selected = None
        beep("correct")

    def _ai_turn(self):
        """Trigger AI move generation."""
        time.sleep(self.ai_delay)
        move = self._get_ai_move()
        if self.board.is_capture(move):
            screen_shake(0.1, 1)
            particle_effect(char="X", color=C_MAGENTA, count=5)
            
        self.board.push(move)
        self.last_move = move
        beep("correct")

    def _get_ai_move(self):
        """Generate move using Stockfish if available, otherwise random."""
        try:
            engine = chess.engine.SimpleEngine.popen_uci("stockfish")
            res = engine.play(self.board, chess.engine.Limit(time=0.1))
            engine.quit()
            return res.move
        except:
            return random.choice(list(self.board.legal_moves))

    def _update_game_state(self):
        """Check for end of game conditions."""
        if self.board.is_game_over():
            self._handle_game_over()

    def _handle_game_over(self):
        """Manage game result and stats."""
        self._render() # One final draw
        res = self.board.result()
        won = (res == "1-0" and self.u_white) or (res == "0-1" and not self.u_white)
        
        if won: self.add_xp(500)
        beep("win" if won else "lose")
        show_popup(f"GAME OVER: {res}", color=C_MAGENTA, delay=3)
        
        # Save persistence
        stats = load_stats().get("chess", {})
        if res == "1-0":
            key = "wins" if self.u_white else "losses"
            update_stats("chess", key, stats.get(key, 0) + 1)
        elif res == "0-1":
            key = "losses" if self.u_white else "wins"
            update_stats("chess", key, stats.get(key, 0) + 1)
        else:
            update_stats("chess", "draws", stats.get("draws", 0) + 1)
            
        self.save_stats({
            'result': res,
            'xp_earned': self.xp_earned,
            'won': won
        })
        self.game_over = True

def play_chess():
    """Wrapper function for arcade.py compatibility."""
    game = ChessGame()
    return game.play()

if __name__ == "__main__":
    play_chess()
