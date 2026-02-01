import time
import os
import random
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, update_stats, load_stats, animated_flash, print_big_title, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK

WIDTH = 30
HEIGHT = 20
PLAYER_CHAR = "▲"
ENEMY_CHAR = "W"
BULLET_CHAR = "|"

def play_space_shooter():
    clear_screen()
    print_big_title("SPACE SHOOTER", color=C_MAGENTA)
    time.sleep(1)
    
    player_x = WIDTH // 2
    bullets = []
    enemies = []
    
    score = 0
    lives = 3
    spawn_timer = 0
    stats = load_stats().get('space_shooter', {})
    high_score = stats.get('high_score', 0)
    
    while True:
        # 1. Update Game State
        # Spawn enemies
        spawn_timer += 1
        if spawn_timer > 10: # Adjust spawn rate
            enemies.append({'x': random.randint(1, WIDTH-2), 'y': 0})
            spawn_timer = 0
            
        # Move bullets
        for b in bullets:
            b['y'] -= 1
        bullets = [b for b in bullets if b['y'] > 0]
        
        # Move enemies
        move_enemies = (random.randint(0, 5) == 0) # Move slower
        if move_enemies:
            for e in enemies:
                e['y'] += 1
        
        # Collisions
        # Bullet - Enemy
        for b in bullets[:]:
            hit = False
            for e in enemies[:]:
                if b['x'] == e['x'] and b['y'] == e['y']:
                    bullets.remove(b)
                    enemies.remove(e)
                    score += 10
                    beep("eat")
                    hit = True
                    break
            if hit: continue
            
        # Enemy - Player / Bottom
        hit_player = False
        for e in enemies[:]:
            if e['y'] >= HEIGHT - 1:
                enemies.remove(e)
                lives -= 1
                hit_player = True
            elif e['x'] == player_x and e['y'] == HEIGHT - 1:
                 enemies.remove(e)
                 lives -= 1
                 hit_player = True
        
        if hit_player:
            animated_flash(C_RED)
            beep("lose")
            if lives <= 0:
                show_popup(f"GAME OVER! Score: {score}", C_RED)
                if score > high_score:
                    update_stats("space_shooter", "high_score", score)
                break
        
        # 2. Draw
        clear_screen()
        print(f"{C_MAGENTA}╔{'═' * WIDTH}╗")
        print(f"║ SCORE: {score:<10} HI: {high_score:<10} LIVES: {lives} ║")
        print(f"╚{'═' * WIDTH}╝{C_RESET}")
        
        print(f"{C_MAGENTA}╔{'═' * WIDTH}╗{C_RESET}")
        for r in range(HEIGHT):
            line = f"{C_MAGENTA}║{C_RESET}"
            row = [" "] * WIDTH
            
            if r == HEIGHT - 1:
                row[player_x] = f"{C_CYAN}{PLAYER_CHAR}{C_RESET}"
                
            for b in bullets:
                if b['y'] == r: row[b['x']] = f"{C_YELLOW}{BULLET_CHAR}{C_RESET}"
                
            for e in enemies:
                if e['y'] == r: row[e['x']] = f"{C_RED}{ENEMY_CHAR}{C_RESET}"
                
            line += "".join(row) + f"{C_MAGENTA}║{C_RESET}"
            print(line)
        print(f"{C_MAGENTA}╚{'═' * WIDTH}╝{C_RESET}")
        print(f"{C_WHITE}ARROWS to Move | SPACE to Shoot | Q to Quit{C_RESET}")
        
        # 3. Input
        if os.name == 'nt':
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':
                    key = msvcrt.getch()
                    if key == b'K': player_x = max(0, player_x - 1)
                    elif key == b'M': player_x = min(WIDTH - 1, player_x + 1)
                elif key == b' ':
                    bullets.append({'x': player_x, 'y': HEIGHT - 2})
                    beep("correct")
                elif key.lower() == b'q': break
        else:
             # Unix simple check
             import select, sys
             if select.select([sys.stdin], [], [], 0)[0]:
                 k = sys.stdin.read(1) # simplified
                 if k == 'q': break
                 
        time.sleep(0.05)

if __name__ == "__main__":
    play_space_shooter()
