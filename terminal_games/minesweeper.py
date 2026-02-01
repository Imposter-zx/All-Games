import random
import time
import os
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK, update_stats, load_stats

NUM_COLORS = {1: "\033[34m", 2: "\033[32m", 3: "\033[31m", 4: "\033[35m", 5: "\033[33m", 6: "\033[36m", 7: "\033[30m", 8: "\033[37m"}

def create_board(rows, cols, mines):
    board = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_pos = set()
    while len(mine_pos) < mines:
        r, c = random.randint(0, rows-1), random.randint(0, cols-1)
        if (r, c) not in mine_pos:
            mine_pos.add((r, c))
            board[r][c] = 'M'
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 'M': continue
            cnt = sum(1 for dr in [-1,0,1] for dc in [-1,0,1] if 0 <= r+dr < rows and 0 <= c+dc < cols and board[r+dr][c+dc] == 'M')
            board[r][c] = cnt
    return board, mine_pos

def draw_header(elapsed, flags, mines):
    header_lines = [
        f"⏱ TIME: {elapsed//60:02}:{elapsed%60:02}  |  ⚑ FLAGS: {flags}/{mines}",
        f"💣 MINES TOTAL: {mines}"
    ]
    draw_retro_box(45, "💣 MINESWEEPER ULTIMATE", header_lines, color=C_YELLOW)

def print_board(board, revealed, flagged, cursor, elapsed, mines, exploded=None, flash_red=False):
    rows, cols = len(board), len(board[0])
    clear_screen()
    f_count = sum(row.count(True) for row in flagged)
    
    draw_header(elapsed, f_count, mines)
    
    term_width = 80
    try: term_width = os.get_terminal_size().columns
    except: pass
    
    padding = (term_width - (cols * 3 + 2)) // 2
    indent = " " * padding
    
    border_color = C_RED if flash_red else C_CYAN
    
    print(indent + f"{border_color}╔" + "═══" * cols + f"═╗{C_RESET}")
    
    for r in range(rows):
        line = indent + f"{border_color}║{C_RESET} "
        for c in range(rows if rows == cols else cols): # Using cols logic
            if c >= cols: break
            style = ""
            if (r, c) == cursor: style = "\033[47;30m"
            
            if (r, c) == exploded: char = f"{style}{C_RED}💥{C_RESET}"
            elif flagged[r][c]: char = f"{style}{C_YELLOW}⚑{C_RESET} "
            elif revealed[r][c]:
                val = board[r][c]
                if val == 'M': char = f"{style}{C_RED}💣{C_RESET}"
                elif val == 0: char = f"{style}{C_BLACK}·{C_RESET} "
                else: char = f"{style}{NUM_COLORS.get(val, '')}{val}{C_RESET} "
            else: char = f"{style}{C_WHITE}■{C_RESET} "
            line += char + " "
        print(line + f"{border_color}║{C_RESET}")
    print(indent + f"{border_color}╚" + "═══" * cols + f"═╝{C_RESET}")
    
    controls = "ARROWS: Move | ENTER: Reveal | F: Flag | Q: Exit"
    ctrl_indent = (term_width - len(controls)) // 2
    print("\n" + " " * ctrl_indent + f"{C_WHITE}{controls}{C_RESET}")

def reveal(board, revealed, flagged, r, c, animate=True):
    if not (0 <= r < len(board) and 0 <= c < len(board[0])) or revealed[r][c] or flagged[r][c]: return
    revealed[r][c] = True
    if animate and board[r][c] == 0:
        time.sleep(0.02) # Small reveal delay
    
    if board[r][c] == 0:
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                reveal(board, revealed, flagged, r+dr, c+dc, animate=animate)

def explosion_effect(board, revealed, flagged, cursor, elapsed, mines, cr, cc):
    beep("lose")
    for _ in range(3):
        print_board(board, revealed, flagged, tuple(cursor), elapsed, mines, exploded=(cr, cc), flash_red=True)
        time.sleep(0.1)
        print_board(board, revealed, flagged, tuple(cursor), elapsed, mines, exploded=(cr, cc), flash_red=False)
        time.sleep(0.1)
    
    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] == 'M': revealed[r][c] = True
    print_board(board, revealed, flagged, tuple(cursor), elapsed, mines, exploded=(cr, cc))
    show_popup("BOOM! GAME OVER", color=C_RED)

def play_minesweeper():
    clear_screen()
    draw_retro_box(50, "SELECT DIFFICULTY", ["(1) BEGINNER", "(2) INTERMEDIATE", "(3) EXPERT", "(Q) BACK"], color=C_YELLOW)
    while True:
        choice = get_key()
        if choice in ['q', 'Q']: return
        if choice in ['1', '2', '3']: break

    diff_name = {"2": "intermediate", "3": "expert"}.get(choice, "beginner")
    r, c, mines = {"beginner": (8, 8, 10), "intermediate": (12, 12, 25), "expert": (14, 20, 50)}[diff_name] # Adjusted for visibility
    
    board, mine_pos = create_board(r, c, mines)
    revealed = [[False for _ in range(c)] for _ in range(r)]
    flagged = [[False for _ in range(c)] for _ in range(r)]
    cursor = [0, 0]
    start_time = time.time()
    
    while True:
        elapsed = int(time.time() - start_time)
        print_board(board, revealed, flagged, tuple(cursor), elapsed, mines)
        
        if sum(1 for i in range(r) for j in range(c) if not revealed[i][j] and board[i][j] != 'M') == 0:
            beep("win")
            show_popup("VICTORY! FIELD CLEARED", color=C_GREEN)
            stats = load_stats().get("minesweeper", {})
            update_stats("minesweeper", "wins", stats.get("wins", {}).get(diff_name, 0) + 1, diff_name)
            break

        key = get_key()
        if key in ['q', 'Q']: break
        elif key == 'up': cursor[0] = max(0, cursor[0] - 1); beep("correct")
        elif key == 'down': cursor[0] = min(r - 1, cursor[0] + 1); beep("correct")
        elif key == 'left': cursor[1] = max(0, cursor[1] - 1); beep("correct")
        elif key == 'right': cursor[1] = min(c - 1, cursor[1] + 1); beep("correct")
        elif key in ['\r', '\n', ' ', 'r', 'R']:
            cr, cc = cursor
            if flagged[cr][cc]: continue
            if board[cr][cc] == 'M':
                explosion_effect(board, revealed, flagged, cursor, elapsed, mines, cr, cc)
                break
            reveal(board, revealed, flagged, cr, cc)
            beep("correct")
        elif key in ['f', 'F']:
            flagged[cursor[0]][cursor[1]] = not flagged[cursor[0]][cursor[1]]
            beep("correct")

if __name__ == "__main__":
    play_minesweeper()

if __name__ == "__main__":
    play_minesweeper()
