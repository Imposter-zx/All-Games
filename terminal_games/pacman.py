import time
import os
import random
from arcade_utils import (
    clear_screen, get_key, draw_retro_box, beep, show_popup, 
    update_stats, load_stats, animated_flash, print_big_title, 
    add_xp, screen_shake, particle_effect, 
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

# 1 = Wall, 0 = Pellet, 2 = Power Pellet, 3 = Empty
PACMAN_MAP = [
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

PACMANchar = f"{C_YELLOW}C{C_RESET}"
GHOSTchar = f"{C_RED}M{C_RESET}"
PELLETchar = f"{C_WHITE}.{C_RESET}"
POWERchar = f"{C_CYAN}o{C_RESET}"
WALLchar = f"{C_BLUE}█{C_RESET}"

class PacmanGame(BaseGame):
    """Pac-Man game implementation using BaseGame."""
    
    def __init__(self, difficulty='normal'):
        super().__init__("pacman", difficulty)
        self.game_map = [row[:] for row in PACMAN_MAP]
        self.pac_x, self.pac_y = 7, 8
        self.ghosts = [[1, 1], [13, 1], [1, 12], [13, 12]]
        self.power_timer = 0
        self.total_pellets = sum(row.count(0) + row.count(2) for row in self.game_map)
        self.pellets_eaten = 0
        self.last_move_time = time.time()
        self.input_handler = get_safe_input_handler()

    def play(self) -> dict:
        """Main Pac-Man game loop."""
        self.start_timer()
        clear_screen()
        print_big_title("PAC-MAN", color=C_YELLOW)
        time.sleep(1)
        
        while not self.game_over:
            self._render()
            self._handle_input()
            self._update_game_state()
            time.sleep(0.1) # Game tick
            
        self.end_timer()
        
        # Save stats
        stats = self.stats_manager.get_stats('pacman')
        wins = stats.get('wins', 0)
        high_score = self.stats_manager.get_high_score('pacman')
        
        if self.score > high_score:
            show_popup("NEW HIGH SCORE!", C_YELLOW)
            
        self.save_stats({
            'high_score': max(self.score, high_score),
            'wins': wins + (1 if self.pellets_eaten >= self.total_pellets else 0),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })
        
        return self.get_final_stats()

    def _render(self):
        """Render the Pac-Man map and entities."""
        clear_screen()
        high_score = self.stats_manager.get_high_score('pacman')
        
        print(f" SCORE: {C_GREEN}{self.score:<6}{C_RESET} | HI: {high_score:<6} | POWER: {f'{C_CYAN}{self.power_timer}{C_RESET}' if self.power_timer > 0 else 'OFF'}")
        
        for y, row in enumerate(self.game_map):
            line = ""
            for x, cell in enumerate(row):
                # Check entities
                is_entity = False
                if (x, y) == (self.pac_x, self.pac_y):
                    line += PACMANchar + " "
                    is_entity = True
                else:
                    for gx, gy in self.ghosts:
                        if (x, y) == (gx, gy):
                            if self.power_timer > 0:
                                line += f"{C_BLUE}m{C_RESET} "
                            else:
                                line += GHOSTchar + " "
                            is_entity = True
                            break
                
                if not is_entity:
                    if cell == 1: line += WALLchar * 2
                    elif cell == 0: line += PELLETchar + " "
                    elif cell == 2: line += POWERchar + " "
                    else: line += "  "
            print(line)
        print(f"\n{C_WHITE}ARROWS/WASD: Move | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle movement input using SafeInputHandler."""
        k = self.input_handler.get_safe_key()
        if not k:
            return
            
        if k == 'q':
            self.game_over = True
            return
            
        direction = self.input_handler.validator.validate_direction(k)
        dx, dy = 0, 0
        if direction == 'up': dy = -1
        elif direction == 'down': dy = 1
        elif direction == 'left': dx = -1
        elif direction == 'right': dx = 1
        
        if dx != 0 or dy != 0:
            self._move_pacman(dx, dy)

    def _move_pacman(self, dx, dy):
        """Move Pac-Man if possible."""
        new_x = self.pac_x + dx
        new_y = self.pac_y + dy
        
        if self.game_map[new_y][new_x] != 1:
            self.pac_x = new_x
            self.pac_y = new_y
            self._eat_cell(new_x, new_y)

    def _eat_cell(self, x, y):
        """Handle eating pellets."""
        cell = self.game_map[y][x]
        if cell == 0: # Pellet
            self.game_map[y][x] = 3
            self.score += 10
            self.award_xp_for_action(10) # Award XP based on difficulty
            self.pellets_eaten += 1
            beep("eat")
        elif cell == 2: # Power Pellet
            self.game_map[y][x] = 3
            self.score += 50
            self.award_xp_for_action(50)
            self.power_timer = 30
            self.pellets_eaten += 1
            beep("win") # Powerup sound
            screen_shake(0.05, 1)

    def _update_game_state(self):
        """Update ghost movement and game status."""
        self._move_ghosts()
        self._check_collisions()
        
        if self.power_timer > 0:
            self.power_timer -= 1
            
        if self.pellets_eaten >= self.total_pellets:
            self._handle_win()

    def _move_ghosts(self):
        """Simple AI to move ghosts towards/away from Pac-Man."""
        if random.random() > 0.4: # Move ghosts every few frames
            return
            
        for i in range(len(self.ghosts)):
            gx, gy = self.ghosts[i]
            g_dx, g_dy = 0, 0
            
            if self.power_timer > 0:
                # Run away!
                if self.pac_x > gx: g_dx = -1
                else: g_dx = 1
                if self.pac_y > gy: g_dy = -1
                else: g_dy = 1
            else:
                # Hunter mode
                if self.pac_x > gx: g_dx = 1
                elif self.pac_x < gx: g_dx = -1
                if self.pac_y > gy: g_dy = 1
                elif self.pac_y < gy: g_dy = -1
            
            # Decide horizontal or vertical
            if random.random() > 0.5:
                if self.game_map[gy][gx + g_dx] != 1: gx += g_dx
            else:
                if self.game_map[gy + g_dy][gx] != 1: gy += g_dy
                
            self.ghosts[i] = [gx, gy]

    def _check_collisions(self):
        """Check for contact with ghosts."""
        for i, (gx, gy) in enumerate(self.ghosts):
            if (self.pac_x, self.pac_y) == (gx, gy):
                if self.power_timer > 0:
                    # Eat ghost
                    self.score += 200
                    self.award_xp_for_action(100)
                    self.ghosts[i] = [7, 7] # Send to house
                    screen_shake(0.1, 1)
                    particle_effect(char="*", color=C_CYAN, count=5)
                    beep("win")
                else:
                    self._handle_death()
                    break

    def _handle_death(self):
        """Handle player getting caught."""
        beep("lose")
        animated_flash(C_RED)
        show_popup(f"GHOST CAUGHT YOU! Score: {self.score}", C_RED)
        self.game_over = True

    def _handle_win(self):
        """Handle level completion."""
        beep("win")
        show_popup(f"LEVEL CLEAR! YOU WIN! Score: {self.score}", C_YELLOW)
        self.game_over = True

def play_pacman(difficulty='normal'):
    """Wrapper function for arcade.py compatibility."""
    game = PacmanGame(difficulty)
    return game.play()

if __name__ == "__main__":
    play_pacman()
