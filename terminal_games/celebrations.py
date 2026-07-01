"""High score celebration effects."""
import random
import time

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
    screen_shake,
)
from stats_manager import get_stats_manager


def celebrate_high_score(game_name: str, score: int, prev_best: int) -> None:
    """Show a celebration effect when beating a high score."""
    if score <= prev_best:
        return

    clear_screen()
    print("\n" * 3)

    colors = [C_RED, C_YELLOW, C_GREEN, C_CYAN, C_MAGENTA, C_WHITE]
    for burst in range(3):
        color = random.choice(colors)
        print(f"  {color}{'★' * 60}{C_RESET}")
        time.sleep(0.08)

    print()
    color = C_YELLOW if score > prev_best * 2 else C_GREEN
    print(f"  {color}{C_BOLD}╔═══════════════════════════════════════╗{C_RESET}")
    print(f"  {color}{C_BOLD}║      ★★  NEW HIGH SCORE!  ★★        ║{C_RESET}")
    print(f"  {color}{C_BOLD}╚═══════════════════════════════════════╝{C_RESET}")
    print()
    print(f"  {C_WHITE}  {game_name:<20}  {color}{score:>8}{C_RESET}")
    print(f"  {C_WHITE}  Previous Best:      {C_RED}{prev_best:>8}{C_RESET}")

    improvement = score - prev_best
    if improvement > 0:
        pct = int((improvement / prev_best) * 100) if prev_best > 0 else 100
        print(f"  {C_WHITE}  Improvement:        +{C_GREEN}{improvement}{C_RESET}  ({C_YELLOW}+{pct}%{C_RESET})")

    print()
    for row in range(3):
        line_chars = []
        for _ in range(20):
            line_chars.append(random.choice(["✦", "✧", "★", "☆", "·"]))
        c = random.choice(colors)
        print(f"  {c}{' '.join(line_chars)}{C_RESET}")
        time.sleep(0.06)

    time.sleep(1.5)


def celebrate_level_up(level: int) -> None:
    """Celebration when player levels up."""
    clear_screen()
    print("\n" * 4)
    print(f"  {C_YELLOW}╔═══════════════════════════════════════╗{C_RESET}")
    print(f"  {C_YELLOW}║                                       ║{C_RESET}")
    print(f"  {C_YELLOW}║      ★  LEVEL UP!  LEVEL {level}  ★     ║{C_RESET}")
    print(f"  {C_YELLOW}║                                       ║{C_RESET}")
    print(f"  {C_YELLOW}╚═══════════════════════════════════════╝{C_RESET}")
    print()
    rewards = ["✦ New game title unlocked!", "✦ +50 XP Bonus!", "✦ Rank increased!"]
    for r in rewards:
        print(f"    {C_GREEN}{r}{C_RESET}")
    print()
    for _ in range(5):
        print(f"  {C_MAGENTA}{'✦' * 50}{C_RESET}")
        time.sleep(0.1)
    time.sleep(1.5)
    screen_shake(0.3, 1)


def check_and_celebrate(game_name: str, new_score: int, game_key: str = None) -> None:
    """Check if this is a new high score and celebrate if so."""
    if game_key is None:
        game_key = game_name.lower().replace(" ", "_")
    mgr = get_stats_manager()
    prev = mgr.get_high_score(game_key)
    if new_score > prev and new_score > 0:
        celebrate_high_score(game_name, new_score, prev)
