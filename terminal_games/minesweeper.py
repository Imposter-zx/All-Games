import time
import os
import random
from arcade_utils import (
    clear_screen, get_key, draw_retro_box, beep, show_popup, 
    update_stats, load_stats, animated_flash, print_big_title, 
    add_xp, screen_shake, particle_effect, 
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK,
    BG_DARK, BG_LIGHT, BG_RED
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

class MinesweeperGame(BaseGame):
    """Minesweeper game implementation using BaseGame."""
    
    def __init__(self, difficulty='normal'):
        super().__init__("minesweeper", difficulty)
        self.width = 10
        self.height = 10
        self.num_mines = 15
        self._init_board()
        self.cursor_x = 0
        self.cursor_y = 0
        self.input_handler = get_safe_input_handler()
        
    def _init_board(self):
        """Initialize board with mines and counts."""
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flags = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # Place mines
        placed = 0
        while placed < self.num_mines:
            rx, ry = random.randint(0, self.width-1), random.randint(0, self.height-1)
            if self.board[ry][rx] != -1:
                self.board[ry][rx] = -1
                placed += 1
                
        # Calculate counts
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] == -1: continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.height and 0 <= nc < self.width:
                            if self.board[nr][nc] == -1: count += 1
                self.board[r][c] = count

    def play(self) -> dict:
        """Main Minesweeper loop."""
        self.start_timer()
        clear_screen()
        print_big_title("MINESWEEPER", color=C_RED)
        time.sleep(1)
        
        while not self.game_over:
            self._render()
            self._handle_input()
            if self._check_win():
                self._handle_win()
            
        self.end_timer()
        
        # Save stats
        stats = self.stats_manager.get_stats('minesweeper')
        diff_key = self.difficulty
        wins = stats.get('wins', {})
        if not isinstance(wins, dict): wins = {}
        
        won = self._check_win()
        if won:
            wins[diff_key] = wins.get(diff_key, 0) + 1
        
        self.save_stats({
            'wins': wins,
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })
        
        return self.get_final_stats()

    def _render(self):
        """Render the minefield."""
        clear_screen()
        print(f" MINES: {C_RED}{self.num_mines}{C_RESET} | FLAGS: {C_YELLOW}{sum(row.count(True) for row in self.flags)}{C_RESET}")
        
        print(f"{C_WHITE}╔{'══' * self.width}╗")
        for r in range(self.height):
            line = f"║"
            for c in range(self.width):
                char = "░ "
                color = C_WHITE
                bg = BG_DARK if (r + c) % 2 == 0 else BG_LIGHT
                
                if (c, r) == (self.cursor_x, self.cursor_y):
                    bg = "\033[48;5;220m" # Cursor color
                
                if self.revealed[r][c]:
                    val = self.board[r][c]
                    if val == -1:
                        char = "💣"
                        bg = BG_RED
                    elif val == 0:
                        char = "  "
                        bg = C_RESET # Use default empty
                    else:
                        colors = [C_RESET, C_BLUE, C_GREEN, C_RED, C_CYAN, C_MAGENTA, C_YELLOW, C_WHITE, C_BLACK]
                        char = f"{val} "
                        color = colors[val]
                elif self.flags[r][c]:
                    char = "🚩"
                    color = C_YELLOW
                
                line += f"{bg}{color}{char}{C_RESET}"
            print(line + f"{C_WHITE}║")
        print(f"╚{'══' * self.width}╝{C_RESET}")
        print(f"\n{C_WHITE}ARROWS/WASD: Move | SPACE/ENTER: Reveal | F: Flag | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle player interaction using SafeInputHandler."""
        k = self.input_handler.get_safe_key()
        if not k:
            return
            
        if k == 'q':
            self.game_over = True
        elif k in [' ', '\r', '\n', 'enter']:
            self._reveal(self.cursor_x, self.cursor_y)
        elif k in ['f', 'F']:
            self.flags[self.cursor_y][self.cursor_x] = not self.flags[self.cursor_y][self.cursor_x]
            beep("correct")
        else:
            direction = self.input_handler.validator.validate_direction(k)
            if direction == 'up': self.cursor_y = max(0, self.cursor_y - 1)
            elif direction == 'down': self.cursor_y = min(self.height - 1, self.cursor_y + 1)
            elif direction == 'left': self.cursor_x = max(0, self.cursor_x - 1)
            elif direction == 'right': self.cursor_x = min(self.width - 1, self.cursor_x + 1)

    def _reveal(self, x, y):
        """Reveal a cell and handle cascading for empty cells."""
        if self.revealed[y][x] or self.flags[y][x]:
            return
            
        self.revealed[y][x] = True
        
        if self.board[y][x] == -1:
            self._handle_loss()
            return
            
        self.score += 10
        self.award_xp_for_action(5) # 5 base XP per reveal
        beep("correct")
        
        if self.board[y][x] == 0:
            # Cascade
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nx, ny = x + dc, y + dr
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self._reveal(nx, ny)

    def _check_win(self) -> bool:
        """Check if all non-mine cells are revealed."""
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] != -1 and not self.revealed[r][c]:
                    return False
        return True

    def _handle_win(self):
        """Handle victory."""
        beep("win")
        self.award_xp_for_action(200) # 200 base XP for win
        show_popup("YOU CLEARED THE MINEFIELD!", C_GREEN)
        self.game_over = True

    def _handle_loss(self):
        """Handle hitting a mine."""
        # Reveal all mines
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] == -1: self.revealed[r][c] = True
        
        self._render()
        beep("game_over")
        screen_shake(0.3, 2)
        animated_flash(C_RED)
        show_popup("BOOM! GAME OVER", C_RED)
        self.game_over = True

def play_minesweeper(difficulty='normal'):
    """Wrapper function for arcade.py compatibility."""
    game = MinesweeperGame(difficulty)
    return game.play()

if __name__ == "__main__":
    play_minesweeper()
