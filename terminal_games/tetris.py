import random
import time
from typing import Any, Dict, List

from arcade_utils import (
    C_BLACK,
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

WIDTH = 10
HEIGHT = 20

SHAPES: List[List[List[int]]] = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]]
]

COLORS = [C_CYAN, C_YELLOW, C_MAGENTA, C_WHITE, C_BLUE, C_GREEN, C_RED]


def rotate(shape: List[List[int]]) -> List[List[int]]:
    return [list(row) for row in zip(*shape[::-1])]


class TetrisGame(BaseGame):
    """Tetris game implementation using BaseGame."""

    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__("tetris", difficulty)
        self.board: List[List[int]] = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.piece = self._new_piece()
        self.next_piece = self._new_piece()
        self.level = 1
        self.fall_speed = 0.5
        self.last_fall_time = time.time()
        self.input_handler = get_safe_input_handler()

    def save_state_json(self) -> dict:
        return {
            'board': self.board,
            'piece': self.piece,
            'next_piece': self.next_piece,
            'score': self.score,
            'fall_speed': self.fall_speed,
            'last_fall_time': self.last_fall_time,
        }

    def load_state_json(self, state: dict) -> None:
        self.board = state['board']
        self.piece = state['piece']
        self.next_piece = state['next_piece']
        self.score = state['score']
        self.fall_speed = state['fall_speed']
        self.last_fall_time = time.time()

    def _new_piece(self) -> Dict[str, Any]:
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = COLORS[shape_idx]
        return {
            'shape': [row[:] for row in shape],
            'color': color,
            'x': WIDTH // 2 - len(shape[0]) // 2,
            'y': 0
        }

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        clear_screen()
        print_big_title("TETRIS", color=C_BLUE)
        time.sleep(1)

        while not self.game_over:
            self.renderer.render_frame(self._render)
            self._handle_input()
            self._update_game_state()
            self.fall_speed = max(0.1, 0.5 - (self.level * 0.05))
            time.sleep(0.05)

            if self.score >= 1000:
                self.unlock_achievement("tetris_1000", "Block Architect")

        self.end_timer()

        high_score = self.stats_manager.get_high_score('tetris')
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
        high_score = self.stats_manager.get_high_score('tetris')

        print(f"{C_BLUE}╔{'═' * (WIDTH * 2)}╗")
        print(f"║ SCORE: {self.score:<6} LVL: {self.level:<3} HI: {high_score:<6} ║")
        print(f"╚{'═' * (WIDTH * 2)}╝{C_RESET}")

        print(f"{C_BLUE}╔{'═' * (WIDTH * 2)}╗{C_RESET}  NEXT PIECE:")

        for r in range(HEIGHT):
            line = f"{C_BLUE}║{C_RESET}"
            for c in range(WIDTH):
                is_piece = False
                if (0 <= r - self.piece['y'] < len(self.piece['shape']) and
                    0 <= c - self.piece['x'] < len(self.piece['shape'][0])):
                    if self.piece['shape'][r - self.piece['y']][c - self.piece['x']]:
                        line += f"{self.piece['color']}██{C_RESET}"
                        is_piece = True
                if not is_piece:
                    val = self.board[r][c]
                    if val == 0:
                        line += f"{C_BLACK} . {C_RESET}"
                    else:
                        line += f"{val}██{C_RESET}"
            line += f"{C_BLUE}║{C_RESET}"
            if r == 1:
                nw = len(self.next_piece['shape'][0])
                line += f"  {self.next_piece['color']}{'████' if nw > 2 else '██'}{C_RESET}"
            print(line)

        print(f"{C_BLUE}╚{'═' * (WIDTH * 2)}╝{C_RESET}")
        print(f"{C_WHITE}Arrows/WASD: Move/Rotate | Q: Quit | H: Help{C_RESET}")

    def _handle_input(self) -> None:
        k = self.input_handler.get_safe_key()
        if not k:
            return
        if self._save_and_quit(k):
            return
        if k == 'p':
            self._pause_game()
        if k == 'h':
            show_popup("TETRIS: UP=Rotate, DOWN=Drop, LEFT/RIGHT=Move. Clear full rows!", C_BLUE, delay=1.5)
            return
        direction = self.input_handler.validator.validate_direction(k)
        if direction == 'up':
            rotated = rotate(self.piece['shape'])
            if not self._check_collision(rotated, (self.piece['x'], self.piece['y'])):
                self.piece['shape'] = rotated
                beep("move")
        elif direction == 'left':
            if not self._check_collision(self.piece['shape'], (self.piece['x'] - 1, self.piece['y'])):
                self.piece['x'] -= 1
                beep("move")
        elif direction == 'right':
            if not self._check_collision(self.piece['shape'], (self.piece['x'] + 1, self.piece['y'])):
                self.piece['x'] += 1
                beep("move")
        elif direction == 'down':
            if not self._check_collision(self.piece['shape'], (self.piece['x'], self.piece['y'] + 1)):
                self.piece['y'] += 1
                self.score += 1
                beep("move")

    def _update_game_state(self) -> None:
        if time.time() - self.last_fall_time > self.fall_speed:
            if not self._check_collision(self.piece['shape'], (self.piece['x'], self.piece['y'] + 1)):
                self.piece['y'] += 1
            else:
                self._lock_piece()
                self._clear_lines()
                self.piece = self.next_piece
                self.next_piece = self._new_piece()
                if self._check_collision(self.piece['shape'], (self.piece['x'], self.piece['y'])):
                    self._trigger_game_over()
            self.last_fall_time = time.time()

    def _check_collision(self, shape: List[List[int]], offset: tuple) -> bool:
        off_x, off_y = offset
        for cy, row in enumerate(shape):
            for cx, cell in enumerate(row):
                if cell:
                    target_x = off_x + cx
                    target_y = off_y + cy
                    if (target_x < 0 or target_x >= WIDTH or
                        target_y >= HEIGHT or
                        (target_y >= 0 and self.board[target_y][target_x])):
                        return True
        return False

    def _lock_piece(self) -> None:
        for cy, row in enumerate(self.piece['shape']):
            for cx, val in enumerate(row):
                if val:
                    y = self.piece['y'] + cy
                    x = self.piece['x'] + cx
                    if 0 <= y < HEIGHT:
                        self.board[y][x] = self.piece['color']

    def _clear_lines(self) -> None:
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = HEIGHT - len(new_board)

        if lines_cleared > 0:
            self.score += (100 * lines_cleared * self.level)
            self.award_xp_for_action(lines_cleared * 10)
            screen_shake(0.1 * lines_cleared, lines_cleared)
            particle_effect(char="*", color=self.piece['color'], count=10 * lines_cleared)
            beep("win")

            for _ in range(lines_cleared):
                new_board.insert(0, [0] * WIDTH)
            self.board = new_board

            if self.score // 1000 > self.level:
                self.level += 1
                show_popup(f"LEVEL UP: {self.level}", C_CYAN)

    def _trigger_game_over(self) -> None:
        beep("game_over")
        screen_shake(0.3, 2)
        animated_flash(C_RED)
        show_popup(f"GAME OVER! Score: {self.score}", C_RED)
        self.game_over = True


def play_tetris(difficulty: str = 'normal') -> dict:
    game = TetrisGame(difficulty)
    return game.play()


if __name__ == "__main__":
    play_tetris()
