"""Marathon Mode — play all 37 games in one session with cumulative scoring."""
import time
from typing import Any, Callable, Dict, List, Tuple

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

GAME_PLAY_FUNCS: Dict[str, Callable] = {}

GAME_NAMES: List[Tuple[str, str]] = [
    ("snake", "Snake"),
    ("breakout", "Breakout"),
    ("space_shooter", "Space Shooter"),
    ("tetris", "Tetris"),
    ("pacman", "Pac-Man"),
    ("dungeon", "Dungeon Crawler"),
    ("minesweeper", "Minesweeper"),
    ("chess", "Chess"),
    ("sudoku", "Sudoku"),
    ("2048", "2048"),
    ("pong", "Pong"),
    ("asteroids", "Asteroids"),
    ("frogger", "Frogger"),
    ("flappy", "Flappy Bird"),
    ("racing", "Racing"),
    ("blackjack", "Blackjack"),
    ("connect_four", "Connect Four"),
    ("hangman", "Hangman"),
    ("wordle", "Wordle"),
    ("tictactoe", "Tic-Tac-Toe"),
    ("simon", "Simon Says"),
    ("trivia", "Trivia"),
    ("slots", "Slots"),
    ("memory", "Memory"),
    ("battleship", "Battleship"),
    ("crossword", "Crossword"),
    ("hanoi", "Tower of Hanoi"),
    ("typer", "Typer"),
    ("solitaire", "Solitaire"),
    ("rpsls", "RPSLS"),
    ("poker", "Poker"),
    ("mastermind", "Mastermind"),
    ("gomoku", "Gomoku"),
    ("othello", "Othello"),
    ("nonograms", "Nonograms"),
    ("sokoban", "Sokoban"),
    ("invaders", "Invaders"),
]


