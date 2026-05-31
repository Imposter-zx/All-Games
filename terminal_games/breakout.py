import time
from typing import Any, Dict, List

from arcade_utils import (
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

WIDTH = 40
HEIGHT = 20
PADDLE_WIDTH = 6


class BreakoutGame(BaseGame):
    """Breakout game implementation using BaseGame."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("breakout", difficulty)
        self.paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
        self.ball_x = float(WIDTH // 2)
        self.ball_y = float(HEIGHT - 2)
        self.ball_dx = 1
        self.ball_dy = -1
        self.lives = 3
        self.bricks: List[Dict[str, Any]] = self._init_bricks()
        self.input_handler = get_safe_input_handler()

    def save_state_json(self) -> dict:
        return {
            'paddle_x': self.paddle_x,
            'ball_x': self.ball_x,
            'ball_y': self.ball_y,
            'ball_dx': self.ball_dx,
            'ball_dy': self.ball_dy,
            'bricks': self.bricks,
            'score': self.score,
            'lives': self.lives,
        }

    def load_state_json(self, state: dict) -> None:
        self.paddle_x = state['paddle_x']
        self.ball_x = state['ball_x']
        self.ball_y = state['ball_y']
        self.ball_dx = state['ball_dx']
        self.ball_dy = state['ball_dy']
        self.bricks = state['bricks']
        self.score = state['score']
        self.lives = state['lives']

    def _init_bricks(self) -> List[Dict[str, Any]]:
        bricks: List[Dict[str, Any]] = []
        colors = [C_RED, C_YELLOW, C_GREEN]
        for r in range(3):
            for c in range(0, WIDTH - 2, 4):
                bricks.append({'x': c + 1, 'y': r + 2, 'color': colors[r], 'active': True})
        return bricks

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("BREAKOUT", color=C_CYAN)
        time.sleep(1)

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            time.sleep(0.04)

        self.end_timer()

        high_score = self.stats_manager.get_high_score('breakout')
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
        high_score = self.stats_manager.get_high_score('breakout')

        print(f"{C_CYAN}╔{'═' * WIDTH}╗")
        print(f"║ SCORE: {self.score:<10} HI: {high_score:<10} LIVES: {self.lives} ║")
        print(f"╚{'═' * WIDTH}╝{C_RESET}")

        print(f"{C_CYAN}╔{'═' * WIDTH}╗{C_RESET}")
        for r in range(HEIGHT):
            line = f"{C_CYAN}║{C_RESET}"
            row_content = ""
            c = 0
            while c < WIDTH:
                if r == int(self.ball_y) and c == int(self.ball_x):
                    row_content += f"{C_WHITE}●{C_RESET}"
                    c += 1
                    continue
                if r == HEIGHT - 1 and self.paddle_x <= c < self.paddle_x + PADDLE_WIDTH:
                    row_content += f"{C_MAGENTA}═{C_RESET}"
                    c += 1
                    continue
                found_brick: Any = None
                for b in self.bricks:
                    if b['active'] and b['y'] == r and b['x'] <= c < b['x'] + 3:
                        found_brick = b
                        break
                if found_brick:
                    row_content += f"{found_brick['color']}█{C_RESET}"
                    c += 1
                else:
                    row_content += " "
                    c += 1
            line += row_content + f"{C_CYAN}║{C_RESET}"
            print(line)

        print(f"{C_CYAN}╚{'═' * WIDTH}╝{C_RESET}")
        print(f"{C_WHITE}LEFT/RIGHT to Move | Q to Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        if k == 'p':
            self._pause_game()
        if k == 'h':
            show_popup("BREAKOUT: Destroy all bricks with the ball. Move paddle with LEFT/RIGHT.", C_CYAN, delay=1.5)
            return
        direction = self.input_handler.validator.validate_direction(k)
        if direction == 'left':
            self.paddle_x = max(0, self.paddle_x - 2)
        elif direction == 'right':
            self.paddle_x = min(WIDTH - PADDLE_WIDTH, self.paddle_x + 2)

    def _update_game_state(self) -> None:
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        if self.ball_x <= 0 or self.ball_x >= WIDTH - 1:
            self.ball_dx *= -1
            beep("correct")
            self.ball_x = max(0, min(WIDTH - 1, self.ball_x))

        if self.ball_y <= 0:
            self.ball_dy *= -1
            beep("correct")
            self.ball_y = 0

        if self.ball_y >= HEIGHT - 1:
            if self.paddle_x <= self.ball_x <= self.paddle_x + PADDLE_WIDTH:
                self.ball_dy *= -1
                self.ball_y = HEIGHT - 2
                beep("correct")
            else:
                self._handle_life_lost()

        for b in self.bricks:
            if b['active']:
                if int(self.ball_y) == b['y'] and b['x'] <= int(self.ball_x) < b['x'] + 3:
                    b['active'] = False
                    self.ball_dy *= -1
                    self.score += 10
                    self.award_xp_for_action(10)
                    screen_shake(0.05, 1)
                    particle_effect(char="*", color=b['color'], count=5)
                    beep("eat")
                    break

        if all(not b['active'] for b in self.bricks):
            self.unlock_achievement("breakout_win", "Wall Breaker")
            self._handle_win()

    def _handle_life_lost(self) -> None:
        self.lives -= 1
        beep("lose")
        screen_shake(0.3, 2)
        animated_flash(C_RED)

        if self.lives == 0:
            show_popup(f"GAME OVER! Score: {self.score}", C_RED)
            self.game_over = True
        else:
            self.ball_x = float(WIDTH // 2)
            self.ball_y = float(HEIGHT - 2)
            self.ball_dy = -1
            self.paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
            time.sleep(1)

    def _handle_win(self) -> None:
        beep("win")
        show_popup("YOU WON! LEVEL CLEARED", C_GREEN)
        self.game_over = True


def play_breakout(difficulty: str = 'normal') -> dict:
    game = BreakoutGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_breakout()
