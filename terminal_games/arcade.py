import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import time
from typing import Optional

from arcade_utils import (
    C_BLACK,
    C_BOLD,
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    THEMES,
    Renderer,
    apply_theme,
    beep,
    check_terminal_size,
    clear_screen,
    draw_retro_box,
    get_terminal_size,
    show_popup,
    u_safe,
)
from error_handler import safe_game_call
from input_handler import get_safe_input_handler
from logger_setup import setup_logger
from sound_engine import start_background_music, stop_background_music
from stats_manager import get_stats_manager

logger = setup_logger()

import online_leaderboard as olb
from asteroids import play_asteroids
from battleship import play_battleship
from blackjack import play_blackjack
from breakout import play_breakout

try:
    from chess_game import play_chess
except ImportError:
    play_chess = None
from connect_four import play_connect_four
from crossword import play_crossword

try:
    from dungeon import play_dungeon
except ImportError:
    play_dungeon = None
from flappy import play_flappy
from frogger import play_frogger
from game_2048 import play_2048
from hangman import play_hangman
from hanoi import play_hanoi
from memory import play_memory
from minesweeper import play_minesweeper
from pacman import play_pacman
from pong import play_pong
from racing import play_racing
from rpsls import play_rpsls
from simon import play_simon
from slots import play_slots
from snake import play_snake
from solitaire import play_solitaire
from space_shooter import play_space_shooter
from sudoku import play_sudoku
from tetris import play_tetris
from tictactoe import play_tictactoe
from trivia import play_trivia
from typer import play_typer
from wordle import play_wordle

BANNER_TEXT: list[str] = [
    "  ____  _  _  ____  _   _  _____  _   _  ",
    " |  _ \\| || ||_  _|| | | ||  _  || \\ | | ",
    " |  __/| \\/ |  ||  | |_| || |_| ||  \\| | ",
    " |_|    \\__/   |_|  \\___/ |_| |_||_|\\__| ",
    "  _____  ____  ____  __  ____  ____  ____",
    " |  _  ||  _ \\|  _ \\|  ||  _ \\|  __||_  _|",
    " | |_| ||  _/| |  | \\__/|  _/|  __|  ||  ",
    " |_| |_||_|  |_|__| |__| |_|  |____| |_| ",
    "                                         ",
    "       --- RETRO ARCADE SYSTEM ---       "
]

GAMES: list[str] = [
    "snake", "breakout", "space_shooter", "tetris", "pacman",
    "dungeon", "minesweeper", "chess", "sudoku", "2048",
    "pong", "asteroids", "frogger", "flappy", "racing",
    "blackjack", "connect_four", "hangman", "wordle", "tictactoe",
    "simon", "trivia", "typer", "slots", "memory", "battleship", "crossword", "hanoi", "solitaire", "rpsls"
]


def _format_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{h}h{m}m"
    return f"{m}m{s}s" if m else f"{s}s"


