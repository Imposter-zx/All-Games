import os
import sys
import time
from arcade_utils import clear_screen, get_key, load_stats, draw_retro_box, beep, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA, C_BLACK, get_level_info, add_xp
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

def draw_profile(stats):
    """Render the high-score and XP profile."""
    # Calculate Total Score
    games = ["snake", "breakout", "space_shooter", "tetris", "pacman", "dungeon", "minesweeper", "chess", "sudoku"]
    total_score = 0
    for game in games:
        g_stats = stats.get(game, {})
        total_score += g_stats.get("high_score", 0)
        total_score += g_stats.get("score", 0) # Some use 'score' as high_score field
        
    m_stats = stats.get("minesweeper", {})
    m_wins = sum(m_stats.get('wins', {}).values()) if isinstance(m_stats.get('wins'), dict) else 0
    c_stats = stats.get("chess", {})
    c_wins = c_stats.get("wins", 0)
    p_wins = stats.get("pacman", {}).get("wins", 0)
    d_stats = stats.get("dungeon", {})
    d_max = d_stats.get("max_level", 1)
    
    level, xp, progress = get_level_info()
    bar_width = 20
    filled = int(progress * bar_width)
    xp_bar = f"[{C_GREEN}{'█' * filled}{C_BLACK}{'░' * (bar_width - filled)}{C_WHITE}]"
    
    profile_lines = [
        f"PLAYER: {C_YELLOW}RETRO_MASTER{C_WHITE}  LVL: {C_CYAN}{level}{C_WHITE}",
        f"XP: {xp} {xp_bar}",
        f"══════════════════════════════",
        f"🏆 TOTAL ARCADE SCORE: {C_YELLOW}{total_score}{C_WHITE}",
        f"🐍 Snake Best        : {C_GREEN}{stats.get('snake', {}).get('high_score', 0)}{C_WHITE}",
        f"🧱 Breakout Best     : {C_CYAN}{stats.get('breakout', {}).get('high_score', 0)}{C_WHITE}",
        f"🚀 Shooter High      : {C_MAGENTA}{stats.get('space_shooter', {}).get('high_score', 0)}{C_WHITE}",
        f"🧩 Tetris Best       : {C_BLUE}{stats.get('tetris', {}).get('high_score', 0)}{C_WHITE}",
        f"🟡 Pacman Wins       : {C_YELLOW}{p_wins}{C_WHITE}",
        f"💣 Minesweeper Wins  : {C_RED}{m_wins}{C_WHITE}",
        f"⚔️ Dungeon Max Lvl   : {C_MAGENTA}{d_max}{C_WHITE}",
        f"♟️ Chess Wins        : {C_WHITE}{c_wins}{C_WHITE}",
        f"🔢 Sudoku Wins       : {C_GREEN}{stats.get('sudoku', {}).get('wins', 0)}{C_WHITE}"
    ]
    draw_retro_box(40, "👤 PLAYER PROFILE", profile_lines, color=C_WHITE, title_color=C_CYAN)

def print_menu(selection):
    """Render the main arcade menu."""
    clear_screen()
    stats = load_stats()
    
    term_width = 80
    try: term_width = os.get_terminal_size().columns
    except: pass
    
    for line in BANNER_TEXT:
        print(" " * max(0, (term_width - 45) // 2) + f"{C_CYAN}{line}{C_RESET}")
    print("\n")
    
    draw_profile(stats)
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

def main():
    """Application entry point."""
    if os.name == 'nt': os.system('') # Initialize ANSI
    selection = 0
    num_options = 10 
    
    while True:
        print_menu(selection)
        key = get_key()
        
        if key == 'up': 
            selection = (selection - 1) % num_options
            beep("correct")
        elif key == 'down': 
            selection = (selection + 1) % num_options
            beep("correct")
        elif key in ['\r', '\n', ' ']:
            beep("correct")
            if selection == 0:   play_snake()
            elif selection == 1: play_breakout()
            elif selection == 2: play_space_shooter()
            elif selection == 3: play_tetris()
            elif selection == 4: play_pacman()
            elif selection == 5: 
                if play_dungeon: play_dungeon()
                else: show_popup("Dungeon module missing!", C_RED)
            elif selection == 6: play_minesweeper()
            elif selection == 7:
                if play_chess: play_chess()
                else: show_popup("Chess (python-chess) missing!", C_RED)
            elif selection == 8: play_sudoku()
            elif selection == 9: break
        elif key in ['q', 'Q']:
            break
        elif key in [str(i) for i in range(1, 10)]:
             selection = int(key) - 1
             # Immediately play if number pressed? Or just select? 
             # Let's just select to match the arrow behavior.
             pass

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
