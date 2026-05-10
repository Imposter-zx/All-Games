import os
import sys
import time
import logging
from arcade_utils import Renderer, clear_screen, load_stats, draw_retro_box, beep, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK, get_level_info, add_xp, show_popup, u_safe
from stats_manager import get_stats_manager
from input_handler import get_safe_input_handler
from error_handler import safe_game_call
from logger_setup import setup_logger

# Initialize Logger
logger = setup_logger()

from sudoku import play_sudoku
from minesweeper import play_minesweeper
try:
    from chess_game import play_chess
except ImportError:
    play_chess = None
from snake import play_snake
from breakout import play_breakout
from space_shooter import play_space_shooter
from tetris import play_tetris

from pacman import play_pacman
try:
    from dungeon import play_dungeon
except ImportError:
    play_dungeon = None

BANNER_TEXT = [
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

def draw_profile():
    """Render the high-score and XP profile."""
    mgr = get_stats_manager()
    stats = mgr.get_stats()
    
    # Calculate Total Score
    games = ["snake", "breakout", "space_shooter", "tetris", "pacman", "dungeon", "minesweeper", "chess", "sudoku"]
    total_score = 0
    for game in games:
        total_score += mgr.get_high_score(game)
        
    m_wins = sum(mgr.get_stats("minesweeper").get('wins', {}).values()) if isinstance(mgr.get_stats("minesweeper").get('wins'), dict) else 0
    c_wins = mgr.get_stats("chess").get("wins", 0)
    p_wins = mgr.get_stats("pacman").get("wins", 0)
    d_max = mgr.get_stats("dungeon").get("max_level", 1)
    
    level, xp, progress = mgr.get_level_and_xp()
    achievements = stats.get('achievements', [])
    bar_width = 20
    filled = int(progress * bar_width)
    xp_bar = f"[{C_GREEN}{u_safe('█', '#') * filled}{C_BLACK}{u_safe('░', '-') * (bar_width - filled)}{C_WHITE}]"
    level_bar = f"[{C_YELLOW}{u_safe('★', '*') * (level % 5)}{C_WHITE}]"
    
    profile_lines = [
        f"LEVEL: {level} {level_bar}",
        f"XP: {xp} {xp_bar}",
        f"🏆 ACHIEVEMENTS: {C_YELLOW}{len(achievements)}{C_WHITE}",
        f"══════════════════════════════",
        f"🎯 TOTAL SCORE: {C_YELLOW}{total_score}{C_WHITE}",
        f"{u_safe('🐍', 'S')} Snake Best        : {C_GREEN}{mgr.get_high_score('snake')}{C_WHITE}",
        f"{u_safe('🧱', 'B')} Breakout Best     : {C_CYAN}{mgr.get_high_score('breakout')}{C_WHITE}",
        f"{u_safe('🚀', 'X')} Shooter High      : {C_MAGENTA}{mgr.get_high_score('space_shooter')}{C_WHITE}",
        f"{u_safe('🧩', 'T')} Tetris Best       : {C_BLUE}{mgr.get_high_score('tetris')}{C_WHITE}",
        f"{u_safe('🟡', 'P')} Pacman Wins       : {C_YELLOW}{p_wins}{C_WHITE}",
        f"{u_safe('💣', 'M')} Minesweeper Wins  : {C_RED}{m_wins}{C_WHITE}",
        f"{u_safe('⚔️', 'D')} Dungeon Max Lvl   : {C_MAGENTA}{d_max}{C_WHITE}",
        f"{u_safe('♟️', 'C')} Chess Wins        : {C_WHITE}{c_wins}{C_WHITE}",
        f"{u_safe('🔢', '#')} Sudoku Wins       : {C_GREEN}{mgr.get_stats('sudoku').get('wins', 0)}{C_WHITE}"
    ]
    
    # Add a mini achievement list if they exist
    if achievements:
        from achievements_config import get_achievement
        recent_ids = achievements[-2:] # Last 2
        ach_names = [get_achievement(aid)['name'] for aid in recent_ids if get_achievement(aid)]
        if ach_names:
            profile_lines.append(f"══════════════════════════════")
            profile_lines.append(f"RECENT: {', '.join(ach_names)}")

    draw_retro_box(40, f"{u_safe('👤', '')} PLAYER PROFILE", profile_lines, color=C_WHITE, title_color=C_CYAN)

def print_menu(selection, renderer):
    """Render the main arcade menu."""
    term_width = 80
    try: term_width = os.get_terminal_size().columns
    except: pass
    
    for line in BANNER_TEXT:
        print(" " * max(0, (term_width - 45) // 2) + f"{C_CYAN}{line}{C_RESET}")
    print("\n")
    
    draw_profile()
    print("\n")
    
    options = [
        "1. 🐍 Snake",
        "2. 🧱 Breakout",
        "3. 🚀 Space Shooter",
        "4. 🧩 Tetris",
        "5. 🟡 Pacman",
        "6. ⚔️ Dungeon Crawler",
        "7. 💣 Minesweeper",
        "8. ♟️ Chess vs AI",
        "9. 🔢 Sudoku",
        "Q. 🚪 Quit"
    ]
    
    menu_content = []
    for i, opt in enumerate(options):
        is_sel = (i == selection)
        prefix = f"{C_YELLOW}► {C_RESET}" if is_sel else "  "
        style = f"\033[47;30m" if is_sel else f"{C_WHITE}"
        menu_content.append(f"{prefix}{style} {opt:<20} {C_RESET}")
        
    draw_retro_box(30, "🕹️ GAME MENU", menu_content, color=C_CYAN)
    print("\n" + " " * max(0, (term_width - 36) // 2) + f"{C_WHITE}Use Arrows to navigate, Enter to play{C_RESET}")

def select_game_difficulty():
    """Let player choose difficulty before game starts."""
    from arcade_utils import draw_retro_box, C_YELLOW, C_RESET, get_key, clear_screen
    
    difficulties = ['EASY', 'NORMAL', 'HARD']
    selection = 1 # Start on NORMAL
    
    while True:
        clear_screen()
        print("\n" * 2)
        
        diff_lines = []
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

def main():
    """Application entry point."""
    if os.name == 'nt': os.system('') # Initialize ANSI
    selection = 0
    num_options = 10 
    
    renderer = Renderer(fps=60) # High FPS for menu
    input_handler = get_safe_input_handler()
    
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
            
            # Select difficulty before playing (except for Quit)
            if selection < 9:
                difficulty = select_game_difficulty()
                if not difficulty: continue # Back to menu
            
            if selection == 0:   safe_game_call(play_snake, "Snake", difficulty=difficulty)
            elif selection == 1: safe_game_call(play_breakout, "Breakout", difficulty=difficulty)
            elif selection == 2: safe_game_call(play_space_shooter, "Space Shooter", difficulty=difficulty)
            elif selection == 3: safe_game_call(play_tetris, "Tetris", difficulty=difficulty)
            elif selection == 4: safe_game_call(play_pacman, "Pac-Man", difficulty=difficulty)
            elif selection == 5: 
                if play_dungeon: safe_game_call(play_dungeon, "Dungeon Crawler", difficulty=difficulty)
                else: show_popup("Dungeon module missing!", C_RED)
            elif selection == 6: safe_game_call(play_minesweeper, "Minesweeper", difficulty=difficulty)
            elif selection == 7:
                if play_chess: safe_game_call(play_chess, "Chess", difficulty=difficulty)
                else: show_popup("Chess (python-chess) missing!", C_RED)
            elif selection == 8: safe_game_call(play_sudoku, "Sudoku", difficulty=difficulty)
            elif selection == 9: break
            
            renderer.clear() # Clear after game returns
        elif key in ['q', 'Q']:
            renderer.show_cursor()
            break
        elif key in [str(i) for i in range(1, 10)]:
             selection = int(key) - 1
             beep("move")
    
    renderer.show_cursor()

if __name__ == "__main__":
    main()
