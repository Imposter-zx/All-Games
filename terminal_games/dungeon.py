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
from input_handler import get_safe_input_handler

class DungeonGame(BaseGame):
    """Dungeon Crawler game implementation using BaseGame."""
    
    def __init__(self, difficulty='normal'):
        super().__init__("dungeon", difficulty)
        self.hp = 100
        self.max_hp = 100
        self.level = 1
        self.enemies_defeated = 0
        self.player_pos = [1, 1]
        self.dungeon_map = self._generate_level()
        self.input_handler = get_safe_input_handler()

    def _generate_level(self):
        """Generate a simple random dungeon level."""
        # 1 = wall, 0 = floor, 2 = enemy, 3 = health, 4 = exit
        size = 10
        m = [[1]*size for _ in range(size)]
        for r in range(1, size-1):
            for c in range(1, size-1):
                m[r][c] = 0
                if random.random() < 0.15: m[r][c] = 2
                elif random.random() < 0.1: m[r][c] = 3
        
        m[size-2][size-2] = 4 # Exit
        m[1][1] = 0 # Player start
        return m

    def play(self) -> dict:
        """Main Dungeon Crawler loop."""
        self.start_timer()
        clear_screen()
        print_big_title("DUNGEON", color=C_RED)
        time.sleep(1)
        
        while not self.game_over:
            self._render()
            self._handle_input()
            if self.hp <= 0:
                self._handle_death()
            time.sleep(0.05)
            
        self.end_timer()
        
        # Save stats
        stats = self.stats_manager.get_stats('dungeon')
        max_lvl = max(stats.get('max_level', 1), self.level)
        
        self.save_stats({
            'max_level': max_lvl,
            'enemies_defeated': stats.get('enemies_defeated', 0) + self.enemies_defeated,
            'last_level': self.level,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })
        
        return self.get_final_stats()

    def _render(self):
        """Render the dungeon map and UI."""
        clear_screen()
        print(f" LEVEL: {C_YELLOW}{self.level}{C_RESET} | HP: {C_RED}{self.hp}/{self.max_hp}{C_RESET} | KILLS: {C_MAGENTA}{self.enemies_defeated}{C_RESET}")
        
        for r, row in enumerate(self.dungeon_map):
            line = ""
            for c, cell in enumerate(row):
                if [r, c] == self.player_pos:
                    line += f"{C_CYAN}@{C_RESET} "
                elif cell == 1: line += f"{C_WHITE}█{C_RESET} "
                elif cell == 2: line += f"{C_RED}E{C_RESET} "
                elif cell == 3: line += f"{C_GREEN}H{C_RESET} "
                elif cell == 4: line += f"{C_YELLOW}X{C_RESET} "
                else: line += "  "
            print(line)
        print(f"\n{C_WHITE}ARROWS/WASD: Move | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle movement and combat using SafeInputHandler."""
        k = self.input_handler.get_safe_key()
        if not k:
            return
            
        if k == 'q':
            self.game_over = True
            return
            
        direction = self.input_handler.validator.validate_direction(k)
        dr, dc = 0, 0
        if direction == 'up': dr = -1
        elif direction == 'down': dr = 1
        elif direction == 'left': dc = -1
        elif direction == 'right': dc = 1
        
        if dr != 0 or dc != 0:
            self._move_player(dr, dc)

    def _move_player(self, dr, dc):
        """Logic for player movement and interactions."""
        nr, nc = self.player_pos[0] + dr, self.player_pos[1] + dc
        
        # Boundary and Wall check
        if nr < 0 or nr >= len(self.dungeon_map) or nc < 0 or nc >= len(self.dungeon_map[0]):
            return
        if self.dungeon_map[nr][nc] == 1:
            beep("invalid")
            return
            
        cell = self.dungeon_map[nr][nc]
        if cell == 2: # Enemy
            self._combat(nr, nc)
        elif cell == 3: # Health
            self.hp = min(self.max_hp, self.hp + 20)
            self.dungeon_map[nr][nc] = 0
            show_popup("HEALED +20 HP", C_GREEN, delay=0.5)
            beep("win")
        elif cell == 4: # Exit
            self._next_level()
        
        if cell != 2: # Don't move into enemy, stay and fight
            self.player_pos = [nr, nc]

    def _combat(self, r, c):
        """Simple combat resolution."""
        dmg_to_enemy = random.randint(15, 40)
        dmg_to_player = random.randint(5, 20)
        
        self.hp -= dmg_to_player
        self.enemies_defeated += 1
        self.dungeon_map[r][c] = 0
        self.score += 50
        self.award_xp_for_action(20) # 20 base XP for enemy defeat
        
        screen_shake(0.1, 1)
        particle_effect(char="X", color=C_RED, count=5)
        beep("eat")
        show_popup(f"DEFEATED ENEMY! -{dmg_to_player} HP", C_RED, delay=0.5)

    def _next_level(self):
        """Progress to the next level."""
        self.level += 1
        self.score += 100
        self.award_xp_for_action(50) # 50 base XP for level clear
        beep("win")
        show_popup(f"DESCENDING TO LEVEL {self.level}", C_YELLOW)
        self.dungeon_map = self._generate_level()
        self.player_pos = [1, 1]

    def _handle_death(self):
        """Manage player death."""
        beep("game_over")
        show_popup(f"DIED IN THE DUNGEON! Level: {self.level}", C_RED)
        self.game_over = True

def play_dungeon(difficulty='normal'):
    """Wrapper function for arcade.py compatibility."""
    game = DungeonGame(difficulty)
    return game.play()

if __name__ == "__main__":
    play_dungeon()