def _register_funcs() -> None:
    if GAME_PLAY_FUNCS:
        return
    try:
        from asteroids import play_asteroids
        GAME_PLAY_FUNCS["asteroids"] = play_asteroids
    except ImportError:
        pass
    try:
        from battleship import play_battleship
        GAME_PLAY_FUNCS["battleship"] = play_battleship
    except ImportError:
        pass
    try:
        from blackjack import play_blackjack
        GAME_PLAY_FUNCS["blackjack"] = play_blackjack
    except ImportError:
        pass
    try:
        from breakout import play_breakout
        GAME_PLAY_FUNCS["breakout"] = play_breakout
    except ImportError:
        pass
    try:
        from chess_game import play_chess
        GAME_PLAY_FUNCS["chess"] = play_chess
    except ImportError:
        pass
    try:
        from connect_four import play_connect_four
        GAME_PLAY_FUNCS["connect_four"] = play_connect_four
    except ImportError:
        pass
    try:
        from crossword import play_crossword
        GAME_PLAY_FUNCS["crossword"] = play_crossword
    except ImportError:
        pass
    try:
        from flappy import play_flappy
        GAME_PLAY_FUNCS["flappy"] = play_flappy
    except ImportError:
        pass
    try:
        from frogger import play_frogger
        GAME_PLAY_FUNCS["frogger"] = play_frogger
    except ImportError:
        pass
    try:
        from game_2048 import play_2048
        GAME_PLAY_FUNCS["2048"] = play_2048
    except ImportError:
        pass
    try:
        from gomoku import play_gomoku
        GAME_PLAY_FUNCS["gomoku"] = play_gomoku
    except ImportError:
        pass
    try:
        from hangman import play_hangman
        GAME_PLAY_FUNCS["hangman"] = play_hangman
    except ImportError:
        pass
    try:
        from hanoi import play_hanoi
        GAME_PLAY_FUNCS["hanoi"] = play_hanoi
    except ImportError:
        pass
    try:
        from mastermind import play_mastermind
        GAME_PLAY_FUNCS["mastermind"] = play_mastermind
    except ImportError:
        pass
    try:
        from memory import play_memory
        GAME_PLAY_FUNCS["memory"] = play_memory
    except ImportError:
        pass
    try:
        from minesweeper import play_minesweeper
        GAME_PLAY_FUNCS["minesweeper"] = play_minesweeper
    except ImportError:
        pass
    try:
        from nonograms import play_nonograms
        GAME_PLAY_FUNCS["nonograms"] = play_nonograms
    except ImportError:
        pass
    try:
        from othello import play_othello
        GAME_PLAY_FUNCS["othello"] = play_othello
    except ImportError:
        pass
    try:
        from pacman import play_pacman
        GAME_PLAY_FUNCS["pacman"] = play_pacman
    except ImportError:
        pass
    try:
        from poker import play_poker
        GAME_PLAY_FUNCS["poker"] = play_poker
    except ImportError:
        pass
    try:
        from pong import play_pong
        GAME_PLAY_FUNCS["pong"] = play_pong
    except ImportError:
        pass
    try:
        from racing import play_racing
        GAME_PLAY_FUNCS["racing"] = play_racing
    except ImportError:
        pass
    try:
        from rpsls import play_rpsls
        GAME_PLAY_FUNCS["rpsls"] = play_rpsls
    except ImportError:
        pass
    try:
        from simon import play_simon
        GAME_PLAY_FUNCS["simon"] = play_simon
    except ImportError:
        pass
    try:
        from slots import play_slots
        GAME_PLAY_FUNCS["slots"] = play_slots
    except ImportError:
        pass
    try:
        from snake import play_snake
        GAME_PLAY_FUNCS["snake"] = play_snake
    except ImportError:
        pass
    try:
        from sokoban import play_sokoban
        GAME_PLAY_FUNCS["sokoban"] = play_sokoban
    except ImportError:
        pass
    try:
        from solitaire import play_solitaire
        GAME_PLAY_FUNCS["solitaire"] = play_solitaire
    except ImportError:
        pass
    try:
        from sudoku import play_sudoku
        GAME_PLAY_FUNCS["sudoku"] = play_sudoku
    except ImportError:
        pass
    try:
        from tetris import play_tetris
        GAME_PLAY_FUNCS["tetris"] = play_tetris
    except ImportError:
        pass
    try:
        from tictactoe import play_tictactoe
        GAME_PLAY_FUNCS["tictactoe"] = play_tictactoe
    except ImportError:
        pass
    try:
        from trivia import play_trivia
        GAME_PLAY_FUNCS["trivia"] = play_trivia
    except ImportError:
        pass
    try:
        from typer import play_typer
        GAME_PLAY_FUNCS["typer"] = play_typer
    except ImportError:
        pass
    try:
        from wordle import play_wordle
        GAME_PLAY_FUNCS["wordle"] = play_wordle
    except ImportError:
        pass
    try:
        from dungeon import play_dungeon
        GAME_PLAY_FUNCS["dungeon"] = play_dungeon
    except ImportError:
        pass
    try:
        from invaders import play_invaders
        GAME_PLAY_FUNCS["invaders"] = play_invaders
    except ImportError:
        pass
    try:
        from space_shooter import play_space_shooter
        GAME_PLAY_FUNCS["space_shooter"] = play_space_shooter
    except ImportError:
        pass


