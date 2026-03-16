import time
import os
import random
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, update_stats, load_stats, animated_flash, print_big_title, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK

# Pacman Map
# 1 = Wall, 0 = Pellet, 2 = Power Pellet, 3 = Empty
ORIGINAL_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,0,1,0,1,1,0,1],
    [1,2,0,0,0,0,0,0,0,0,0,0,0,2,1],
    [1,0,1,1,0,1,1,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
    [1,1,1,1,0,1,0,0,0,1,0,1,1,1,1],
    [1,1,1,1,0,1,1,3,1,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,1,1,0,0,0,1,0,0,0,1,1,0,1],
    [1,2,0,1,0,1,0,1,0,1,0,1,0,2,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

PACMAN = f"{C_YELLOW}C{C_RESET}"
GHOST = f"{C_RED}M{C_RESET}"
PELLET = f"{C_WHITE}.{C_RESET}"
POWER = f"{C_CYAN}o{C_RESET}"
WALL = f"{C_BLUE}█{C_RESET}"

def draw_game(game_map, pac_pos, ghosts, score, power_timer):
    clear_screen()
    print_big_title("PAC-MAN", color=C_YELLOW)
    print(f" SCORE: {C_GREEN}{score}{C_RESET} | POWER: {'READY' if power_timer > 0 else 'OFF'}")
    
    for y, row in enumerate(game_map):
        line = ""
        for x, cell in enumerate(row):
            # Check entities
            is_entity = False
            if (x, y) == pac_pos:
                line += PACMAN + " "
                is_entity = True
            else:
                for gx, gy in ghosts:
                    if (x, y) == (gx, gy):
                        line += GHOST + " "
                        is_entity = True
                        break
            
            if not is_entity:
                if cell == 1: line += WALL * 2
                elif cell == 0: line += PELLET + " "
                elif cell == 2: line += POWER + " "
                else: line += "  "
        print(line)
    print(f"\n{C_WHITE}Use Arrows to move, Q to quit{C_RESET}")

def play_pacman():
    game_map = [row[:] for row in ORIGINAL_MAP]
    pac_x, pac_y = 7, 8
    ghosts = [[1, 1], [13, 1], [1, 12], [13, 12]]
    score = 0
    power_timer = 0
    
    # Calculate total pellets
    total_pellets = sum(row.count(0) + row.count(2) for row in game_map)
    pellets_eaten = 0
    
    while True:
        draw_game(game_map, (pac_x, pac_y), ghosts, score, power_timer)
        
        # Collision with ghosts
        for gx, gy in ghosts:
            if (pac_x, pac_y) == (gx, gy):
                if power_timer > 0:
                    score += 200
                    # Reset ghost (simplified)
                    ghosts[ghosts.index([gx, gy])] = [7, 7]
                    beep("win")
                else:
                    beep("lose")
                    show_popup(f"GHOST CAUGHT YOU! Score: {score}", C_RED)
                    return
        
        key = get_key()
        if key == 'q': break
        
        dx, dy = 0, 0
        if key == 'up': dy = -1
        elif key == 'down': dy = 1
        elif key == 'left': dx = -1
        elif key == 'right': dx = 1
        
        # Move Pacman
        if game_map[pac_y + dy][pac_x + dx] != 1:
            pac_x += dx
            pac_y += dy
            
            # Eat pellets
            cell = game_map[pac_y][pac_x]
            if cell == 0:
                game_map[pac_y][pac_x] = 3
                score += 10
                pellets_eaten += 1
                beep("eat")
            elif cell == 2:
                game_map[pac_y][pac_x] = 3
                score += 50
                power_timer = 20
                pellets_eaten += 1
                beep("win")
        
        # Move Ghosts (Simple AI)
        if random.random() > 0.3: # Move ghosts occasionally
            for i in range(len(ghosts)):
                gx, gy = ghosts[i]
                g_dx, g_dy = 0, 0
                if pac_x > gx: g_dx = 1
                elif pac_x < gx: g_dx = -1
                if pac_y > gy: g_dy = 1
                elif pac_y < gy: g_dy = -1
                
                # Try move towards pacman
                if random.random() > 0.5:
                    if game_map[gy][gx + g_dx] != 1: gx += g_dx
                else:
                    if game_map[gy + g_dy][gx] != 1: gy += g_dy
                ghosts[i] = [gx, gy]

        if power_timer > 0: power_timer -= 1
        
        if pellets_eaten >= total_pellets:
            show_popup(f"LEVEL CLEAR! YOU WIN! Score: {score}", C_YELLOW)
            update_stats("pacman", "wins", 1)
            break

if __name__ == "__main__":
    play_pacman()
