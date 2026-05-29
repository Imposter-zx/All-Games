"""
Asteroids Game implementation for the Retro Arcade.
Navigate your ship through a field of floating asteroids.
"""

import logging
import random
import time
from typing import Any, Dict, List

from arcade_utils import (
    C_BOLD,
    C_CYAN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    beep,
    draw_retro_box,
    show_popup,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)


class AsteroidsGame(BaseGame):
    """Asteroids Game logic and rendering."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('asteroids', difficulty)
        self.width = 40
        self.height = 15
        self.px, self.py = float(self.width // 2), float(self.height // 2)
        self.vx, self.vy = 0.0, 0.0
        self.direction = 'up'
        self.asteroids: List[Dict[str, Any]] = []
        self.bullets: List[Dict[str, float]] = []
        self.spawn_timer = 0

        diff_config = {'easy': 20, 'normal': 12, 'hard': 8}
        speed_config = {'easy': 0.3, 'normal': 0.4, 'hard': 0.6}
        self.spawn_rate = diff_config.get(difficulty, 12)
        self.asteroid_speed_max = speed_config.get(difficulty, 0.4)

        for _ in range(3):
            self.spawn_asteroid()

    def spawn_asteroid(self) -> None:
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x, y = random.randint(0, self.width - 1), 0
            dx, dy = random.uniform(-0.2, 0.2), random.uniform(0.1, self.asteroid_speed_max)
        elif side == 'bottom':
            x, y = random.randint(0, self.width - 1), self.height - 1
            dx, dy = random.uniform(-0.2, 0.2), random.uniform(-self.asteroid_speed_max, -0.1)
        elif side == 'left':
            x, y = 0, random.randint(0, self.height - 1)
            dx, dy = random.uniform(0.1, self.asteroid_speed_max), random.uniform(-0.2, 0.2)
        else:
            x, y = self.width - 1, random.randint(0, self.height - 1)
            dx, dy = random.uniform(-self.asteroid_speed_max, -0.1), random.uniform(-0.2, 0.2)

        if abs(x - self.px) < 5 and abs(y - self.py) < 5:
            return

        self.asteroids.append({
            'x': float(x), 'y': float(y), 'dx': dx, 'dy': dy,
            'char': random.choice(['O', '0', '@'])
        })

    def update(self) -> None:
        self.px = (self.px + self.vx) % self.width
        self.py = (self.py + self.vy) % self.height

        self.vx *= 0.92
        self.vy *= 0.92
        if abs(self.vx) < 0.01:
            self.vx = 0.0
        if abs(self.vy) < 0.01:
            self.vy = 0.0

        for b in self.bullets[:]:
            b['x'] += b['dx']
            b['y'] += b['dy']
            if not (0 <= b['x'] < self.width and 0 <= b['y'] < self.height):
                self.bullets.remove(b)

        for a in self.asteroids[:]:
            a['x'] = (a['x'] + a['dx']) % self.width
            a['y'] = (a['y'] + a['dy']) % self.height

            if int(a['x']) == int(self.px) and int(a['y']) == int(self.py):
                self.game_over = True
                beep("lose")
                show_popup(
                    f"GAME OVER! Score: {self.score}",
                    C_RED, delay=1.5,
                )
                return

            for b in self.bullets[:]:
                if int(a['x']) == int(b['x']) and int(a['y']) == int(b['y']):
                    if a in self.asteroids:
                        self.asteroids.remove(a)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    self.score += 50
                    self.award_xp_for_action(10)
                    beep("correct")
                    break

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            if len(self.asteroids) < 10:
                self.spawn_asteroid()
            self.spawn_timer = 0

        if self.score >= 1000:
            self.unlock_achievement("asteroids_1000", "Void Master")
        elif self.score >= 500:
            self.unlock_achievement("asteroids_500", "Space Pilot")

    def render(self) -> None:
        lines: list[str] = []
        lines.append(
            f" SCORE: {C_YELLOW}{self.score}{C_RESET} | "
            f"SPEED: {abs(self.vx) + abs(self.vy):.1f} | "
            f"DIFFICULTY: {self.difficulty.upper()}"
        )
        lines.append("─" * self.width)

        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        for b in self.bullets:
            field[int(b['y'])][int(b['x'])] = f"{C_WHITE}.{C_RESET}"

        for a in self.asteroids:
            field[int(a['y'])][int(a['x'])] = f"{C_RED}{a['char']}{C_RESET}"

        chars = {'up': '^', 'down': 'v', 'left': '<', 'right': '>'}
        field[int(self.py)][int(self.px)] = f"{C_CYAN}{C_BOLD}{chars[self.direction]}{C_RESET}"

        for row in field:
            lines.append("".join(row))

        lines.append("─" * self.width)
        draw_retro_box(self.width + 4, "☄️ ASTEROIDS", lines, color=C_MAGENTA)
        print(f"\n{C_WHITE}   [ARROWS] Thrust  [SPACE] Shoot  [Q] Quit  [H] Help{C_RESET}")

    def _show_help(self) -> None:
        show_popup("ASTEROIDS: ARROWS=thrust, SPACE=shoot. Avoid asteroids!", C_MAGENTA, delay=1.5)

    def save_state_json(self) -> dict:
        return {
            'px': self.px, 'py': self.py, 'vx': self.vx, 'vy': self.vy,
            'direction': self.direction,
            'asteroids': list(self.asteroids),
            'bullets': list(self.bullets),
            'score': self.score,
            'spawn_timer': self.spawn_timer,
        }

    def load_state_json(self, state: dict) -> None:
        self.px = state.get('px', float(self.width // 2))
        self.py = state.get('py', float(self.height // 2))
        self.vx = state.get('vx', 0.0)
        self.vy = state.get('vy', 0.0)
        self.direction = state.get('direction', 'up')
        self.asteroids = list(state.get('asteroids', []))
        self.bullets = list(state.get('bullets', []))
        self.score = state.get('score', 0)
        self.spawn_timer = state.get('spawn_timer', 0)

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                self.renderer.render_frame(self.render)

                key = input_handler.get_safe_key()
                if self._save_and_quit(key):
                    break
                if key == 'h':
                    self._show_help()
                elif key == ' ':
                    dx, dy = 0.0, 0.0
                    if self.direction == 'up':
                        dy = -1.0
                    elif self.direction == 'down':
                        dy = 1.0
                    elif self.direction == 'left':
                        dx = -1.0
                    elif self.direction == 'right':
                        dx = 1.0
                    self.bullets.append({'x': float(self.px), 'y': float(self.py), 'dx': dx, 'dy': dy})
                    beep("move")
                else:
                    direction = input_handler.validator.validate_direction(key)
                    if direction:
                        self.direction = direction
                        if direction == 'up':
                            self.vy = max(-0.8, self.vy - 0.2)
                        elif direction == 'down':
                            self.vy = min(0.8, self.vy + 0.2)
                        elif direction == 'left':
                            self.vx = max(-0.8, self.vx - 0.2)
                        elif direction == 'right':
                            self.vx = min(0.8, self.vx + 0.2)

                self.update()
                time.sleep(0.02)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats


def play_asteroids(difficulty: str = 'normal') -> dict:
    game = AsteroidsGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_asteroids()
