import logging
import random
import time
from typing import Optional

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
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

MOVES = ["Rock", "Paper", "Scissors", "Lizard", "Spock"]
MOVE_KEYS = ['r', 'p', 's', 'l', 'k']
MOVE_ICONS = ["👊", "✋", "✂️", "🦎", "🖖"]
MOVE_ICONS_FALLBACK = ["O", "[]", "X", "~", "^"]

WINNERS = {
    "Scissors": ["Paper", "Lizard"],
    "Paper": ["Rock", "Spock"],
    "Rock": ["Lizard", "Scissors"],
    "Lizard": ["Spock", "Paper"],
    "Spock": ["Scissors", "Rock"],
}

VERBS = {
    ("Scissors", "Paper"): "cuts",
    ("Scissors", "Lizard"): "decapitates",
    ("Paper", "Rock"): "covers",
    ("Paper", "Spock"): "disproves",
    ("Rock", "Lizard"): "crushes",
    ("Rock", "Scissors"): "crushes",
    ("Lizard", "Spock"): "poisons",
    ("Lizard", "Paper"): "eats",
    ("Spock", "Scissors"): "smashes",
    ("Spock", "Rock"): "vaporizes",
}


class RPSLSGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('rpsls', difficulty)
        self.player_wins = 0
        self.ai_wins = 0
        self.round_num = 0
        self.total_rounds = 5
        self.input_handler = get_safe_input_handler()
        self.last_result: Optional[str] = None
        self.last_detail: Optional[str] = None

    def get_ai_move(self) -> str:
        difficulty_map = {"easy": 0.3, "normal": 0.5, "hard": 0.7}
        skill = difficulty_map.get(self.difficulty, 0.5)
        if random.random() < skill:
            best = "Rock"
            score = 0
            for move in MOVES:
                beats = WINNERS[move]
                if "Rock" in beats:
                    score += 1
                if score > 0:
                    best = move
            return best
        return random.choice(MOVES)

    def resolve(self, player: str, ai: str) -> str:
        if player == ai:
            return "draw"
        if ai in WINNERS[player]:
            return "win"
        return "lose"

    def get_verb(self, winner: str, loser: str) -> str:
        return VERBS.get((winner, loser), "beats")

    def render_game(self) -> None:
        clear_screen()
        print("\n" * 1)

        lines = [
            f"{C_YELLOW}Round {self.round_num + 1}/{self.total_rounds}{C_RESET}",
            "",
            f"  {C_CYAN}You:{C_RESET} {self.player_wins}  "
            f"{C_MAGENTA}AI:{C_RESET} {self.ai_wins}",
            "",
            f"{C_WHITE}Choose your move:{C_RESET}",
            f"  {C_GREEN}R{C_RESET}ock     {C_GREEN}P{C_RESET}aper    {C_GREEN}S{C_RESET}cissors",
            f"  {C_GREEN}L{C_RESET}izard   {C_GREEN}K{C_RESET} (SpocK)",
            "",
        ]

        if self.last_result:
            color = C_GREEN if self.last_result == "win" else C_RED if self.last_result == "lose" else C_YELLOW
            lines.append(f"{color}{self.last_result.upper()}{C_RESET}")
            if self.last_detail:
                lines.append(f"  {self.last_detail}")

        draw_retro_box(38, "RPSLS", lines, color=C_CYAN)

    def show_move_result(self, player_move: str, ai_move: str,
                         result: str) -> None:
        icon = MOVE_ICONS_FALLBACK
        p_idx = MOVES.index(player_move)
        a_idx = MOVES.index(ai_move)

        lines = [
            f"{C_CYAN}You chose:{C_RESET}  {icon[p_idx]} {player_move}",
            f"{C_CYAN}AI chose:{C_RESET}   {icon[a_idx]} {ai_move}",
            "",
        ]

        if result == "win":
            verb = self.get_verb(player_move, ai_move)
            lines.append(f"{C_GREEN}{player_move} {verb} {ai_move}!{C_RESET}")
            lines.append(f"{C_GREEN}YOU WIN!{C_RESET}")
        elif result == "lose":
            verb = self.get_verb(ai_move, player_move)
            lines.append(f"{C_RED}{ai_move} {verb} {player_move}!{C_RESET}")
            lines.append(f"{C_RED}YOU LOSE!{C_RESET}")
        else:
            lines.append(f"{C_YELLOW}It's a DRAW!{C_RESET}")

        clear_screen()
        print("\n" * 3)
        draw_retro_box(34, "RESULT", lines, color=C_CYAN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()

    def show_final(self) -> None:
        clear_screen()
        print("\n" * 2)

        if self.player_wins > self.ai_wins:
            title = f"{C_GREEN}YOU WIN THE MATCH!{C_RESET}"
            self.award_xp_for_action(50)
        elif self.player_wins < self.ai_wins:
            title = f"{C_RED}AI WINS THE MATCH!{C_RESET}"
        else:
            title = f"{C_YELLOW}MATCH DRAW!{C_RESET}"

        lines = [
            title,
            "",
            f"{C_WHITE}Final Score:{C_RESET}  {C_CYAN}You:{C_RESET} {self.player_wins}  "
            f"{C_MAGENTA}AI:{C_RESET} {self.ai_wins}",
            f"{C_WHITE}XP Earned:{C_RESET} {C_MAGENTA}{self.xp_earned}{C_RESET}",
        ]
        draw_retro_box(34, "GAME OVER", lines, color=C_CYAN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()

    def play(self) -> dict:
        self.start_timer()
        self.renderer.hide_cursor()

        try:
            while self.round_num < self.total_rounds and not self.game_over:
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

                if key and key.lower() in MOVE_KEYS:
                    idx = MOVE_KEYS.index(key.lower())
                    player_move = MOVES[idx]
                    ai_move = self.get_ai_move()
                    result = self.resolve(player_move, ai_move)

                    if result == "win":
                        self.player_wins += 1
                        self.award_xp_for_action(15)
                        beep("win")
                    elif result == "lose":
                        self.ai_wins += 1
                        beep("wrong")
                    else:
                        beep("move")

                    self.last_result = result
                    self.show_move_result(player_move, ai_move, result)
                    self.round_num += 1

                time.sleep(0.05)

            self.show_final()
            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.player_wins
            self.save_stats(final_stats)
            return final_stats

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            self.renderer.show_cursor()
            return self.get_final_stats()

    def _show_help(self) -> None:
        lines = [
            "Rock-Paper-Scissors-Lizard-Spock!",
            "",
            f"{C_CYAN}Rules:{C_RESET}",
            "  ✂ Scissors cuts Paper",
            "  📄 Paper covers Rock",
            "  ✊ Rock crushes Lizard",
            "  🦎 Lizard poisons Spock",
            "  🖖 Spock smashes Scissors",
            "  ✂ Scissors decapitates Lizard",
            "  🦎 Lizard eats Paper",
            "  📄 Paper disproves Spock",
            "  🖖 Spock vaporizes Rock",
            "  ✊ Rock crushes Scissors",
            "",
            f"{C_CYAN}Controls:{C_RESET}",
            "  R=Rock  P=Paper  S=Scissors",
            "  L=Lizard  K=Spock",
            "  Q=Quit",
        ]
        draw_retro_box(36, "RPSLS HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_rpsls(difficulty: str = 'normal') -> dict:
    game = RPSLSGame(difficulty)
    return game.play()
