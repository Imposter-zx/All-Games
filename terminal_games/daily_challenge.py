"""Daily Challenge — seed-based daily mode for arcade games."""
import datetime
import hashlib
import random
from typing import Optional

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
    draw_retro_box,
    get_key,
    show_popup,
)
from stats_manager import get_stats_manager


def daily_seed() -> str:
    """Generate a consistent daily seed based on date."""
    today = datetime.date.today().isoformat()
    h = hashlib.md5(today.encode()).hexdigest()
    return h[:8]


def has_daily_played(game_name: str) -> bool:
    """Check if daily challenge already played today."""
    mgr = get_stats_manager()
    today = datetime.date.today().isoformat()
    key = f"daily_{game_name}_{today}"
    return mgr._get_profile_str(key) == "done"


def mark_daily_played(game_name: str) -> None:
    """Mark daily challenge as played for today."""
    mgr = get_stats_manager()
    today = datetime.date.today().isoformat()
    key = f"daily_{game_name}_{today}"
    mgr._set_profile_str(key, "done")


def get_daily_high_score(game_name: str) -> int:
    """Get best daily score for today."""
    mgr = get_stats_manager()
    today = datetime.date.today().isoformat()
    key = f"daily_score_{game_name}_{today}"
    return mgr._get_profile_int(key, 0)


def set_daily_high_score(game_name: str, score: int) -> None:
    """Update daily high score if better."""
    mgr = get_stats_manager()
    current = get_daily_high_score(game_name)
    if score > current:
        today = datetime.date.today().isoformat()
        key = f"daily_score_{game_name}_{today}"
        mgr._set_profile_int(key, score)


def show_daily_challenge_menu(games_list) -> Optional[str]:
    """Show daily challenge menu with today's featured game."""
    seed = daily_seed()
    rng = random.Random(seed)
    featured = rng.choice(games_list)
    featured_name = featured.replace("_", " ").title()

    already = has_daily_played(featured)
    high = get_daily_high_score(featured)

    while True:
        clear_screen()
        print("\n" * 2)
        lines = [
            f"{C_YELLOW}Daily Challenge — {datetime.date.today().strftime('%B %d, %Y')}{C_RESET}",
            "",
            f"  {C_MAGENTA}Featured Game: {C_BOLD}{featured_name}{C_RESET}",
            f"  {C_CYAN}Seed: {seed}{C_RESET}",
            "",
            f"  {C_GREEN}Best Today: {high}{C_RESET}",
            f"  {C_YELLOW}Status: {'Completed' if already else 'Not played'}{C_RESET}",
            "",
            f"  {C_WHITE}[ENTER] Play Daily Challenge{C_RESET}",
            f"  {C_WHITE}[Q] Back{C_RESET}",
        ]
        draw_retro_box(44, "DAILY CHALLENGE", lines, color=C_YELLOW)

        key = get_key()
        if key in ["\r", "\n", " ", "enter"]:
            if already:
                show_popup("Already played today! Come back tomorrow.", C_RED, delay=1.5)
                continue
            return featured
        if key and key.lower() == "q":
            return None


def show_daily_leaderboard() -> None:
    """Show daily challenge leaderboard across all games."""
    mgr = get_stats_manager()
    today = datetime.date.today().isoformat()

    clear_screen()
    print("\n" * 2)
    lines = [f"{C_YELLOW}Daily Challenge Scores — {today}{C_RESET}", ""]
    count = 0
    for game_key in ["snake", "tetris", "racing", "flappy", "blackjack", "pong"]:
        key = f"daily_score_{game_key}_{today}"
        score = mgr._get_profile_int(key, 0)
        if score > 0:
            gname = game_key.replace("_", " ").title()
            lines.append(f"  {C_GREEN}{gname:<15}{C_RESET} {C_YELLOW}{score:>8}{C_RESET}")
            count += 1
    if count == 0:
        lines.append(f"  {C_WHITE}No daily scores yet. Play today's challenge!{C_RESET}")
    lines.append("")
    lines.append(f"{C_WHITE}[Any Key] Back{C_RESET}")
    draw_retro_box(44, "DAILY LEADERBOARD", lines, color=C_CYAN)
    get_key()
