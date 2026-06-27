"""Terminal rhythm game — notes fall, press matching keys in time."""
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


class RhythmGame:
    """Terminal rhythm game with falling notes."""

    LANES = [
        ("D", C_RED, "d"),
        ("F", C_GREEN, "f"),
        ("J", C_YELLOW, "j"),
        ("K", C_CYAN, "k"),
    ]

    DIFFICULTIES: Dict[str, Dict[str, Any]] = {
        "easy": {"speed": 0.4, "interval": 0.8, "max_notes": 30, "lane_count": 3},
        "normal": {"speed": 0.3, "interval": 0.6, "max_notes": 40, "lane_count": 4},
        "hard": {"speed": 0.2, "interval": 0.4, "max_notes": 60, "lane_count": 4},
    }

    SONGS: List[Dict[str, Any]] = [
        {"name": "Classic Beat", "bpm": 120, "pattern": "base"},
        {"name": "Synthwave", "bpm": 140, "pattern": "synth"},
        {"name": "Speed Core", "bpm": 180, "pattern": "speed"},
    ]

    def __init__(self, difficulty: str = "normal", song_idx: int = 0):
        self.difficulty = difficulty
        self.config = self.DIFFICULTIES.get(difficulty, self.DIFFICULTIES["normal"])
        self.song = self.SONGS[song_idx % len(self.SONGS)]
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.notes_hit = 0
        self.notes_missed = 0
        self.notes: List[dict] = []
        self.active_notes: List[dict] = []
        self.total_notes = 0
        self.start_time = 0.0
        self.elapsed = 0.0
        self.finished = False

    def _generate_notes(self) -> None:
        pattern_type = self.song["pattern"]
        max_notes = self.config["max_notes"]
        lane_count = self.config["lane_count"]
        interval = self.config["interval"]

        if pattern_type == "synth":
            for i in range(max_notes):
                lane = random.randint(0, lane_count - 1)
                offset = random.uniform(-0.1, 0.1) if i % 3 == 0 else 0
                self.notes.append({
                    "lane": lane,
                    "beat": i * interval + offset,
                    "hit": False,
                })
        elif pattern_type == "speed":
            for i in range(max_notes):
                lane = i % lane_count
                speed_interval = interval * (0.5 + (i / max_notes) * 0.5)
                self.notes.append({
                    "lane": lane,
                    "beat": sum(speed_interval for _ in range(i)),
                    "hit": False,
                })
        else:
            for i in range(max_notes):
                lane = random.randint(0, lane_count - 1)
                self.notes.append({
                    "lane": lane,
                    "beat": i * interval + random.uniform(-0.05, 0.05),
                    "hit": False,
                })

        self.total_notes = len(self.notes)

    def play(self) -> dict:
        self._generate_notes()
        lane_count = self.config["lane_count"]
        speed = self.config["speed"]
        lane_keys = {self.LANES[li][2]: li for li in range(lane_count)}

        self.start_time = time.time()

        note_idx = 0
        last_render = 0.0
        lane_glow: Dict[int, float] = {}

        clear_screen()
        print(f"\n  {C_MAGENTA}{C_BOLD}♫ {self.song['name']} — {self.difficulty.upper()} ♫{C_RESET}")
        print(f"  {C_WHITE}Press D F J K as notes reach the line!{C_RESET}")
        print(f"  {C_WHITE}Press Q to quit anytime.{C_RESET}")
        print()
        time.sleep(1.5)
        clear_screen()

        self.start_time = time.time()

        while not self.finished:
            now = time.time()
            self.elapsed = now - self.start_time
            beat = self.elapsed

            if note_idx < self.total_notes and beat >= self.notes[note_idx]["beat"]:
                self.active_notes.append(self.notes[note_idx])
                note_idx += 1

            if note_idx >= self.total_notes and not self.active_notes:
                self.finished = True
                break

            if now - last_render >= 0.05:
                last_render = now
                clear_screen()

                print(f"  {C_MAGENTA}{C_BOLD}♫ {self.song['name']}{C_RESET}  "
                      f"{C_YELLOW}{self.difficulty.upper()}{C_RESET}  "
                      f"{C_WHITE}SCORE: {self.score}{C_RESET}")
                if self.combo >= 5:
                    combo_color = C_GREEN if self.combo < 15 else C_YELLOW if self.combo < 30 else C_MAGENTA
                    print(f"  {combo_color}COMBO: x{self.combo}{C_RESET}")
                print()

                for y in range(12, 0, -1):
                    beat_pos = beat + y * speed
                    line = "  "
                    for lane_idx in range(lane_count):
                        line += "    "
                        draw = False
                        for n in self.active_notes:
                            if n["lane"] != lane_idx or n["hit"]:
                                continue
                            if abs(n["beat"] - beat_pos) < speed * 0.6:
                                draw = True
                                break
                        line += f"{C_WHITE}♩{C_RESET}" if draw else " "
                    print(line)

                print(f"  {'─' * (lane_count * 5)}")

                glow_str = "  "
                for lane_idx in range(lane_count):
                    key_label, key_color, _ = self.LANES[lane_idx]
                    glow = lane_idx in lane_glow and time.time() - lane_glow[lane_idx] < 0.15
                    if glow:
                        glow_str += f" {C_BOLD}{key_color}[{key_label}]{C_RESET} "
                    else:
                        glow_str += f"  {key_color}{key_label}{C_RESET}  "
                print(glow_str)

                if self.combo >= 5:
                    pass

            key = get_key()
            if key:
                if key.lower() == "q":
                    self.finished = True
                    break

                if key.lower() in lane_keys:
                    lane = lane_keys[key.lower()]
                    hit = False
                    for n in self.active_notes:
                        if n["lane"] == lane and not n["hit"]:
                            timing = abs(self.elapsed - n["beat"])
                            if timing < 0.2:
                                self.notes_hit += 1
                                self.combo += 1
                                self.max_combo = max(self.max_combo, self.combo)
                                bonus = 50 if timing < 0.08 else (30 if timing < 0.14 else 10)
                                self.score += max(10, 100 + bonus * self.combo)
                                n["hit"] = True
                                lane_glow[lane] = time.time()
                                hit = True
                                break

                    if not hit:
                        self.combo = 0
                        self.notes_missed += 1

            self.active_notes = [n for n in self.active_notes if not n["hit"]
                                 and self.elapsed - n["beat"] < 1.0]

        total_xp = self.score // 10
        from xp_config import get_xp_system
        xp_sys = get_xp_system(self.difficulty)
        final_xp = xp_sys.calculate_xp("rhythm", total_xp)

        from stats_manager import get_stats_manager
        mgr = get_stats_manager()
        mgr.add_xp(final_xp)
        mgr.record_session("Rhythm Game", self.score, final_xp, 0, self.difficulty)

        clear_screen()
        print(f"\n  {C_MAGENTA}{C_BOLD}♫ RHYTHM COMPLETE! ♫{C_RESET}")
        print(f"\n  {C_YELLOW}Score:     {C_WHITE}{self.score}{C_RESET}")
        print(f"  {C_YELLOW}Max Combo: {C_GREEN}x{self.max_combo}{C_RESET}")
        print(f"  {C_YELLOW}Hit:       {C_GREEN}{self.notes_hit}{C_RESET}  "
              f"{C_YELLOW}Miss: {C_RED}{self.notes_missed}{C_RESET}")
        print(f"  {C_YELLOW}Accuracy:  {C_WHITE}"
              f"{self.notes_hit / max(1, self.notes_hit + self.notes_missed) * 100:.0f}%{C_RESET}")
        print(f"  {C_MAGENTA}XP Earned: {final_xp}{C_RESET}")
        print(f"\n  {C_WHITE}[Any Key] Continue{C_RESET}")
        get_key()

        return {
            "score": self.score,
            "xp_earned": final_xp,
            "high_score": self.score,
            "duration_seconds": int(self.elapsed),
        }


def play_rhythm(difficulty: str = "normal") -> dict:
    return RhythmGame(difficulty).play()