def draw_profile() -> None:
    """Render the high-score and XP profile."""
    mgr = get_stats_manager()
    settings = mgr.get_settings()
    player_name = settings.get('player_name', 'RETRO_MASTER')
    term_width, _ = get_terminal_size()
    box_width = min(50, term_width - 4)

    total_score = 0
    total_played = 0
    for game in GAMES:
        total_score += mgr.get_high_score(game)
        total_played += mgr.get_game_play_count(game)

    level, xp, progress = mgr.get_level_and_xp()
    achievements = mgr.get_unlocked_achievements()
    bar_width = 20
    filled = int(progress * bar_width)
    xp_bar = f"[{C_GREEN}{u_safe('█', '#') * filled}{C_BLACK}{u_safe('░', '-') * (bar_width - filled)}{C_WHITE}]"
    level_bar = f"[{C_YELLOW}{u_safe('★', '*') * (level % 5)}{C_WHITE}]"

    total_time = sum(mgr.get_game_total_time(g) for g in GAMES)

    profile_lines: list[str] = [
        f"LV:{level} {level_bar} XP:{xp} {xp_bar}",
        f"{u_safe('🏆', 'A')} {len(achievements)}ach  {u_safe('🎯', 'S')} {total_score}pts  "
        f"{u_safe('🕹️', 'G')} {total_played}plays  {u_safe('⏱️', 'T')} {_format_time(total_time)}",
        u_safe("══════════════════════════════", "------------------------------"),
    ]

    game_entries = [
        ("snake", u_safe("🐍", "S")),
        ("breakout", u_safe("🧱", "B")),
        ("space_shooter", u_safe("🚀", "X")),
        ("tetris", u_safe("🧩", "T")),
        ("pacman", u_safe("🟡", "P")),
        ("dungeon", u_safe("⚔️", "D")),
        ("minesweeper", u_safe("💣", "M")),
        ("chess", u_safe("♟️", "C")),
        ("sudoku", u_safe("🔢", "#")),
        ("2048", u_safe("🔢", "2")),
        ("pong", u_safe("🏓", "O")),
        ("asteroids", u_safe("☄️", "A")),
        ("frogger", u_safe("🐸", "F")),
        ("flappy", u_safe("🐦", "V")),
        ("racing", u_safe("🏎️", "R")),
        ("blackjack", u_safe("🃏", "B")),
        ("connect_four", u_safe("🔴", "C")),
        ("hangman", u_safe("📝", "H")),
        ("wordle", u_safe("🔤", "W")),
        ("tictactoe", u_safe("❌", "T")),
        ("simon", u_safe("🎨", "S")),
    ]

    for gname, icon in game_entries:
        hs = mgr.get_high_score(gname)
        pc = mgr.get_game_play_count(gname)
        gt = _format_time(mgr.get_game_total_time(gname))
        profile_lines.append(f"{icon} {hs:>6}  {pc:>2}pl  {gt}")

    if achievements:
        from achievements_config import get_achievement
        recent_ids = achievements[-2:]
        ach_names = [get_achievement(aid)['name'] for aid in recent_ids if get_achievement(aid)]
        if ach_names:
            profile_lines.append(u_safe("══════════════════════════════", "------------------------------"))
            profile_lines.append(f"RECENT: {', '.join(ach_names)}")

    draw_retro_box(box_width, f"{u_safe('👤', '')} {player_name}", profile_lines, color=C_WHITE, title_color=C_CYAN)


