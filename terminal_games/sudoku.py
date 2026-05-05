import time
import os
import random
from arcade_utils import (
    clear_screen, get_key, draw_retro_box, beep, show_popup, 
    update_stats, load_stats, animated_flash, print_big_title, 
    add_xp, screen_shake, particle_effect, 
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK,
    BG_DARK, BG_LIGHT, BG_CUR, BG_SEL
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

class SudokuGame(BaseGame):
    """Sudoku game implementation using BaseGame."""
    
    def __init__(self, difficulty='normal'):
        super().__init__("sudoku", difficulty)
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.original = [[0 for _ in range(9)] for _ in range(9)]
        self._generate_board()
        self.cursor_x = 0
        self.cursor_y = 0
        self.input_handler = get_safe_input_handler()
        
    def _generate_board(self):
        """Generate a valid Sudoku board (simplified)."""
        # In a real game, this would use a proper Sudoku generator.
        # For now, we'll use a fixed board with some random removals.
        base_board = [
            [5,3,4,6,7,8,9,1,2],
            [6,7,2,1,9,5,3,4,8],
            [1,9,8,3,4,2,5,6,7],
            [8,5,9,7,6,1,4,2,3],
            [4,2,6,8,5,3,7,9,1],
            [7,1,3,9,2,4,8,5,6],
            [9,6,1,5,3,7,2,8,4],
            [2,8,7,4,1,9,6,3,5],
            [3,4,5,2,8,6,1,7,9]
        ]
        
        # Shuffle rows and columns within blocks to randomize
        # (Simplified)
        self.board = [row[:] for row in base_board]
        
        # Remove numbers based on difficulty
        to_remove = 30
        if self.difficulty == 'normal': to_remove = 45
        elif self.difficulty == 'hard': to_remove = 55
        
        removed = 0
        while removed < to_remove:
            r, c = random.randint(0, 8), random.randint(0, 8)
            if self.board[r][c] != 0:
                self.board[r][c] = 0
                removed += 1
                
        self.original = [row[:] for row in self.board]

    def play(self) -> dict:
        """Main Sudoku loop."""
        self.start_timer()
        clear_screen()
        print_big_title("SUDOKU", color=C_GREEN)
        time.sleep(1)
        
        while not self.game_over:
            self._render()
            self._handle_input()
            if self._check_win():
                self._handle_win()
            
        self.end_timer()
        
        # Save stats
        stats = self.stats_manager.get_stats('sudoku')
        wins = stats.get('wins', 0)
        
        self.save_stats({
            'wins': wins + (1 if self._check_win() else 0),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })
        
        return self.get_final_stats()

    def _render(self):
        """Render the Sudoku board."""
        clear_screen()
        print(f" DIFFICULTY: {C_YELLOW}{self.difficulty.upper()}{C_RESET} | SCORE: {C_GREEN}{self.score}{C_RESET}")
        
        print(f"{C_WHITE}╔═══════╦═══════╦═══════╗")
        for r in range(9):
            if r > 0 and r % 3 == 0:
                print(f"╠═══════╬═══════╬═══════╣")
            
            line = "║ "
            for c in range(9):
                if c > 0 and c % 3 == 0:
                    line += "║ "
                
                val = self.board[r][c]
                char = str(val) if val != 0 else "."
                
                # Colors
                color = C_WHITE
                if self.original[r][c] != 0: color = C_CYAN # Original numbers
                elif val != 0: color = C_GREEN # User entered
                
                bg = C_RESET
                if (c, r) == (self.cursor_x, self.cursor_y):
                    bg = "\033[48;5;220m"
                    color = C_BLACK
                
                line += f"{bg}{color}{char}{C_RESET} "
            print(line + "║")
        print(f"╚═══════╩═══════╩═══════╝{C_RESET}")
        print(f"\n{C_WHITE}ARROWS: Move | 1-9: Enter Number | 0/BACKSPACE: Clear | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle user input using SafeInputHandler."""
        k = self.input_handler.get_safe_key()
        if not k:
            return
            
        if k == 'q':
            self.game_over = True
        elif k in '123456789':
            if self.original[self.cursor_y][self.cursor_x] == 0:
                self.board[self.cursor_y][self.cursor_x] = int(k)
                self.score += 5
                self.award_xp_for_action(2) # 2 base XP for entering a number
                beep("correct")
        elif k in ['0', '\b', 'backspace']:
            if self.original[self.cursor_y][self.cursor_x] == 0:
                self.board[self.cursor_y][self.cursor_x] = 0
                beep("correct")
        else:
            direction = self.input_handler.validator.validate_direction(k)
            if direction == 'up': self.cursor_y = max(0, self.cursor_y - 1)
            elif direction == 'down': self.cursor_y = min(8, self.cursor_y + 1)
            elif direction == 'left': self.cursor_x = max(0, self.cursor_x - 1)
            elif direction == 'right': self.cursor_x = min(8, self.cursor_x + 1)

    def _check_win(self) -> bool:
        """Check if board is correctly filled (simplified check)."""
        # In a real game, this would validate Sudoku rules.
        # For now, we check if all cells are non-zero.
        for r in range(9):
            if 0 in self.board[r]: return False
        return True

    def _handle_win(self):
        """Handle victory."""
        beep("win")
        self.award_xp_for_action(300) # 300 base XP for win
        show_popup("SUDOKU COMPLETE! YOU WIN!", C_GREEN)
        self.game_over = True

def play_sudoku(difficulty='normal'):
    """Wrapper function for arcade.py compatibility."""
    game = SudokuGame(difficulty)
    return game.play()

if __name__ == "__main__":
    play_sudoku()
