import random
import time
import os
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, update_stats, load_stats

def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for n in nums:
                    if is_valid_move(board, r, c, n)[0]:
                        board[r][c] = n
                        if solve(board): return True
                        board[r][c] = 0
                return False
    return True

def generate_board(difficulty):
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve(board)
    solution = [row[:] for row in board]
    remove = {"easy": 35, "medium": 45, "hard": 55}.get(difficulty, 35)
    while remove > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            remove -= 1
    return board, solution

def is_valid_move(board, row, col, num):
    for i in range(9):
        if board[row][i] == num: return False, "Row conflict"
        if board[i][col] == num: return False, "Column conflict"
    br, bc = (row // 3) * 3, (col // 3) * 3
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == num: return False, "3x3 Box conflict"
    return True, ""

def draw_header(elapsed, difficulty):
    term_width = 80
    try: term_width = os.get_terminal_size().columns
    except: pass
    
    header_text = [
        f"DIFFICULTY: {difficulty.upper()}",
        f"TIME: {elapsed//60:02}:{elapsed%60:02}"
    ]
    draw_retro_box(40, "🧩 SUDOKU 2D", header_text, color=C_MAGENTA)

def print_board(board, original_cells, cursor, msg, hints, difficulty, elapsed):
    clear_screen()
    draw_header(elapsed, difficulty)
    
    term_width = 80
    try: term_width = os.get_terminal_size().columns
    except: pass
    
    padding = (term_width - 37) // 2
    indent = " " * padding
    
    print(indent + f"{C_CYAN}╔═══════════╦═══════════╦═══════════╗{C_RESET}")
    for r in range(9):
        line = indent + f"{C_CYAN}║{C_RESET}"
        for c in range(9):
            cell = board[r][c]
            style = ""
            
            # Cursor blink effect (simulated with time check if this were a render loop, but here just highlight)
            if (r, c) == cursor:
                style = "\033[47;30m"
            elif (r, c) in original_cells:
                style = C_CYAN
            elif cell != 0:
                style = C_GREEN
            else:
                style = C_WHITE
                
            val = f"{style} {cell if cell != 0 else '.'} {C_RESET}"
            line += val
            if (c + 1) % 3 == 0:
                line += f"{C_CYAN}║{C_RESET}"
            else:
                line += " "
        print(line)
        if (r + 1) % 3 == 0 and r < 8:
            print(indent + f"{C_CYAN}╠═══════════╬═══════════╬═══════════╣{C_RESET}")
    print(indent + f"{C_CYAN}╚═══════════╩═══════════╩═══════════╝{C_RESET}")
    
    if msg:
        msg_indent = (term_width - len(msg) - 4) // 2
        print("\n" + " " * msg_indent + f"{C_RED}⚠ {msg}{C_RESET}")
    
    controls = "ARROWS: Move | 1-9: Place | H: Hint | Q: Exit"
    ctrl_indent = (term_width - len(controls)) // 2
    print("\n" + " " * ctrl_indent + f"{C_YELLOW}{controls}{C_RESET}")

def victory_animation(elapsed):
    beep("win")
    frames = ["V", "VI", "VIC", "VICT", "VICTO", "VICTOR", "VICTORY", "VICTORY!", "VICTORY!!"]
    for frame in frames:
        clear_screen()
        print("\n" * 10)
        draw_retro_box(40, "🎉 CONGRATULATIONS", [frame, f"Time: {elapsed//60:02}:{elapsed%60:02}"], color=C_GREEN)
        time.sleep(0.1)
    time.sleep(1.5)

def play_sudoku():
    clear_screen()
    draw_retro_box(50, "SELECT DIFFICULTY", ["(1) EASY", "(2) MEDIUM", "(3) HARD", "(Q) BACK"], color=C_MAGENTA)
    while True:
        choice = get_key()
        if choice in ['q', 'Q']: return
        if choice in ['1', '2', '3']: break
        
    diff = {"2": "medium", "3": "hard"}.get(choice, "easy")
    board, solution = generate_board(diff)
    original_cells = [(r, c) for r in range(9) for c in range(9) if board[r][c] != 0]
    cursor = [0, 0]
    start_time = time.time()
    msg = ""
    hints_used = 0

    while True:
        elapsed = int(time.time() - start_time)
        print_board(board, original_cells, tuple(cursor), msg, hints_used, diff, elapsed)
        msg = ""

        if all(board[r][c] == solution[r][c] for r in range(9) for c in range(9)):
            victory_animation(elapsed)
            stats = load_stats().get("sudoku", {})
            best = stats.get("best_times", {}).get(diff)
            if best is None or elapsed < best:
                update_stats("sudoku", "best_times", elapsed, diff)
            update_stats("sudoku", "wins", stats.get("wins", 0) + 1)
            break

        key = get_key()
        if key in ['q', 'Q']: break
        elif key == 'up': cursor[0] = max(0, cursor[0] - 1); beep("correct")
        elif key == 'down': cursor[0] = min(8, cursor[0] + 1); beep("correct")
        elif key == 'left': cursor[1] = max(0, cursor[1] - 1); beep("correct")
        elif key == 'right': cursor[1] = min(8, cursor[1] + 1); beep("correct")
        elif key in '123456789':
            r, c = cursor
            if (r, c) in original_cells:
                beep("invalid")
                msg = "Locked Cell!"
                continue
            num = int(key)
            valid, err = is_valid_move(board, r, c, num)
            if valid: 
                board[r][c] = num
                beep("correct")
            else: 
                beep("invalid")
                msg = err
        elif key in ['0', ' ']:
            r, c = cursor
            if (r, c) not in original_cells: 
                board[r][c] = 0
                beep("correct")
        elif key in ['h', 'H']:
            hints_used += 1
            r, c = cursor
            if (r, c) not in original_cells:
                board[r][c] = solution[r][c]
                beep("correct")
                msg = f"Hint Applied! ({hints_used})"

if __name__ == "__main__":
    play_sudoku()

if __name__ == "__main__":
    play_sudoku()
