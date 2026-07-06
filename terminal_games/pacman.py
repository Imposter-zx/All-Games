import math
import random
import time
from typing import List, Tuple

from arcade_utils import (
    C_BLUE,
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    animated_flash,
    beep,
    clear_screen,
    particle_effect,
    print_big_title,
    screen_shake,
    show_popup,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

PACMAN_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,0,1,0,1,1,0,1],
    [1,2,0,0,0,0,0,0,0,0,0,0,0,2,1],
    [1,0,1,1,0,1,1,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
    [1,1,1,1,0,1,0,0,0,1,0,1,1,1,1],
    [1,1,1,1,0,1,1,3,1,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,1,1,0,0,0,1,0,0,0,1,1,0,1],
    [1,2,0,1,0,1,0,1,0,1,0,1,0,2,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

PACMAN_CHAR = f"{C_YELLOW}C{C_RESET}"
PELLET_CHAR = f"{C_WHITE}.{C_RESET}"
POWER_CHAR = f"{C_CYAN}o{C_RESET}"
WALL_CHAR = f"{C_BLUE}█{C_RESET}"

# Ghost colors/personalities
GHOST_CONFIG = [
    {'color': C_RED,     'name': 'Blinky', 'aggro': 1.0},   # Chases directly
    {'color': C_MAGENTA, 'name': 'Pinky',  'aggro': 0.8},   # Ambushes
    {'color': C_CYAN,    'name': 'Inky',   'aggro': 0.6},   # Semi-random
    {'color': C_YELLOW,  'name': 'Sue',    'aggro': 0.3},   # Shy
]


class Ghost:
    """Individual ghost with personality-driven AI."""

    def __init__(self, index: int, x: int, y: int) -> None:
        cfg = GHOST_CONFIG[index % len(GHOST_CONFIG)]
        self.index = index
        self.x = x
        self.y = y
        self.color = cfg['color']
        self.name = cfg['name']
        self.aggro = cfg['aggro']
        self.scatter_target = (1, 1) if index < 2 else (13, 12)
        self.direction = (0, 0)
        self.mode = 'chase'
        self.frightened_timer = 0

    def get_target(self, pac_x: int, pac_y: int, power_timer: int) -> Tuple[int, int]:
        """Return the target tile based on ghost personality."""
        if power_timer > 0:
            # Flee to scatter corner
            return self.scatter_target

        # Mix of chase and scatter based on aggro
        if random.random() < self.aggro:
            return (pac_x, pac_y)
        return self.scatter_target


class PacmanGame(BaseGame):
    """Pac-Man game implementation using BaseGame."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("pacman", difficulty)
        self.game_map = [row[:] for row in PACMAN_MAP]
        self.pac_x, self.pac_y = 7, 8
        self.ghosts: List[Ghost] = [
            Ghost(0, 1, 1),
            Ghost(1, 13, 1),
            Ghost(2, 1, 12),
            Ghost(3, 13, 12),
        ]
        self.power_timer = 0
        self.total_pellets = sum(row.count(0) + row.count(2) for row in self.game_map)
        self.pellets_eaten = 0
        self.last_move_time = time.time()
        self.lives = 3
        self.input_handler = get_safe_input_handler()

    def save_state_json(self) -> dict:
        return {
            'player_pos': (self.pac_x, self.pac_y),
            'ghosts': [
                {
                    'pos': (g.x, g.y),
                    'direction': g.direction,
                    'mode': g.mode,
                    'frightened_timer': g.frightened_timer,
                }
                for g in self.ghosts
            ],
            'dots': self.game_map,
            'power_timer': self.power_timer,
            'score': self.score,
            'lives': self.lives,
        }

    def load_state_json(self, state: dict) -> None:
        self.pac_x, self.pac_y = state['player_pos']
        for i, g in enumerate(self.ghosts):
            gd = state['ghosts'][i]
            g.x, g.y = gd['pos']
            g.direction = gd['direction']
            g.mode = gd['mode']
            g.frightened_timer = gd['frightened_timer']
        self.game_map = state['dots']
        self.power_timer = state['power_timer']
        self.score = state['score']
        self.lives = state['lives']

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("PAC-MAN", color=C_YELLOW)
        time.sleep(1)

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            time.sleep(0.05)

        self.end_timer()

        stats = self.stats_manager.get_stats('pacman')
        wins = stats.get('wins', 0)
        high_score = self.stats_manager.get_high_score('pacman')

        if self.score > high_score:
            show_popup("NEW HIGH SCORE!", C_YELLOW)

        self.save_stats({
            'high_score': max(self.score, high_score),
            'wins': wins + (1 if self.pellets_eaten >= self.total_pellets else 0),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })

        return self.get_final_stats()

    def _render(self) -> None:
        high_score = self.stats_manager.get_high_score('pacman')
        ghost_status = " ".join(f"{g.color}{g.name[:1]}{C_RESET}" for g in self.ghosts)
        print(f" SCORE: {C_GREEN}{self.score:<6}{C_RESET} | HI: {high_score:<6} | GHOSTS: {ghost_status}")
        if self.power_timer > 0:
            print(f" POWER: {C_CYAN}{'█' * (self.power_timer // 5)}{C_RESET}")

        for y, row in enumerate(self.game_map):
            line = ""
            for x, cell in enumerate(row):
                is_entity = False
                if (x, y) == (self.pac_x, self.pac_y):
                    line += PACMAN_CHAR + " "
                    is_entity = True
                else:
                    for g in self.ghosts:
                        if (x, y) == (g.x, g.y):
                            if self.power_timer > 0:
                                line += f"{C_BLUE}m{C_RESET} "
                            else:
                                line += f"{g.color}M{C_RESET} "
                            is_entity = True
                            break
                if not is_entity:
                    if cell == 1:
                        line += WALL_CHAR * 2
                    elif cell == 0:
                        line += PELLET_CHAR + " "
                    elif cell == 2:
                        line += POWER_CHAR + " "
                    else:
                        line += "  "
            print(line)
        print(f"\n{C_WHITE}ARROWS/WASD: Move | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        if k == 'p':
            self._pause_game()
        if k == 'h':
            show_popup("Eat pellets. Power pellets let you eat ghosts! Avoid ghosts without power.", C_CYAN, delay=1.5)
            return

        direction = self.input_handler.validator.validate_direction(k)
        dx, dy = 0, 0
        if direction == 'up':
            dy = -1
        elif direction == 'down':
            dy = 1
        elif direction == 'left':
            dx = -1
        elif direction == 'right':
            dx = 1
        if dx != 0 or dy != 0:
            self._move_pacman(dx, dy)

    def _move_pacman(self, dx: int, dy: int) -> None:
        new_x = self.pac_x + dx
        new_y = self.pac_y + dy
        if self.game_map[new_y][new_x] != 1:
            self.pac_x = new_x
            self.pac_y = new_y
            self._eat_cell(new_x, new_y)

    def _eat_cell(self, x: int, y: int) -> None:
        cell = self.game_map[y][x]
        if cell == 0:
            self.game_map[y][x] = 3
            self.score += 10
            self.award_xp_for_action(10)
            self.pellets_eaten += 1
            beep("eat")
        elif cell == 2:
            self.game_map[y][x] = 3
            self.score += 50
            self.award_xp_for_action(50)
            self.power_timer = 30
            self.pellets_eaten += 1
            beep("win")
            screen_shake(0.05, 1)

    def _update_game_state(self) -> None:
        self._move_ghosts()
        self._check_collisions()
        if self.power_timer > 0:
            self.power_timer -= 1
        if self.pellets_eaten >= self.total_pellets:
            self.unlock_achievement("pacman_clear", "Ghost Hunter")
            self._handle_win()

    def _move_ghosts(self) -> None:
        """Move each ghost using its personality-based AI."""
        if random.random() > 0.3:
            return

        for g in self.ghosts:
            target_x, target_y = g.get_target(self.pac_x, self.pac_y, self.power_timer)
            best_move = None
            best_dist = float('inf')

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = g.x + dx, g.y + dy
                if 0 <= ny < len(self.game_map) and 0 <= nx < len(self.game_map[0]):
                    if self.game_map[ny][nx] != 1:
                        dist = math.sqrt((nx - target_x) ** 2 + (ny - target_y) ** 2)
                        if dist < best_dist:
                            best_dist = dist
                            best_move = (nx, ny)

            if best_move:
                g.x, g.y = best_move

    def _check_collisions(self) -> None:
        for g in self.ghosts:
            if (self.pac_x, self.pac_y) == (g.x, g.y):
                if self.power_timer > 0:
                    self.score += 200
                    self.award_xp_for_action(100)
                    g.x, g.y = 7, 7
                    screen_shake(0.1, 1)
                    particle_effect(char="*", color=C_CYAN, count=5)
                    beep("win")
                else:
                    self._handle_death()
                    break

    def _handle_death(self) -> None:
        beep("lose")
        animated_flash(C_RED)
        self.lives -= 1
        if self.lives > 0:
            show_popup(f"GHOST CAUGHT YOU! {self.lives} lives left", C_RED, delay=1)
            self._reset_positions()
        else:
            show_popup(f"GAME OVER! Score: {self.score}", C_RED)
            self.game_over = True

    def _handle_win(self) -> None:
        beep("win")
        show_popup(f"LEVEL CLEAR! YOU WIN! Score: {self.score}", C_YELLOW)

    def _reset_positions(self) -> None:
        self.pac_x, self.pac_y = 7, 8
        self.ghosts = [
            Ghost(0, 1, 1),
            Ghost(1, 13, 1),
            Ghost(2, 1, 12),
            Ghost(3, 13, 12),
        ]
        self.power_timer = 0
        self.last_move_time = time.time()
        self.game_over = True


def play_pacman(difficulty: str = 'normal') -> dict:
    game = PacmanGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_pacman()
