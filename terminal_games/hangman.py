import logging
import random
import time
from typing import List

from arcade_utils import (
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

WORDS = [
    "python", "arcade", "retro", "terminal", "gaming", "adventure",
    "puzzle", "strategy", "rhythm", "action", "mystery", "quest",
    "dungeon", "dragon", "knight", "wizard", "potion", "sword",
    "cosmic", "nebula", "rocket", "asteroid", "galaxy", "orbit",
    "cascade", "temple", "crystal", "phoenix", "thunder", "shadow",
    "vortex", "ember", "frost", "blaze", "storm", "dynamo",
    "jigsaw", "hacker", "circuit", "binary", "pixel", "vector",
    "zenith", "voyage", "fusion", "prism", "serene", "echo",
]

HANGMAN_STAGES = [
    "",
    "  O",
    "  O\n  |",
    "  O\n /|",
    "  O\n /|\\",
    "  O\n /|\\\n / ",
    "  O\n /|\\\n / \\",
]


class HangmanGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('hangman', difficulty)
        self.word = random.choice(WORDS).upper()
        self.guessed: List[str] = []
        self.wrong_guesses: List[str] = []
        self.max_wrong = 6
        self.round = 1
        self.streak = 0

    def display_word(self) -> str:
        return " ".join(c if c in self.guessed else "_" for c in self.word)

    def is_won(self) -> bool:
        return all(c in self.guessed for c in self.word)

    def render_game(self) -> None:
        lines: list[str] = [
            f"{C_CYAN}ROUND {self.round}{C_RESET}   DIFFICULTY: {self.difficulty.upper()}",
            "",
            f"{C_YELLOW}WORD:{C_RESET}  {C_GREEN}{self.display_word()}{C_RESET}",
            "",
            f"{C_MAGENTA}HANGMAN:{C_RESET}",
        ]
        stage_lines = HANGMAN_STAGES[len(self.wrong_guesses)].split("\n")
        for line in stage_lines:
            lines.append(f"  {C_RED}{line}{C_RESET}")

        lines.append("")
        if self.wrong_guesses:
            lines.append(f"{C_RED}WRONG: {' '.join(self.wrong_guesses)}{C_RESET}")
        if self.guessed:
            correct = [c for c in self.guessed if c not in self.wrong_guesses]
            if correct:
                lines.append(f"{C_GREEN}USED: {' '.join(sorted(correct))}{C_RESET}")

        draw_retro_box(36, "GUESS THE WORD", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Enter a letter (A-Z)  [Q] Quit  [?] Help{C_RESET}")

    def save_state_json(self) -> dict:
        return {
            'word': self.word,
            'guessed': list(self.guessed),
            'wrong_guesses': list(self.wrong_guesses),
            'score': self.score,
            'round': self.round,
            'streak': self.streak,
        }

    def load_state_json(self, state: dict) -> None:
        self.word = state.get('word', random.choice(WORDS).upper())
        self.guessed = list(state.get('guessed', []))
        self.wrong_guesses = list(state.get('wrong_guesses', []))
        self.score = state.get('score', 0)
        self.round = state.get('round', 1)
        self.streak = state.get('streak', 0)

    def _show_help(self) -> None:
        show_popup(
            "HANGMAN: Guess the hidden word one letter at a time. "
            "Each wrong guess adds a body part. "
            "6 wrong guesses and you lose!",
            C_GREEN, delay=1.5
        )

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        input_handler = get_safe_input_handler()

        try:
            while not self.game_over:
                clear_screen()
                print("\n" * 1)
                self.render_game()

                if self.is_won():
                    xp = 50 + (self.max_wrong - len(self.wrong_guesses)) * 10
                    self.score += 100 + xp
                    self.award_xp_for_action(xp)
                    beep("win")
                    show_popup(f"CORRECT! The word was {self.word}", C_GREEN, delay=1.5)
                    self.streak += 1
                    if self.streak >= 3:
                        self.unlock_achievement("hangman_streak", "Hangman Streak")
                    self.unlock_achievement("hangman_first_win", "Word Detective")
                    self.round += 1
                    self.word = random.choice(WORDS).upper()
                    self.guessed = []
                    self.wrong_guesses = []
                    continue

                if len(self.wrong_guesses) >= self.max_wrong:
                    show_popup(f"GAME OVER! The word was {self.word}", C_RED, delay=2.0)
                    self.award_xp_for_action(10)
                    self.streak = 0
                    self.round += 1
                    self.word = random.choice(WORDS).upper()
                    self.guessed = []
                    self.wrong_guesses = []
                    continue

                key = input_handler.get_safe_key()
                if key and self._save_and_quit(key.lower()):
                    break
                if key == '?':
                    self._show_help()
                    continue

                if key and key.isalpha() and len(key) == 1:
                    letter = key.upper()
                    if letter in self.guessed or letter in self.wrong_guesses:
                        beep("lose")
                        continue
                    if letter in self.word:
                        self.guessed.append(letter)
                        beep("correct")
                    else:
                        self.wrong_guesses.append(letter)
                        beep("lose")

                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats


def play_hangman(difficulty: str = 'normal') -> dict:
    game = HangmanGame(difficulty)
    return game.play()
