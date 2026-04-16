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

WIDTH = 30
HEIGHT = 20
PLAYER_CHAR = "▲"
ENEMY_CHAR = "W"
BULLET_CHAR = "|"

class SpaceShooterGame(BaseGame):
    """Space Shooter game implementation using BaseGame."""
    
    def __init__(self):
        super().__init__("space_shooter")
        self.player_x = WIDTH // 2
        self.bullets = []
        self.enemies = []
        self.lives = 3
        self.spawn_timer = 0
        self.enemy_move_speed = 5 # Higher is slower
        self.frame_count = 0

    def play(self) -> dict:
        """Main Space Shooter game loop."""
        self.start_timer()
        clear_screen()
        print_big_title("SPACE SHOOTER", color=C_MAGENTA)
        time.sleep(1)
        
        while not self.game_over:
            self._render()
            self._handle_input()
            self._update_game_state()
            time.sleep(0.05)
            self.frame_count += 1
            
        self.end_timer()
        
        # Save stats
        stats = load_stats().get('space_shooter', {})
        high_score = stats.get('high_score', 0)
        if self.score > high_score:
            update_stats('space_shooter', 'high_score', self.score)
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
        stats = load_stats().get('space_shooter', {})
        high_score = stats.get('high_score', 0)
        
        # Header
        print(f"{C_MAGENTA}╔{'═' * WIDTH}╗")
        print(f"║ SCORE: {self.score:<10} HI: {high_score:<10} LIVES: {self.lives} ║")
        print(f"╚{'═' * WIDTH}╝{C_RESET}")
        
        # Field
        print(f"{C_MAGENTA}╔{'═' * WIDTH}╗{C_RESET}")
        for r in range(HEIGHT):
            line = f"{C_MAGENTA}║{C_RESET}"
            row = [" "] * WIDTH
            
            if r == HEIGHT - 1:
                row[self.player_x] = f"{C_CYAN}{PLAYER_CHAR}{C_RESET}"
                
            for b in self.bullets:
                if b['y'] == r: 
                    row[b['x']] = f"{C_YELLOW}{BULLET_CHAR}{C_RESET}"
                
            for e in self.enemies:
                if e['y'] == r: 
                    row[e['x']] = f"{C_RED}{ENEMY_CHAR}{C_RESET}"
                
            line += "".join(row) + f"{C_MAGENTA}║{C_RESET}"
            print(line)
            
        print(f"{C_MAGENTA}╚{'═' * WIDTH}╝{C_RESET}")
        print(f"{C_WHITE}ARROWS: Move | SPACE: Shoot | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle player input."""
        k = get_key(timeout=0.01)
        if k == 'q':
            self.game_over = True
        elif k == 'left':
            self.player_x = max(0, self.player_x - 1)
        elif k == 'right':
            self.player_x = min(WIDTH - 1, self.player_x + 1)
        elif k == ' ': # Shoot
            self.bullets.append({'x': self.player_x, 'y': HEIGHT - 2})
            beep("correct")

    def _update_game_state(self):
        """Update physics and collisions."""
        # Spawn enemies
        self.spawn_timer += 1
        spawn_rate = max(3, 10 - (self.score // 200)) # Get faster with score
        if self.spawn_timer > spawn_rate:
            self.enemies.append({'x': random.randint(0, WIDTH-1), 'y': 0})
            self.spawn_timer = 0
            
        # Move bullets
        for b in self.bullets:
            b['y'] -= 1
        self.bullets = [b for b in self.bullets if b['y'] >= 0]
        
        # Move enemies
        if self.frame_count % self.enemy_move_speed == 0:
            for e in self.enemies:
                e['y'] += 1
        
        # Bullet-Enemy Collision
        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if b['x'] == e['x'] and (b['y'] == e['y'] or b['y'] == e['y'] - 1):
                    if b in self.bullets: self.bullets.remove(b)
                    if e in self.enemies: self.enemies.remove(e)
                    self.score += 10
                    self.add_xp(5)
                    screen_shake(0.05, 1)
                    particle_effect(char="*", color=C_RED, count=3)
                    beep("eat")
                    break
                    
        # Enemy-Player or Bottom Collision
        for e in self.enemies[:]:
            if e['y'] >= HEIGHT - 1:
                if e['x'] == self.player_x and e['y'] == HEIGHT - 1:
                    self._handle_collision()
                    self.enemies.remove(e)
                else:
                    # Enemy reached bottom but missed player
                    self.enemies.remove(e)
                    # Optional: lose life if enemy reaches bottom? (Original logic does)
                    self._handle_collision()
            elif e['x'] == self.player_x and e['y'] == HEIGHT - 1:
                 self._handle_collision()
                 self.enemies.remove(e)

    def _handle_collision(self):
        """Handle player taking damage."""
        self.lives -= 1
        screen_shake(0.3, 2)
        animated_flash(C_RED)
        beep("lose")
        
        if self.lives <= 0:
            show_popup(f"GAME OVER! Score: {self.score}", C_RED)
            self.game_over = True

def play_space_shooter():
    """Wrapper function for arcade.py compatibility."""
    game = SpaceShooterGame()
    return game.play()

if __name__ == "__main__":
    play_space_shooter()

if __name__ == "__main__":
    play_space_shooter()
