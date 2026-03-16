import os
import sys
import time
from arcade_utils import clear_screen, get_key, load_stats, draw_retro_box, beep, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_BLUE, C_CYAN, C_WHITE, C_MAGENTA
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
    # Calculate Total Score
    total_score = 0
    total_score += stats.get("snake", {}).get("high_score", 0)
    total_score += stats.get("breakout", {}).get("best_score", 0)
    total_score += stats.get("space_shooter", {}).get("high_score", 0)
    total_score += stats.get("tetris", {}).get("best_score", 0)
    total_score += stats.get("pacman", {}).get("high_score", 0)
    
    # Existing stats
    m_stats = stats.get("minesweeper", {})
    m_wins = sum(m_stats.get('wins', {}).values()) if isinstance(m_stats.get('wins'), dict) else 0
    c_wins = stats.get("chess", {}).get("wins", 0)
    p_wins = stats.get("pacman", {}).get("wins", 0)
    
    profile_lines = [
        f"PLAYER: {C_YELLOW}RETRO_MASTER{C_WHITE}",
        f"══════════════════════════════",
        f"🏆 TOTAL ARCADE SCORE: {C_YELLOW}{total_score}{C_WHITE}",
        f"🐍 Snake Best        : {C_GREEN}{stats.get('snake', {}).get('high_score', 0)}{C_WHITE}",
        f"🧱 Breakout Best     : {C_CYAN}{stats.get('breakout', {}).get('best_score', 0)}{C_WHITE}",
        f"🚀 Shooter High      : {C_MAGENTA}{stats.get('space_shooter', {}).get('high_score', 0)}{C_WHITE}",
        f"🧩 Tetris Best       : {C_BLUE}{stats.get('tetris', {}).get('best_score', 0)}{C_WHITE}",
        f"🟡 Pacman Wins       : {C_YELLOW}{p_wins}{C_WHITE}",
        f"💣 Minesweeper Wins  : {C_RED}{m_wins}{C_WHITE}",
        f"♟️ Chess Wins        : {C_WHITE}{c_wins}{C_WHITE}"
    ]
    draw_retro_box(40, "👤 PLAYER PROFILE", profile_lines, color=C_WHITE, title_color=C_CYAN)

def print_menu(selection):
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
        "6. 💣 Minesweeper",
        "7. ♟️ Chess vs AI",
        "8. 🔢 Sudoku",
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
    if os.name == 'nt': os.system('') # Initialize ANSI
    selection = 0
    num_options = 9 # Updated for Pacman
    
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
            if selection == 0: play_snake()
            elif selection == 1: play_breakout()
            elif selection == 2: play_space_shooter()
            elif selection == 3: play_tetris()
            elif selection == 4: play_pacman()
            elif selection == 5: play_minesweeper()
            elif selection == 6:
                if play_chess:
                    try:
                        play_chess()
                    except ImportError:
                        print(f"\n{C_RED} Error: python-chess not found!{C_RESET}")
                        time.sleep(2)
                else:
                    print(f"\n{C_RED} Error: python-chess not found! (Module missing){C_RESET}")
                    time.sleep(2)
            elif selection == 7: play_sudoku()
            elif selection == 8: break
        elif key in ['q', 'Q']:
            break
        elif key in [str(i) for i in range(1, 10)]:
             idx = int(key) - 1
             selection = idx
             pass

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
