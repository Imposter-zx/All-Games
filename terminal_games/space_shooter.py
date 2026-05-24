import random
import time
from typing import Dict, List

from arcade_utils import (
    C_CYAN,
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
    u_safe,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

WIDTH = 30
HEIGHT = 20
PLAYER_CHAR = u_safe("▲", "^")
ENEMY_CHAR = "W"
BULLET_CHAR = "|"


class SpaceShooterGame(BaseGame):
    """Space Shooter game implementation using BaseGame."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("space_shooter", difficulty)
        self.player_x = WIDTH // 2
        self.bullets: List[Dict[str, int]] = []
        self.enemies: List[Dict[str, int]] = []
        self.lives = 3
        self.spawn_timer = 0
        self.enemy_move_speed = 5
        self.frame_count = 0
        self.input_handler = get_safe_input_handler()

    def save_state_json(self) -> dict:
        return {
            'player_x': self.player_x,
            'enemies': self.enemies,
            'bullets': self.bullets,
            'score': self.score,
            'lives': self.lives,
            'spawn_timer': self.spawn_timer,
        }

    def load_state_json(self, state: dict) -> None:
        self.player_x = state['player_x']
        self.enemies = state['enemies']
        self.bullets = state['bullets']
        self.score = state['score']
        self.lives = state['lives']
        self.spawn_timer = state['spawn_timer']

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("SPACE SHOOTER", color=C_MAGENTA)
        time.sleep(1)

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            time.sleep(0.05)
            self.frame_count += 1

        self.end_timer()

        high_score = self.stats_manager.get_high_score('space_shooter')
        if self.score > high_score:
            show_popup("NEW HIGH SCORE!", C_YELLOW)

        self.save_stats({
            'high_score': max(self.score, high_score),
            'last_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })

        return self.get_final_stats()

    def _render(self) -> None:
        high_score = self.stats_manager.get_high_score('space_shooter')

        print(f"{C_MAGENTA}╔{'═' * WIDTH}╗")
        print(f"║ SCORE: {self.score:<10} HI: {high_score:<10} LIVES: {self.lives} ║")
        print(f"╚{'═' * WIDTH}╝{C_RESET}")

        print(f"{C_MAGENTA}╔{'═' * WIDTH}╗{C_RESET}")
        for r in range(HEIGHT):
            line = f"{C_MAGENTA}║{C_RESET}"
            row_chars = [" "] * WIDTH

            if r == HEIGHT - 1:
                row_chars[self.player_x] = f"{C_CYAN}{PLAYER_CHAR}{C_RESET}"

            for b in self.bullets:
                if b['y'] == r:
                    row_chars[b['x']] = f"{C_YELLOW}{BULLET_CHAR}{C_RESET}"

            for e in self.enemies:
                if e['y'] == r:
                    row_chars[e['x']] = f"{C_RED}{ENEMY_CHAR}{C_RESET}"

            line += "".join(row_chars) + f"{C_MAGENTA}║{C_RESET}"
            print(line)

        print(f"{C_MAGENTA}╚{'═' * WIDTH}╝{C_RESET}")
        print(f"{C_WHITE}ARROWS/WASD: Move | SPACE: Shoot | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        if k == 'h':
            show_popup("SPACE SHOOTER: Move LEFT/RIGHT, shoot SPACE. Don't let enemies past you!", C_MAGENTA, delay=1.5)
            return
        if k == ' ':
            self.bullets.append({'x': self.player_x, 'y': HEIGHT - 2})
            beep("correct")
        else:
            direction = self.input_handler.validator.validate_direction(k)
            if direction == 'left':
                self.player_x = max(0, self.player_x - 1)
            elif direction == 'right':
                self.player_x = min(WIDTH - 1, self.player_x + 1)

    def _update_game_state(self) -> None:
        self.spawn_timer += 1
        spawn_rate = max(3, 10 - (self.score // 200))
        if self.spawn_timer > spawn_rate:
            self.enemies.append({'x': random.randint(0, WIDTH - 1), 'y': 0})
            self.spawn_timer = 0

        for b in self.bullets:
            b['y'] -= 1
        self.bullets = [b for b in self.bullets if b['y'] >= 0]

        if self.frame_count % self.enemy_move_speed == 0:
            for e in self.enemies:
                e['y'] += 1

        if self.score >= 1000:
            self.unlock_achievement("space_shooter_1000", "Space Ace")

        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if b['x'] == e['x'] and (b['y'] == e['y'] or b['y'] == e['y'] - 1):
                    if b in self.bullets:
                        self.bullets.remove(b)
                    if e in self.enemies:
                        self.enemies.remove(e)
                    self.score += 10
                    self.award_xp_for_action(10)
                    screen_shake(0.05, 1)
                    particle_effect(char="*", color=C_RED, count=3)
                    beep("eat")
                    break

        for e in self.enemies[:]:
            if e['y'] >= HEIGHT - 1:
                if e['x'] == self.player_x and e['y'] == HEIGHT - 1:
                    self._handle_collision()
                self.enemies.remove(e)
            elif e['x'] == self.player_x and e['y'] == HEIGHT - 1:
                self._handle_collision()
                self.enemies.remove(e)

    def _handle_collision(self) -> None:
        self.lives -= 1
        screen_shake(0.3, 2)
        animated_flash(C_RED)
        beep("lose")

        if self.lives <= 0:
            show_popup(f"GAME OVER! Score: {self.score}", C_RED)
            self.game_over = True


def play_space_shooter(difficulty: str = 'normal') -> dict:
    game = SpaceShooterGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_space_shooter()
