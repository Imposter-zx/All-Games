"""Game Roulette — randomly picks a game for you, weighted toward unplayed ones."""
import random
import time
from typing import Dict, List, Optional

from arcade_utils import (
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    clear_screen,
    get_key,
)
from stats_manager import get_stats_manager


def pick_roulette_game(games_list: List[str]) -> Optional[str]:
    """Pick a random game weighted by play count (less played = higher chance)."""
    mgr = get_stats_manager()
    weights: Dict[str, float] = {}

    for g in games_list:
        count = mgr.get_game_play_count(g)
        weight = 1.0 / (count + 1)
        weights[g] = weight

    total = sum(weights.values())
    if total <= 0:
        return random.choice(games_list)

    r = random.uniform(0, total)
    cumulative = 0.0
    for g in games_list:
        cumulative += weights[g]
        if r <= cumulative:
            return g
    return games_list[-1]


def show_roulette_spin(game_name: str) -> str:
    """Animated roulette spin showing the selected game."""
    display = game_name.replace("_", " ").title()

    clear_screen()
    print("\n" * 3)
    print(f"  {C_MAGENTA}╔═══════════════════════════════════════╗{C_RESET}")
    print(f"  {C_MAGENTA}║         GAME ROULETTE!               ║{C_RESET}")
    print(f"  {C_MAGENTA}╚═══════════════════════════════════════╝{C_RESET}")
    print()
    print(f"  {C_YELLOW}Spinning...{C_RESET}")

    for _ in range(10):
        placeholder = random.choice(["🐍", "🧩", "🚀", "♟️", "🏓", "🎰", "🃏", "🧠", "⬤", "📦"])
        print(f"\r  {C_CYAN}{placeholder}  ????{C_RESET}", end="", flush=True)
        time.sleep(0.08)

    icons = {
        "snake": "🐍", "tetris": "🧩", "space_shooter": "🚀", "chess": "♟️",
        "pong": "🏓", "slots": "🎰", "blackjack": "🃏", "mastermind": "🧠",
        "othello": "⬤", "sokoban": "📦",
    }
    icon = icons.get(game_name, "🎮")

    print(f"\r  {C_GREEN}{icon}  {display:<20}{C_RESET}  ")
    print()
    print(f"  {C_WHITE}[ENTER] Play Now  |  [Q] Cancel{C_RESET}")

    while True:
        key = get_key()
        if key in ["\r", "\n", " ", "enter"]:
            return game_name
        if key and key.lower() == "q":
            return None
