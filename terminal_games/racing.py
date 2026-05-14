import time
import random
import logging
from base_game import BaseGame
from input_handler import get_safe_input_handler
from arcade_utils import (
    clear_screen, print_big_title, beep, show_popup, 
    screen_shake, particle_effect, animated_flash,
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_MAGENTA, C_WHITE, C_BLACK
)

logger = logging.getLogger(__name__)

BOARD_WIDTH = 20
BOARD_HEIGHT = 15

class RacingGame(BaseGame):
    """Terminal Racing game implementation."""
    
    def __init__(self, difficulty='normal'):
        super().__init__("racing", difficulty)
        self.input_handler = get_safe_input_handler()
        self.player_x = BOARD_WIDTH // 2
        self.enemies = [] # List of [y, x]
        self.frame_count = 0
        self.speed = 0.1
        self.road_offset = 0
        
        # Difficulty scaling
        if difficulty == 'easy': self.speed = 0.15
        elif difficulty == 'hard': self.speed = 0.07

    def play(self) -> dict:
        self.start_timer()
        clear_screen()
        print_big_title("RACING", color=C_RED)
        time.sleep(1)
        
        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            time.sleep(self.speed)
            
        self.end_timer()
        high_score = self.stats_manager.get_high_score('racing')
        if self.score > high_score:
            show_popup("NEW HIGH SCORE!", C_YELLOW)
            
        self.save_stats({
            'high_score': max(self.score, high_score),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })
        return self.get_final_stats()

    def _render(self):
        print(f"{C_BOLD}{C_RED}RACING - SCORE: {self.score}{C_RESET}")
        
        # Grid
        grid = [[' ' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        
        # Draw road markers
        self.road_offset = (self.road_offset + 1) % 4
        for y in range(BOARD_HEIGHT):
            if (y + self.road_offset) % 4 == 0:
                grid[y][0] = '║'
                grid[y][BOARD_WIDTH-1] = '║'
        
        # Draw enemies
        for ey, ex in self.enemies:
            if 0 <= ey < BOARD_HEIGHT:
                grid[int(ey)][int(ex)] = '▼'
        
        # Draw player
        grid[BOARD_HEIGHT - 2][self.player_x] = '▲'
        
        # Render
        print(f"{C_WHITE}╔{'═' * BOARD_WIDTH}╗{C_RESET}")
        for r in range(BOARD_HEIGHT):
            line = f"{C_WHITE}║{C_RESET}"
            for c in range(BOARD_WIDTH):
                char = grid[r][c]
                if char == '▲': line += f"{C_CYAN}{char}{C_RESET}"
                elif char == '▼': line += f"{C_RED}{char}{C_RESET}"
                elif char == '║': line += f"{C_WHITE}{char}{C_RESET}"
                else: line += char
            line += f"{C_WHITE}║{C_RESET}"
            print(line)
        print(f"{C_WHITE}╚{'═' * BOARD_WIDTH}╝{C_RESET}")

    def _handle_input(self):
        k = self.input_handler.get_safe_key()
        if k == 'q':
            self.game_over = True
        elif k == 'left' and self.player_x > 1:
            self.player_x -= 1
        elif k == 'right' and self.player_x < BOARD_WIDTH - 2:
            self.player_x += 1

    def _update_game_state(self):
        # Move enemies
        new_enemies = []
        for ey, ex in self.enemies:
            ey += 1
            if ey < BOARD_HEIGHT:
                # Collision
                if int(ey) == BOARD_HEIGHT - 2 and int(ex) == self.player_x:
                    self._die("CRASHED!")
                    return
                new_enemies.append([ey, ex])
            else:
                # Passed
                self.score += 10
                self.award_xp_for_action(10)
                if self.score == 100: self.unlock_achievement("racing_100", "Speedster")
                if self.score == 500: self.unlock_achievement("racing_500", "Pro Racer")
        self.enemies = new_enemies
        
        # Spawn new enemies
        self.frame_count += 1
        spawn_rate = 10
        if self.difficulty == 'hard': spawn_rate = 7
        if self.frame_count % spawn_rate == 0:
            self.enemies.append([0, random.randint(1, BOARD_WIDTH - 2)])

    def _die(self, msg):
        beep("game_over")
        screen_shake(0.5, 5)
        animated_flash(C_RED)
        show_popup(msg, C_RED)
        self.game_over = True

def play_racing(difficulty='normal'):
    game = RacingGame(difficulty)
    return game.play()

if __name__ == "__main__":
    play_racing()
