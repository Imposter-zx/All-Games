import logging
import os
import re
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from sound_engine import play_sound
from stats_manager import get_stats_manager

logger = logging.getLogger(__name__)


def u_safe(text: str, fallback: str = "") -> str:
    """Return text with only characters encodable in the current stdout."""
    if not isinstance(text, str):
        return text
    try:
        text.encode(sys.stdout.encoding)
        return text
    except (UnicodeEncodeError, AttributeError):
        safe_chars: List[str] = []
        for char in text:
            try:
                char.encode(sys.stdout.encoding)
                safe_chars.append(char)
            except (UnicodeEncodeError, AttributeError):
                pass
        return "".join(safe_chars) or fallback


def strip_ansi(text: str) -> str:
    """Removes ANSI escape codes from a string to get its visual length."""
    return re.sub(r'\x1b\[[0-9;]*[mGJKH]', '', text)


class Color:
    """Dynamic color object that allows theme switching without re-importing."""
    def __init__(self, value: str) -> None:
        self.value = value
    def __str__(self) -> str: return str(self.value)
    def __repr__(self) -> str: return str(self.value)
    def __format__(self, spec: str) -> str: return str(self.value)
    def __add__(self, other: object) -> str: return str(self.value) + str(other)
    def __radd__(self, other: object) -> str: return str(other) + str(self.value)

# ANSI Color Codes
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = Color("\033[31m")
C_GREEN = Color("\033[32m")
C_YELLOW = Color("\033[33m")
C_BLUE = Color("\033[34m")
C_MAGENTA = Color("\033[35m")
C_CYAN = Color("\033[36m")
C_WHITE = Color("\033[37m")
C_BLACK = Color("\033[30m")
C_GRAY = Color("\033[90m")

THEMES: Dict[str, Dict[str, str]] = {
    "classic": {
        "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
        "blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m",
        "white": "\033[37m", "black": "\033[30m", "gray": "\033[90m"
    },
    "neon": {
        "red": "\033[38;5;196m", "green": "\033[38;5;82m", "yellow": "\033[38;5;226m",
        "blue": "\033[38;5;27m", "magenta": "\033[38;5;201m", "cyan": "\033[38;5;51m",
        "white": "\033[38;5;231m", "black": "\033[30m", "gray": "\033[38;5;244m"
    },
    "retro": {
        "red": "\033[38;5;124m", "green": "\033[38;5;64m", "yellow": "\033[38;5;172m",
        "blue": "\033[38;5;24m", "magenta": "\033[38;5;89m", "cyan": "\033[38;5;30m",
        "white": "\033[38;5;250m", "black": "\033[30m", "gray": "\033[38;5;240m"
    },
    "monochrome": {
        "red": "\033[37m", "green": "\033[37m", "yellow": "\033[37m",
        "blue": "\033[37m", "magenta": "\033[37m", "cyan": "\033[37m",
        "white": "\033[37m", "black": "\033[30m", "gray": "\033[37m"
    },
    "matrix": {
        "red": "\033[38;5;160m", "green": "\033[38;5;46m", "yellow": "\033[38;5;40m",
        "blue": "\033[38;5;22m", "magenta": "\033[38;5;28m", "cyan": "\033[38;5;34m",
        "white": "\033[38;5;46m", "black": "\033[30m", "gray": "\033[38;5;22m"
    }
}


def apply_theme() -> None:
    """Update all Color objects based on current setting in StatsManager."""
    mgr = get_stats_manager()
    settings = mgr.get_settings()
    theme_name = settings.get('theme', 'classic')
    theme = THEMES.get(theme_name, THEMES['classic'])

    C_RED.value = theme['red']
    C_GREEN.value = theme['green']
    C_YELLOW.value = theme['yellow']
    C_BLUE.value = theme['blue']
    C_MAGENTA.value = theme['magenta']
    C_CYAN.value = theme['cyan']
    C_WHITE.value = theme['white']
    C_BLACK.value = theme['black']
    C_GRAY.value = theme.get('gray', "\033[90m")


try:
    apply_theme()
except (AttributeError, KeyError, TypeError):
    pass

# Backgrounds
BG_DARK = "\033[48;5;236m"
BG_LIGHT = "\033[48;5;250m"
BG_CUR = "\033[48;5;220m"
BG_SEL = "\033[48;5;34m"
BG_RED = "\033[41m"
BG_BLUE = "\033[44m"


def beep(event: str = "correct") -> None:
    """Delegate to sound engine's play_sound."""
    play_sound(event)


