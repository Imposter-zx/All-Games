import logging
import random
import time
from typing import List, Optional

from arcade_utils import (
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    beep,
    clear_screen,
    draw_retro_box,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

WORD_POOLS = {
    "easy": [
        "the", "cat", "dog", "run", "big", "red", "hat", "sun", "bed", "cup",
        "pen", "top", "map", "leg", "arm", "eye", "car", "bus", "sky", "sea",
        "hot", "old", "new", "fun", "toy", "box", "bee", "cow", "pig", "hen",
        "fox", "ice", "key", "lip", "mug", "net", "owl", "pot", "rat", "saw",
    ],
    "normal": [
        "apple", "house", "water", "light", "green", "table", "horse", "smile",
        "cloud", "dance", "bread", "sleep", "stone", "plant", "dream", "crane",
        "frame", "grace", "globe", "heart", "juice", "knife", "lemon", "melon",
        "night", "ocean", "piano", "queen", "river", "sugar", "tiger", "union",
        "voice", "waste", "youth", "zebra", "candy", "daisy", "eagle", "flame",
    ],
    "hard": [
        "journey", "whisper", "blanket", "capture", "diamond", "explore",
        "fortune", "glimpse", "harmony", "imagine", "justice", "kingdom",
        "liberty", "miracle", "network", "orchard", "penguin", "quarter",
        "rainbow", "silence", "trouble", "uniform", "vibrant", "whistle",
        "ancient", "bridge", "crystal", "drawer", "elastic", "fiction",
        "garden", "hollow", "insect", "jumble", "kettle", "lantern",
        "mellow", "notion", "puzzle", "rocket", "saddle", "throne",
    ],
}

DURATIONS = {"easy": 30, "normal": 45, "hard": 60}

KINDS = {"easy": "Easy Words", "normal": "Normal Words", "hard": "Hard Words"}


class TyperGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('typer', difficulty)
        self.duration = DURATIONS.get(difficulty, 45)
        self.word_pool = WORD_POOLS.get(difficulty, WORD_POOLS["normal"])
        self.current_input = ""
        self.current_word = ""
        self.word_index = 0
        self.word_list: List[str] = []
        self._generate_words()

        self.correct_chars = 0
        self.total_chars = 0
        self.correct_words = 0
        self.total_words = 0
        self.start_time: Optional[float] = None
        self.time_elapsed = 0.0
        self.input_handler = get_safe_input_handler()

    def _generate_words(self) -> None:
        self.word_list = []
        while len(self.word_list) < 100:
            self.word_list += random.sample(self.word_pool, min(20, len(self.word_pool)))
        self.current_word = self.word_list[0]

    def render_game(self) -> None:
        clear_screen()
        print("\n" * 1)

        remaining = max(0, int(self.duration - self.time_elapsed))
        wpm = 0
        if self.time_elapsed > 0:
            minutes = self.time_elapsed / 60.0
            wpm = int((self.correct_words / minutes) if minutes > 0 else 0)

        accuracy = 0
        if self.total_chars > 0:
            accuracy = int((self.correct_chars / self.total_chars) * 100)

        header = (
            f"{C_YELLOW}Time:{C_RESET} {remaining}s  "
            f"{C_GREEN}WPM:{C_RESET} {wpm}  "
            f"{C_CYAN}Accuracy:{C_RESET} {accuracy}%  "
            f"{C_WHITE}Words:{C_RESET} {self.correct_words}"
        )

        upcoming = " ".join(self.word_list[self.word_index:self.word_index + 5])
        if self.current_input:
            typed_sofar = self.current_input
        else:
            typed_sofar = ""

        lines = [
            header,
            "",
            f"{C_WHITE}Type this word:{C_RESET}",
            "",
            f"  {C_GREEN}{self.current_word}{C_RESET}",
            "",
            f"{C_YELLOW}Your input:{C_RESET}",
            f"  {C_WHITE}{typed_sofar}{C_RESET}",
            "",
            f"{C_MAGENTA}Upcoming:{C_RESET} {upcoming}",
            "",
            f"{C_WHITE}SPACE = next word   ESC = quit{C_RESET}",
        ]

        draw_retro_box(48, KINDS.get(self.difficulty, ""), lines, color=C_CYAN)

    def submit_word(self) -> None:
        self.total_words += 1
        self.total_chars += len(self.current_input)

        if self.current_input == self.current_word:
            self.correct_words += 1
            self.correct_chars += len(self.current_input)
            beep("correct")
        else:
            beep("wrong")

        self.word_index += 1
        if self.word_index >= len(self.word_list):
            self._generate_words()
        self.current_word = self.word_list[self.word_index]
        self.current_input = ""

    def show_results(self) -> None:
        clear_screen()
        print("\n" * 2)

        minutes = max(0.1, self.time_elapsed) / 60.0
        wpm = int(self.correct_words / minutes) if minutes > 0 else 0
        accuracy = 0
        if self.total_chars > 0:
            accuracy = int((self.correct_chars / self.total_chars) * 100)

        lines = [
            f"{C_GREEN}Time's up!{C_RESET}",
            "",
            f"{C_WHITE}WPM:{C_RESET}      {C_YELLOW}{wpm}{C_RESET}",
            f"{C_WHITE}Accuracy:{C_RESET}  {accuracy}%",
            f"{C_WHITE}Words:{C_RESET}     {self.correct_words}/{self.total_words}",
            f"{C_WHITE}Score:{C_RESET}     {C_YELLOW}{self.score}{C_RESET}",
            f"{C_WHITE}XP Earned:{C_RESET} {C_MAGENTA}{self.xp_earned}{C_RESET}",
        ]
        draw_retro_box(36, "TYPING RESULTS", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()

    def play(self) -> dict:
        self.start_timer()
        self.renderer.hide_cursor()

        try:
            while not self.game_over:
                self.render_game()
                key = self.input_handler.get_safe_key()

                if key and self._save_and_quit(key.lower()):
                    break
                if key == '?':
                    self._show_help()
                    continue
                if key == 'p':
                    self._pause_game()
                    continue

                if self.start_time is None:
                    if key and len(key) == 1 and key.isalpha():
                        self.start_time = time.time()

                if self.start_time:
                    self.time_elapsed = time.time() - self.start_time
                    if self.time_elapsed >= self.duration:
                        self.end_timer()
                        self._score_and_show()
                        break

                if key == ' ':
                    if self.current_input:
                        self.submit_word()
                elif key == '\b' or key == '\x7f':
                    if self.current_input:
                        self.current_input = self.current_input[:-1]
                elif key and len(key) == 1 and key.isalpha():
                    self.current_input += key.lower()

                time.sleep(0.02)

            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            self.renderer.show_cursor()
            return self.get_final_stats()

    def _score_and_show(self) -> None:
        minutes = max(0.1, self.time_elapsed) / 60.0
        wpm = int(self.correct_words / minutes) if minutes > 0 else 0
        accuracy = 0
        if self.total_chars > 0:
            accuracy = int((self.correct_chars / self.total_chars) * 100)

        self.score = wpm * accuracy
        base_xp = max(10, wpm * accuracy // 10)
        self.award_xp_for_action(base_xp)

        self.show_results()
        self.game_over = True

    def _show_help(self) -> None:
        lines = [
            "Type as many words as you can",
            "before time runs out!",
            "",
            f"{C_CYAN}Controls:{C_RESET}",
            "  A-Z     Type the word",
            "  SPACE   Submit current word",
            "  BKSP    Delete last character",
            "  Q       Quit",
            "  P       Pause",
            "",
            f"{C_CYAN}Scoring:{C_RESET}",
            "  Score = WPM x Accuracy%",
            "  Faster and more accurate",
            "  = higher score!",
            "",
            f"{C_CYAN}Time:{C_RESET}",
            "  Easy:   30 seconds",
            "  Normal: 45 seconds",
            "  Hard:   60 seconds",
        ]
        draw_retro_box(36, "TYPER HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_typer(difficulty: str = 'normal') -> dict:
    game = TyperGame(difficulty)
    return game.play()
