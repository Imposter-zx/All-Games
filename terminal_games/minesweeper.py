import random
import time
import os
from arcade_utils import (
    clear_screen, get_key, draw_retro_box, beep, show_popup, 
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK, 
    update_stats, load_stats, add_xp, screen_shake, particle_effect
)
from base_game import BaseGame

NUM_COLORS = {1: "\033[34m", 2: "\033[32m", 3: "\033[31m", 4: "\033[35m", 5: "\033[33m", 6: "\033[36m", 7: "\033[30m", 8: "\033[37m"}

class MinesweeperGame(BaseGame):
    """Minesweeper game implementation using BaseGame."""
    
    def __init__(self):
        super().__init__("minesweeper")
        self.rows = 0
        self.cols = 0
        self.mines = 0
        self.board = []
        self.revealed = []
        self.flagged = []
        self.cursor = [0, 0]
        self.diff_name = "beginner"
        self.exploded_at = None
        self.flash_red = False

    def play(self) -> dict:
        """Main Minesweeper game loop."""
        if not self._select_difficulty():
            return self.get_final_stats()
            
        self.start_timer()
        self._init_board()
        
        while not self.game_over:
            self._render()
            self._handle_input()
            self._update_game_state()
            
        self.end_timer()
        
        # Save stats if won
        if self.score > 0 and self.exploded_at is None:
            stats = load_stats().get("minesweeper", {})
            wins_dict = stats.get("wins", {})
            if not isinstance(wins_dict, dict): wins_dict = {}
            
            current_wins = wins_dict.get(self.diff_name, 0)
            wins_dict[self.diff_name] = current_wins + 1
            
            update_stats("minesweeper", "wins", wins_dict)
            
        self.save_stats({
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.diff_name
        })
        
        return self.get_final_stats()

    def _select_difficulty(self) -> bool:
        """Show difficulty selection menu."""
        clear_screen()
        draw_retro_box(50, "SELECT DIFFICULTY", ["(1) BEGINNER", "(2) INTERMEDIATE", "(3) EXPERT", "(Q) BACK"], color=C_YELLOW)
        while True:
            choice = get_key()
            if choice in ['q', 'Q']: return False
            if choice == '1':
                self.diff_name = "beginner"
                self.rows, self.cols, self.mines = 8, 8, 10
                break
            if choice == '2':
                self.diff_name = "intermediate"
                self.rows, self.cols, self.mines = 12, 12, 25
                break
            if choice == '3':
                self.diff_name = "expert"
                self.rows, self.cols, self.mines = 14, 20, 50
                break
        return True

    def _init_board(self):
        """Initialize the board and place mines."""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        
        mine_pos = set()
        while len(mine_pos) < self.mines:
            r, c = random.randint(0, self.rows-1), random.randint(0, self.cols-1)
            if (r, c) not in mine_pos:
                mine_pos.add((r, c))
                self.board[r][c] = 'M'
                
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M': continue
                cnt = sum(1 for dr in [-1,0,1] for dc in [-1,0,1] 
                          if 0 <= r+dr < self.rows and 0 <= c+dc < self.cols and self.board[r+dr][c+dc] == 'M')
                self.board[r][c] = cnt

    def _render(self):
        """Render the Minesweeper board."""
        clear_screen()
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        f_count = sum(row.count(True) for row in self.flagged)
        
        # Header
        header_lines = [
            f"⏱ TIME: {elapsed//60:02}:{elapsed%60:02}  |  ⚑ FLAGS: {f_count}/{self.mines}",
            f"💣 DIFFICULTY: {self.diff_name.upper()}"
        ]
        draw_retro_box(45, "💣 MINESWEEPER V5", header_lines, color=C_YELLOW)
        
        term_width = 80
        try: term_width = os.get_terminal_size().columns
        except: pass
        
        padding = (term_width - (self.cols * 3 + 2)) // 2
        indent = " " * padding
        border_color = C_RED if self.flash_red else C_CYAN
        
        print(indent + f"{border_color}╔" + "═══" * self.cols + "═╗{C_RESET}")
        for r in range(self.rows):
            line = indent + f"{border_color}║{C_RESET} "
            for c in range(self.cols):
                style = ""
                if [r, c] == self.cursor: style = "\033[47;30m"
                
                if (r, c) == self.exploded_at: char = f"{style}{C_RED}💥{C_RESET}"
                elif self.flagged[r][c]: char = f"{style}{C_YELLOW}⚑{C_RESET} "
                elif self.revealed[r][c]:
                    val = self.board[r][c]
                    if val == 'M': char = f"{style}{C_RED}💣{C_RESET}"
                    elif val == 0: char = f"{style}{C_BLACK}·{C_RESET} "
                    else: char = f"{style}{NUM_COLORS.get(val, '')}{val}{C_RESET} "
                else: char = f"{style}{C_WHITE}■{C_RESET} "
                line += char + " "
            print(line + f"{border_color}║{C_RESET}")
        print(indent + f"{border_color}╚" + "═══" * self.cols + "═╝{C_RESET}")
        
        print("\n" + " " * ((term_width - 46) // 2) + f"{C_WHITE}ARROWS: Move | ENTER: Reveal | F: Flag | Q: Exit{C_RESET}")

    def _handle_input(self):
        """Handle user input."""
        k = get_key()
        if k == 'q':
            self.game_over = True
        elif k == 'up': self.cursor[0] = max(0, self.cursor[0] - 1); beep("correct")
        elif k == 'down': self.cursor[0] = min(self.rows - 1, self.cursor[0] + 1); beep("correct")
        elif k == 'left': self.cursor[1] = max(0, self.cursor[1] - 1); beep("correct")
        elif k == 'right': self.cursor[1] = min(self.cols - 1, self.cursor[1] + 1); beep("correct")
        elif k in ['\r', '\n', ' ']:
            cr, cc = self.cursor
            if not self.flagged[cr][cc]:
                if self.board[cr][cc] == 'M':
                    self._handle_explosion(cr, cc)
                else:
                    self._reveal_cell(cr, cc)
                    beep("correct")
        elif k == 'f':
            cr, cc = self.cursor
            if not self.revealed[cr][cc]:
                self.flagged[cr][cc] = not self.flagged[cr][cc]
                beep("correct")

    def _reveal_cell(self, r, c):
        """Recursively reveal cells."""
        if not (0 <= r < self.rows and 0 <= c < self.cols) or self.revealed[r][c] or self.flagged[r][c]:
            return
        
        self.revealed[r][c] = True
        if self.board[r][c] == 0:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    self._reveal_cell(r+dr, c+dc)

    def _update_game_state(self):
        """Check for win condition."""
        if self.game_over: return
        
        # Win check: All non-mine cells revealed
        unrevealed_non_mines = sum(1 for r in range(self.rows) for c in range(self.cols) 
                                   if not self.revealed[r][c] and self.board[r][c] != 'M')
        if unrevealed_non_mines == 0:
            self._handle_win()

    def _handle_explosion(self, r, c):
        """Handle mine hit."""
        self.exploded_at = (r, c)
        beep("lose")
        screen_shake(0.5, 3)
        particle_effect(char="X", color=C_RED, count=15)
        
        # Flash effect
        for _ in range(3):
            self.flash_red = True
            self._render()
            time.sleep(0.1)
            self.flash_red = False
            self._render()
            time.sleep(0.1)
            
        # Reveal all mines
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == 'M': self.revealed[i][j] = True
        
        self.game_over = True
        self._render()
        show_popup("BOOM! GAME OVER", color=C_RED)

    def _handle_win(self):
        """Handle victory."""
        beep("win")
        self.score = self.mines * 10 # Base score
        xp = {"expert": 500, "intermediate": 250, "beginner": 100}[self.diff_name]
        self.add_xp(xp)
        show_popup("VICTORY! FIELD CLEARED", color=C_GREEN)
        self.game_over = True

def play_minesweeper():
    """Wrapper for arcade.py compatibility."""
    game = MinesweeperGame()
    return game.play()

if __name__ == "__main__":
    play_minesweeper()
