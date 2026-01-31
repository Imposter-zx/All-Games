import os
import sys
import time
from arcade_utils import clear_screen, get_key, load_stats, draw_retro_box, beep, C_RESET, C_BOLD, C_RED, C_GREEN, C_YELLOW, C_CYAN, C_WHITE, C_MAGENTA
from sudoku import play_sudoku
from minesweeper import play_minesweeper
from chess_game import play_chess

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
    "         --- TERMINAL ARCADE V3 ---      "
]

def draw_profile(stats):
    m_stats = stats.get("minesweeper", {})
    m_wins = sum(m_stats.get('wins', {}).values()) if isinstance(m_stats.get('wins'), dict) else 0
    s_best = stats.get("sudoku", {}).get("best_times", {}).get("hard", "N/A")
    c_wins = stats.get("chess", {}).get("wins", 0)
    
    profile_lines = [
        f"PLAYER: {C_YELLOW}ZORD{C_WHITE}",
        f"══════════════════════════════",
        f"🧩 Sudoku Best (Hard): {C_CYAN}{s_best}{C_WHITE}s",
        f"💣 Minesweeper Wins  : {C_GREEN}{m_wins}{C_WHITE}",
        f"♟️ Chess Wins vs AI : {C_MAGENTA}{c_wins}{C_WHITE}",
        f"🏅 Achievements     : {C_YELLOW}3{C_WHITE}"
    ]
    draw_retro_box(40, "👤 PLAYER PROFILE", profile_lines, color=C_WHITE, title_color=C_CYAN)

def print_menu(selection):
    clear_screen()
    stats = load_stats()
    
    # Center banner
    term_width = 80
    try: term_width = os.get_terminal_size().columns
    except: pass
    
    for line in BANNER_TEXT:
        print(" " * ((term_width - 45) // 2) + f"{C_CYAN}{line}{C_RESET}")
    print("\n")
    
    draw_profile(stats)
    print("\n")
    
    options = [
        "🧩 Sudoku",
        "♟️ Chess vs AI",
        "💣 Minesweeper",
        "🚪 Quit"
    ]
    
    menu_content = []
    for i, opt in enumerate(options):
        prefix = f"{C_YELLOW}► {C_RESET}" if i == selection else "  "
        style = f"\033[47;30m" if i == selection else f"{C_WHITE}"
        menu_content.append(f"{prefix}{style} {opt:<20} {C_RESET}")
        
    draw_retro_box(30, "🕹️ MAIN MENU", menu_content, color=C_CYAN)
    print("\n" + " " * ((term_width - 36) // 2) + f"{C_WHITE}Use Arrows to navigate, Enter to play{C_RESET}")

def main():
    if os.name == 'nt': os.system('') # Initialize ANSI on Windows
    selection = 0
    while True:
        print_menu(selection)
        key = get_key()
        
        if key == 'up': 
            selection = (selection - 1) % 4
            beep("correct")
        elif key == 'down': 
            selection = (selection + 1) % 4
            beep("correct")
        elif key in ['\r', '\n', ' ']:
            beep("correct")
            if selection == 0: play_sudoku()
            elif selection == 1:
                try:
                    import chess
                    play_chess()
                except ImportError:
                    clear_screen()
                    print(f"\n{C_RED} Error: python-chess not found! Run pip install -r requirements.txt{C_RESET}")
                    time.sleep(2)
            elif selection == 2: play_minesweeper()
            elif selection == 3: break
        elif key in ['1', '2', '3', 'q', 'Q']:
            beep("correct")
            if key == '1': play_sudoku()
            elif key == '2': play_chess()
            elif key == '3': play_minesweeper()
            elif key in ['q', 'Q']: break

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
