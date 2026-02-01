import time
import os
import random
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, update_stats, load_stats, animated_flash, print_big_title, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK

WIDTH = 40
HEIGHT = 20
PADDLE_WIDTH = 6

def play_breakout():
    clear_screen()
    print_big_title("BREAKOUT", color=C_CYAN)
    time.sleep(1)
    
    # Init
    paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
    ball_x = WIDTH // 2
    ball_y = HEIGHT - 2
    ball_dx = 1
    ball_dy = -1
    
    # Bricks: 3 rows
    # Row 0: Red, Row 1: Orange(Yellow), Row 2: Green
    bricks = []
    colors = [C_RED, C_YELLOW, C_GREEN]
    for r in range(3):
        for c in range(0, WIDTH-2, 4):
            bricks.append({'x': c+1, 'y': r+2, 'color': colors[r], 'active': True})
            
    score = 0
    lives = 3
    
    stats = load_stats().get('breakout', {})
    best_score = stats.get('best_score', 0)
    
    while True:
        # Draw
        clear_screen()
        # Header
        print(f"{C_CYAN}╔{'═' * WIDTH}╗")
        print(f"║ SCORE: {score:<10} BEST: {best_score:<10} LIVES: {lives} ║")
        print(f"╚{'═' * WIDTH}╝{C_RESET}")
        
        # Field
        print(f"{C_CYAN}╔{'═' * WIDTH}╗{C_RESET}")
        for r in range(HEIGHT):
            line = f"{C_CYAN}║{C_RESET}"
            row_content = ""
            c = 0
            while c < WIDTH:
                # Ball
                if r == int(ball_y) and c == int(ball_x):
                    row_content += f"{C_WHITE}●{C_RESET}"
                    c += 1
                    continue
                
                # Paddle
                if r == HEIGHT - 1 and paddle_x <= c < paddle_x + PADDLE_WIDTH:
                    row_content += f"{C_MAGENTA}═{C_RESET}"
                    c += 1
                    continue
                    
                # Bricks
                found_brick = None
                for b in bricks:
                    if b['active'] and b['y'] == r and b['x'] <= c < b['x'] + 3:
                         found_brick = b
                         break
                
                if found_brick:
                    row_content += f"{found_brick['color']}█{C_RESET}"
                    c += 1
                else:
                    row_content += " "
                    c += 1
            line += row_content + f"{C_CYAN}║{C_RESET}"
            print(line)
        print(f"{C_CYAN}╚{'═' * WIDTH}╝{C_RESET}")
        print(f"{C_WHITE}LEFT/RIGHT to Move | Q to Quit{C_RESET}")
        
        # Input (Non-blocking check simple for now)
        # We'll use a simple approach: wait a tiny bit for input, update physics
        
        if os.name == 'nt':
             import msvcrt
             if msvcrt.kbhit():
                 key = msvcrt.getch()
                 if key == b'\xe0': # Arrow
                     key = msvcrt.getch()
                     if key == b'K': paddle_x = max(0, paddle_x - 2)
                     elif key == b'M': paddle_x = min(WIDTH - PADDLE_WIDTH, paddle_x + 2)
                 elif key.lower() == b'q': break
        else:
             # Unix simple check
             import select, sys
             if select.select([sys.stdin], [], [], 0)[0]:
                 k = sys.stdin.read(1)
                 if k == '\033': # Arrow
                     sys.stdin.read(2) # skip [ and code roughly
                     # Simplified for prototype, ideally strict parsing
                     # In real usage we might need better key mapping
                     pass 
                 elif k == 'q': break
                 
        # Physics
        ball_x += ball_dx
        ball_y += ball_dy
        
        # Walls
        if ball_x <= 0 or ball_x >= WIDTH - 1:
            ball_dx *= -1
            beep("correct")
        if ball_y <= 0:
            ball_dy *= -1
            beep("correct")
            
        # Paddle
        if ball_y >= HEIGHT - 1:
            if paddle_x <= ball_x <= paddle_x + PADDLE_WIDTH:
                ball_dy *= -1
                # Angle tweak?
                beep("correct")
            else:
                lives -= 1
                beep("lose")
                animated_flash(C_RED)
                if lives == 0:
                    show_popup(f"GAME OVER! Score: {score}", C_RED)
                    if score > best_score:
                        update_stats('breakout', 'best_score', score)
                    break
                else:
                    ball_x, ball_y = WIDTH // 2, HEIGHT - 2
                    ball_dy = -1
                    time.sleep(1)

        # Bricks
        hit = False
        for b in bricks:
            if b['active']:
                if int(ball_y) == b['y'] and b['x'] <= int(ball_x) < b['x'] + 3:
                    b['active'] = False
                    ball_dy *= -1
                    score += 10
                    beep("eat")
                    hit = True
                    break
        
        if hit:
             # Speed up slightly?
             pass
             
        if all(not b['active'] for b in bricks):
            beep("win")
            show_popup("YOU WON! LEVEL CLEARED", C_GREEN)
            if score > best_score:
                update_stats('breakout', 'best_score', score)
            break
            
        time.sleep(0.05)

if __name__ == "__main__":
    play_breakout()