def print_menu(selection: int, renderer: Renderer) -> None:
    """Render the main arcade menu, adapting to terminal size."""
    term_width, _ = get_terminal_size()
    use_compact = term_width < 70

    for line in BANNER_TEXT:
        print(" " * max(0, (term_width - 45) // 2) + f"{C_CYAN}{line}{C_RESET}")
    print("\n")

    draw_profile()
    print("\n")

    if use_compact:
        options: list[str] = [
            "1.Snake  2.Breakout  3.Shooter  4.Tetris",
            "5.Pac-Man 6.Dungeon  7.Mineswp  8.Chess",
            "9.Sudoku  10.2048   11.Pong   12.Asteroid",
            "13.Frogger 14.Flappy 15.Racing 16.Blackjack",
            "17.Connect4 18.Hangman 19.Wordle 20.TTT 21.Simon",
            "L.Leaderboard  S.Settings  H.Help  Q.Quit",
        ]
        menu_cols = 30
    else:
        options: list[str] = [
            f"1. {u_safe('🐍', 'S')} Snake",
            f"2. {u_safe('🧱', 'B')} Breakout",
            f"3. {u_safe('🚀', 'X')} Space Shooter",
            f"4. {u_safe('🧩', 'T')} Tetris",
            f"5. {u_safe('🟡', 'P')} Pacman",
            f"6. {u_safe('⚔️', 'D')} Dungeon Crawler",
            f"7. {u_safe('💣', 'M')} Minesweeper",
            f"8. {u_safe('♟️', 'C')} Chess vs AI",
            f"9. {u_safe('🔢', '#')} Sudoku",
            f"10. {u_safe('🔢', '2')} 2048",
            f"11. {u_safe('🏓', 'O')} Pong",
            f"12. {u_safe('☄️', 'A')} Asteroids",
            f"13. {u_safe('🐸', 'F')} Frogger",
            f"14. {u_safe('🐦', 'V')} Flappy Bird",
            f"15. {u_safe('🏎️', 'R')} Racing",
            f"16. {u_safe('🃏', 'B')} Blackjack",
            f"17. {u_safe('🔴', 'C')} Connect Four",
            f"18. {u_safe('📝', 'H')} Hangman",
            f"19. {u_safe('🔤', 'W')} Wordle",
            f"20. {u_safe('❌', 'T')} Tic-Tac-Toe",
            f"21. {u_safe('🎨', 'S')} Simon Says",
            f"L. {u_safe('🏆', 'L')} Leaderboard",
            f"S. {u_safe('⚙️', 'S')} Settings",
            "H. Tutorial",
            f"Q. {u_safe('🚪', 'Q')} Quit"
        ]
        menu_cols = 30

    menu_content: list[str] = []
    for i, opt in enumerate(options):
        is_sel = (i == selection)
        prefix = f"{C_YELLOW}► {C_RESET}" if is_sel else "  "
        style = "\033[47;30m" if is_sel else f"{C_WHITE}"
        menu_content.append(f"{prefix}{style} {opt:<20} {C_RESET}")

    draw_retro_box(menu_cols, "🕹️ GAME MENU", menu_content, color=C_CYAN)
    print("\n" + " " * max(0, (term_width - 36) // 2) + f"{C_WHITE}Use Arrows to navigate, Enter to play{C_RESET}")


def select_game_difficulty() -> Optional[str]:
    """Let player choose difficulty before game starts."""
    from arcade_utils import C_RESET, C_YELLOW, clear_screen, draw_retro_box, get_key

    difficulties = ['EASY', 'NORMAL', 'HARD']
    selection = 1

    while True:
        clear_screen()
        print("\n" * 2)

        diff_lines: list[str] = []
        for i, diff in enumerate(difficulties):
            marker = "→ " if i == selection else "  "
            style = f"{C_YELLOW}{C_BOLD}" if i == selection else f"{C_WHITE}"
            diff_lines.append(f"{marker}{style}{diff:<10}{C_RESET}")

        draw_retro_box(30, "⚙️ SELECT DIFFICULTY", diff_lines, color=C_YELLOW)
        print("\n" + " " * 25 + f"{C_WHITE}[UP/DOWN] Select  [ENTER] Start  [Q] Back{C_RESET}")

        key = get_key()
        if key == 'up':
            selection = (selection - 1) % len(difficulties)
            beep("correct")
        elif key == 'down':
            selection = (selection + 1) % len(difficulties)
            beep("correct")
        elif key in ['\r', '\n', ' ', 'enter']:
            beep("win")
            return difficulties[selection].lower()
        elif key and key.lower() == 'q':
            return None
        time.sleep(0.05)


def show_online_leaderboard() -> None:
    """Display online (global) leaderboard."""
    from arcade_utils import get_key

    clear_screen()
    print("\n" * 2)

    if not olb.health_check():
        lines = [f"{C_RED}Online leaderboard unavailable.{C_RESET}",
                 f"{C_WHITE}The server may be offline or your{C_RESET}",
                 f"{C_WHITE}internet connection is down.{C_RESET}"]
        draw_retro_box(40, "🌐 ONLINE LEADERBOARD", lines, color=C_RED)
        print("\n" + " " * 28 + f"{C_WHITE}[Any Key] Back{C_RESET}")
        get_key()
        return

    entries = olb.fetch_leaderboard(limit=20)
    if not entries:
        lines = [f"{C_YELLOW}No scores submitted yet!{C_RESET}",
                 f"{C_WHITE}Play a game and your score will{C_RESET}",
                 f"{C_WHITE}automatically upload.{C_RESET}"]
        draw_retro_box(40, "🌐 ONLINE LEADERBOARD", lines, color=C_YELLOW)
    else:
        lines: list[str] = []
        for e in entries:
            rank = e['rank']
            medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f"{rank:>2}.")
            name = e['player_name'][:12]
            score = e['score']
            game = e.get('game_name', '')
            entry = f"{medal} {C_GREEN}{name:<10}{C_RESET}:{C_YELLOW}{score:>6}{C_RESET} {C_CYAN}{game:<10}{C_RESET}"
            lines.append(entry)
        draw_retro_box(40, "🌐 GLOBAL HALL OF FAME", lines, color=C_YELLOW)
    print("\n" + " " * 28 + f"{C_WHITE}[Any Key] Back{C_RESET}")
    get_key()


def show_leaderboard() -> None:
    """Display high scores (local or online)."""
    from arcade_utils import get_key
    mgr = get_stats_manager()

    while True:
        lines: list[str] = []
        for game in GAMES:
            score = mgr.get_high_score(game)
            lines.append(f"{game.replace('_', ' ').title():<15} : {C_YELLOW}{score:>6}{C_RESET}")

        clear_screen()
        print("\n" * 2)
        draw_retro_box(40, "🏆 ARCADE HALL OF FAME", lines, color=C_YELLOW)
        print("\n" + " " * 24 + f"{C_WHITE}[O] Online  [Any Key] Back{C_RESET}")

        key = get_key()
        if key and key.lower() == 'o':
            show_online_leaderboard()
        else:
            break


def show_settings() -> None:
    """Menu to change arcade settings."""
    from arcade_utils import get_key
    mgr = get_stats_manager()

    while True:
        settings = mgr.get_settings()
        sound = "ON" if settings.get('sound_enabled', True) else "OFF"
        name = settings.get('player_name', 'RETRO_MASTER')
        theme = settings.get('theme', 'classic').upper()

        lines: list[str] = [
            f"1. Sound Effects : {C_YELLOW}{sound}{C_RESET}",
            f"2. Player Name   : {C_CYAN}{name}{C_RESET}",
            f"3. Visual Theme  : {C_GREEN}{theme}{C_RESET}",
            " ",
            "Q. Back to Menu"
        ]

        clear_screen()
        print("\n" * 2)
        draw_retro_box(40, "⚙️ SYSTEM SETTINGS", lines, color=C_WHITE)

        key = get_key()
        if key == '1':
            settings['sound_enabled'] = not settings.get('sound_enabled', True)
            mgr.set_setting('sound_enabled', str(settings['sound_enabled']))
            mgr.save()
            beep("correct")
        elif key == '2':
            clear_screen()
            print("\n" * 5)
            print(" " * 25 + f"{C_WHITE}ENTER NEW NAME: {C_RESET}", end="", flush=True)
            new_name = input().strip().upper()[:12]
            if new_name:
                settings['player_name'] = new_name
                mgr.set_setting('player_name', new_name)
                mgr.save()
            beep("win")
        elif key == '3':
            theme_names = list(THEMES.keys())
            current = settings.get('theme', 'classic')
            idx = theme_names.index(current) if current in theme_names else 0
            new_theme = theme_names[(idx + 1) % len(theme_names)]
            mgr.set_setting('theme', new_theme)
            mgr.save()
            apply_theme()
            beep("correct")
        elif key and key.lower() == 'q':
            break


def show_tutorial() -> None:
    """Display interactive tutorial overlay."""
    from arcade_utils import get_key
    clear_screen()
    tutorial_lines: list[str] = [
        "",
        f"{C_BOLD}{C_YELLOW}RETRO TERMINAL ARCADE - QUICK TUTORIAL{C_RESET}",
        "",
        f"{C_CYAN}NAVIGATION:{C_RESET}",
        "  ARROW KEYS or WASD  - Move / Navigate menus",
        "  ENTER / SPACE       - Select / Confirm",
        "  Q                   - Quit game / Go back",
        "  H                   - Show this help (in-game)",
        "",
        f"{C_CYAN}DIFFICULTY:{C_RESET}",
        "  EASY   - 0.5x XP, slower gameplay",
        "  NORMAL - 1.0x XP, balanced",
        "  HARD   - 2.0x XP, faster, more challenging",
        "",
        f"{C_CYAN}XP & LEVELING:{C_RESET}",
        "  Gain XP across ALL games to level up.",
        "  Higher level = higher rank display.",
        "  Difficulty multiplies XP earned.",
        "",
        f"{C_CYAN}ACHIEVEMENTS:{C_RESET}",
        "  Earn achievements for milestones.",
        "  Each achievement grants bonus XP.",
        "",
        f"{C_CYAN}SETTINGS:{C_RESET}",
        "  Press S in main menu to change:",
        "  - Sound ON/OFF",
        "  - Player Name",
        "  - Visual Theme (Classic/Neon/Retro/Monochrome/Matrix)",
        "",
        f"{C_CYAN}GAMES ({len(GAMES)} total):{C_RESET}",
        "  Snake, Breakout, Space Shooter, Tetris, Pac-Man,",
        "  Dungeon Crawler, Minesweeper, Chess, Sudoku, 2048,",
        "  Pong, Asteroids, Frogger, Flappy Bird, Racing,",
        "  Blackjack, Connect Four, Hangman, Wordle, Tic-Tac-Toe,",
        "  Simon Says, Trivia, Typer, Slots, Memory, Battleship, Crossword, Hanoi, Solitaire, RPSLS",
        "",
        f"{C_WHITE}Press any key to return to menu...{C_RESET}"
    ]
    for line in tutorial_lines:
        print(line)
    get_key()


def show_shortcuts() -> None:
    """Display keyboard shortcuts reference."""
    from arcade_utils import get_key
    clear_screen()
    print("\n" * 1)
    lines: list[str] = [
        f"{C_BOLD}{C_YELLOW}ARCADE KEYBOARD SHORTCUTS{C_RESET}",
        "",
        f"{C_CYAN}ARCADE MENU{C_RESET}",
        f"  {C_GREEN}1-30{C_RESET}          Quick-select game by number",
        f"  {C_GREEN}UP/DOWN{C_RESET}       Navigate menu",
        f"  {C_GREEN}ENTER{C_RESET}          Launch selected game",
        f"  {C_GREEN}A{C_RESET}              View achievements",
        f"  {C_GREEN}R{C_RESET}              View recent activity",
        f"  {C_GREEN}L{C_RESET}              Open leaderboard (local + online)",
        f"  {C_GREEN}S{C_RESET}              Open settings",
        f"  {C_GREEN}H / ?{C_RESET}          Show this help",
        f"  {C_GREEN}Q{C_RESET}              Quit arcade",
        "",
        f"{C_CYAN}IN-GAME (universal){C_RESET}",
        f"  {C_GREEN}Q{C_RESET}              Quit (saves progress, resume later)",
        f"  {C_GREEN}H / ?{C_RESET}          Show game-specific help",
        f"  {C_GREEN}ARROWS / WASD{C_RESET}  Move / Navigate",
        f"  {C_GREEN}ENTER / SPACE{C_RESET}  Confirm / Select",
        "",
        f"{C_CYAN}GAMES ({len(GAMES)} total){C_RESET}",
        "  1-Snake  2-Breakout  3-Shooter  4-Tetris  5-Pac-Man",
        "  6-Dungeon  7-Minesweeper  8-Chess  9-Sudoku  10-2048",
        "  11-Pong  12-Asteroids  13-Frogger  14-Flappy  15-Racing",
        "  16-Blackjack  17-Connect Four  18-Hangman  19-Wordle  20-TTT",
        "  21-Simon  22-Trivia  23-Slots  24-Memory  25-Battleship",
        "  26-Crossword  27-Hanoi  28-Typer",
        "  29-Solitaire  30-RPSLS",
        "",
        f"{C_WHITE}Press any key to return...{C_RESET}",
    ]
    for line in lines:
        print(line)
    get_key()


def show_achievements() -> None:
    """Display all achievements with unlock status."""
    from achievements_config import ACHIEVEMENTS
    from arcade_utils import get_key
    mgr = get_stats_manager()
    unlocked = set(mgr.get_unlocked_achievements())

    # Group achievements by game
    groups: dict = {}
    for aid, ach in ACHIEVEMENTS.items():
        group = "General"
        for g in GAMES:
            if aid.startswith(g):
                group = g.replace("_", " ").title()
                break
        groups.setdefault(group, []).append((aid, ach))

    clear_screen()
    print("\n" * 1)

    total = len(ACHIEVEMENTS)
    page = 0
    per_page = 14

    while True:
        clear_screen()
        print("\n" * 1)

        ordered = sorted(groups.items())
        lines: list[str] = []
        count = 0
        start = page * per_page
        end = start + per_page

        for group_name, achs in ordered:
            if count >= end:
                break
            for aid, ach in achs:
                if count < start:
                    count += 1
                    continue
                if count >= end:
                    break
                status = f"{C_GREEN}✓{C_RESET}" if aid in unlocked else f"{C_RED}✗{C_RESET}"
                lines.append(f" {status} {ach['name']:<18} {C_YELLOW}{ach['xp']:>4}xp{C_RESET}")
                count += 1
            if count < end and count >= start:
                lines.append("")

        if total > per_page:
            pages = (total + per_page - 1) // per_page
            lines.append(f"{C_CYAN}Page {page + 1}/{pages}  [← →] Navigate{C_RESET}")
        lines.append(f"{C_WHITE}[Any Key] Back  {C_GREEN}{len(unlocked)}/{total} unlocked{C_RESET}")

        draw_retro_box(min(50, get_terminal_size()[0] - 4), "ACHIEVEMENTS", lines, color=C_YELLOW)

        key = get_key()
        if key in ["left"] and page > 0:
            page -= 1
        elif key in ["right"] and (page + 1) * per_page < total:
            page += 1
        else:
            break


def show_recent_activity() -> None:
    """Display recent play sessions."""
    from arcade_utils import get_key
    mgr = get_stats_manager()
    sessions = mgr.get_recent_sessions(10)

    clear_screen()
    print("\n" * 1)

    if not sessions:
        lines = [f"{C_YELLOW}No games played yet!{C_RESET}",
                 "", f"{C_WHITE}Play a game to see your activity here.{C_RESET}"]
        draw_retro_box(40, "RECENT ACTIVITY", lines, color=C_YELLOW)
        print(f"\n{C_WHITE}[Any Key] Back{C_RESET}")
        get_key()
        return

    lines: list[str] = []
    for s in sessions:
        gname = s.get('game_name', '').replace('_', ' ').title()[:12]
        score = s.get('score', 0)
        xp = s.get('xp_earned', 0)
        dur = int(s.get('duration_seconds', 0))
        diff = s.get('difficulty', 'normal').upper()[:4]
        m, sec = divmod(dur, 60)
        time_str = f"{m}m{sec}s" if m else f"{sec}s"
        lines.append(
            f"{C_CYAN}{gname:<12}{C_RESET} "
            f"{C_GREEN}{score:>6}{C_RESET} "
            f"{C_YELLOW}{xp:>4}xp{C_RESET} "
            f"{C_WHITE}{time_str:>6}{C_RESET} "
            f"{C_MAGENTA}{diff:>4}{C_RESET}"
        )

    draw_retro_box(min(50, get_terminal_size()[0] - 4), "RECENT ACTIVITY", lines, color=C_CYAN)
    print(f"\n{C_WHITE}[Any Key] Back{C_RESET}")
    get_key()


def _check_saved_state(game_name: str) -> None:
    """Prompt to resume if a saved state exists, otherwise start fresh."""
    mgr = get_stats_manager()
    if mgr.has_game_state(game_name):
        from arcade_utils import clear_screen, draw_retro_box, get_key
        clear_screen()
        print("\n" * 5)
        draw_retro_box(40, "SAVED GAME FOUND", [
            f"Resume your saved {game_name} game?",
            "",
            f"{C_GREEN}[ENTER] Resume{C_RESET}",
            f"{C_RED}[Q] Start Fresh{C_RESET}",
        ], color=C_YELLOW)
        while True:
            key = get_key()
            if key in ['\r', '\n', ' ']:
                return
            if key and key.lower() == 'q':
                mgr.delete_game_state(game_name)
                return


def _show_game_summary(result: dict, game_name: str, diff: str) -> None:
    from arcade_utils import get_key
    score = result.get('high_score', result.get('score', 0))
    xp = result.get('xp_earned', 0)
    dur = result.get('duration_seconds', 0)
    mgr = get_stats_manager()
    high = mgr.get_high_score(game_name.lower().replace(' ', '_').replace('-', '_'))
    lines = [
        f"{C_YELLOW}SCORE     :{C_RESET} {C_GREEN}{score}{C_RESET}",
        f"{C_YELLOW}XP EARNED :{C_RESET} {C_MAGENTA}{xp}{C_RESET}",
        f"{C_YELLOW}TIME      :{C_RESET} {C_WHITE}{dur // 60}m {dur % 60}s{C_RESET}",
        f"{C_YELLOW}BEST      :{C_RESET} {C_CYAN}{high}{C_RESET}",
        "",
        f"{C_WHITE}[Any Key] Continue{C_RESET}",
    ]
    draw_retro_box(36, f"GAME SUMMARY — {game_name.upper()}", lines, color=C_GREEN)
    get_key()


def _play_and_submit(game_func, game_name: str, difficulty: Optional[str]) -> None:
    """Play a game and submit score to online leaderboard."""
    mgr = get_stats_manager()
    _check_saved_state(game_name)
    result = safe_game_call(game_func, game_name, difficulty=difficulty)
    if result:
        clear_screen()
        print("\n" * 2)
        _show_game_summary(result, game_name, difficulty or 'normal')
    if result and result.get('high_score', 0) > 0:
        name = mgr.get_settings().get('player_name', 'RETRO_MASTER')
        olb.submit_score(name, game_name, result['high_score'], difficulty or 'normal')


def main() -> None:
    """Application entry point."""
    if os.name == 'nt':
        os.system('')
    if not check_terminal_size(60, 15):
        clear_screen()
        print(f"{C_RED}Terminal too small! Minimum 60x15 required.{C_RESET}")
        print(f"{C_YELLOW}Resize your terminal and restart.{C_RESET}")
        input(f"\n{C_WHITE}Press ENTER to continue anyway...{C_RESET}")
    selection = 0
    num_options = 34

    renderer = Renderer(fps=60)
    input_handler = get_safe_input_handler()

    # Record app start telemetry
    mgr = get_stats_manager()
    mgr.record_telemetry('app_start', 'arcade')

    # Start background music
    start_background_music(bpm=120)

    while True:
        renderer.render_frame(lambda: print_menu(selection, renderer))
        key = input_handler.get_safe_key()

        if key == 'up':
            selection = (selection - 1) % num_options
            beep("move")
        elif key == 'down':
            selection = (selection + 1) % num_options
            beep("move")
        elif key in ['\r', '\n', ' ']:
            beep("win")
            stop_background_music()

            difficulty: Optional[str] = None
            if selection < 30:
                difficulty = select_game_difficulty()
                if not difficulty:
                    start_background_music()
                    continue

            if selection == 0:
                _play_and_submit(play_snake, "Snake", difficulty)
            elif selection == 1:
                _play_and_submit(play_breakout, "Breakout", difficulty)
            elif selection == 2:
                _play_and_submit(play_space_shooter, "Space Shooter", difficulty)
            elif selection == 3:
                _play_and_submit(play_tetris, "Tetris", difficulty)
            elif selection == 4:
                _play_and_submit(play_pacman, "Pac-Man", difficulty)
            elif selection == 5:
                if play_dungeon:
                    _play_and_submit(play_dungeon, "Dungeon Crawler", difficulty)
                else:
                    show_popup("Dungeon module missing!", C_RED)
            elif selection == 6:
                _play_and_submit(play_minesweeper, "Minesweeper", difficulty)
            elif selection == 7:
                if play_chess:
                    _play_and_submit(play_chess, "Chess", difficulty)
                else:
                    show_popup("Chess (python-chess) missing!", C_RED)
            elif selection == 8:
                _play_and_submit(play_sudoku, "Sudoku", difficulty)
            elif selection == 9:
                _play_and_submit(play_2048, "2048", difficulty)
            elif selection == 10:
                _play_and_submit(play_pong, "Pong", difficulty)
            elif selection == 11:
                _play_and_submit(play_asteroids, "Asteroids", difficulty)
            elif selection == 12:
                _play_and_submit(play_frogger, "Frogger", difficulty)
            elif selection == 13:
                _play_and_submit(play_flappy, "Flappy Bird", difficulty)
            elif selection == 14:
                _play_and_submit(play_racing, "Racing", difficulty)
            elif selection == 15:
                _play_and_submit(play_blackjack, "Blackjack", difficulty)
            elif selection == 16:
                _play_and_submit(play_connect_four, "Connect Four", difficulty)
            elif selection == 17:
                _play_and_submit(play_hangman, "Hangman", difficulty)
            elif selection == 18:
                _play_and_submit(play_wordle, "Wordle", difficulty)
            elif selection == 19:
                _play_and_submit(play_tictactoe, "Tic-Tac-Toe", difficulty)
            elif selection == 20:
                _play_and_submit(play_simon, "Simon Says", difficulty)
            elif selection == 21:
                _play_and_submit(play_trivia, "Trivia", difficulty)
            elif selection == 22:
                _play_and_submit(play_slots, "Slots", difficulty)
            elif selection == 23:
                _play_and_submit(play_memory, "Memory", difficulty)
            elif selection == 24:
                _play_and_submit(play_battleship, "Battleship", difficulty)
            elif selection == 25:
                if play_crossword:
                    _play_and_submit(play_crossword, "Crossword", difficulty)
                else:
                    show_popup("Crossword module missing!", C_RED)
            elif selection == 26:
                _play_and_submit(play_hanoi, "Tower of Hanoi", difficulty)
            elif selection == 27:
                _play_and_submit(play_typer, "Typer", difficulty)
            elif selection == 28:
                _play_and_submit(play_solitaire, "Solitaire", difficulty)
            elif selection == 29:
                _play_and_submit(play_rpsls, "RPSLS", difficulty)
            elif selection == 30:
                show_leaderboard()
            elif selection == 31:
                show_settings()
            elif selection == 32:
                show_tutorial()
            elif selection == 33:
                break

            renderer.clear()
            start_background_music()
        elif key and key.lower() == 'h':
            stop_background_music()
            show_tutorial()
            renderer.clear()
            start_background_music()
        elif key == '?':
            stop_background_music()
            show_shortcuts()
            renderer.clear()
            start_background_music()
        elif key and key.lower() == 'q':
            renderer.show_cursor()
            break
        elif key and key.lower() == 'a':
            stop_background_music()
            show_achievements()
            renderer.clear()
            start_background_music()
        elif key and key.lower() == 'r':
            stop_background_music()
            show_recent_activity()
            renderer.clear()
            start_background_music()
        elif key and key.lower() == 'l':
            show_leaderboard()
            renderer.clear()
        elif key and key.lower() == 's':
            stop_background_music()
            show_settings()
            renderer.clear()
            start_background_music()
        elif key in [str(i) for i in range(1, 11)]:
            selection = int(key) - 1
            beep("move")

    stop_background_music()
    renderer.show_cursor()
    mgr.record_telemetry('app_exit', 'arcade')


if __name__ == "__main__":
    main()
