import random
import time
import os
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, update_stats, load_stats, animated_flash, print_big_title, add_xp, screen_shake, particle_effect, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK
from base_game import BaseGame

BOARD_WIDTH = 30
BOARD_HEIGHT = 15

def create_food(snake):
    while True:
        food = (random.randint(1, BOARD_HEIGHT-2), random.randint(1, BOARD_WIDTH-2))
        if food not in snake:
            return food


class SnakeGame(BaseGame):
    """Snake game implementation using BaseGame."""
    
    def __init__(self):
        super().__init__("snake")
        self.snake = []
        self.food = None
        self.direction = (0, 1)
        self.speed = 0.15
        self.key_map = {
            'up': (-1, 0), 'down': (1, 0),
            'left': (0, -1), 'right': (0, 1)
        }
    
    def play(self) -> dict:
        """Main snake game loop."""
        self.start_timer()
        clear_screen()
        print_big_title("SNAKE", color=C_GREEN)
        time.sleep(1)
        
        self.snake = [(BOARD_HEIGHT//2, BOARD_WIDTH//2)]
        self.direction = (0, 1)
        self.food = create_food(self.snake)
        self.score = 0
        self.speed = 0.15
        
        while not self.game_over:
            start_time = time.time()
            self._render()
            self._handle_input()
            self._update_game_state()
            
            # Frame rate limiting
            elapsed = time.time() - start_time
            sleep_time = self.speed - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.end_timer()
        
        # Save stats
        stats = load_stats().get('snake', {})
        high_score = stats.get('high_score', 0)
        if self.score > high_score:
            update_stats('snake', 'high_score', self.score)
            show_popup("NEW HIGH SCORE!", C_YELLOW)
        
        self.save_stats({
            'high_score': max(self.score, high_score),
            'last_score': self.score,
            'xp_earned': self.xp_earned
        })
        
        return {
            'score': self.score,
            'xp_earned': self.xp_earned
        }
    
    def _render(self):
        """Render game board."""
        clear_screen()
        stats = load_stats().get('snake', {})
        high_score = stats.get('high_score', 0)
        
        print(f"{C_YELLOW}╔{'═' * BOARD_WIDTH}╗")
        print(f"║ SCORE: {self.score:<10} HI: {high_score:<10} ║")
        print(f"╚{'═' * BOARD_WIDTH}╝{C_RESET}")
        
        print(f"{C_GREEN}╔{'═' * BOARD_WIDTH}╗{C_RESET}")
        for r in range(BOARD_HEIGHT):
            line = f"{C_GREEN}║{C_RESET}"
            for c in range(BOARD_WIDTH):
                if (r, c) == self.snake[0]:
                    line += f"{C_GREEN}█{C_RESET}"
                elif (r, c) in self.snake:
                    line += f"{C_GREEN}▒{C_RESET}"
                elif (r, c) == self.food:
                    line += f"{C_RED}●{C_RESET}"
                else:
                    line += " "
            line += f"{C_GREEN}║{C_RESET}"
            print(line)
        print(f"{C_GREEN}╚{'═' * BOARD_WIDTH}╝{C_RESET}")
    
    def _handle_input(self):
        """Handle player input."""
        if os.name == 'nt':
            import msvcrt
            if msvcrt.kbhit():
                k = get_key()
                if k == 'q':
                    self.game_over = True
                elif k in self.key_map:
                    test_dir = self.key_map[k]
                    # Prevent reversing into self
                    if (test_dir[0] + self.direction[0] != 0) or (test_dir[1] + self.direction[1] != 0):
                        self.direction = test_dir
        else:
            import select
            import sys
            if select.select([sys.stdin], [], [], 0)[0]:
                k = get_key()
                if k == 'q':
                    self.game_over = True
                elif k in self.key_map:
                    test_dir = self.key_map[k]
                    if (test_dir[0] + self.direction[0] != 0) or (test_dir[1] + self.direction[1] != 0):
                        self.direction = test_dir
    
    def _update_game_state(self):
        """Update game logic."""
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Collision detection
        if (new_head[0] < 0 or new_head[0] >= BOARD_HEIGHT or 
            new_head[1] < 0 or new_head[1] >= BOARD_WIDTH or 
            new_head in self.snake):
            beep("game_over")
            screen_shake(0.3, 2)
            animated_flash(C_RED)
            show_popup(f"GAME OVER! Score: {self.score}", C_RED)
            self.game_over = True
            return
        
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.score += 10
            self.add_xp(10)
            screen_shake(0.05, 1)
            particle_effect(char="+", color=C_GREEN, count=3)
            beep("eat")
            self.food = create_food(self.snake)
            if self.score % 50 == 0:
                self.speed = max(0.05, self.speed - 0.01)
        else:
            self.snake.pop()


def play_snake():
    """Wrapper function to play snake using SnakeGame class."""
    game = SnakeGame()
    return game.play()
            
if __name__ == "__main__":
    play_snake()