class Renderer:
    """Handles terminal rendering with FPS control and flicker reduction."""

    def __init__(self, fps: int = 30) -> None:
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.last_frame_time = time.time()
        self.terminal_width = 80
        self.terminal_height = 24
        self._update_terminal_size()
        self.hide_cursor()

    def hide_cursor(self) -> None:
        try:
            print("\033[?25l", end="", flush=True)
        except (OSError, ValueError):
            pass

    def show_cursor(self) -> None:
        try:
            print("\033[?25h", end="", flush=True)
        except (OSError, ValueError):
            pass

    def _update_terminal_size(self) -> None:
        try:
            size = os.get_terminal_size()
            self.terminal_width = size.columns
            self.terminal_height = size.lines
        except (OSError, ValueError):
            pass

    def clear(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def move_to_top(self) -> None:
        print("\033[H", end="", flush=True)

    def render_frame(self, content_callback: Callable[[], None]) -> None:
        now = time.time()
        elapsed = now - self.last_frame_time
        if elapsed < self.frame_time:
            time.sleep(self.frame_time - elapsed)
            now = time.time()
        self.move_to_top()
        content_callback()
        self.last_frame_time = now

    def draw_bar(self, current: float, maximum: float, width: int = 20,
                 label: str = "", color: Color = C_GREEN) -> None:
        percent = min(1.0, max(0.0, current / maximum)) if maximum > 0 else 0
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        print(f"{label} [{color}{bar}{C_RESET}] {int(percent*100)}%")


def get_input_util() -> Callable[[], Optional[str]]:
    if os.name == 'nt':
        import msvcrt
        def getch() -> Optional[str]:
            try:
                ch = msvcrt.getch()
                if ch in (b'\x00', b'\xe0'):
                    ch2 = msvcrt.getch()
                    return {b'H': 'up', b'P': 'down', b'K': 'left', b'M': 'right'}.get(ch2, None)
                return ch.decode('utf-8')
            except (UnicodeDecodeError, AttributeError, TypeError):
                return None
        return getch
    else:
        import termios
        import tty
        def getch() -> Optional[str]:
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


get_key: Callable[[], Optional[str]] = get_input_util()


def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def load_stats() -> Dict[str, Any]:
    return get_stats_manager().get_stats()


def save_stats(stats: Dict[str, Any]) -> None:
    mgr = get_stats_manager()
    mgr.save()


def update_stats(game: str, key: str, value: Any, subkey: Optional[str] = None) -> None:
    mgr = get_stats_manager()
    if subkey:
        stats = mgr.get_stats(game)
        if key not in stats or not isinstance(stats[key], dict):
            if isinstance(stats.get(key), dict):
                pass
            else:
                stats[key] = {}
        if isinstance(stats.get(key), dict):
            stats[key][subkey] = value  # type: ignore
        mgr.update_game_stats(game, stats)
    else:
        mgr.update_game_stats(game, {key: value})


def add_xp(amount: int) -> Dict[str, Any]:
    mgr = get_stats_manager()
    mgr.add_xp(amount)
    return mgr.get_stats()


def get_level_info() -> Tuple[int, int, float]:
    mgr = get_stats_manager()
    return mgr.get_level_and_xp()


def screen_shake(duration: float = 0.3, intensity: int = 1) -> None:
    for _ in range(3):
        print("\033[1;1H", end="")
        if intensity > 0:
            print(" " * intensity)
        time.sleep(duration / 6)
        clear_screen()
        time.sleep(duration / 6)


def particle_effect(char: str = "*", color: Color = C_WHITE, count: int = 10) -> None:
    print(color, end="")
    for _ in range(count):
        print(char, end=" ", flush=True)
        time.sleep(0.01)
    print(C_RESET)


def animated_flash(color: Color = C_RED, duration: float = 0.1, count: int = 1) -> None:
    bg = "\033[41m" if color == C_RED else "\033[47m"
    for _ in range(count):
        print(bg, end="", flush=True)
        clear_screen()
        time.sleep(duration)
        print(C_RESET, end="", flush=True)
        clear_screen()
        time.sleep(duration)


def print_big_title(text: str, color: Color = C_CYAN) -> None:
    border = "═" * (len(text) + 4)
    print(f"{color}╔{border}╗")
    print(f"║  {C_BOLD}{text}{C_RESET}{color}  ║")
    print(f"╚{border}╝{C_RESET}")


def draw_retro_box(width: int, title: str, content_lines: List[str],
                   color: Color = C_CYAN, title_color: Color = C_YELLOW) -> None:
    terminal_width = 80
    try:
        terminal_width = os.get_terminal_size().columns
    except (OSError, ValueError):
        pass

    padding = max(0, (terminal_width - width) // 2)
    indent = " " * padding

    try:
        "╔═╗".encode(sys.stdout.encoding)
        b_tl, b_tr, b_bl, b_br, b_h, b_v, b_ml, b_mr = "╔", "╗", "╚", "╝", "═", "║", "╠", "╣"
    except (UnicodeEncodeError, TypeError):
        b_tl, b_tr, b_bl, b_br, b_h, b_v, b_ml, b_mr = "+", "+", "+", "+", "-", "|", "|", "|"

    print(indent + f"{color}{b_tl}" + b_h * (width - 2) + f"{b_tr}")

    safe_title = u_safe(title)
    stripped_title = strip_ansi(safe_title)
    title_padding = (width - 2 - len(stripped_title)) // 2
    title_line = " " * title_padding + f"{title_color}{C_BOLD}{safe_title}{C_RESET}{color}"
    title_line += " " * (width - 2 - len(stripped_title) - title_padding)
    print(indent + f"{b_v}{title_line}{b_v}")

    print(indent + f"{b_ml}" + b_h * (width - 2) + f"{b_mr}")

    for line in content_lines:
        safe_line = u_safe(line)
        stripped_line = strip_ansi(safe_line)
        content_len = len(stripped_line)
        content_padding = max(0, (width - 2 - content_len) // 2)
        l_text = " " * content_padding + f"{C_WHITE}{safe_line}{C_RESET}{color}"
        l_text += " " * (width - 2 - content_len - content_padding)
        print(indent + f"{b_v}{l_text}{b_v}")

    print(indent + f"{b_bl}" + b_h * (width - 2) + f"{b_br}{C_RESET}")


def show_popup(msg: str, color: Color = C_CYAN, delay: float = 2) -> None:
    clear_screen()
    print("\n" * 5)
    draw_retro_box(40 + len(msg)//2, "POPUP", [msg], color=color)
    time.sleep(delay)
