"""
Pong Game implementation for the Retro Arcade.
A classic table tennis game where you control a paddle and bounce a ball.
"""

import random
import time
import logging
from base_game import BaseGame
from input_handler import get_safe_input_handler
from arcade_utils import C_WHITE, C_YELLOW, C_CYAN, C_GREEN, C_MAGENTA, C_RED, C_BLUE, C_BOLD, C_RESET, draw_retro_box, beep

logger = logging.getLogger(__name__)

class PongGame(BaseGame):
    """Pong Game logic and rendering."""
    
    def __init__(self, difficulty='normal'):
        super().__init__('pong', difficulty)
        self.width = 40
        self.height = 15
        self.paddle_size = 3
        self.paddle_pos = self.height // 2 - self.paddle_size // 2
        
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = 1
        self.ball_dy = random.choice([-1, 1])
        
        # Difficulty settings
        if difficulty == 'easy':
            self.paddle_size = 5
            self.speed = 0.1
        elif difficulty == 'hard':
            self.paddle_size = 2
            self.speed = 0.04
        else:
            self.paddle_size = 3
            self.speed = 0.07
            
        self.paddle_pos = max(0, min(self.height - self.paddle_size, self.paddle_pos))
        self.hits = 0
        
    def move_paddle(self, direction):
        """Move the paddle up or down."""
        if direction == 'up' and self.paddle_pos > 0:
            self.paddle_pos -= 1
        elif direction == 'down' and self.paddle_pos < self.height - self.paddle_size:
            self.paddle_pos += 1

    def update_ball(self):
        """Update ball position and handle collisions."""
        new_x = self.ball_x + self.ball_dx
        new_y = self.ball_y + self.ball_dy
        
        # Wall collisions (top/bottom)
        if new_y <= 0 or new_y >= self.height - 1:
            self.ball_dy *= -1
            beep("move")
            new_y = self.ball_y + self.ball_dy
            
        # Paddle collision (left side)
        if new_x == 1:
            if self.paddle_pos <= new_y < self.paddle_pos + self.paddle_size:
                self.ball_dx *= -1
                self.hits += 1
                self.score += 10
                self.award_xp_for_action(10)
                beep("correct")
                
                # Check achievements
                if self.hits == 10:
                    self.unlock_achievement("pong_pro", "Pong Pro")
                elif self.hits == 25:
                    self.unlock_achievement("pong_master", "Pong Master")
            else:
                # Game Over
                self.game_over = True
                beep("lose")
                return
        
        # Right wall collision (bounce)
        if new_x >= self.width - 1:
            self.ball_dx *= -1
            beep("move")
            new_x = self.ball_x + self.ball_dx
            
        self.ball_x = new_x
        self.ball_y = new_y

    def render(self):
        """Draw the game board."""
        lines = []
        lines.append(f" SCORE: {C_YELLOW}{self.score}{C_RESET}  |  HITS: {C_GREEN}{self.hits}{C_RESET}  |  DIFFICULTY: {self.difficulty.upper()}")
        lines.append("─" * self.width)
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if x == 0:
                    if self.paddle_pos <= y < self.paddle_pos + self.paddle_size:
                        row += f"{C_CYAN}█{C_RESET}"
                    else:
                        row += " "
                elif x == self.ball_x and y == self.ball_y:
                    row += f"{C_YELLOW}●{C_RESET}"
                elif x == self.width - 1:
                    row += f"{C_WHITE}│{C_RESET}"
                else:
                    row += " "
            lines.append(row)
            
        lines.append("─" * self.width)
        draw_retro_box(self.width + 4, "🏓 PONG ARCADE", lines, color=C_BLUE)
        print(f"\n{C_WHITE}   [UP/DOWN] Move  [Q] Quit{C_RESET}")

    def play(self):
        self.start_timer()
        input_handler = get_safe_input_handler()
        
        try:
            while not self.game_over:
                self.renderer.render_frame(self.render)
                
                direction = input_handler.get_direction()
                if direction:
                    self.move_paddle(direction)
                
                self.update_ball()
                
                key = input_handler.get_safe_key()
                if key and key.lower() == 'q':
                    break
                    
                time.sleep(self.speed)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            # Add high_score key for compatibility with stats_manager
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats

def play_pong(difficulty='normal'):
    """Entry point for the Pong game."""
    game = PongGame(difficulty)
    return game.play()

if __name__ == "__main__":
    play_pong()
