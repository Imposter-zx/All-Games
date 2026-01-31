import chess
import chess.engine
import time
import os
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, BG_DARK, BG_LIGHT, BG_CUR, BG_SEL, BG_RED, update_stats, load_stats

# --- ASCII ART PIECES ---
# Each piece is exactly 3 lines high and up to 5 chars wide.
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

def get_ai_move(board):
    try:
        engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        res = engine.play(board, chess.engine.Limit(time=0.1))
        engine.quit(); return res.move
    except:
        import random
        return random.choice(list(board.legal_moves))

def print_board(board, cursor, selected, last_move=None, flash_check=False):
    clear_screen()
    term_width = 80
    try: term_width = os.get_terminal_size().columns
    except: pass
    
    draw_retro_box(50, "♟️ ULTIMATE CHESS 2D", ["VS STOCKFISH AI"], color=C_MAGENTA)
    
    padding = (term_width - 46) // 2
    indent = " " * padding
    
    print(indent + "     A     B     C     D     E     F     G     H")
    print(indent + "  ╔" + "═════" * 8 + "╗")
    
    for r in range(8):
        # We need to print 3 lines for each row of the board
        for line_idx in range(3):
            row_str = indent
            if line_idx == 1:
                row_str += f"{8-r} ║"
            else:
                row_str += "  ║"
                
            for c in range(8):
                sq = chess.square(c, 7-r)
                p = board.piece_at(sq)
                symbol = p.symbol() if p else ' '
                art_lines = PIECE_ART.get(symbol, PIECE_ART[' '])
                
                # Determine Background
                bg = BG_LIGHT if (r + c) % 2 == 0 else BG_DARK
                if sq == cursor: bg = BG_CUR
                if sq == selected: bg = BG_SEL
                if last_move and (sq == last_move.from_square or sq == last_move.to_square):
                    bg = BG_SEL # Highlight last move
                
                # Flash Red if king in check
                if flash_check and p and p.piece_type == chess.KING and p.color == board.turn:
                    bg = BG_RED
                
                # Determine Foreground
                fg = C_WHITE if p and p.color == chess.WHITE else C_MAGENTA
                if sq == cursor: fg = "\033[30m" # Black text on yellow cursor
                
                row_str += f"{bg}{fg}{art_lines[line_idx]}{C_RESET}"
            
            if line_idx == 1:
                row_str += f"║ {8-r}"
            else:
                row_str += "║"
            print(row_str)
            
    print(indent + "  ╚" + "═════" * 8 + "╝")
    print(indent + "     A     B     C     D     E     F     G     H")
    
    if board.is_check():
        msg = "⚠️ CHECK!"
        print("\n" + " " * ((term_width - len(msg)) // 2) + f"{C_RED}{C_BOLD}{msg}{C_RESET}")
    
    controls = "ARROWS: Move | ENTER: Select/Move | U: Undo | Q: Exit"
    print("\n" + " " * ((term_width - len(controls)) // 2) + f"{C_YELLOW}{controls}{C_RESET}")

def animate_move(board, move, cursor):
    # Simple animation: highlight the square momentarily
    print_board(board, cursor, None, last_move=move)
    time.sleep(0.2)

def play_chess():
    board = chess.Board()
    cursor = 0 # a1 (bottom left)
    selected = None
    last_move = None
    
    clear_screen()
    draw_retro_box(40, "CHESS", ["SELECT COLOR", "(W) WHITE", "(B) BLACK", "(Q) BACK"], color=C_MAGENTA)
    while True:
        choice = get_key()
        if choice in ['q', 'Q']: return
        if choice in ['w', 'W', 'b', 'B', '\r', '\n']: break
    u_white = choice.lower() != 'b'
    
    while not board.is_game_over():
        is_p = board.turn == (chess.WHITE if u_white else chess.BLACK)
        flash = board.is_check()
        print_board(board, cursor, selected, last_move=last_move, flash_check=flash)
        
        if is_p:
            key = get_key()
            if key in ['q', 'Q']: break
            elif key == 'up': cursor = min(63, cursor + 8) if cursor < 56 else cursor; beep("correct")
            elif key == 'down': cursor = max(0, cursor - 8) if cursor > 7 else cursor; beep("correct")
            elif key == 'left': cursor = max(0, cursor - 1) if cursor % 8 > 0 else cursor; beep("correct")
            elif key == 'right': cursor = min(63, cursor + 1) if cursor % 8 < 7 else cursor; beep("correct")
            elif key in ['u', 'U']:
                if len(board.move_stack) >= 2: board.pop(); board.pop(); beep("correct")
            elif key in ['\r', '\n', ' ']:
                if selected is None:
                    if board.piece_at(cursor) and board.piece_at(cursor).color == board.turn:
                        selected = cursor
                        beep("correct")
                    else:
                        beep("invalid")
                else:
                    move = chess.Move(selected, cursor)
                    # Promotion logic
                    if board.piece_at(selected).piece_type == chess.PAWN:
                        if (chess.square_rank(cursor) == 7 and board.turn == chess.WHITE) or (chess.square_rank(cursor) == 0 and board.turn == chess.BLACK):
                            move.promotion = chess.QUEEN
                    if move in board.legal_moves:
                        board.push(move)
                        last_move = move
                        selected = None
                        beep("correct")
                    else:
                        selected = None
                        beep("invalid")
        else:
            time.sleep(0.5)
            m = get_ai_move(board)
            animate_move(board, m, cursor)
            board.push(m)
            last_move = m
            beep("correct")

    # End of game
    print_board(board, cursor, selected, last_move=last_move)
    res = board.result()
    beep("win" if (res == "1-0" and u_white) or (res == "0-1" and not u_white) else "lose")
    show_popup(f"GAME OVER: {res}", color=C_MAGENTA, delay=3)
    
    # Update Stats
    stats = load_stats().get("chess", {})
    if res == "1-0": update_stats("chess", "wins" if u_white else "losses", stats.get("wins" if u_white else "losses", 0) + 1)
    elif res == "0-1": update_stats("chess", "losses" if u_white else "wins", stats.get("losses" if u_white else "wins", 0) + 1)
    else: update_stats("chess", "draws", stats.get("draws", 0) + 1)

if __name__ == "__main__":
    play_chess()

    print_board(board, cursor, selected, capt_w, capt_b)
    res = board.result()
    print(f"\n{C_BOLD}GAME OVER: {res}{C_RESET}")
    # Update Stats
    stats = load_stats().get("chess", {})
    if res == "1-0": update_stats("chess", "wins" if u_white else "losses", stats.get("wins" if u_white else "losses", 0) + 1)
    elif res == "0-1": update_stats("chess", "losses" if u_white else "wins", stats.get("losses" if u_white else "wins", 0) + 1)
    else: update_stats("chess", "draws", stats.get("draws", 0) + 1)
    time.sleep(2)

if __name__ == "__main__":
    play_chess()
