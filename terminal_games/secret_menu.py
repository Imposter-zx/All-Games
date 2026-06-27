"""Easter egg system — Konami code unlocks secret content."""
import random
import time
from typing import Callable, Optional

from arcade_utils import (
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    clear_screen,
    get_key,
    show_popup,
)
from sound_engine import play_sound

KONAMI_CODE: list[str] = ["up", "up", "down", "down", "left", "right", "left", "right", "b", "a"]
_entry: list[str] = []
_unlocked: bool = False

SECRET_PHRASES: list[str] = [
    "You found the DEBUG ROOM...",
    "REALITY INDEX: CORRUPTED",
    "The arcade remembers everything.",
    "Hello, World. From the other side.",
    "▓▓▓▓▓▓▓▓▓▓ LOADING...",
    "TIP: Try pressing Q in the secret menu.",
    "There is no spoon. Only bytes.",
    "SYSTEM: ARCADE OS v∞.∞.∞",
    "▓▓▓▓▓▓▓▓▓▓ ADMIN ACCESS GRANTED",
    ">> The games are playing YOU.",
]


def feed_key(key: str) -> bool:
    """Feed a key to the Konami code detector. Returns True if code complete."""
    global _entry, _unlocked
    if _unlocked:
        return False
    if not key:
        return False
    k = key.lower().strip()
    _entry.append(k)
    expected = KONAMI_CODE[len(_entry) - 1]
    if k != expected:
        _entry = []
        return False
    if len(_entry) == len(KONAMI_CODE):
        _unlocked = True
        _entry = []
        return True
    return False


def is_unlocked() -> bool:
    return _unlocked


def reset() -> None:
    global _unlocked, _entry
    _unlocked = False
    _entry = []


def show_secret_menu(
    on_marathon: Optional[Callable] = None,
    on_boss: Optional[Callable] = None,
    on_chaos_toggle: Optional[Callable[[bool], None]] = None,
    on_rhythm: Optional[Callable] = None,
) -> bool:
    """Show the secret developer menu. Returns True if user wants to quit arcade."""
    from chaos_mutator import is_chaos, set_chaos

    chaos_state = is_chaos()
    selection = 0
    options = [
        "MARATHON MODE — Play all 36 games!",
        f"CHAOS MODE — {'ON' if chaos_state else 'OFF'}",
        "SECRET BOSS — The Final Challenge",
        "RHYTHM GAME — Terminal beats",
        "EASTER EGG OS — Hack the mainframe",
        "Back to Arcade",
    ]

    while True:
        clear_screen()
        lines: list[str] = [
            "",
            f"{C_RED}╔═══════════════════════════════════════╗{C_RESET}",
            f"{C_RED}║     !!  SECRET DEVELOPER MENU  !!     ║{C_RESET}",
            f"{C_RED}╚═══════════════════════════════════════╝{C_RESET}",
            "",
            f"{C_GREEN}{random.choice(SECRET_PHRASES)}{C_RESET}",
            "",
        ]
        for i, opt in enumerate(options):
            marker = f"{C_YELLOW}►{C_RESET}" if i == selection else " "
            lines.append(f"  {marker}  {opt}")
        lines.append("")
        lines.append(f"{C_WHITE}[↑↓] Navigate  [ENTER] Select  [Q] Back{C_RESET}")

        for line in lines:
            print(line)

        key = get_key()
        if key == "up":
            selection = (selection - 1) % len(options)
            play_sound("move")
        elif key == "down":
            selection = (selection + 1) % len(options)
            play_sound("move")
        elif key in ["\r", "\n", " ", "enter"]:
            play_sound("win")
            if selection == 0 and on_marathon:
                on_marathon()
            elif selection == 1:
                chaos_state = not chaos_state
                set_chaos(chaos_state)
                options[1] = f"CHAOS MODE — {'ON' if chaos_state else 'OFF'}"
                show_popup(f"Chaos Mode: {'ACTIVATED' if chaos_state else 'DEACTIVATED'}", C_MAGENTA)
            elif selection == 2 and on_boss:
                on_boss()
            elif selection == 3 and on_rhythm:
                on_rhythm()
            elif selection == 4:
                _show_easter_egg_os()
            elif selection == 5:
                reset()
                return False
        elif key and key.lower() == "q":
            reset()
            return False


