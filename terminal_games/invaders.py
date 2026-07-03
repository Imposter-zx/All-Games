"""Invaders — a hidden unlockable retro shooter."""

import random
import time
from typing import Any, Dict, List

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


def is_invaders_unlocked() -> bool:
    """Check if invaders is unlocked (5+ achievements)."""
    mgr = get_stats_manager()
    unlocked = mgr.get_unlocked_achievements()
    return len(unlocked) >= 5


class InvadersGame:
    """Terminal Galaga/Space Invaders clone."""

    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty
        diff_config = {"easy": 4, "normal": 6, "hard": 9}
        self.enemy_cols = diff_config.get(difficulty, 6)
        self.width = self.enemy_cols * 6 + 4
        self.player_x = self.width // 2
        self.player_y = 18
        self.enemies: List[Dict[str, Any]] = []
        self.bullets: List[Dict[str, Any]] = []
        self.enemy_bullets: List[Dict[str, Any]] = []
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.dir = 1
        self.move_counter = 0
        self.move_delay = 8
        self.game_over = False
        self.won = False
        self.start_time = 0.0

    def _init_wave(self) -> None:
        self.enemies = []
        for row in range(3):
            for col in range(self.enemy_cols):
                self.enemies.append({
                    "x": 3 + col * 5,
                    "y": 1 + row * 2,
                    "hp": 1,
                    "type": "basic" if row < 2 else "elite",
                })
        self.move_delay = max(3, 8 - (self.wave - 1))

    def play(self) -> dict:
        self.start_time = time.time()
        self._init_wave()
        self.player_x = self.width // 2

        while not self.game_over:
            clear_screen()
            print(f"  {C_RED}INVADERS  {C_WHITE}WAVE:{self.wave}  SCORE:{self.score}  "
                  f"LIVES:{'♥' * self.lives}{C_RESET}")
            print(f"  {C_CYAN}{'─' * (self.width + 2)}{C_RESET}")

            grid: List[List[str]] = [[" "] * (self.width + 2) for _ in range(22)]
            for e in self.enemies:
                if e["hp"] > 0:
                    ch = "▀" if e["type"] == "basic" else "█"
                    color = C_RED if e["type"] == "basic" else C_YELLOW
                    x, y = int(e["x"]), int(e["y"])
                    if 0 <= y < 22 and 0 <= x < self.width:
                        grid[y][x] = f"{color}{ch}{C_RESET}"

            for b in self.bullets:
                x, y = int(b["x"]), int(b["y"])
                if 0 <= y < 22 and 0 <= x < self.width:
                    grid[y][x] = f"{C_GREEN}│{C_RESET}"

            for b in self.enemy_bullets:
                x, y = int(b["x"]), int(b["y"])
                if 0 <= y < 22 and 0 <= x < self.width:
                    grid[y][x] = f"{C_RED}*{C_RESET}"

            px, py = self.player_x, self.player_y
            if 0 <= py < 22 and 0 <= px < self.width:
                grid[py][px] = f"{C_GREEN}▲{C_RESET}"
                if px > 0:
                    grid[py][px - 1] = f"{C_GREEN}◀{C_RESET}"
                if px < self.width:
                    grid[py][px + 1] = f"{C_GREEN}▶{C_RESET}"

            for row in grid:
                print("  " + "".join(str(c) for c in row) + "  ")

            print(f"  {C_CYAN}{'─' * (self.width + 2)}{C_RESET}")
            print(f"  {C_WHITE}[A/D] Move  [SPACE] Fire  [Q] Quit{C_RESET}")

            key = get_key()
            if key and key.lower() == "q":
                self.game_over = True
                break
            if key in ["a", "left"]:
                self.player_x = max(1, self.player_x - 1)
            elif key in ["d", "right"]:
                self.player_x = min(self.width - 1, self.player_x + 1)
            elif key in [" ", "\r", "\n", "enter", "space"]:
                if len(self.bullets) < 2:
                    self.bullets.append({"x": self.player_x, "y": self.player_y - 1})

            self.bullets = [b for b in self.bullets if b["y"] > 0]
            self.enemy_bullets = [b for b in self.enemy_bullets if b["y"] < 22]
            for b in self.bullets:
                b["y"] -= 1
            for b in self.enemy_bullets:
                b["y"] += 1

            for b in list(self.bullets):
                for e in list(self.enemies):
                    if e["hp"] > 0 and abs(b["x"] - e["x"]) < 2 and abs(b["y"] - e["y"]) < 1:
                        e["hp"] -= 1
                        self.score += 50 if e["type"] == "elite" else 25
                        self.bullets.remove(b)
                        break

            self.move_counter += 1
            if self.move_counter >= self.move_delay:
                self.move_counter = 0
                lowest = 0
                for e in self.enemies:
                    if e["hp"] > 0:
                        e["x"] += self.dir
                        lowest = max(lowest, int(e["y"]))
                leftmost = min((e["x"] for e in self.enemies if e["hp"] > 0), default=10)
                rightmost = max((e["x"] for e in self.enemies if e["hp"] > 0), default=10)
                if rightmost >= self.width - 1 or leftmost <= 1:
                    self.dir *= -1
                if random.random() < 0.15:
                    living = [e for e in self.enemies if e["hp"] > 0]
                    if living:
                        shooter = random.choice(living)
                        self.enemy_bullets.append({"x": shooter["x"], "y": shooter["y"] + 1})

            for b in list(self.enemy_bullets):
                if abs(b["x"] - self.player_x) < 2 and abs(b["y"] - self.player_y) < 1:
                    self.lives -= 1
                    self.enemy_bullets.remove(b)
                    if self.lives <= 0:
                        self.game_over = True
                        break

            alive = sum(1 for e in self.enemies if e["hp"] > 0)
            if alive == 0:
                self.wave += 1
                self.score += 500
                self._init_wave()
                self.player_x = self.width // 2

            if self.game_over:
                break

            time.sleep(0.05)

        total_xp = self.score // 10
        from xp_config import get_xp_system
        xp_sys = get_xp_system(self.difficulty)
        final_xp = xp_sys.calculate_xp("invaders", total_xp)

        mgr = get_stats_manager()
        mgr.add_xp(final_xp)
        elapsed = int(time.time() - self.start_time)
        mgr.record_session("Invaders", self.score, final_xp, elapsed, self.difficulty)

        clear_screen()
        print(f"\n  {C_RED}{C_BOLD}INVADERS — GAME OVER{C_RESET}")
        print(f"  {C_YELLOW}Score: {self.score}{C_RESET}")
        print(f"  {C_GREEN}Waves: {self.wave}{C_RESET}")
        print(f"  {C_MAGENTA}XP: {final_xp}{C_RESET}")
        print(f"\n  {C_WHITE}[Any Key] Continue{C_RESET}")
        get_key()

        return {"score": self.score, "xp_earned": final_xp, "high_score": self.score,
                "duration_seconds": elapsed}


def play_invaders(difficulty: str = "normal") -> dict:
    return InvadersGame(difficulty).play()
