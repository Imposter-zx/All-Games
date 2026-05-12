import os
import sys
import json
import time
import re
from stats_manager import get_stats_manager

def u_safe(text, fallback=""):
    """Return text with only characters encodable in the current stdout."""
    if not isinstance(text, str): return text
    
    # Check entire string
    try:
        text.encode(sys.stdout.encoding)
        return text
    except:
        # Fallback character by character
        safe_chars = []
        for char in text:
            try:
                char.encode(sys.stdout.encoding)
                safe_chars.append(char)
            except:
                # If we have a single char fallback, use it only for the first failure?
                # No, just skip or use a generic fallback
                pass
        return "".join(safe_chars) or fallback

def strip_ansi(text):
    """Removes ANSI escape codes from a string to get its visual length."""
    return re.sub(r'\x1b\[[0-9;]*[mGJKH]', '', text)

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
    """Terminal beeps for arcade feedback with varying patterns."""
    mgr = get_stats_manager()
    if not mgr.stats.get('settings', {}).get('sound_enabled', True):
        return
        
    try:
        if event == "correct":
            print("\a", end="", flush=True)
        elif event == "invalid":
            print("\a", end="", flush=True)
            time.sleep(0.05)
            print("\a", end="", flush=True)
        elif event == "win":
            # Rising sequence simulation (limited by terminal beep)
            for i in range(3):
                print("\a", end="", flush=True)
                time.sleep(0.1)
        elif event == "lose":
            # Falling sequence simulation
            print("\a", end="", flush=True)
            time.sleep(0.3)
            print("\a", end="", flush=True)
        elif event == "game_over":
            for _ in range(3):
                print("\a", end="", flush=True)
                time.sleep(0.5)
        elif event == "achievement":
            # Rapid fancy beep
            for _ in range(4):
                print("\a", end="", flush=True)
                time.sleep(0.05)
        elif event == "move":
            # Very short subtle beep
            print("\a", end="", flush=True)
        elif event == "eat":
            # Quick double beep
            print("\a", end="", flush=True)
            time.sleep(0.05)
            print("\a", end="", flush=True)
        elif event == "level_up":
            # Fast rising sequence
            for i in range(5):
                print("\a", end="", flush=True)
                time.sleep(0.05)
    except:
        pass

