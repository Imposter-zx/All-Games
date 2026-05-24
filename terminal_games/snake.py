import random
import time
from typing import List, Optional, Tuple

from arcade_utils import (
    C_GREEN,
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

BOARD_WIDTH = 30
BOARD_HEIGHT = 15


def create_food(snake: List[Tuple[int, int]]) -> Tuple[int, int]:
    while True:
        food = (random.randint(1, BOARD_HEIGHT - 2), random.randint(1, BOARD_WIDTH - 2))
        if food not in snake:
            return food


class SnakeGame(BaseGame):
    """Snake game implementation using BaseGame."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("snake", difficulty)
        self.snake: List[Tuple[int, int]] = []
        self.food: Optional[Tuple[int, int]] = None
        self.direction = (0, 1)
        self.speed = 0.15
        self.input_handler = get_safe_input_handler()
        self.key_map = {
            'up': (-1, 0), 'down': (1, 0),
            'left': (0, -1), 'right': (0, 1)
        }

    def save_state_json(self) -> dict:
        return {
            'snake': self.snake,
            'food': self.food,
            'direction': self.direction,
            'speed': self.speed,
            'score': self.score,
        }

    def load_state_json(self, state: dict) -> None:
        self.snake = state['snake']
        self.food = tuple(state['food']) if state['food'] else None
        self.direction = tuple(state['direction'])
        self.speed = state['speed']
        self.score = state['score']

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("SNAKE", color=C_GREEN)
        time.sleep(1)

        self.snake = [(BOARD_HEIGHT // 2, BOARD_WIDTH // 2)]
        self.direction = (0, 1)
        self.food = create_food(self.snake)
        self.score = 0
        self.speed = 0.15

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            time.sleep(self.speed)

        self.end_timer()

        high_score = self.stats_manager.get_high_score('snake')
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
        high_score = self.stats_manager.get_high_score('snake')

        print(f"{C_YELLOW}╔{'═' * BOARD_WIDTH}╗")
        print(f"║ SCORE: {self.score:<10} HI: {high_score:<10} ║")
        print(f"╚{'═' * BOARD_WIDTH}╝{C_RESET}")

        print(f"{C_GREEN}╔{'═' * BOARD_WIDTH}╗{C_RESET}")
        for r in range(BOARD_HEIGHT):
            line = f"{C_GREEN}║{C_RESET}"
            for c in range(BOARD_WIDTH):
                if (r, c) == self.snake[0]:
                    line += f"{C_GREEN}█{C_RESET}"
                elif (r, c) in self.snake:
                    line += f"{C_GREEN}▒{C_RESET}"
                elif self.food and (r, c) == self.food:
                    line += f"{C_RED}●{C_RESET}"
                else:
                    line += " "
            line += f"{C_GREEN}║{C_RESET}"
            print(line)
        print(f"{C_GREEN}╚{'═' * BOARD_WIDTH}╝{C_RESET}")
        print(f"{C_WHITE}ARROWS/WASD: Move | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        if k == 'h':
            show_popup("SNAKE: Eat food to grow and score. Don't hit walls or yourself!", C_GREEN, delay=1.5)
            return
        direction_name = self.input_handler.validator.validate_direction(k)
        if direction_name in self.key_map:
            test_dir = self.key_map[direction_name]
            if (test_dir[0] + self.direction[0] != 0) or (test_dir[1] + self.direction[1] != 0):
                self.direction = test_dir

    def _update_game_state(self) -> None:
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if (new_head[0] < 0 or new_head[0] >= BOARD_HEIGHT or
            new_head[1] < 0 or new_head[1] >= BOARD_WIDTH or
            new_head in self.snake):
            beep("game_over")
            screen_shake(0.3, 2)
            animated_flash(C_RED)
            show_popup(f"GAME OVER! Score: {self.score}", C_RED)
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.award_xp_for_action(10)
            screen_shake(0.05, 1)
            particle_effect(char="+", color=C_GREEN, count=3)
            beep("eat")
            self.food = create_food(self.snake)

            if self.score == 100:
                self.unlock_achievement("snake_100", "Slither Master")
            elif self.score == 500:
                self.unlock_achievement("snake_500", "Python King")

            if self.score % 50 == 0:
                self.speed = max(0.05, self.speed - 0.01)
        else:
            self.snake.pop()


def play_snake(difficulty: str = 'normal') -> dict:
    game = SnakeGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_snake()
