import time
import random
import logging
from base_game import BaseGame
from input_handler import get_safe_input_handler
from arcade_utils import (
    clear_screen, print_big_title, beep, show_popup, 
    screen_shake, particle_effect, animated_flash,
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_MAGENTA, C_WHITE, u_safe
)

logger = logging.getLogger(__name__)

BOARD_WIDTH = 40
BOARD_HEIGHT = 10 # 0-9

class FroggerGame(BaseGame):
    """Frogger game implementation."""
    
    def __init__(self, difficulty='normal'):
        super().__init__("frogger", difficulty)
        self.input_handler = get_safe_input_handler()
        self.player_pos = [BOARD_HEIGHT - 1, BOARD_WIDTH // 2]
        self.obstacles = [] # List of {'row': int, 'type': str, 'pos': float, 'speed': float, 'char': str}
        self.lives = 3
        self.goal_reached = 0
        
        # Difficulty scaling
        speed_mult = 1.0
        if difficulty == 'easy': speed_mult = 0.7
        elif difficulty == 'hard': speed_mult = 1.4
        self.speed_mult = speed_mult
        
        self._init_level()

    def _init_level(self):
        self.obstacles = []
        # Row 1-3: River (Logs)
        for r in range(1, 4):
            # Alternate directions
            direction = 1 if r % 2 == 0 else -1
            speed = (random.random() * 0.15 + 0.1) * direction
            char = "==== "
            # Add logs per row
            for i in range(0, BOARD_WIDTH, 12):
                self.obstacles.append({
                    'row': r, 
                    'type': 'log', 
                    'pos': float(i), 
                    'speed': speed, 
                    'char': char
                })
        
        # Row 5-7: Road (Cars)
        for r in range(5, 8):
            direction = -1 if r % 2 == 0 else 1
            speed = (random.random() * 0.25 + 0.15) * direction
            char = "[XX] "
            for i in range(0, BOARD_WIDTH, 15):
                 self.obstacles.append({
                     'row': r, 
                     'type': 'car', 
                     'pos': float(i), 
                     'speed': speed, 
                     'char': char
                 })

    def play(self) -> dict:
        """Main game loop."""
        self.start_timer()
        clear_screen()
        print_big_title("FROGGER", color=C_GREEN)
        time.sleep(1)
        
        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            time.sleep(0.05)
            
        self.end_timer()
        
        # Save stats
        high_score = self.stats_manager.get_high_score('frogger')
        if self.score > high_score:
            show_popup("NEW HIGH SCORE!", C_YELLOW)
        
        self.save_stats({
            'high_score': max(self.score, high_score),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty,
            'goals': self.goal_reached
        })
        
        return self.get_final_stats()

    def _render(self):
        """Render the game board."""
        # Header
        heart = u_safe("♥", "v")
        lives_display = f"{C_RED}{heart}{C_GREEN}" * self.lives
        print(f"{C_BOLD}{C_GREEN}FROGGER - LIVES: {lives_display} | SCORE: {self.score} | GOALS: {self.goal_reached}{C_RESET}")
        print(u_safe("≈", "~") * BOARD_WIDTH + f"{C_RESET}")
        
        # Grid
        grid = [[' ' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        
        # Draw obstacles
        for obs in self.obstacles:
            r = obs['row']
            char = obs['char']
            for i, c in enumerate(char):
                pos = int(obs['pos'] + i) % BOARD_WIDTH
                grid[r][pos] = c
        
        # Render board with colors
        for r in range(BOARD_HEIGHT):
            line = ""
            # Determine row base color
            if r == 0: row_color = C_CYAN # Goal
            elif 1 <= r <= 3: row_color = C_BLUE # River
            elif r == 4 or r == 8 or r == 9: row_color = C_GREEN # Safe
            elif 5 <= r <= 7: row_color = C_RED # Road
            else: row_color = C_WHITE
            
            for c in range(BOARD_WIDTH):
                if [r, c] == self.player_pos:
                    line += f"{C_YELLOW}@{C_RESET}"
                else:
                    char = grid[r][c]
                    if char in '[]X': 
                        line += f"{C_RED}{char}{C_RESET}"
                    elif char == '=': 
                        line += f"{C_MAGENTA}{char}{C_RESET}"
                    else: 
                        # Background coloring for river/road
                        if 1 <= r <= 3 and char == ' ':
                            line += f"{C_BLUE}{u_safe('≋', '~')}{C_RESET}"
                        elif 5 <= r <= 7 and char == ' ':
                            line += f"{C_BLACK}{u_safe('▒', '#')}{C_RESET}"
                        else:
                            line += f"{row_color}{char}{C_RESET}"
            print(line)
        print(f"{C_BLUE}" + u_safe("≈", "~") * BOARD_WIDTH + f"{C_RESET}")

    def _handle_input(self):
        """Process player movement."""
        k = self.input_handler.get_safe_key()
        if not k:
            return
            
        if k == 'q':
            self.game_over = True
        elif k == 'up' and self.player_pos[0] > 0:
            self.player_pos[0] -= 1
        elif k == 'down' and self.player_pos[0] < BOARD_HEIGHT - 1:
            self.player_pos[0] += 1
        elif k == 'left' and self.player_pos[1] > 0:
            self.player_pos[1] -= 1
        elif k == 'right' and self.player_pos[1] < BOARD_WIDTH - 1:
            self.player_pos[1] += 1

    def _update_game_state(self):
        """Update positions and check collisions."""
        player_on_log = False
        log_speed = 0
        
        # Move obstacles
        for obs in self.obstacles:
            obs['pos'] = (obs['pos'] + obs['speed'] * self.speed_mult) % BOARD_WIDTH
            
            # Check collision
            r, c = self.player_pos
            if obs['row'] == r:
                # Car collision
                if obs['type'] == 'car':
                    # Check if player is within the car's range (approx 4 chars)
                    obs_start = int(obs['pos'])
                    # Check wrapping range
                    hit = False
                    for i in range(4):
                        if (obs_start + i) % BOARD_WIDTH == c:
                            hit = True
                            break
                    if hit:
                        self._death("SQUASHED!")
                        return
                        
                # Log interaction
                elif obs['type'] == 'log':
                    obs_start = int(obs['pos'])
                    for i in range(4):
                        if (obs_start + i) % BOARD_WIDTH == c:
                            player_on_log = True
                            log_speed = obs['speed']
                            break

        # River logic
        r, c = self.player_pos
        if 1 <= r <= 3:
            if not player_on_log:
                self._death("SPLASH!")
                return
            else:
                # Move player with log
                self.player_pos[1] = int(self.player_pos[1] + log_speed * self.speed_mult)
                # Wrap or die at edge? Frogger usually dies if it leaves screen
                if self.player_pos[1] < 0 or self.player_pos[1] >= BOARD_WIDTH:
                    self._death("SWEPT AWAY!")
                    return

        # Goal logic
        if r == 0:
            self.score += 100
            self.award_xp_for_action(100)
            self.goal_reached += 1
            beep("win")
            particle_effect(char=u_safe("★", "*"), color=C_YELLOW, count=10)
            show_popup("GOAL REACHED!", C_GREEN)
            self.player_pos = [BOARD_HEIGHT - 1, BOARD_WIDTH // 2]
            
            # Achievements
            if self.goal_reached == 1:
                self.unlock_achievement("frogger_first", "Crosser")
            elif self.goal_reached == 5:
                self.unlock_achievement("frogger_5", "Highway Hero")
            elif self.goal_reached == 10:
                self.unlock_achievement("frogger_10", "Leap Master")
                
            # Increase difficulty
            self.speed_mult += 0.1

    def _death(self, msg):
        """Handle player death."""
        self.lives -= 1
        beep("game_over")
        screen_shake(0.3, 3)
        animated_flash(C_RED)
        show_popup(msg, C_RED)
        if self.lives <= 0:
            self.game_over = True
        else:
            self.player_pos = [BOARD_HEIGHT - 1, BOARD_WIDTH // 2]

def play_frogger(difficulty='normal'):
    """Wrapper to run the game."""
    game = FroggerGame(difficulty)
    return game.play()

if __name__ == "__main__":
    play_frogger()
