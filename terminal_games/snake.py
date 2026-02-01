import random
import time
import os
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, update_stats, load_stats, animated_flash, print_big_title, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK

BOARD_WIDTH = 30
BOARD_HEIGHT = 15

def create_food(snake):
    while True:
        food = (random.randint(1, BOARD_HEIGHT-2), random.randint(1, BOARD_WIDTH-2))
        if food not in snake:
            return food

def play_snake():
    clear_screen()
    print_big_title("SNAKE", color=C_GREEN)
    time.sleep(1)
    
    snake = [(BOARD_HEIGHT//2, BOARD_WIDTH//2)]
    direction = (0, 1) # Moving right initially
    food = create_food(snake)
    score = 0
    speed = 0.15
    game_over = False
    
    # Simple input mapping
    key_map = {
        'up': (-1, 0), 'down': (1, 0),
        'left': (0, -1), 'right': (0, 1)
    }
    
    while not game_over:
        start_time = time.time()
        
        # 1. Draw Board
        clear_screen()
        # Header
        stats = load_stats().get('snake', {})
        high_score = stats.get('high_score', 0)
        print(f"{C_YELLOW}╔{'═' * BOARD_WIDTH}╗")
        print(f"║ SCORE: {score:<10} HI: {high_score:<10} ║")
        print(f"╚{'═' * BOARD_WIDTH}╝{C_RESET}")
        
        # Grid
        print(f"{C_GREEN}╔{'═' * BOARD_WIDTH}╗{C_RESET}")
        for r in range(BOARD_HEIGHT):
            line = f"{C_GREEN}║{C_RESET}"
            for c in range(BOARD_WIDTH):
                if (r, c) == snake[0]:
                    line += f"{C_GREEN}█{C_RESET}" # Head
                elif (r, c) in snake:
                    line += f"{C_GREEN}▒{C_RESET}" # Body
                elif (r, c) == food:
                    line += f"{C_RED}●{C_RESET}" # Food
                else:
                    line += " "
            line += f"{C_GREEN}║{C_RESET}"
            print(line)
        print(f"{C_GREEN}╚{'═' * BOARD_WIDTH}╝{C_RESET}")
        print(f"{C_WHITE}ARROWS to Move | Q to Quit{C_RESET}")

        # 2. Input Handling (Non-blocking check would be ideal but get_key is blocking/semi-blocking depending on impl)
        # Since get_key is blocking/raw, we need a way to move continuously.
        # The provided get_key in utils is blocking. We need a non-blocking approach or a timeout.
        # Standard msvcrt.kbhit() for windows or select for unix.
        
        # Let's try to adapt get_key to be non-blocking or use a timeout if possible?
        # The current `get_key` implementation waits for input. 
        # For a real-time game like Snake in a terminal without curses/pygame, we usually use kbhit.
        
        # Quick fix: We will re-implement a localized non-blocking input check for Snake if possible, 
        # or stick to a "step-based" snake if non-blocking is too risky regarding cross-platform utils.
        # HOWEVER, the prompt asks for "Snake grows... Speed increases". Interactive snake needs non-blocking.
        
        # Attempting a safe non-blocking read using msvcrt (Windows) and select (Unix) inside the loop.
        
        new_dir = direction
        
        if os.name == 'nt':
            import msvcrt
            start_wait = time.time()
            while time.time() - start_wait < speed:
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    if ch in [b'\x00', b'\xe0']: # Arrow keys
                        ch = msvcrt.getch()
                        k = {b'H': 'up', b'P': 'down', b'K': 'left', b'M': 'right'}.get(ch, None)
                        if k and k in key_map:
                            test_dir = key_map[k]
                            # Prevent 180 turn
                            if (test_dir[0] + direction[0] != 0) or (test_dir[1] + direction[1] != 0):
                                new_dir = test_dir
                                break # Input received, move immediately? or wait? usually wait frame
                    elif ch.lower() == b'q':
                        return
        else:
            # Unix non-blocking (simplified)
            import select
            import sys
            if select.select([sys.stdin], [], [], speed)[0]:
                k = get_key() # This might still block if not careful, but select says data is ready
                if k == 'q': return
                if k in key_map:
                    test_dir = key_map[k]
                    if (test_dir[0] + direction[0] != 0) or (test_dir[1] + direction[1] != 0):
                        new_dir = test_dir

        direction = new_dir
        
        # 3. Logic Update
        head = snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        
        # Collision Check
        if (new_head[0] < 0 or new_head[0] >= BOARD_HEIGHT or 
            new_head[1] < 0 or new_head[1] >= BOARD_WIDTH or 
            new_head in snake):
            beep("game_over")
            animated_flash(C_RED)
            show_popup(f"GAME OVER! Score: {score}", C_RED)
            if score > high_score:
                update_stats('snake', 'high_score', score)
                show_popup("NEW HIGH SCORE!", C_YELLOW)
            return

        snake.insert(0, new_head)
        
        if new_head == food:
            score += 10
            beep("eat")
            food = create_food(snake)
            if score % 50 == 0: speed = max(0.05, speed - 0.01) # Speed up
        else:
            snake.pop()
            
if __name__ == "__main__":
    play_snake()
