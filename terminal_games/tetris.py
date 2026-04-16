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

WIDTH = 10
HEIGHT = 20

SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[1, 0, 0], [1, 1, 1]], # L
    [[0, 0, 1], [1, 1, 1]], # J
    [[0, 1, 1], [1, 1, 0]], # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

COLORS = [C_CYAN, C_YELLOW, C_MAGENTA, C_WHITE, C_BLUE, C_GREEN, C_RED]

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

class TetrisGame(BaseGame):
    """Tetris game implementation using BaseGame."""
    
    def __init__(self):
        super().__init__("tetris")
        self.board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.piece = self._new_piece()
        self.next_piece = self._new_piece()
        self.level = 1
        self.fall_speed = 0.5
        self.last_fall_time = time.time()
    
    def _new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = COLORS[shape_idx]
        return {
            'shape': shape, 
            'color': color, 
            'x': WIDTH // 2 - len(shape[0]) // 2, 
            'y': 0
        }

    def play(self) -> dict:
        """Main Tetris game loop."""
        self.start_timer()
        clear_screen()
        print_big_title("TETRIS", color=C_BLUE)
        time.sleep(1)
        
        while not self.game_over:
            self._render()
            self._handle_input()
            self._update_game_state()
            
            # Control game speed based on level
            self.fall_speed = max(0.1, 0.5 - (self.level * 0.05))
            time.sleep(0.05) # Small sleep to prevent CPU hogging
            
        self.end_timer()
        
        # Final stats save handled by caller or here
        stats = load_stats().get('tetris', {})
        high_score = stats.get('high_score', 0)
        if self.score > high_score:
            update_stats('tetris', 'high_score', self.score)
            show_popup("NEW HIGH SCORE!", C_YELLOW)
        
        self.save_stats({
            'high_score': max(self.score, high_score),
            'last_score': self.score,
            'xp_earned': self.xp_earned
        })
        
        return self.get_final_stats()

    def _render(self):
        """Render the Tetris board and UI."""
        clear_screen()
        stats = load_stats().get('tetris', {})
        high_score = stats.get('high_score', 0)
        
        # Header
        print(f"{C_BLUE}╔{'═' * (WIDTH * 2)}╗")
        print(f"║ SCORE: {self.score:<6} LVL: {self.level:<3} HI: {high_score:<6} ║")
        print(f"╚{'═' * (WIDTH * 2)}╝{C_RESET}")
        
        # Board + Next Piece Info
        print(f"{C_BLUE}╔{'═' * (WIDTH * 2)}╗{C_RESET}  NEXT PIECE:")
        
        for r in range(HEIGHT):
            line = f"{C_BLUE}║{C_RESET}"
            for c in range(WIDTH):
                # Check for active piece
                is_piece = False
                if (0 <= r - self.piece['y'] < len(self.piece['shape']) and 
                    0 <= c - self.piece['x'] < len(self.piece['shape'][0])):
                    if self.piece['shape'][r - self.piece['y']][c - self.piece['x']]:
                        line += f"{self.piece['color']}██{C_RESET}"
                        is_piece = True
                
                if not is_piece:
                    val = self.board[r][c]
                    if val == 0:
                        line += f"{C_BLACK} . {C_RESET}"
                    else:
                        line += f"{val}██{C_RESET}"
            
            line += f"{C_BLUE}║{C_RESET}"
            
            # Next piece preview (simple)
            if r == 1:
                line += f"  {self.next_piece['color']}████{C_RESET}" if len(self.next_piece['shape'][0]) > 2 else f"  {self.next_piece['color']}██{C_RESET}"
            
            print(line)
            
        print(f"{C_BLUE}╚{'═' * (WIDTH * 2)}╝{C_RESET}")
        print(f"{C_WHITE}Arrows: Move/Rotate | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle user input for movement and rotation."""
        k = get_key(timeout=0.05)
        if not k:
            return
            
        if k == 'q':
            self.game_over = True
        elif k == 'up': # Rotate
            rotated = rotate(self.piece['shape'])
            if not self._check_collision(rotated, (self.piece['x'], self.piece['y'])):
                self.piece['shape'] = rotated
                beep("move")
        elif k == 'left':
            if not self._check_collision(self.piece['shape'], (self.piece['x'] - 1, self.piece['y'])):
                self.piece['x'] -= 1
                beep("move")
        elif k == 'right':
            if not self._check_collision(self.piece['shape'], (self.piece['x'] + 1, self.piece['y'])):
                self.piece['x'] += 1
                beep("move")
        elif k == 'down': # Soft Drop
            if not self._check_collision(self.piece['shape'], (self.piece['x'], self.piece['y'] + 1)):
                self.piece['y'] += 1
                self.score += 1
                beep("move")

    def _update_game_state(self):
        """Update game logic (gravity, line clears)."""
        # Gravity
        if time.time() - self.last_fall_time > self.fall_speed:
            if not self._check_collision(self.piece['shape'], (self.piece['x'], self.piece['y'] + 1)):
                self.piece['y'] += 1
            else:
                self._lock_piece()
                self._clear_lines()
                self.piece = self.next_piece
                self.next_piece = self._new_piece()
                
                # Check for game over
                if self._check_collision(self.piece['shape'], (self.piece['x'], self.piece['y'])):
                    self._trigger_game_over()
            
            self.last_fall_time = time.time()

    def _check_collision(self, shape, offset):
        """Check if shape collides with walls or board pieces."""
        off_x, off_y = offset
        for cy, row in enumerate(shape):
            for cx, cell in enumerate(row):
                if cell:
                    target_x = off_x + cx
                    target_y = off_y + cy
                    if (target_x < 0 or target_x >= WIDTH or 
                        target_y >= HEIGHT or 
                        (target_y >= 0 and self.board[target_y][target_x])):
                        return True
        return False

    def _lock_piece(self):
        """Lock the current piece into the board."""
        for cy, row in enumerate(self.piece['shape']):
            for cx, val in enumerate(row):
                if val:
                    y = self.piece['y'] + cy
                    x = self.piece['x'] + cx
                    if 0 <= y < HEIGHT:
                        self.board[y][x] = self.piece['color']

    def _clear_lines(self):
        """Clear full lines and update score/XP."""
        lines_cleared = 0
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = HEIGHT - len(new_board)
        
        if lines_cleared > 0:
            self.score += (100 * lines_cleared * self.level)
            self.add_xp(25 * lines_cleared)
            screen_shake(0.1 * lines_cleared, lines_cleared)
            particle_effect(char="*", color=self.piece['color'], count=10 * lines_cleared)
            beep("win")
            
            # Fill top with empty rows
            for _ in range(lines_cleared):
                new_board.insert(0, [0] * WIDTH)
            self.board = new_board
            
            # Level up every 10 lines
            if self.score // 1000 > self.level:
                self.level += 1
                show_popup(f"LEVEL UP: {self.level}", C_CYAN)

    def _trigger_game_over(self):
        """Handle end of game."""
        beep("game_over")
        screen_shake(0.3, 2)
        animated_flash(C_RED)
        show_popup(f"GAME OVER! Score: {self.score}", C_RED)
        self.game_over = True

def play_tetris():
    """Wrapper function for arcade.py compatibility."""
    game = TetrisGame()
    return game.play()

if __name__ == "__main__":
    play_tetris()
