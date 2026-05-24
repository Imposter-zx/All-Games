"""
Pong Game implementation for the Retro Arcade.
Classic table tennis — play against an AI opponent.
"""

import logging
import random
import time

from arcade_utils import (
    C_BLUE,
    C_CYAN,
    C_GRAY,
    C_GREEN,
    C_MAGENTA,
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


class PongGame(BaseGame):
    """Pong Game logic and rendering with AI opponent."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('pong', difficulty)
        self.width = 40
        self.height = 15
        self.paddle_size = 2
        self.ai_paddle_size = 2
        self.paddle_pos = self.height // 2 - self.paddle_size // 2
        self.ai_paddle_pos = self.height // 2 - self.ai_paddle_size // 2

        self.ball_x = float(self.width // 2)
        self.ball_y = float(self.height // 2)
        self.ball_dx = random.choice([-1, 1])
        self.ball_dy = random.choice([-0.8, -0.5, 0.5, 0.8])
        self.ball_speed = 1.0

        # Difficulty settings
        diff_config = {
            'easy':   {'paddle': 4, 'ai_paddle': 3, 'speed': 0.9, 'ai_reaction': 0.3},
            'normal': {'paddle': 3, 'ai_paddle': 3, 'speed': 1.0, 'ai_reaction': 0.15},
            'hard':   {'paddle': 2, 'ai_paddle': 4, 'speed': 1.3, 'ai_reaction': 0.05},
        }
        cfg = diff_config.get(difficulty, diff_config['normal'])
        self.paddle_size = cfg['paddle']
        self.ai_paddle_size = cfg['ai_paddle']
        self.ball_speed = cfg['speed']
        self.ai_reaction_delay = cfg['ai_reaction']

        self.player_score = 0
        self.ai_score = 0
        self.hits = 0
        self.ai_miss_timer = 0.0
        self.game_over = False

    def save_state_json(self) -> dict:
        return {
            'ball_x': self.ball_x,
            'ball_y': self.ball_y,
            'ball_dx': self.ball_dx,
            'ball_dy': self.ball_dy,
            'ball_speed': self.ball_speed,
            'paddle_pos': self.paddle_pos,
            'ai_paddle_pos': self.ai_paddle_pos,
            'player_score': self.player_score,
            'ai_score': self.ai_score,
            'hits': self.hits,
        }

    def load_state_json(self, state: dict) -> None:
        self.ball_x = state.get('ball_x', float(self.width // 2))
        self.ball_y = state.get('ball_y', float(self.height // 2))
        self.ball_dx = state.get('ball_dx', 1.0)
        self.ball_dy = state.get('ball_dy', 0.5)
        self.ball_speed = state.get('ball_speed', 1.0)
        self.paddle_pos = state.get('paddle_pos', self.height // 2 - self.paddle_size // 2)
        self.ai_paddle_pos = state.get('ai_paddle_pos', self.height // 2 - self.ai_paddle_size // 2)
        self.player_score = state.get('player_score', 0)
        self.ai_score = state.get('ai_score', 0)
        self.hits = state.get('hits', 0)

    def move_paddle(self, direction: str) -> None:
        if direction == 'up' and self.paddle_pos > 0:
            self.paddle_pos -= 1
        elif direction == 'down' and self.paddle_pos < self.height - self.paddle_size:
            self.paddle_pos += 1

    def _update_ai(self) -> None:
        """AI paddle tracks the ball with configurable reaction delay."""
        self.ai_miss_timer -= 1
        if self.ai_miss_timer > 0:
            return

        # Predict where ball will be when it reaches AI side
        predict_y = self.ball_y
        if self.ball_dx > 0:
            # Ball moving towards AI — track it
            predict_y = self.ball_y
        else:
            # Ball moving away — return to center
            predict_y = self.height / 2

        # Add some imperfection based on difficulty
        if self.difficulty == 'easy':
            predict_y += random.uniform(-2, 2)
        elif self.difficulty == 'normal':
            predict_y += random.uniform(-1, 1)

        target = int(predict_y) - self.ai_paddle_size // 2
        if self.ai_paddle_pos < target:
            self.ai_paddle_pos += 1
        elif self.ai_paddle_pos > target:
            self.ai_paddle_pos -= 1

        self.ai_paddle_pos = max(0, min(self.height - self.ai_paddle_size, self.ai_paddle_pos))

    def update_ball(self) -> None:
        """Update ball position and handle collisions."""
        self.ball_x += self.ball_dx * self.ball_speed * 0.3
        self.ball_y += self.ball_dy * self.ball_speed * 0.3

        # Top/bottom wall
        if self.ball_y <= 0 or self.ball_y >= self.height - 1:
            self.ball_dy *= -0.9
            self.ball_y = max(0.1, min(self.height - 1.1, self.ball_y))
            beep("move")

        # Player paddle (left)
        if self.ball_x <= 1.5:
            paddle_top = self.paddle_pos
            paddle_bottom = self.paddle_pos + self.paddle_size
            if paddle_top <= int(self.ball_y) < paddle_bottom:
                self.ball_dx = abs(self.ball_dx)
                # Angle based on where ball hits paddle
                hit_pos = (self.ball_y - paddle_top) / self.paddle_size - 0.5
                self.ball_dy = hit_pos * 1.5
                self.ball_x = 1.5
                self.hits += 1
                self.score += 10
                self.award_xp_for_action(10)
                beep("correct")
                self.ball_speed = min(2.0, self.ball_speed + 0.05)

                if self.hits == 10:
                    self.unlock_achievement("pong_pro", "Pong Pro")
                elif self.hits == 25:
                    self.unlock_achievement("pong_master", "Pong Master")
            else:
                self.ai_score += 1
                beep("lose")

        # AI paddle (right)
        if self.ball_x >= self.width - 2.5:
            ai_top = self.ai_paddle_pos
            ai_bottom = self.ai_paddle_pos + self.ai_paddle_size
            if ai_top <= int(self.ball_y) < ai_bottom:
                self.ball_dx = -abs(self.ball_dx)
                hit_pos = (self.ball_y - ai_top) / self.ai_paddle_size - 0.5
                self.ball_dy = hit_pos * 1.5
                self.ball_x = self.width - 2.5
                beep("correct")
            else:
                self.player_score += 10
                self.score += 10
                self.award_xp_for_action(10)

        # Check win condition
        if self.player_score >= 100 or self.ai_score >= 100:
            self.game_over = True

    def render(self) -> None:
        lines: list[str] = []
        lines.append(
            f" YOU: {C_YELLOW}{self.player_score}{C_RESET}  "
            f"AI: {C_MAGENTA}{self.ai_score}{C_RESET}  "
            f"HITS: {C_GREEN}{self.hits}{C_RESET}  "
            f"DIFF: {self.difficulty.upper()}"
        )
        lines.append("─" * self.width)

        for y in range(self.height):
            row = ""
            for x in range(self.width):
                # Player paddle
                if x == 0 and self.paddle_pos <= y < self.paddle_pos + self.paddle_size:
                    row += f"{C_CYAN}█{C_RESET}"
                # AI paddle
                elif x == self.width - 1 and self.ai_paddle_pos <= y < self.ai_paddle_pos + self.ai_paddle_size:
                    row += f"{C_MAGENTA}█{C_RESET}"
                # Ball
                elif abs(x - self.ball_x) < 0.6 and abs(y - self.ball_y) < 0.6:
                    row += f"{C_YELLOW}●{C_RESET}"
                elif x == self.width // 2:
                    row += f"{C_GRAY}│{C_RESET}" if y % 2 == 0 else " "
                else:
                    row += " "
            lines.append(row)

        lines.append("─" * self.width)
        draw_retro_box(self.width + 4, "🏓 PONG ARCADE", lines, color=C_BLUE)
        print(f"\n{C_WHITE}   [UP/DOWN] Move  [Q] Quit  [H] Help{C_RESET}")

    def _show_help(self) -> None:
        show_popup("PONG: Beat the AI to 100 points. First to 100 wins! Use UP/DOWN to move your paddle (left).",
                   C_CYAN, delay=1.5)

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

                direction = input_handler.get_direction()
                if direction:
                    self.move_paddle(direction)

                self._update_ai()
                self.update_ball()

                key = input_handler.get_safe_key()
                if key and self._save_and_quit(key):
                    break
                if key and key.lower() == 'h':
                    self._show_help()

                time.sleep(0.03)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats


def play_pong(difficulty: str = 'normal') -> dict:
    game = PongGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_pong()
