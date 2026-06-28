"""VS Hot-Seat Mode — 2 players alternate on the same keyboard."""
import random
import time
from typing import Dict

from arcade_utils import (
    C_BOLD,
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    clear_screen,
    get_key,
)
from stats_manager import get_stats_manager


class VSMode:
    """Two players take turns playing games, competing for highest total."""

    def __init__(self, games_list: list):
        self.games = games_list[:10]
        self.scores: Dict[str, int] = {"Player 1": 0, "Player 2": 0}
        self.round = 0
        self.max_rounds = 3

    def run(self) -> None:
        clear_screen()
        print("\n" * 3)
        print(f"  {C_MAGENTA}{C_BOLD}╔═══════════════════════════════════════╗{C_RESET}")
        print(f"  {C_MAGENTA}{C_BOLD}║        VS HOT-SEAT MODE!             ║{C_RESET}")
        print(f"  {C_MAGENTA}{C_BOLD}╚═══════════════════════════════════════╝{C_RESET}")
        print()
        print(f"  {C_YELLOW}Two players. One keyboard. Three rounds.{C_RESET}")
        print(f"  {C_WHITE}Highest total score wins!{C_RESET}")
        print()
        print(f"  {C_CYAN}Player 1: WASD + SPACE{ C_RESET}")
        print(f"  {C_CYAN}Player 2: Arrow keys + ENTER{C_RESET}")
        print()
        print(f"  {C_WHITE}[ENTER] Start VS Match  |  [Q] Cancel{C_RESET}")

        while True:
            key = get_key()
            if key in ["\r", "\n", " ", "enter"]:
                break
            if key and key.lower() == "q":
                return

        for self.round in range(1, self.max_rounds + 1):
            for player in ["Player 1", "Player 2"]:
                self._player_turn(player)

        self._show_results()

    def _player_turn(self, player: str) -> None:
        clear_screen()
        print(f"\n  {C_YELLOW}VS MODE — Round {self.round}/{self.max_rounds}{C_RESET}")
        print(f"  {C_CYAN}╔═══════════════════════════════════════╗{C_RESET}")
        print(f"  {C_CYAN}║{C_RESET}  {C_BOLD}{player}'s Turn!{C_RESET}             {C_CYAN}        ║{C_RESET}")
        print(f"  {C_CYAN}║{C_RESET}  Current Scores:                     {C_CYAN}║{C_RESET}")
        p1c = C_GREEN if self.scores["Player 1"] >= self.scores["Player 2"] else C_WHITE
        score_line = (f"  P1: {p1c}{self.scores['Player 1']}{C_RESET}  "
                      f"P2: {C_CYAN}{self.scores['Player 2']}{C_RESET}")
        print(f"  {C_CYAN}║{C_RESET}{score_line}{C_CYAN}         ║{C_RESET}")
        print(f"  {C_CYAN}╚═══════════════════════════════════════╝{C_RESET}")
        print(f"\n  {C_WHITE}[ENTER] Play  |  [Q] Abort VS Mode{C_RESET}")

        while True:
            key = get_key()
            if key in ["\r", "\n", " ", "enter"]:
                break
            if key and key.lower() == "q":
                return

        print(f"\n  {C_GREEN}Playing game for {player}...{C_RESET}")
        time.sleep(0.5)

        from error_handler import safe_game_call
        result = safe_game_call(self._pick_game, "VS Game Round", difficulty="normal")

        if result:
            score = result.get("high_score", result.get("score", 0))
            self.scores[player] += score

            clear_screen()
            print(f"\n  {C_GREEN}{player} scored {score} points!{C_RESET}")
            print(f"  {C_YELLOW}Total: {self.scores[player]}{C_RESET}")
            print(f"\n  {C_WHITE}[ENTER] Next Player{C_RESET}")
            while True:
                key = get_key()
                if key in ["\r", "\n", " ", "enter"]:
                    break

    def _pick_game(self, difficulty: str = "normal") -> dict:
        """Play a random mini-challenge for VS mode."""
        challenges = [
            self._vs_tapper,
            self._vs_reflex,
            self._vs_countdown,
        ]
        game = random.choice(challenges)
        result = game()
        return result

    def _vs_tapper(self) -> dict:
        """Who can tap faster in 5 seconds."""
        clear_screen()
        print(f"\n  {C_YELLOW}TAP CHALLENGE — Press SPACE as fast as you can!{C_RESET}")
        print(f"  {C_WHITE}You have 5 seconds...{C_RESET}")
        print(f"\n  {C_GREEN}Starting in...{C_RESET}")
        for i in range(3, 0, -1):
            print(f"  {C_RED}{i}...{C_RESET}")
            time.sleep(0.5)

        print(f"  {C_GREEN}{C_BOLD}GO!{C_RESET}")
        taps = 0
        start = time.time()
        while time.time() - start < 5:
            clear_screen()
            remaining = int(5 - (time.time() - start))
            print(f"\n  {C_YELLOW}TAPS: {taps}  TIME: {remaining}s{C_RESET}")
            print(f"\n  {C_WHITE}Press SPACE as fast as you can!{C_RESET}")
            key = get_key()
            if key in [" ", "space", "\r", "\n", "enter"]:
                taps += 1
                from arcade_utils import beep
                beep("correct")
            elif key and key.lower() == "q":
                break

        score = taps * 10
        return {"score": score, "high_score": score, "xp_earned": score // 5, "duration_seconds": 5}

    def _vs_reflex(self) -> dict:
        """Quick reflex challenge."""
        clear_screen()
        print(f"\n  {C_YELLOW}REFLEX CHALLENGE — Hit the right key!{C_RESET}")
        time.sleep(1)

        score = 0
        keys = [("W", "w"), ("A", "a"), ("S", "s"), ("D", "d")]
        for _ in range(8):
            target, key_name = random.choice(keys)
            clear_screen()
            print(f"\n  {C_BOLD}{C_MAGENTA}Press: {C_YELLOW}{target}{C_RESET}")
            start = time.time()
            hit = False
            while time.time() - start < 1.0:
                k = get_key()
                if k and k.lower() == key_name:
                    score += 25
                    print(f"  {C_GREEN}HIT! +25{C_RESET}")
                    hit = True
                    break
            if not hit:
                print(f"  {C_RED}MISS!{C_RESET}")
            time.sleep(0.2)

        return {"score": score, "high_score": score, "xp_earned": score // 5, "duration_seconds": 0}

    def _vs_countdown(self) -> dict:
        """Press ENTER at exactly the right moment."""
        clear_screen()
        print(f"\n  {C_YELLOW}COUNTDOWN — Hit ENTER at 0!{C_RESET}")
        time.sleep(1)

        score = 0
        for _ in range(5):
            delay = random.uniform(2.0, 4.0)
            clear_screen()
            print(f"\n  {C_MAGENTA}Wait for it...{C_RESET}")
            start = time.time()
            while time.time() - start < delay:
                remaining = delay - (time.time() - start)
                print(f"\r  {C_CYAN}{remaining:.1f}s{C_RESET}", end="", flush=True)
                k = get_key()
                if k in ["\r", "\n", " ", "enter"]:
                    diff = time.time() - start - delay
                    if abs(diff) < 0.1:
                        score += 100
                        print(f"\n  {C_GREEN}{C_BOLD}PERFECT! +100{C_RESET}")
                    elif abs(diff) < 0.3:
                        score += 50
                        print(f"\n  {C_YELLOW}Close! +50{C_RESET}")
                    else:
                        print(f"\n  {C_RED}Way off...{C_RESET}")
                    break
                time.sleep(0.02)
            else:
                print(f"\n\n  {C_YELLOW}You waited too long!{C_RESET}")
            time.sleep(0.5)

        return {"score": score, "high_score": score, "xp_earned": score // 5, "duration_seconds": 0}

    def _show_results(self) -> None:
        clear_screen()
        p1, p2 = self.scores["Player 1"], self.scores["Player 2"]

        print(f"\n  {C_MAGENTA}{C_BOLD}╔═══════════════════════════════════════╗{C_RESET}")
        print(f"  {C_MAGENTA}{C_BOLD}║        VS MODE — RESULTS!            ║{C_RESET}")
        print(f"  {C_MAGENTA}{C_BOLD}╚═══════════════════════════════════════╝{C_RESET}")
        print()
        print(f"  {C_CYAN}Player 1:{C_RESET} {C_BOLD}{p1} points{C_RESET}")
        print(f"  {C_MAGENTA}Player 2:{C_RESET} {C_BOLD}{p2} points{C_RESET}")
        print()

        if p1 > p2:
            print(f"  {C_YELLOW}★ {C_BOLD}Player 1 WINS! ★{C_RESET}")
        elif p2 > p1:
            print(f"  {C_YELLOW}★ {C_BOLD}Player 2 WINS! ★{C_RESET}")
        else:
            print(f"  {C_GREEN}{C_BOLD}TIE!{C_RESET}")

        mgr = get_stats_manager()
        mgr.add_xp(abs(p1 - p2) * 2)
        mgr.record_session("VS Mode", p1 + p2, abs(p1 - p2) * 2, 0, "normal")

        print(f"\n  {C_WHITE}[Any Key] Continue{C_RESET}")
        get_key()


def run_vs_mode(games_list: list) -> None:
    VSMode(games_list).run()
