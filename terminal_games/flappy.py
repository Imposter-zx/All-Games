import logging
import random
import time
from typing import Any, Dict, List

from arcade_utils import (
    C_BOLD,
    C_CYAN,
    C_GREEN,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    animated_flash,
    beep,
    clear_screen,
    print_big_title,
    screen_shake,
    show_popup,
    u_safe,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

BOARD_WIDTH = 50
BOARD_HEIGHT = 20


class FlappyGame(BaseGame):
    """Flappy Bird terminal implementation."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("flappy", difficulty)
        self.input_handler = get_safe_input_handler()
        self.bird_pos: List[float] = [float(BOARD_HEIGHT // 2), 10.0]
        self.velocity = 0.0
        self.gravity = 0.6
        self.jump_strength = -1.5
        self.pipes: List[Dict[str, Any]] = []
        self.pipe_width = 4
        self.pipe_gap = 6
        self.frame_count = 0

        if difficulty == 'easy':
            self.pipe_gap = 8
            self.gravity = 0.4
        elif difficulty == 'hard':
            self.pipe_gap = 5
            self.gravity = 0.8

    def _spawn_pipe(self) -> None:
        gap_y = random.randint(3, BOARD_HEIGHT - self.pipe_gap - 3)
        self.pipes.append({'x': BOARD_WIDTH, 'gap_y': gap_y})

    def save_state_json(self) -> dict:
        return {
            'bird_pos': list(self.bird_pos),
            'velocity': self.velocity,
            'pipes': list(self.pipes),
            'score': self.score,
        }

    def load_state_json(self, state: dict) -> None:
        self.bird_pos = list(state.get('bird_pos', [float(BOARD_HEIGHT // 2), 10.0]))
        self.velocity = state.get('velocity', 0.0)
        self.pipes = list(state.get('pipes', []))
        self.score = state.get('score', 0)

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("FLAPPY", color=C_YELLOW)
        time.sleep(1)

        self._spawn_pipe()

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            time.sleep(0.05)

        self.end_timer()
        high_score = self.stats_manager.get_high_score('flappy')
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
        print(f"{C_BOLD}{C_YELLOW}FLAPPY BIRD - SCORE: {self.score}{C_RESET}")

        grid: List[List[str]] = [[' ' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        for pipe in self.pipes:
            px = int(pipe['x'])
            gap_y = pipe['gap_y']
            for x in range(px, px + self.pipe_width):
                if 0 <= x < BOARD_WIDTH:
                    for y in range(BOARD_HEIGHT):
                        if y < gap_y or y >= gap_y + self.pipe_gap:
                            grid[y][x] = '█'

        by, bx = int(self.bird_pos[0]), int(self.bird_pos[1])
        if 0 <= by < BOARD_HEIGHT:
            grid[by][bx] = u_safe('►', '>')

        print(f"{C_CYAN}╔{'═' * BOARD_WIDTH}╗{C_RESET}")
        for r in range(BOARD_HEIGHT):
            line = f"{C_CYAN}║{C_RESET}"
            for c in range(BOARD_WIDTH):
                char = grid[r][c]
                if char == '►':
                    line += f"{C_YELLOW}{char}{C_RESET}"
                elif char == '█':
                    line += f"{C_GREEN}{char}{C_RESET}"
                else:
                    line += char
            line += f"{C_CYAN}║{C_RESET}"
            print(line)
        print(f"{C_CYAN}╚{'═' * BOARD_WIDTH}╝{C_RESET}")
        print(f"{C_WHITE}UP/SPACE/W: Jump | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        if k == 'p':
            self._pause_game()
        if k == 'h':
            show_popup("FLAPPY BIRD: Press UP/SPACE to flap. Navigate through the pipe gaps!", C_YELLOW, delay=1.5)
            return
        if k in ['up', ' ', 'w']:
            self.velocity = self.jump_strength
            beep("move")

    def _update_game_state(self) -> None:
        self.velocity += self.gravity
        self.bird_pos[0] += self.velocity

        if self.bird_pos[0] < 0 or self.bird_pos[0] >= BOARD_HEIGHT:
            self._die("CRASHED!")
            return

        for pipe in self.pipes:
            pipe['x'] -= 1
            if pipe['x'] + self.pipe_width == self.bird_pos[1]:
                self.score += 1
                self.award_xp_for_action(1)
                beep("correct")
                if self.score == 10:
                    self.unlock_achievement("flappy_10", "Birdie")
                if self.score == 50:
                    self.unlock_achievement("flappy_50", "Ace Flyer")

        self.pipes = [p for p in self.pipes if p['x'] > -self.pipe_width]

        self.frame_count += 1
        if self.frame_count % 15 == 0:
            self._spawn_pipe()

        by, bx = int(self.bird_pos[0]), int(self.bird_pos[1])
        for pipe in self.pipes:
            px = int(pipe['x'])
            if px <= bx < px + self.pipe_width:
                if by < pipe['gap_y'] or by >= pipe['gap_y'] + self.pipe_gap:
                    self._die("OVAL HIT!")
                    return

    def _die(self, msg: str) -> None:
        beep("game_over")
        screen_shake(0.4, 4)
        animated_flash(C_RED)
        show_popup(msg, C_RED)
        self.game_over = True


def play_flappy(difficulty: str = 'normal') -> dict:
    game = FlappyGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_flappy()
