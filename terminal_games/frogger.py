import logging
import random
import time
from typing import List, Dict, Any

from arcade_utils import (
    clear_screen, print_big_title, beep, show_popup,
    screen_shake, particle_effect, animated_flash,
    C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_MAGENTA, C_WHITE, C_BLACK, u_safe
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

BOARD_WIDTH = 40
BOARD_HEIGHT = 10


class FroggerGame(BaseGame):
    """Frogger game implementation."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("frogger", difficulty)
        self.input_handler = get_safe_input_handler()
        self.player_pos = [BOARD_HEIGHT - 1, BOARD_WIDTH // 2]
        self.obstacles: List[Dict[str, Any]] = []
        self.lives = 3
        self.goal_reached = 0

        speed_mult = 1.0
        if difficulty == 'easy':
            speed_mult = 0.7
        elif difficulty == 'hard':
            speed_mult = 1.4
        self.speed_mult = speed_mult

        self._init_level()

    def _init_level(self) -> None:
        self.obstacles = []
        for r in range(1, 4):
            direction = 1 if r % 2 == 0 else -1
            speed = (random.random() * 0.15 + 0.1) * direction
            char = "==== "
            for i in range(0, BOARD_WIDTH, 12):
                self.obstacles.append({
                    'row': r, 'type': 'log', 'pos': float(i),
                    'speed': speed, 'char': char
                })

        for r in range(5, 8):
            direction = -1 if r % 2 == 0 else 1
            speed = (random.random() * 0.25 + 0.15) * direction
            char = "[XX] "
            for i in range(0, BOARD_WIDTH, 15):
                self.obstacles.append({
                    'row': r, 'type': 'car', 'pos': float(i),
                    'speed': speed, 'char': char
                })

    def play(self) -> dict:
        self.start_timer()
        clear_screen()
        print_big_title("FROGGER", color=C_GREEN)
        time.sleep(1)

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            time.sleep(0.05)

        self.end_timer()

        high_score = self.stats_manager.get_high_score('frogger')
        if self.score > high_score:
            show_popup("NEW HIGH SCORE!", C_YELLOW)

        self.save_stats({
            'high_score': max(self.score, high_score),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty,
            'goals': self.goal_reached
        })

        return self.get_final_stats()

    def _render(self) -> None:
        heart = u_safe("♥", "v")
        lives_display = f"{C_RED}{heart}{C_GREEN}" * self.lives
        print(f"{C_BOLD}{C_GREEN}FROGGER - LIVES: {lives_display} | SCORE: {self.score} | GOALS: {self.goal_reached}{C_RESET}")
        print(u_safe("≈", "~") * BOARD_WIDTH + f"{C_RESET}")

        grid = [[' ' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        for obs in self.obstacles:
            r = obs['row']
            char = obs['char']
            for i, c in enumerate(char):
                pos = int(obs['pos'] + i) % BOARD_WIDTH
                grid[r][pos] = c

        for r in range(BOARD_HEIGHT):
            line = ""
            if r == 0:
                row_color = C_CYAN
            elif 1 <= r <= 3:
                row_color = C_BLUE
            elif r == 4 or r == 8 or r == 9:
                row_color = C_GREEN
            elif 5 <= r <= 7:
                row_color = C_RED
            else:
                row_color = C_WHITE

            for c in range(BOARD_WIDTH):
                if [r, c] == self.player_pos:
                    line += f"{C_YELLOW}@{C_RESET}"
                else:
                    char = grid[r][c]
                    if char in '[]X':
                        line += f"{C_RED}{char}{C_RESET}"
                    elif char == '=':
                        line += f"{C_MAGENTA}{char}{C_RESET}"
                    else:
                        if 1 <= r <= 3 and char == ' ':
                            line += f"{C_BLUE}{u_safe('≋', '~')}{C_RESET}"
                        elif 5 <= r <= 7 and char == ' ':
                            line += f"{C_BLACK}{u_safe('▒', '#')}{C_RESET}"
                        else:
                            line += f"{row_color}{char}{C_RESET}"
            print(line)
        print(f"{C_BLUE}" + u_safe("≈", "~") * BOARD_WIDTH + f"{C_RESET}")
        print(f"{C_WHITE}ARROWS/WASD: Move | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if k == 'q':
            self.game_over = True
            return
        if k == 'h':
            show_popup("FROGGER: Cross the river on logs, dodge cars on the road. Reach the goal at the top!", C_GREEN, delay=1.5)
            return
        direction = self.input_handler.validator.validate_direction(k)
        if direction == 'up' and self.player_pos[0] > 0:
            self.player_pos[0] -= 1
        elif direction == 'down' and self.player_pos[0] < BOARD_HEIGHT - 1:
            self.player_pos[0] += 1
        elif direction == 'left' and self.player_pos[1] > 0:
            self.player_pos[1] -= 1
        elif direction == 'right' and self.player_pos[1] < BOARD_WIDTH - 1:
            self.player_pos[1] += 1

    def _update_game_state(self) -> None:
        player_on_log = False
        log_speed = 0

        for obs in self.obstacles:
            obs['pos'] = (obs['pos'] + obs['speed'] * self.speed_mult) % BOARD_WIDTH

            r, c = self.player_pos
            if obs['row'] == r:
                if obs['type'] == 'car':
                    obs_start = int(obs['pos'])
                    hit = False
                    for i in range(4):
                        if (obs_start + i) % BOARD_WIDTH == c:
                            hit = True
                            break
                    if hit:
                        self._death("SQUASHED!")
                        return

                elif obs['type'] == 'log':
                    obs_start = int(obs['pos'])
                    for i in range(4):
                        if (obs_start + i) % BOARD_WIDTH == c:
                            player_on_log = True
                            log_speed = obs['speed']
                            break

        r, c = self.player_pos
        if 1 <= r <= 3:
            if not player_on_log:
                self._death("SPLASH!")
                return
            else:
                self.player_pos[1] = int(self.player_pos[1] + log_speed * self.speed_mult)
                if self.player_pos[1] < 0 or self.player_pos[1] >= BOARD_WIDTH:
                    self._death("SWEPT AWAY!")
                    return

        if r == 0:
            self.score += 100
            self.award_xp_for_action(100)
            self.goal_reached += 1
            beep("win")
            particle_effect(char=u_safe("★", "*"), color=C_YELLOW, count=10)
            show_popup("GOAL REACHED!", C_GREEN)
            self.player_pos = [BOARD_HEIGHT - 1, BOARD_WIDTH // 2]

            if self.goal_reached == 1:
                self.unlock_achievement("frogger_first", "Crosser")
            elif self.goal_reached == 5:
                self.unlock_achievement("frogger_5", "Highway Hero")
            elif self.goal_reached == 10:
                self.unlock_achievement("frogger_10", "Leap Master")

            self.speed_mult += 0.1

    def _death(self, msg: str) -> None:
        self.lives -= 1
        beep("game_over")
        screen_shake(0.3, 3)
        animated_flash(C_RED)
        show_popup(msg, C_RED)
        if self.lives <= 0:
            self.game_over = True
        else:
            self.player_pos = [BOARD_HEIGHT - 1, BOARD_WIDTH // 2]


def play_frogger(difficulty: str = 'normal') -> dict:
    game = FroggerGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_frogger()