def _show_easter_egg_os() -> None:
    """Fake terminal OS with filesystem and secrets."""
    fake_fs: dict[str, dict] = {
        "/": {"type": "dir", "children": ["home", "etc", "var", "usr"]},
        "/home": {"type": "dir", "children": ["player", "guest"]},
        "/home/player": {
            "type": "dir",
            "children": ["notes.txt", ".secret", "games.log", "config.cfg"],
        },
        "/home/player/notes.txt": {
            "type": "file",
            "content": [
                "ARCADE DEVELOPMENT NOTES",
                "=========================",
                "- All games must pass lint",
                "- Theme system uses 256-color ANSI",
                "- TODO: Add more easter eggs",
                "- The Konami code was here all along...",
            ],
        },
        "/home/player/.secret": {
            "type": "file",
            "content": [
                "CLASSIFIED",
                "==========",
                "To unlock the BOSS FIGHT:",
                "  Get 1000+ XP in any single game",
                "  then press K on the main menu.",
                "",
                "Or just access it from the secret menu.",
                "You already found it. Nice.",
            ],
        },
        "/home/player/games.log": {
            "type": "file",
            "content": [
                "[LOG] Session started",
                "[LOG] 36 games loaded",
                "[LOG] Theme: classic",
                "[LOG] Achievements: 80+ registered",
                "[LOG] Chaos mode: available",
                "[LOG] Marathon: uncharted",
                f"[LOG] Last boot: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            ],
        },
        "/home/player/config.cfg": {
            "type": "file",
            "content": [
                "# Player Configuration",
                "name = RETRO_MASTER",
                "sound = on",
                "theme = classic",
                "cheats = enabled",
                "fps = 60",
                "renderer = retro",
            ],
        },
        "/etc": {
            "type": "dir",
            "children": ["passwd", "hosts", "motd"],
        },
        "/etc/motd": {
            "type": "file",
            "content": [
                "Welcome to the Retro Terminal Arcade.",
                "All 36 games are ready.",
                "Have fun. Or else.",
            ],
        },
        "/etc/passwd": {
            "type": "file",
            "content": [
                "root:x:0:0:root:/root:/bin/bash",
                "player:x:1000:1000:Player:/home/player:/bin/arcade",
            ],
        },
    }

    cwd = "/home/player"
    running = True

    while running:
        clear_screen()
        print(f"{C_GREEN}╔═══════════════════════════════════════╗{C_RESET}")
        print(f"{C_GREEN}║   RETRO OS v3.1.4 — TERMINAL MODE    ║{C_RESET}")
        print(f"{C_GREEN}╚═══════════════════════════════════════╝{C_RESET}")
        print()
        print(f"  {C_CYAN}Type 'help' for commands. 'exit' to quit.{C_RESET}")
        print()

        while running:
            prompt = f"{C_GREEN}{cwd}${C_RESET} "
            print(prompt, end="", flush=True)
            cmd_input = ""
            while True:
                ch = get_key()
                if ch in ["\r", "\n", "enter"]:
                    print()
                    break
                elif ch and ch.lower() == "q" and not cmd_input:
                    running = False
                    break
                elif ch and ch in ["backspace", "\b", "\x7f"]:
                    if cmd_input:
                        cmd_input = cmd_input[:-1]
                        print("\b \b", end="", flush=True)
                elif ch and len(ch) == 1 and ch.isprintable():
                    cmd_input += ch
                    print(ch, end="", flush=True)

            if not running:
                break

            parts = cmd_input.strip().lower().split()
            if not parts:
                continue

            cmd = parts[0]

            if cmd == "exit" or cmd == "q":
                running = False
            elif cmd == "help":
                print(f"  {C_YELLOW}Available commands:{C_RESET}")
                print(f"  {C_GREEN}ls{C_RESET}     List directory contents")
                print(f"  {C_GREEN}cd{C_RESET}     Change directory")
                print(f"  {C_GREEN}cat{C_RESET}    Read a file")
                print(f"  {C_GREEN}clear{C_RESET}  Clear screen")
                print(f"  {C_GREEN}whoami{C_RESET} Who are you?")
                print(f"  {C_GREEN}date{C_RESET}   Show current date")
                print(f"  {C_GREEN}neofetch{C_RESET} System info")
                print(f"  {C_GREEN}exit/Ctrl+C{C_RESET}  Go back")
            elif cmd == "ls":
                target = parts[1] if len(parts) > 1 else cwd
                if target in fake_fs and fake_fs[target]["type"] == "dir":
                    for child in fake_fs[target]["children"]:
                        full = target.rstrip("/") + "/" + child
                        if full in fake_fs and fake_fs[full]["type"] == "dir":
                            print(f"  {C_CYAN}{child}/{C_RESET}")
                        else:
                            print(f"  {C_WHITE}{child}{C_RESET}")
                else:
                    print(f"  {C_RED}ls: {target}: No such directory{C_RESET}")
            elif cmd == "cd":
                if len(parts) < 2:
                    cwd = "/"
                elif parts[1] == "..":
                    if cwd != "/":
                        cwd = "/" + "/".join(cwd.strip("/").split("/")[:-1]) if cwd.count("/") > 1 else "/"
                else:
                    target = cwd.rstrip("/") + "/" + parts[1]
                    if target in fake_fs and fake_fs[target]["type"] == "dir":
                        cwd = target
                    else:
                        print(f"  {C_RED}cd: {parts[1]}: No such directory{C_RESET}")
            elif cmd == "cat":
                if len(parts) < 2:
                    print(f"  {C_RED}Usage: cat <filename>{C_RESET}")
                else:
                    target = cwd.rstrip("/") + "/" + parts[1]
                    if target in fake_fs and fake_fs[target]["type"] == "file":
                        for line in fake_fs[target]["content"]:
                            print(f"  {line}")
                    else:
                        print(f"  {C_RED}cat: {parts[1]}: No such file{C_RESET}")
            elif cmd == "clear":
                clear_screen()
                print(f"{C_GREEN}╔═══════════════════════════════════════╗{C_RESET}")
                print(f"{C_GREEN}║   RETRO OS v3.1.4 — TERMINAL MODE    ║{C_RESET}")
                print(f"{C_GREEN}╚═══════════════════════════════════════╝{C_RESET}")
                print()
                print(f"  {C_CYAN}Type 'help' for commands. 'exit' to quit.{C_RESET}")
                print()
            elif cmd == "whoami":
                print(f"  {C_GREEN}player{C_RESET}")
            elif cmd == "date":
                print(f"  {C_YELLOW}{time.strftime('%a %b %d %H:%M:%S %Y')}{C_RESET}")
            elif cmd == "neofetch":
                print(f"  {C_CYAN}OS:{C_RESET} Retro Arcade OS v3.1.4")
                print(f"  {C_CYAN}Kernel:{C_RESET} Python 3.11")
                print(f"  {C_CYAN}Shell:{C_RESET} retro-sh")
                print(f"  {C_CYAN}Games:{C_RESET} 36")
                print(f"  {C_CYAN}Terminal:{C_RESET} ANSI 256-color")
                print(f"  {C_CYAN}Theme:{C_RESET} classic")
                print(f"  {C_CYAN}Uptime:{C_RESET} 84 years, 3 days")
            else:
                print(f"  {C_RED}bash: {cmd}: command not found{C_RESET}")
