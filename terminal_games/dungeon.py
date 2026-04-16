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

# Dungeon Symbols
PLAYER_CHAR = f"{C_CYAN}@{C_RESET}"
MONSTER_CHAR = f"{C_RED}M{C_RESET}"
WALL_CHAR = f"{C_WHITE}█{C_RESET}"
FLOOR_CHAR = f"{C_BLACK}.{C_RESET}"
TREASURE_CHAR = f"{C_YELLOW}${C_RESET}"
DOOR_CHAR = f"{C_MAGENTA}∩{C_RESET}"

class DungeonGame(BaseGame):
    """Dungeon Crawler implementation using BaseGame."""
    
    def __init__(self):
        super().__init__("dungeon")
        self.width = 20
        self.height = 10
        self.player_hp = 50
        self.player_atk = 5
        self.level = 1
        self.map = []
        self.monsters = []
        self.treasure = None
        self.door = None
        self.px, self.py = 2, 2
        self.msg = ""
        self._generate_room()

    def play(self) -> dict:
        """Main Dungeon Crawler game loop."""
        self.start_timer()
        clear_screen()
        print_big_title("DUNGEON CRAWLER", color=C_MAGENTA)
        time.sleep(1)
        
        while not self.game_over:
            self._render()
            self._handle_input()
            self._update_game_state()
            time.sleep(0.05)
            
        self.end_timer()
        
        # Save stats
        stats = load_stats().get('dungeon', {})
        high_score = stats.get('high_score', 0)
        max_level = stats.get('max_level', 1)
        
        if self.score > high_score:
            update_stats('dungeon', 'high_score', self.score)
            show_popup("NEW HIGH SCORE!", C_YELLOW)
            
        if self.level > max_level:
            update_stats('dungeon', 'max_level', self.level)
            
        self.save_stats({
            'high_score': max(self.score, high_score),
            'max_level': max(self.level, max_level),
            'last_score': self.score,
            'xp_earned': self.xp_earned
        })
        
        return self.get_final_stats()

    def _generate_room(self):
        """Build the dungeon floor."""
        self.map = [[1 if x == 0 or x == self.width-1 or y == 0 or y == self.height-1 else 0 
                     for x in range(self.width)] for y in range(self.height)]
        
        # Player start
        self.px, self.py = 2, 2
        
        # Monsters
        self.monsters = []
        for _ in range(self.level + 1):
            mx = random.randint(5, self.width-2)
            my = random.randint(1, self.height-2)
            self.monsters.append({
                "x": mx, "y": my, 
                "hp": 10 + (self.level * 2),
                "max_hp": 10 + (self.level * 2)
            })
            
        # Treasure
        self.treasure = (random.randint(5, self.width-2), random.randint(1, self.height-2))
        
        # Door
        self.door = (self.width-2, self.height // 2)

    def _render(self):
        """Render the dungeon map and UI."""
        clear_screen()
        print_big_title(f"DUNGEON L-{self.level}", color=C_MAGENTA)
        
        # Stats Bar
        hp_color = C_GREEN if self.player_hp > 25 else (C_YELLOW if self.player_hp > 10 else C_RED)
        print(f" HP: {hp_color}{self.player_hp}{C_RESET} | SCORE: {C_YELLOW}{self.score}{C_RESET} | LEVEL: {self.level}")
        
        # Map
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if (x, y) == (self.px, self.py):
                    line += PLAYER_CHAR
                else:
                    is_monster = False
                    for m in self.monsters:
                        if (x, y) == (m["x"], m["y"]):
                            line += MONSTER_CHAR
                            is_monster = True
                            break
                    
                    if not is_monster:
                        if (x, y) == self.treasure: line += TREASURE_CHAR
                        elif (x, y) == self.door: line += DOOR_CHAR
                        elif self.map[y][x] == 1: line += WALL_CHAR
                        else: line += FLOOR_CHAR
            print(line)
            
        if self.msg:
            print(f"\n{C_YELLOW}LOG: {self.msg}{C_RESET}")
            self.msg = "" # Flash log
            
        print(f"\n{C_WHITE}ARROWS: Move | Q: Quit{C_RESET}")

    def _handle_input(self):
        """Handle movement keys."""
        k = get_key(timeout=0.01)
        dx, dy = 0, 0
        if k == 'q':
            self.game_over = True
            return
        elif k == 'up': dy = -1
        elif k == 'down': dy = 1
        elif k == 'left': dx = -1
        elif k == 'right': dx = 1
        
        if dx != 0 or dy != 0:
            self._move_player(dx, dy)

    def _move_player(self, dx, dy):
        """Logic for player movement and collisions."""
        nx, ny = self.px + dx, self.py + dy
        
        # Wall Collision
        if self.map[ny][nx] == 1:
            beep("invalid")
            return
            
        # Monster Collision (Combat)
        for m in self.monsters:
            if (nx, ny) == (m["x"], m["y"]):
                self._handle_combat(m)
                return
                
        # Move successfully
        self.px, self.py = nx, ny
        
        # Feature Collisions
        if (self.px, self.py) == self.treasure:
            self._handle_treasure()
        elif (self.px, self.py) == self.door:
            self._handle_exit()

    def _handle_combat(self, m):
        """Calculate and apply damage."""
        dmg = random.randint(self.player_atk, self.player_atk + 3)
        m["hp"] -= dmg
        self.msg = f"Hit Monster for {dmg}!"
        screen_shake(0.05, 1)
        particle_effect(char="*", color=C_RED, count=3)
        
        if m["hp"] <= 0:
            self.monsters.remove(m)
            self.score += 50
            self.add_xp(20)
            beep("win")
            self.msg = "Monster Slain!"
        else:
            # Monster counter-attacks
            e_dmg = random.randint(1 + self.level, 4 + self.level)
            self.player_hp -= e_dmg
            beep("lose")
            self.msg += f" (Monster hits back for {e_dmg}!)"
            animated_flash(C_RED)

    def _handle_treasure(self):
        """Process picking up items."""
        self.score += 100
        self.add_xp(50)
        self.treasure = (-1, -1) # Remove from map
        beep("win")
        self.msg = "You found treasure! (+100)"
        show_popup("FOUND TREASURE!", C_YELLOW, delay=0.5)

    def _handle_exit(self):
        """Descend to the next floor."""
        self.level += 1
        beep("win") # Exit sound
        self.score += 200
        show_popup(f"DESCENDING TO LEVEL {self.level}...", C_MAGENTA, delay=1.0)
        self._generate_room()

    def _update_game_state(self):
        """Check for death."""
        if self.player_hp <= 0:
            self._handle_death()

    def _handle_death(self):
        """Trigger game over."""
        beep("lose")
        screen_shake(0.3, 2)
        show_popup(f"YOU DIED! Score: {self.score}", C_RED)
        self.add_xp(10)
        self.game_over = True

def play_dungeon():
    """Wrapper function for arcade.py compatibility."""
    game = DungeonGame()
    return game.play()

if __name__ == "__main__":
    play_dungeon()