def run_marathon() -> None:
    """Run all 37 games sequentially with cumulative scoring."""
    _register_funcs()
    mgr = get_stats_manager()

    total_score = 0
    total_xp = 0
    completed = 0
    failed = 0
    start_time = time.time()
    results: list[dict[str, Any]] = []
    lives = 3

    clear_screen()
    print("\n" * 3)
    print(f"  {C_YELLOW}{C_BOLD}╔═══════════════════════════════════════╗{C_RESET}")
    print(f"  {C_YELLOW}{C_BOLD}║     37-GAME MARATHON MODE!           ║{C_RESET}")
    print(f"  {C_YELLOW}{C_BOLD}╚═══════════════════════════════════════╝{C_RESET}")
    print()
    print(f"  {C_WHITE}Play ALL 37 games in one session.{C_RESET}")
    print(f"  {C_WHITE}Cumulative score. Permadeath: 3 lives.{C_RESET}")
    print(f"  {C_WHITE}Each failed game costs 1 life.{C_RESET}")
    print(f"  {C_WHITE}Lose all lives = GAME OVER.{C_RESET}")
    print()
    print(f"  {C_GREEN}Difficulty climbs with each game.{C_RESET}")
    print(f"  {C_MAGENTA}Bonus XP for marathon completion!{C_RESET}")
    print()
    print(f"  {C_WHITE}[ENTER] Start marathon  |  [Q] Cancel{C_RESET}")

    while True:
        key = get_key()
        if key in ["\r", "\n", " ", "enter"]:
            break
        if key and key.lower() == "q":
            return

    for idx, (game_id, game_name) in enumerate(GAME_NAMES):
        if lives <= 0:
            clear_screen()
            print(f"\n  {C_RED}MARATHON OVER — No lives remaining!{C_RESET}")
            time.sleep(1.5)
            break

        func = GAME_PLAY_FUNCS.get(game_id)
        if not func:
            failed += 1
            continue

        diff_idx = idx // 12
        diffs = ["easy", "normal", "hard"]
        diff = diffs[min(diff_idx, 2)]

        clear_screen()
        print(f"\n  {C_MAGENTA}{C_BOLD}MARATHON — Game {idx + 1}/37{C_RESET}")
        print(f"  {C_CYAN}╔═══════════════════════════════════════╗{C_RESET}")
        print(f"  {C_CYAN}║{C_RESET}  {C_YELLOW}Next:{C_RESET} {C_BOLD}{game_name:<22}{C_RESET}{C_CYAN}║{C_RESET}")
        print(f"  {C_CYAN}║{C_RESET}  {C_YELLOW}Diff:{C_RESET} {C_BOLD}{diff.upper():<12}{C_RESET}{C_CYAN}║{C_RESET}")
        print(f"  {C_CYAN}║{C_RESET}  {C_YELLOW}Score:{C_RESET} {total_score:<20}{C_CYAN}║{C_RESET}")
        print(f"  {C_CYAN}║{C_RESET}  {C_YELLOW}Lives:{C_RESET} {lives:<20}{C_CYAN}║{C_RESET}")
        print(f"  {C_CYAN}╚═══════════════════════════════════════╝{C_RESET}")
        print(f"\n  {C_WHITE}[ENTER] Play  |  [Q] Abort marathon{C_RESET}")

        while True:
            key = get_key()
            if key in ["\r", "\n", " ", "enter"]:
                break
            if key and key.lower() == "q":
                clear_screen()
                print(f"\n  {C_YELLOW}Marathon aborted at game {idx + 1}/37{C_RESET}")
                time.sleep(1)
                _show_marathon_summary(total_score, total_xp, completed, failed,
                                       int(time.time() - start_time), results, False)
                return

        clear_screen()
        print(f"\n  {C_GREEN}Starting {game_name} ({diff})...{C_RESET}")
        time.sleep(0.5)
        clear_screen()

        try:
            result = func(diff)
            if result and isinstance(result, dict):
                game_score = result.get("high_score", result.get("score", 0))
                game_xp = result.get("xp_earned", 0)
                if game_score > 0 or game_xp > 0:
                    total_score += game_score
                    total_xp += game_xp
                    completed += 1
                    results.append({
                        "game": game_name,
                        "score": game_score,
                        "xp": game_xp,
                    })
                else:
                    failed += 1
                    lives -= 1
                    results.append({"game": game_name, "score": 0, "xp": 0, "failed": True})
            else:
                failed += 1
                lives -= 1
                results.append({"game": game_name, "score": 0, "xp": 0, "failed": True})
        except Exception:
            failed += 1
            lives -= 1
            results.append({"game": game_name, "score": 0, "xp": 0, "failed": True})

        _show_marathon_progress(total_score, total_xp, completed, failed, idx + 1, lives)

    elapsed = int(time.time() - start_time)
    _show_marathon_summary(total_score, total_xp, completed, failed, elapsed, results, lives > 0)

    mgr.add_xp(total_xp)
    marquee_bonus = completed * 50
    mgr.add_xp(marquee_bonus)