class Renderer:
    """Handles terminal rendering with FPS control and flicker reduction."""
    
    def __init__(self, fps=30):
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.last_frame_time = time.time()
        self.terminal_width = 80
        self.terminal_height = 24
        self._update_terminal_size()
        self.hide_cursor()
        
    def hide_cursor(self):
        """Hides the terminal cursor."""
        print("\033[?25l", end="", flush=True)

    def show_cursor(self):
        """Shows the terminal cursor."""
        print("\033[?25h", end="", flush=True)

    def _update_terminal_size(self):
        try:
            size = os.get_terminal_size()
            self.terminal_width = size.columns
            self.terminal_height = size.lines
        except (OSError, ValueError):
            pass

    def clear(self):
        """Clears the screen. Use only at start of game or major transition."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def move_to_top(self):
        """Moves cursor to top-left without clearing, reducing flicker."""
        print("\033[H", end="", flush=True)

    def render_frame(self, content_callback):
        """
        Executes rendering logic and enforces FPS limit.
        
        Args:
            content_callback: Function that prints the game state
        """
        now = time.time()
        elapsed = now - self.last_frame_time
        
        # Enforce FPS
        if elapsed < self.frame_time:
            time.sleep(self.frame_time - elapsed)
            now = time.time()
        
        # move_to_top() is better than clear_screen() for flicker
        self.move_to_top()
        content_callback()
        
        self.last_frame_time = now

    def draw_bar(self, current, maximum, width=20, label="", color=C_GREEN):
        """Draws a progress bar."""
        percent = min(1.0, max(0.0, current / maximum)) if maximum > 0 else 0
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        print(f"{label} [{color}{bar}{C_RESET}] {int(percent*100)}%")

def get_input_util():
    if os.name == 'nt':
        import msvcrt
        def getch():
            ch = msvcrt.getch()
            if ch in [b'\x00', b'\xe0']:
                ch2 = msvcrt.getch()
                return {b'H': 'up', b'P': 'down', b'K': 'left', b'M': 'right'}.get(ch2, None)
            try: return ch.decode('utf-8')
            except (UnicodeDecodeError, AttributeError): return None
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
    """Load stats using StatsManager."""
    return get_stats_manager().get_stats()

def save_stats(stats):
    """Save stats using StatsManager."""
    mgr = get_stats_manager()
    mgr.stats = stats
    mgr.save()

def update_stats(game, key, value, subkey=None):
    """Update stats using StatsManager."""
    mgr = get_stats_manager()
    if subkey:
        stats = mgr.get_stats(game)
        if key not in stats or not isinstance(stats[key], dict):
            stats[key] = {}
        stats[key][subkey] = value
        mgr.update_game_stats(game, stats)
    else:
        mgr.update_game_stats(game, {key: value})

def add_xp(amount):
    """Adds XP to the player profile via StatsManager."""
    mgr = get_stats_manager()
    new_level = mgr.add_xp(amount)
    level, xp, progress = mgr.get_level_and_xp()
    
    # Check if level increased (StatsManager already handled the logic, we just show popup)
    # Note: StatsManager.add_xp handles the level calculation
    return mgr.get_stats()

def get_level_info():
    """Get level, XP and progress from StatsManager."""
    mgr = get_stats_manager()
    return mgr.get_level_and_xp()

def screen_shake(duration=0.3, intensity=1):
    """Simulates a screen shake by clearing and re-printing with offsets."""
    # Terminal screen shake is tricky; we simulate it with rapid clearing/flashing
    # and slight ANSI cursor offsets if the terminal supports it.
    for _ in range(3):
        print("\033[1;1H", end="") # Move to top
        if intensity > 0:
            print(" " * intensity) # Slight offset simulation
        time.sleep(duration / 6)
        clear_screen()
        time.sleep(duration / 6)

def particle_effect(char="*", color=C_WHITE, count=10):
    """Prints a burst of particles at the current cursor position (simplified)."""
    # In terminal, we just print a localized burst of characters
    print(color, end="")
    for _ in range(count):
        print(char, end=" ", flush=True)
        time.sleep(0.01)
    print(C_RESET)

def animated_flash(color=C_RED, duration=0.1, count=1):
    """Flashes the screen background color."""
    for _ in range(count):
        print(f"\033[41m" if color == C_RED else f"\033[47m", end="", flush=True) # Simple red or white flash
        clear_screen()
        time.sleep(duration)
        print(C_RESET, end="", flush=True)
        clear_screen()
        time.sleep(duration)

def print_big_title(text, color=C_CYAN):
    """Prints a large ASCII title (simplified for now)."""
    # In a full implementation, this would use a large font dict.
    # For now, we will just use bold large text with borders.
    border = "═" * (len(text) + 4)
    print(f"{color}╔{border}╗")
    print(f"║  {C_BOLD}{text}{C_RESET}{color}  ║")
    print(f"╚{border}╝{C_RESET}")

def draw_retro_box(width, title, content_lines, color=C_CYAN, title_color=C_YELLOW):
    """Draws a centered retro box with a title and multi-line content."""
    terminal_width = 80 # Default
    try:
        terminal_width = os.get_terminal_size().columns
    except (OSError, ValueError): 
        pass
    
    padding = max(0, (terminal_width - width) // 2)
    indent = " " * padding
    
    # Unicode safe box characters
    try:
        # Test if we can print unicode
        "╔═╗".encode(sys.stdout.encoding)
        b_tl, b_tr, b_bl, b_br, b_h, b_v, b_ml, b_mr = "╔", "╗", "╚", "╝", "═", "║", "╠", "╣"
    except (UnicodeEncodeError, TypeError):
        b_tl, b_tr, b_bl, b_br, b_h, b_v, b_ml, b_mr = "+", "+", "+", "+", "-", "|", "|", "|"

    print(indent + f"{color}{b_tl}" + b_h * (width - 2) + f"{b_tr}")
    
    # Title line
    safe_title = u_safe(title)
    stripped_title = strip_ansi(safe_title)
    title_padding = (width - 2 - len(stripped_title)) // 2
    title_line = " " * title_padding + f"{title_color}{C_BOLD}{safe_title}{C_RESET}{color}"
    title_line += " " * (width - 2 - len(stripped_title) - title_padding)
    print(indent + f"{b_v}{title_line}{b_v}")
    
    print(indent + f"{b_ml}" + b_h * (width - 2) + f"{b_mr}")
    
    for line in content_lines:
        # Strip characters that can't be encoded
        safe_line = u_safe(line)
        stripped_line = strip_ansi(safe_line)
        content_len = len(stripped_line)
        content_padding = max(0, (width - 2 - content_len) // 2)
        l_text = " " * content_padding + f"{C_WHITE}{safe_line}{C_RESET}{color}"
        l_text += " " * (width - 2 - content_len - content_padding)
        print(indent + f"{b_v}{l_text}{b_v}")
        
    print(indent + f"{b_bl}" + b_h * (width - 2) + f"{b_br}{C_RESET}")

def show_popup(msg, color=C_CYAN, delay=2):
    clear_screen()
    print("\n" * 5)
    draw_retro_box(40 + len(msg)//2, "POPUP", [msg], color=color)
    time.sleep(delay)
