import time
import os
import random
from arcade_utils import clear_screen, get_key, draw_retro_box, beep, show_popup, update_stats, load_stats, animated_flash, print_big_title, add_xp, screen_shake, particle_effect, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK

# Dungeon Symbols
PLAYER = f"{C_CYAN}@{C_RESET}"
MONSTER = f"{C_RED}M{C_RESET}"
WALL = f"{C_WHITE}█{C_RESET}"
FLOOR = f"{C_BLACK}.{C_RESET}"
TREASURE = f"{C_YELLOW}${C_RESET}"
DOOR = f"{C_MAGENTA}∩{C_RESET}"

class DungeonCrawler:
    def __init__(self):
        self.width = 20
        self.height = 10
        self.player_hp = 50
        self.player_atk = 5
        self.level = 1
        self.score = 0
        self.game_over = False
        self.generate_room()

    def generate_room(self):
        self.map = [[1 if x == 0 or x == self.width-1 or y == 0 or y == self.height-1 else 0 
                     for x in range(self.width)] for y in range(self.height)]
        
        # Player position
        self.px, self.py = 2, 2
        
        # Place monsters
        self.monsters = []
        for _ in range(self.level + 1):
            mx, my = random.randint(5, self.width-2), random.randint(1, self.height-2)
            self.monsters.append({"x": mx, "y": my, "hp": 10 + (self.level * 2)})
            
        # Place treasure
        self.treasure = (random.randint(5, self.width-2), random.randint(1, self.height-2))
        
        # Place door
        self.door = (self.width-2, self.height // 2)

    def draw(self):
        clear_screen()
        print_big_title(f"DUNGEON L-{self.level}", color=C_MAGENTA)
        print(f" HP: {C_RED}{self.player_hp}{C_RESET} | SCORE: {C_YELLOW}{self.score}{C_RESET}")
        
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if (x, y) == (self.px, self.py): line += PLAYER
                else:
                    is_monster = False
                    for m in self.monsters:
                        if (x, y) == (m["x"], m["y"]):
                            line += MONSTER
                            is_monster = True
                            break
                    if not is_monster:
                        if (x, y) == self.treasure: line += TREASURE
                        elif (x, y) == self.door: line += DOOR
                        elif self.map[y][x] == 1: line += WALL
                        else: line += FLOOR
            print(line)
        print(f"\n{C_WHITE}ARROWS to move | Q to quit{C_RESET}")

    def move(self, dx, dy):
        nx, ny = self.px + dx, self.py + dy
        
        if self.map[ny][nx] == 1:
            beep("invalid")
            return

        # Check combat
        for m in self.monsters:
            if (nx, ny) == (m["x"], m["y"]):
                dmg = random.randint(self.player_atk, self.player_atk + 3)
                m["hp"] -= dmg
                screen_shake(0.1, 1)
                particle_effect(char="!", color=C_RED, count=5)
                if m["hp"] <= 0:
                    self.monsters.remove(m)
                    self.score += 50
                    add_xp(20)
                    beep("win")
                else:
                    self.player_hp -= random.randint(1, 4)
                    beep("lose")
                if self.player_hp <= 0: self.game_over = True
                return

        self.px, self.py = nx, ny
        
        if (self.px, self.py) == self.treasure:
            self.score += 100
            add_xp(50)
            self.treasure = (-1, -1)
            beep("win")
            show_popup("FOUND TREASURE!", C_YELLOW, delay=0.5)
            
        if (self.px, self.py) == self.door:
            self.level += 1
            show_popup(f"DESCENDING TO LEVEL {self.level}...", C_MAGENTA, delay=1.0)
            self.generate_room()

def play_dungeon():
    game = DungeonCrawler()
    while not game.game_over:
        game.draw()
        key = get_key()
        if key == 'q': break
        
        if key == 'up': game.move(0, -1)
        elif key == 'down': game.move(0, 1)
        elif key == 'left': game.move(-1, 0)
        elif key == 'right': game.move(1, 0)
        
    if game.game_over:
        show_popup(f"YOU DIED! Score: {game.score}", C_RED)
        add_xp(10)

if __name__ == "__main__":
    play_dungeon()
