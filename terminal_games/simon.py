import logging
import random
import time
from typing import List

from arcade_utils import (
    C_BLUE,
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    beep,
    clear_screen,
    draw_retro_box,
    show_popup,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

COLORS = [
    (C_RED, "R", "1"),
    (C_GREEN, "G", "2"),
    (C_BLUE, "B", "3"),
    (C_YELLOW, "Y", "4"),
]
COLOR_KEYS = [c[1] for c in COLORS]
NUM_KEYS = [c[2] for c in COLORS]
COLOR_NAMES = ["Red", "Green", "Blue", "Yellow"]


class SimonGame(BaseGame):
    def __init__(self, difficulty: str = "normal") -> None:
        super().__init__("simon", difficulty)
        self.sequence: List[int] = []
        self.player_index = 0
        self.showing = False
        self.round = 1
        self.streak = 0
        self.high_round = 0
        diff_speed = {"easy": 1.2, "normal": 0.9, "hard": 0.6}
        self.speed = diff_speed.get(difficulty, 0.9)

    def _add_step(self) -> None:
        self.sequence.append(random.randint(0, 3))
        self.player_index = 0

    def _render_colors(self, highlight: int = -1) -> str:
        lines = []
        for i, (ansi, key, num) in enumerate(COLORS):
            color = ansi if i != highlight else C_WHITE
            bg = "" if i != highlight else "\033[47m"
            symbol = f"{bg}{color} {key} {C_RESET}"
            label = f"  ({num}) {COLOR_NAMES[i]}"
            lines.append(f"   {symbol} {label}")
        return "\n".join(lines)

    def _show_sequence(self) -> None:
        self.showing = True
        for step in self.sequence:
            clear_screen()
            print("\n" * 3)
            lines = [
                f"{C_CYAN}ROUND {self.round}{C_RESET}   "
                f"{C_YELLOW}Watch carefully...{C_RESET}",
                "",
            ]
            draw_retro_box(28, "SIMON SAYS", lines, color=C_MAGENTA)
            print(f"\n{self._render_colors(step)}")
            c_ansi = COLORS[step][0]
            show_popup(f"{c_ansi}●{C_RESET}", delay=self.speed)
            time.sleep(0.1)
        self.showing = False
        self.player_index = 0

    def save_state_json(self) -> dict:
        return {
            "sequence": list(self.sequence),
            "player_index": self.player_index,
            "score": self.score,
            "round": self.round,
            "streak": self.streak,
            "high_round": self.high_round,
        }

    def load_state_json(self, state: dict) -> None:
        self.sequence = list(state.get("sequence", []))
        self.player_index = state.get("player_index", 0)
        self.score = state.get("score", 0)
        self.round = state.get("round", 1)
        self.streak = state.get("streak", 0)
        self.high_round = state.get("high_round", 0)

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
                self._show_sequence()
        else:
            self._add_step()
            self._add_step()
            self._show_sequence()

        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 2)
                lines = [
                    f"{C_CYAN}ROUND {self.round}{C_RESET}   "
                    f"{C_YELLOW}SPEED: {self.speed:.1f}s{C_RESET}",
                    f"{C_WHITE}Repeat the sequence!{C_RESET}",
                    "",
                ]
                draw_retro_box(28, "SIMON SAYS", lines, color=C_MAGENTA)
                print(f"\n{self._render_colors()}")
                remaining = len(self.sequence) - self.player_index
                progress = f"{'●' * self.player_index}{'○' * remaining}"
                print(f"\n   {C_CYAN}{progress}{C_RESET}")
                print(f"\n  {C_WHITE}Press 1-4 (or R/G/B/Y) to repeat  "
                      f"[Q] Quit  [?] Help{C_RESET}")

                key = input_handler.get_safe_key()
                if not key:
                    time.sleep(0.05)
                    continue

                if self._save_and_quit(key.lower()):
                    break
                if key == "?":
                    show_popup(
                        "SIMON SAYS: Watch the color sequence, "
                        "then repeat it using 1-4 or R/G/B/Y. "
                        "Each round adds one more step!",
                        C_MAGENTA, delay=2.0,
                    )
                    continue

                choice = -1
                k = key.upper()
                if k in COLOR_KEYS:
                    choice = COLOR_KEYS.index(k)
                elif key in NUM_KEYS:
                    choice = NUM_KEYS.index(key)

                if choice >= 0:
                    expected = self.sequence[self.player_index]
                    beep("move")
                    if choice == expected:
                        self.player_index += 1
                        if self.player_index >= len(self.sequence):
                            self.round += 1
                            self.score += self.round * 10
                            self.award_xp_for_action(self.round * 5)
                            self.streak += 1
                            if self.streak >= 3:
                                self.unlock_achievement("simon_streak_3",
                                                        "Simon Streak")
                            if self.streak >= 5:
                                self.unlock_achievement("simon_streak_5",
                                                        "Memory Master")
                            self.unlock_achievement("simon_first_win",
                                                    "Simon Says Champion")
                            self._add_step()
                            self._show_sequence()
                    else:
                        beep("lose")
                        if self.round > self.high_round:
                            self.high_round = self.round
                        self.streak = 0
                        show_popup(
                            f"WRONG! You reached round {self.round}",
                            C_RED, delay=2.0,
                        )
                        self.award_xp_for_action(self.round * 2)
                        self.game_over = True
                        break

                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            final_stats["high_score"] = self.score
            self.save_stats(final_stats)
            return final_stats


def play_simon(difficulty: str = "normal") -> dict:
    game = SimonGame(difficulty)
    return game.play()
