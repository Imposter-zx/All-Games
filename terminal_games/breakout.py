import time
import os
import random
from arcade_utils import (
    clear_screen, get_key, draw_retro_box, beep, show_popup, 
    update_stats, load_stats, animated_flash, print_big_title, 
    add_xp, screen_shake, particle_effect, 
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK
)
from base_game import BaseGame

WIDTH = 40
HEIGHT = 20
PADDLE_WIDTH = 6

class BreakoutGame(BaseGame):
    """Breakout game implementation using BaseGame."""
    
    def __init__(self):
        super().__init__("breakout")
        self.paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT - 2
        self.ball_dx = 1
        self.ball_dy = -1
        self.lives = 3
        self.bricks = self._init_bricks()
        
    def _init_bricks(self):
        bricks = []
        colors = [C_RED, C_YELLOW, C_GREEN]
        for r in range(3):
            for c in range(0, WIDTH - 2, 4):
                bricks.append({'x': c + 1, 'y': r + 2, 'color': colors[r], 'active': True})
        return bricks

    def play(self) -> dict:
        """Main Breakout game loop."""
        self.start_timer()
        clear_screen()
        print_big_title("BREAKOUT", color=C_CYAN)
        time.sleep(1)
        
        while not self.game_over:
            self._render()
            self._handle_input()
            self._update_game_state()
            time.sleep(0.04) # Control game speed
            
        self.end_timer()
        
        # Save stats
        stats = load_stats().get('breakout', {})
        high_score = stats.get('high_score', 0)
        if self.score > high_score:
            update_stats('breakout', 'high_score', self.score)
            show_popup("NEW HIGH SCORE!", C_YELLOW)
            
        self.save_stats({
            'high_score': max(self.score, high_score),
            'last_score': self.score,
            'xp_earned': self.xp_earned
        })
        
        return self.get_final_stats()

    def _render(self):
        """Render the game board and UI."""
        clear_screen()
        stats = load_stats().get('breakout', {})
        high_score = stats.get('high_score', 0)
        
        # Header
        print(f"{C_CYAN}╔{'═' * WIDTH}╗")
        print(f"║ SCORE: {self.score:<10} BEST: {high_score:<10} LIVES: {self.lives} ║")
        print(f"╚{'═' * WIDTH}╝{C_RESET}")
        
        # Field
        print(f"{C_CYAN}╔{'═' * WIDTH}╗{C_RESET}")
        for r in range(HEIGHT):
            line = f"{C_CYAN}║{C_RESET}"
            row_content = ""
            c = 0
            while c < WIDTH:
                # Ball
                if r == int(self.ball_y) and c == int(self.ball_x):
                    row_content += f"{C_WHITE}●{C_RESET}"
                    c += 1
                    continue
                
                # Paddle
                if r == HEIGHT - 1 and self.paddle_x <= c < self.paddle_x + PADDLE_WIDTH:
                    row_content += f"{C_MAGENTA}═{C_RESET}"
                    c += 1
                    continue
                    
                # Bricks
                found_brick = None
                for b in self.bricks:
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

    def _handle_input(self):
        """Handle player movement."""
        k = get_key(timeout=0.01)
        if k == 'q':
            self.game_over = True
        elif k == 'left':
            self.paddle_x = max(0, self.paddle_x - 2)
        elif k == 'right':
            self.paddle_x = min(WIDTH - PADDLE_WIDTH, self.paddle_x + 2)

    def _update_game_state(self):
        """Update ball physics and collisions."""
        # Ball Movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Wall Collisions
        if self.ball_x <= 0 or self.ball_x >= WIDTH - 1:
            self.ball_dx *= -1
            beep("correct")
            self.ball_x = max(0, min(WIDTH - 1, self.ball_x))
            
        if self.ball_y <= 0:
            self.ball_dy *= -1
            beep("correct")
            self.ball_y = 0
            
        # Paddle Collision
        if self.ball_y >= HEIGHT - 1:
            if self.paddle_x <= self.ball_x <= self.paddle_x + PADDLE_WIDTH:
                self.ball_dy *= -1
                self.ball_y = HEIGHT - 2
                beep("correct")
            else:
                self._handle_life_lost()

        # Brick Collisions
        for b in self.bricks:
            if b['active']:
                if int(self.ball_y) == b['y'] and b['x'] <= int(self.ball_x) < b['x'] + 3:
                    b['active'] = False
                    self.ball_dy *= -1
                    self.score += 10
                    self.add_xp(15)
                    screen_shake(0.05, 1)
                    particle_effect(char="*", color=b['color'], count=5)
                    beep("eat")
                    break
        
        # Check Win Condition
        if all(not b['active'] for b in self.bricks):
            self._handle_win()

    def _handle_life_lost(self):
        """Manage life loss and game over."""
        self.lives -= 1
        beep("lose")
        screen_shake(0.3, 2)
        animated_flash(C_RED)
        
        if self.lives == 0:
            show_popup(f"GAME OVER! Score: {self.score}", C_RED)
            self.game_over = True
        else:
            self.ball_x = WIDTH // 2
            self.ball_y = HEIGHT - 2
            self.ball_dy = -1
            self.paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
            time.sleep(1)

    def _handle_win(self):
        """Handle winning the game."""
        beep("win")
        show_popup("YOU WON! LEVEL CLEARED", C_GREEN)
        self.game_over = True

def play_breakout():
    """Wrapper function for arcade.py compatibility."""
    game = BreakoutGame()
    return game.play()

if __name__ == "__main__":
    play_breakout()

if __name__ == "__main__":
    play_breakout()