def _show_marathon_progress(total_score: int, total_xp: int, completed: int,
                            failed: int, current: int, lives: int) -> None:
    clear_screen()
    print(f"\n  {C_CYAN}{C_BOLD}MARATHON PROGRESS{C_RESET}")
    print(f"  {C_WHITE}╔═══════════════════════════════════════╗{C_RESET}")
    print(f"  {C_WHITE}║{C_RESET}  Games: {current}/37  Lives: {'♥' * lives}   {C_WHITE}║{C_RESET}")
    print(f"  {C_WHITE}║{C_RESET}  Score: {total_score:<6}  XP: {total_xp:<6}{C_WHITE}    ║{C_RESET}")
    print(f"  {C_WHITE}║{C_RESET}  ✅ {completed} completed  ❌ {failed} failed{C_WHITE}   ║{C_RESET}")
    print(f"  {C_WHITE}╚═══════════════════════════════════════╝{C_RESET}")
    print(f"\n  {C_WHITE}[ENTER] Continue{C_RESET}")
    while True:
        key = get_key()
        if key in ["\r", "\n", " ", "enter"]:
            break


def _show_marathon_summary(total_score: int, total_xp: int, completed: int,
                           failed: int, elapsed: int, results: list,
                           completed_all: bool) -> None:
    clear_screen()
    m, s = divmod(elapsed, 60)
    h, m = divmod(m, 60)
    time_str = f"{h}h{m}m{s}s" if h else f"{m}m{s}s" if m else f"{s}s"

    title = "🏆 MARATHON COMPLETE!" if completed_all else "💀 MARATHON FAILED"
    title_color = C_GREEN if completed_all else C_RED

    print(f"\n  {title_color}{C_BOLD}╔═══════════════════════════════════════╗{C_RESET}")
    print(f"  {title_color}{C_BOLD}║{C_RESET}      {title:<20}      {title_color}{C_BOLD}║{C_RESET}")
    print(f"  {title_color}{C_BOLD}╚═══════════════════════════════════════╝{C_RESET}")
    print()
    print(f"  {C_YELLOW}Final Score:  {C_WHITE}{total_score}{C_RESET}")
    print(f"  {C_YELLOW}Total XP:     {C_WHITE}{total_xp}{C_RESET}")
    print(f"  {C_YELLOW}Completed:    {C_GREEN}{completed}/36{C_RESET}")
    print(f"  {C_YELLOW}Failed:       {C_RED}{failed}{C_RESET}")
    print(f"  {C_YELLOW}Time:         {C_WHITE}{time_str}{C_RESET}")
    print()

    if completed_all:
        print(f"  {C_MAGENTA}★★★ MARATHON MASTER! +{completed * 50} BONUS XP ★★★{C_RESET}")

    print()
    print(f"  {C_YELLOW}Game Results:{C_RESET}")
    for r in results:
        game = r.get("game", "?")
        score = r.get("score", 0)
        xp = r.get("xp", 0)
        failed_flag = r.get("failed", False)
        if failed_flag:
            print(f"  {C_RED}✗ {game:<18} FAILED{C_RESET}")
        else:
            print(f"  {C_GREEN}✓ {game:<18} {score:>6}pts  {xp:>4}xp{C_RESET}")

    print(f"\n  {C_WHITE}[Any Key] Continue{C_RESET}")
    get_key()
