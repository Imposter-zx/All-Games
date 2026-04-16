import random
import time
import os
from arcade_utils import (
    clear_screen, get_key, draw_retro_box, beep, show_popup, 
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, 
    update_stats, load_stats, add_xp, particle_effect
)
from base_game import BaseGame

class SudokuGame(BaseGame):
    """Sudoku game implementation using BaseGame."""
    
    def __init__(self):
        super().__init__("sudoku")
        self.board = []
        self.solution = []
        self.original_cells = []
        self.cursor = [0, 0]
        self.difficulty = "easy"
        self.msg = ""
        self.hints_used = 0

    def play(self) -> dict:
        """Main Sudoku game loop."""
        if not self._select_difficulty():
            return self.get_final_stats()
            
        self.start_timer()
        self._generate_board()
        
        while not self.game_over:
            self._render()
            self._handle_input()
            self._update_game_state()
            
        self.end_timer()
        
        # Save stats handled by win condition
        return self.get_final_stats()

    def _select_difficulty(self) -> bool:
        """Show difficulty selection menu."""
        clear_screen()
        draw_retro_box(50, "SELECT DIFFICULTY", ["(1) EASY", "(2) MEDIUM", "(3) HARD", "(Q) BACK"], color=C_MAGENTA)
        while True:
            choice = get_key()
            if choice in ['q', 'Q']: return False
            if choice == '1':
                self.difficulty = "easy"
                break
            if choice == '2':
                self.difficulty = "medium"
                break
            if choice == '3':
                self.difficulty = "hard"
                break
        return True

    def _generate_board(self):
        """Generate a new Sudoku board based on difficulty."""
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self._solve_board(self.board)
        self.solution = [row[:] for row in self.board]
        
        remove_count = {"easy": 35, "medium": 45, "hard": 55}.get(self.difficulty, 35)
        while remove_count > 0:
            r, c = random.randint(0, 8), random.randint(0, 8)
            if self.board[r][c] != 0:
                self.board[r][c] = 0
                remove_count -= 1
        
        self.original_cells = [(r, c) for r in range(9) for c in range(9) if self.board[r][c] != 0]

    def _solve_board(self, board):
        """Backtracking solver to generate/complete board."""
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for n in nums:
                        if self._is_valid_move(board, r, c, n)[0]:
                            board[r][c] = n
                            if self._solve_board(board): return True
                            board[r][c] = 0
                    return False
        return True

    def _is_valid_move(self, board, row, col, num):
        """Check if placing a number is legal."""
        for i in range(9):
            if board[row][i] == num: return False, "Row conflict"
            if board[i][col] == num: return False, "Column conflict"
        
        br, bc = (row // 3) * 3, (col // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if board[i][j] == num: return False, "3x3 Box conflict"
        return True, ""

    def _render(self):
        """Render the Sudoku board and current state."""
        clear_screen()
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        
        # Header
        header_text = [
            f"DIFFICULTY: {self.difficulty.upper()}",
            f"TIME: {elapsed//60:02}:{elapsed%60:02}  |  HINTS: {self.hints_used}"
        ]
        draw_retro_box(40, "🧩 SUDOKU V5", header_text, color=C_MAGENTA)
        
        term_width = 80
        try: term_width = os.get_terminal_size().columns
        except: pass
        
        padding = (term_width - 37) // 2
        indent = " " * padding
        
        print(indent + f"{C_CYAN}╔═══════════╦═══════════╦═══════════╗{C_RESET}")
        for r in range(9):
            line = indent + f"{C_CYAN}║{C_RESET}"
            for c in range(9):
                cell = self.board[r][c]
                style = ""
                
                if [r, c] == self.cursor: style = "\033[47;30m"
                elif (r, c) in self.original_cells: style = C_CYAN
                elif cell != 0: style = C_GREEN
                else: style = C_WHITE
                    
                val = f"{style} {cell if cell != 0 else '.'} {C_RESET}"
                line += val
                if (c + 1) % 3 == 0: line += f"{C_CYAN}║{C_RESET}"
                else: line += " "
            print(line)
            if (r + 1) % 3 == 0 and r < 8:
                print(indent + f"{C_CYAN}╠═══════════╬═══════════╬═══════════╣{C_RESET}")
        print(indent + f"{C_CYAN}╚═══════════╩═══════════╩═══════════╝{C_RESET}")
        
        if self.msg:
            print(f"\n" + " " * ((term_width - len(self.msg)) // 2) + f"{C_RED}⚠ {self.msg}{C_RESET}")
        
        controls = "ARROWS: Move | 1-9: Place | SPACE: Clear | H: Hint | Q: Quit"
        print("\n" + " " * ((term_width - len(controls)) // 2) + f"{C_YELLOW}{controls}{C_RESET}")

    def _handle_input(self):
        """Handle user input for movement and placing numbers."""
        k = get_key()
        self.msg = "" # Clear message on new input
        
        if k == 'q':
            self.game_over = True
        elif k == 'up': self.cursor[0] = max(0, self.cursor[0] - 1); beep("correct")
        elif k == 'down': self.cursor[0] = min(8, self.cursor[0] + 1); beep("correct")
        elif k == 'left': self.cursor[1] = max(0, self.cursor[1] - 1); beep("correct")
        elif k == 'right': self.cursor[1] = min(8, self.cursor[1] + 1); beep("correct")
        elif k in '123456789':
            r, c = self.cursor
            if (r, c) in self.original_cells:
                beep("invalid")
                self.msg = "Locked Cell!"
                return
            num = int(k)
            valid, err = self._is_valid_move(self.board, r, c, num)
            if valid: 
                self.board[r][c] = num
                beep("correct")
            else: 
                beep("invalid")
                self.msg = err
        elif k == ' ': # Clear cell
            r, c = self.cursor
            if (r, c) not in self.original_cells: 
                self.board[r][c] = 0
                beep("correct")
        elif k == 'h': # Hint
            self.hints_used += 1
            r, c = self.cursor
            if (r, c) not in self.original_cells:
                self.board[r][c] = self.solution[r][c]
                beep("correct")
                self.msg = f"Hint Applied!"

    def _update_game_state(self):
        """Check for victory."""
        if all(self.board[r][c] == self.solution[r][c] for r in range(9) for c in range(9)):
            self._handle_win()

    def _handle_win(self):
        """Animate victory and save statistics."""
        elapsed = int(time.time() - self.start_time)
        xp = {"hard": 200, "medium": 100, "easy": 50}.get(self.difficulty, 50)
        self.add_xp(xp)
        
        # Victory Animation
        beep("win")
        frames = ["V", "VI", "VIC", "VICT", "VICTO", "VICTOR", "VICTORY", "VICTORY!", "VICTORY!!"]
        for frame in frames:
            clear_screen()
            print("\n" * 10)
            draw_retro_box(40, "🎉 CONGRATULATIONS", [frame, f"Time: {elapsed//60:02}:{elapsed%60:02}"], color=C_GREEN)
            particle_effect(char="*", color=C_YELLOW, count=2)
            time.sleep(0.1)
            
        # Stats
        stats = load_stats().get("sudoku", {})
        best = stats.get("best_times", {}).get(self.difficulty)
        if best is None or elapsed < best:
            times = stats.get("best_times", {})
            times[self.difficulty] = elapsed
            update_stats("sudoku", "best_times", times)
            
        update_stats("sudoku", "wins", stats.get("wins", 0) + 1)
        self.save_stats({
            'last_time': elapsed,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })
        
        self.game_over = True
        time.sleep(1.5)

def play_sudoku():
    """Wrapper for arcade.py compatibility."""
    game = SudokuGame()
    return game.play()

if __name__ == "__main__":
    play_sudoku()
