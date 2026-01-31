import os
import sys
import json
import time

# ANSI Color Codes
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_MAGENTA = "\033[35m"
C_CYAN = "\033[36m"
C_WHITE = "\033[37m"
C_BLACK = "\033[30m"

# Backgrounds
BG_DARK = "\033[48;5;236m"
BG_LIGHT = "\033[48;5;250m"
BG_CUR = "\033[48;5;220m"
BG_SEL = "\033[48;5;34m"
BG_RED = "\033[41m"
BG_BLUE = "\033[44m"

STATS_FILE = "player_stats.json"

def beep(event="correct"):
    """Terminal beeps for arcade feedback."""
    if event == "correct":
        print("\a", end="", flush=True)
    elif event == "invalid":
        print("\a", end="", flush=True)
        time.sleep(0.1)
        print("\a", end="", flush=True)
    elif event == "win":
        for _ in range(3):
            print("\a", end="", flush=True)
            time.sleep(0.15)
    elif event == "lose":
        for _ in range(2):
            print("\a", end="", flush=True)
            time.sleep(0.4)

def get_input_util():
    if os.name == 'nt':
        import msvcrt
        def getch():
            ch = msvcrt.getch()
            if ch in [b'\x00', b'\xe0']:
                ch2 = msvcrt.getch()
                return {b'H': 'up', b'P': 'down', b'K': 'left', b'M': 'right'}.get(ch2, None)
            try: return ch.decode('utf-8')
            except: return None
        return getch
    else:
        import tty, termios
        def getch():
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\033':
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        return {'A': 'up', 'B': 'down', 'D': 'left', 'C': 'right'}.get(ch3, None)
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return getch

get_key = get_input_util()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except: return {}
    return {}

def update_stats(game, key, value, subkey=None):
    stats = load_stats()
    if game not in stats: stats[game] = {}
    if subkey:
        if key not in stats[game] or not isinstance(stats[game][key], dict):
            stats[game][key] = {}
        stats[game][key][subkey] = value
    else:
        stats[game][key] = value
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)

def draw_retro_box(width, title, content_lines, color=C_CYAN, title_color=C_YELLOW):
    """Draws a centered retro box with a title and multi-line content."""
    terminal_width = 80 # Default
    try:
        terminal_width = os.get_terminal_size().columns
    except: pass
    
    padding = (terminal_width - width) // 2
    indent = " " * padding
    
    print(indent + f"{color}╔" + "═" * (width - 2) + "╗")
    
    # Title line
    title_padding = (width - 2 - len(title)) // 2
    title_line = " " * title_padding + f"{title_color}{C_BOLD}{title}{C_RESET}{color}"
    title_line += " " * (width - 2 - len(title) - title_padding)
    print(indent + f"║{title_line}║")
    
    print(indent + f"╠" + "═" * (width - 2) + "╣")
    
    for line in content_lines:
        content_padding = (width - 2 - len(line)) // 2
        l_text = " " * content_padding + f"{C_WHITE}{line}{C_RESET}{color}"
        l_text += " " * (width - 2 - len(line) - content_padding)
        print(indent + f"║{l_text}║")
        
    print(indent + f"╚" + "═" * (width - 2) + "╝{C_RESET}")

def show_popup(msg, color=C_CYAN, delay=2):
    clear_screen()
    print("\n" * 5)
    draw_retro_box(40, "POPUP", [msg], color=color)
    time.sleep(delay)
