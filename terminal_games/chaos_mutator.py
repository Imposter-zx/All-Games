"""Chaos Mutator system — applies random game-altering effects."""
import random
import time
from typing import Any, Callable, Dict, Optional

from arcade_utils import (
    C_BOLD,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    animated_flash,
    clear_screen,
    screen_shake,
)

CHAOS_EFFECTS: list[str] = [
    "speed_surge",
    "speed_slow",
    "screen_shake",
    "invert_colors",
    "color_flash",
    "mirror_input",
    "teleport",
    "glitch_text",
]

EFFECT_NAMES: Dict[str, str] = {
    "speed_surge": "SPEED SURGE!",
    "speed_slow": "SLOW MOTION!",
    "screen_shake": "EARTHQUAKE!",
    "invert_colors": "NEGATIVE WORLD!",
    "color_flash": "DISCO STROBE!",
    "mirror_input": "MIRROR DIMENSION!",
    "teleport": "WORMHOLE!",
    "glitch_text": "GLITCH OVERLOAD!",
}

EFFECT_COLORS: Dict[str, str] = {
    "speed_surge": C_RED,
    "speed_slow": C_MAGENTA,
    "screen_shake": C_YELLOW,
    "invert_colors": C_GREEN,
    "color_flash": C_YELLOW,
    "mirror_input": C_MAGENTA,
    "teleport": C_WHITE,
    "glitch_text": C_GREEN,
}

_chaos_active: bool = False
_current_effects: dict[str, Any] = {}


def set_chaos(enabled: bool) -> None:
    global _chaos_active
    _chaos_active = enabled


def is_chaos() -> bool:
    return _chaos_active


def apply_chaos(effects: Optional[list[str]] = None) -> dict[str, Any]:
    global _current_effects
    if not _chaos_active:
        _current_effects = {}
        return _current_effects

    if effects is None:
        chosen = random.sample(CHAOS_EFFECTS, random.randint(1, 3))
    else:
        chosen = effects if isinstance(effects, list) else [effects]

    _current_effects = {e: _effect_params(e) for e in chosen}
    return _current_effects


def _effect_params(effect: str) -> dict[str, Any]:
    params: dict[str, Any] = {"active": True, "duration": random.uniform(3, 8)}
    if effect == "speed_surge":
        params["multiplier"] = random.uniform(1.5, 3.0)
    elif effect == "speed_slow":
        params["multiplier"] = random.uniform(0.2, 0.5)
    elif effect == "mirror_input":
        params["axis"] = random.choice(["h", "v"])
    elif effect == "color_flash":
        params["interval"] = random.uniform(0.05, 0.15)
        params["count"] = random.randint(5, 15)
    return params


def get_active_effects() -> dict[str, Any]:
    return _current_effects


def clear_effects() -> None:
    global _current_effects
    _current_effects = {}


def trigger_chaos_event() -> str:
    if not _chaos_active:
        return ""
    effects = apply_chaos()
    if not effects:
        return ""
    primary = list(effects.keys())[0]
    color = EFFECT_COLORS.get(primary, C_RED)
    name = EFFECT_NAMES.get(primary, "CHAOS!")
    clear_screen()
    print("\n" * 5)
    print(" " * 30 + f"{color}╔═══════════════════════════╗{C_RESET}")
    print(" " * 30 + f"{color}║     ⚡{C_BOLD} CHAOS STRIKES! ⚡{C_RESET}{color}    ║{C_RESET}")
    print(" " * 30 + f"{color}║                           ║{C_RESET}")
    print(" " * 30 + f"{color}║   {C_BOLD}{name:>20}{C_RESET}{color}   ║{C_RESET}")
    print(" " * 30 + f"{color}╚═══════════════════════════╝{C_RESET}")
    time.sleep(1.5)

    if "screen_shake" in effects:
        screen_shake(duration=0.5, intensity=2)
    if "color_flash" in effects:
        p = effects["color_flash"]
        animated_flash(duration=p.get("interval", 0.1), count=p.get("count", 8))

    return primary


def chaos_time_multiplier() -> float:
    if not _chaos_active:
        return 1.0
    m = 1.0
    for e, p in _current_effects.items():
        if e == "speed_surge":
            m *= p.get("multiplier", 1.5)
        elif e == "speed_slow":
            m *= p.get("multiplier", 0.3)
    return m


def chaos_mutate_input(key: str) -> str:
    if not _chaos_active:
        return key
    if "mirror_input" not in _current_effects:
        return key
    mirror_map = {
        "up": "down", "down": "up",
        "left": "right", "right": "left",
        "w": "s", "s": "w", "a": "d", "d": "a",
    }
    return mirror_map.get(key, key)


def chaos_decorator(func: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not _chaos_active:
            return func(*args, **kwargs)
        trigger_chaos_event()
        result = func(*args, **kwargs)
        clear_effects()
        return result
    return wrapper


def cycle_chaos_effect() -> None:
    if not _chaos_active:
        return
    apply_chaos()
