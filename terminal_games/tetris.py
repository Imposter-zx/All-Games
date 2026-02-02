import time
import os
import random
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, update_stats, load_stats, animated_flash, print_big_title, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK

WIDTH = 10
HEIGHT = 20

SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[1, 0, 0], [1, 1, 1]], # L
    [[0, 0, 1], [1, 1, 1]], # J
    [[0, 1, 1], [1, 1, 0]], # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

COLORS = [C_CYAN, C_YELLOW, C_MAGENTA, C_WHITE, C_BLUE, C_GREEN, C_RED]

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                try:
                    if off_y + cy >= HEIGHT or off_x + cx < 0 or off_x + cx >= WIDTH or board[off_y + cy][off_x + cx]:
                        return True
                except IndexError:
                    return True
    return False

def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
             if val: mat1[off_y + cy][off_x + cx] += val
    return mat1

def new_piece():
    shape = random.choice(SHAPES)
    color = COLORS[SHAPES.index(shape)]
    return {'shape': shape, 'color': color, 'x': WIDTH // 2 - len(shape[0]) // 2, 'y': 0}

def play_tetris():
    clear_screen()
    print_big_title("TETRIS", color=C_BLUE)
    time.sleep(1)
    
    board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    piece = new_piece()
    next_piece_obj = new_piece()
    
    score = 0
    start_time = time.time()
    level = 1
    
    stats = load_stats().get('tetris', {})
    best_score = stats.get('best_score', 0)
    
    while True:
        # Draw
        clear_screen()
        # Header
        print(f"{C_BLUE}╔{'═' * (WIDTH*2)}╗")
        print(f"║ SCORE: {score:<6} LVL: {level} ║")
        print(f"╚{'═' * (WIDTH*2)}╝{C_RESET}")
        
        # Board + Next Piece
        # We need a buffer to draw
        temp_board = [row[:] for row in board]
        
        # Add piece to temp board for drawing
        for cy, row in enumerate(piece['shape']):
            for cx, val in enumerate(row):
                 if val and 0 <= piece['y'] + cy < HEIGHT and 0 <= piece['x'] + cx < WIDTH:
                     temp_board[piece['y'] + cy][piece['x'] + cx] = 1 # Just mark as occupied for now, handle color later?
                     # Ideally we store color in board. 
                     # Simplifying: board stores 0 or ColorCode
        
        # Render Board
        print(f"{C_BLUE}╔{'═' * (WIDTH*2)}╗{C_RESET}  NEXT:")
        for r in range(HEIGHT):
            line = f"{C_BLUE}║{C_RESET}"
            for c in range(WIDTH):
                val = board[r][c]
                # Check dynamic piece
                is_piece = False
                if 0 <= r - piece['y'] < len(piece['shape']) and 0 <= c - piece['x'] < len(piece['shape'][0]):
                     if piece['shape'][r - piece['y']][c - piece['x']]:
                         line += f"{piece['color']}██{C_RESET}"
                         is_piece = True
                
                if not is_piece:
                    if val == 0: line += f"{C_BLACK} . {C_RESET}" # grid dot
                    else: line += f"{val}██{C_RESET}"
            
            line += f"{C_BLUE}║{C_RESET}"
            
            # Side panel (Next piece)
            if r == 1: line += f"  {next_piece_obj['color']}"
            if 1 <= r <= 4:
                 # draw next piece logic simplified or just text
                 pass
            print(line)
        print(f"{C_BLUE}╚{'═' * (WIDTH*2)}╝{C_RESET}")
        
        # Input (Blocking with timeout for gravity)
        if os.name == 'nt':
             import msvcrt
             t0 = time.time()
             has_input = False
             while time.time() - t0 < max(0.1, 0.5 - (level * 0.05)):
                 if msvcrt.kbhit():
                     key = msvcrt.getch()
                     if key == b'\xe0':
                         key = msvcrt.getch()
                         if key == b'H': # Rotate
                             rotated = rotate(piece['shape'])
                             if not check_collision(board, rotated, (piece['x'], piece['y'])):
                                 piece['shape'] = rotated
                                 beep("move")
                         elif key == b'K': # Left
                             if not check_collision(board, piece['shape'], (piece['x'] - 1, piece['y'])):
                                 piece['x'] -= 1
                                 beep("move")
                         elif key == b'M': # Right
                             if not check_collision(board, piece['shape'], (piece['x'] + 1, piece['y'])):
                                 piece['x'] += 1
                                 beep("move")
                         elif key == b'P': # Down (Soft Drop)
                             if not check_collision(board, piece['shape'], (piece['x'], piece['y'] + 1)):
                                 piece['y'] += 1
                                 score += 1
                     elif key.lower() == b'q': return
                     has_input = True
                     break
        else:
            # unix implementation omitted for brevity, similar select logic
             time.sleep(max(0.1, 0.5 - (level * 0.05)))
        
        # Gravity
        if not check_collision(board, piece['shape'], (piece['x'], piece['y'] + 1)):
            piece['y'] += 1
        else:
            # Lock
            for cy, row in enumerate(piece['shape']):
                for cx, val in enumerate(row):
                    if val:
                        board[piece['y'] + cy][piece['x'] + cx] = piece['color']
            
            # Clear lines
            lines_cleared = 0
            new_board = [row for row in board if any(x == 0 for x in row)]
            lines_cleared = HEIGHT - len(new_board)
            if lines_cleared > 0:
                score += (100 * lines_cleared)
                beep("win") # Clear sound
                board = [[0] * WIDTH for _ in range(lines_cleared)] + new_board
            
            piece = next_piece_obj
            next_piece_obj = new_piece()
            
            if check_collision(board, piece['shape'], (piece['x'], piece['y'])):
                beep("game_over")
                show_popup(f"GAME OVER! Score: {score}", C_RED)
                if score > best_score:
                    update_stats('tetris', 'best_score', score)
                break

if __name__ == "__main__":
    play_tetris()
