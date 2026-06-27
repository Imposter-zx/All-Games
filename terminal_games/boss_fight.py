"""Secret Boss Fight — a meta-game combining mechanics from multiple games."""
import random
import time

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


class BossFight:
    """A multi-phase boss fight mashing up game mechanics."""

    def __init__(self) -> None:
        self.phase = 0
        self.boss_hp = 100
        self.player_hp = 100
        self.turn = 0
        self.score = 0
        self.phase_names = [
            "QUICKSHOT — Dodge the falling blocks!",
            "MEMORY — Match the pattern!",
            "REFLEX — Press the right key!",
            "FINAL — All-out assault!",
        ]

    def play(self) -> dict:
        clear_screen()
        print("\n" * 3)
        print(f"  {C_RED}{C_BOLD}╔═══════════════════════════════════════╗{C_RESET}")
        print(f"  {C_RED}{C_BOLD}║      !!  SECRET BOSS FIGHT  !!        ║{C_RESET}")
        print(f"  {C_RED}{C_BOLD}╚═══════════════════════════════════════╝{C_RESET}")
        print()
        print(f"  {C_YELLOW}A mysterious entity emerges from the arcade...{C_RESET}")
        print(f"  {C_WHITE}Defeat the FINAL BOSS across 4 phases!{C_RESET}")
        print()
        print(f"  {C_CYAN}Boss HP: {self.boss_hp}")
        print(f"  Your HP: {self.player_hp}")
        print()
        print(f"  {C_WHITE}[Press ENTER to begin]{C_RESET}")

        while True:
            key = get_key()
            if key in ["\r", "\n", " ", "enter"]:
                break

        for phase_idx in range(4):
            self.phase = phase_idx
            if self.player_hp <= 0:
                break
            result = self._run_phase()
            if not result:
                break

        return self._game_result()

    def _game_result(self) -> dict:
        xp = max(0, self.score * 10)
        from xp_config import get_xp_system
        xp_sys = get_xp_system("hard")
        final_xp = xp_sys.calculate_xp("boss_fight", xp)

        mgr = get_stats_manager()
        mgr.add_xp(final_xp)
        mgr.record_session("Secret Boss", self.score, final_xp, 0, "hard")

        clear_screen()
        print("\n" * 2)
        if self.boss_hp <= 0:
            print(f"  {C_GREEN}{C_BOLD}╔═══════════════════════════════╗{C_RESET}")
            print(f"  {C_GREEN}{C_BOLD}║    BOSS DEFEATED! VICTORY!    ║{C_RESET}")
            print(f"  {C_GREEN}{C_BOLD}╚═══════════════════════════════╝{C_RESET}")
            print(f"  {C_YELLOW}Score: {self.score}{C_RESET}")
            print(f"  {C_MAGENTA}XP Earned: {final_xp}{C_RESET}")
        else:
            print(f"  {C_RED}╔═══════════════════════════════╗{C_RESET}")
            print(f"  {C_RED}║         YOU DIED...           ║{C_RESET}")
            print(f"  {C_RED}╚═══════════════════════════════╝{C_RESET}")
            print(f"  {C_YELLOW}Score: {self.score}{C_RESET}")
            print(f"  {C_MAGENTA}XP Earned: {final_xp}{C_RESET}")

        print(f"\n  {C_WHITE}[Press any key to continue]{C_RESET}")
        get_key()

        return {
            "score": self.score,
            "xp_earned": final_xp,
            "high_score": self.score,
            "duration_seconds": 0,
            "boss_defeated": self.boss_hp <= 0,
        }

    def _run_phase(self) -> bool:
        if self.phase == 0:
            return self._phase_quickshot()
        elif self.phase == 1:
            return self._phase_memory()
        elif self.phase == 2:
            return self._phase_reflex()
        elif self.phase == 3:
            return self._phase_final()
        return True

    def _show_hp(self) -> None:
        bhp_bar = "█" * (self.boss_hp // 10) + "░" * (10 - self.boss_hp // 10)
        php_bar = "█" * (self.player_hp // 10) + "░" * (10 - self.player_hp // 10)
        print(f"  {C_RED}BOSS: [{bhp_bar}] {self.boss_hp}%{C_RESET}")
        print(f"  {C_GREEN}YOU:  [{php_bar}] {self.player_hp}%{C_RESET}")
        print(f"  {C_YELLOW}SCORE: {self.score}{C_RESET}")
        print()

    def _phase_quickshot(self) -> bool:
        """Dodge falling blocks by pressing correct keys."""
        clear_screen()
        print(f"\n  {C_MAGENTA}{C_BOLD}PHASE 1: QUICKSHOT{C_RESET}")
        print(f"  {C_WHITE}Blocks are falling! Press the matching key to destroy them!{C_RESET}")
        print(f"  {C_WHITE}Keys: W A S D — Miss 3 and take damage!{C_RESET}\n")
        time.sleep(2)

        mistakes = 0
        targets = ["w", "a", "s", "d"]

        for wave in range(10):
            clear_screen()
            print(f"\n  {C_MAGENTA}{C_BOLD}PHASE 1: QUICKSHOT — Wave {wave + 1}/10{C_RESET}\n")
            self._show_hp()

            target = random.choice(targets)
            dirs = {"w": "↑ UP", "a": "← LEFT", "s": "↓ DOWN", "d": "→ RIGHT"}
            print(f"  {C_YELLOW}{dirs[target]} block incoming!{C_RESET}")
            print(f"  {' ' * 10}{'▓' * 5}")
            print(f"  {' ' * 8}{'▓' * 9}")
            print(f"  {' ' * 6}{'▓' * 13}")
            print(f"  {' ' * 4}{'▓' * 17}")
            print(f"  {' ' * 2}{'▓' * 21}")
            print(f"  {'▓' * 25}")
            print()

            start = time.time()
            pressed = False
            while time.time() - start < 2.0:
                key = get_key()
                if key and key.lower() == target:
                    self.score += 100
                    print(f"  {C_GREEN}DIRECT HIT! +100{C_RESET}")
                    time.sleep(0.3)
                    pressed = True
                    break
                elif key and key.lower() in targets:
                    print(f"  {C_RED}MISS!{C_RESET}")
                    mistakes += 1
                    if mistakes >= 3:
                        self.player_hp -= 15
                        print(f"  {C_RED}TOO MANY MISSES! -15 HP{C_RESET}")
                        mistakes = 0
                        time.sleep(1)
                    pressed = True
                    break
            if not pressed:
                self.boss_hp -= 5
                print(f"  {C_GREEN}Boss takes 5 damage from timeout!{C_RESET}")
                time.sleep(0.5)

            if self.player_hp <= 0:
                return False
            if self.boss_hp <= 0:
                return True

        self.boss_hp -= 15
        if self.boss_hp < 0:
            self.boss_hp = 0
        return self.player_hp > 0

    def _phase_memory(self) -> bool:
        """Simon Says style memory pattern."""
        clear_screen()
        print(f"\n  {C_MAGENTA}{C_BOLD}PHASE 2: MEMORY CHALLENGE{C_RESET}")
        print(f"  {C_WHITE}Watch the pattern! Repeat it to damage the boss!{C_RESET}")
        print(f"  {C_WHITE}Keys: 1 2 3 4 (matching colored positions){C_RESET}\n")
        time.sleep(2)

        colors = [C_RED, C_GREEN, C_YELLOW, C_CYAN]
        pattern: list[int] = []
        round_num = 1

        while round_num <= 5:
            clear_screen()
            print(f"\n  {C_MAGENTA}{C_BOLD}PHASE 2: MEMORY — Round {round_num}/5{C_RESET}\n")
            self._show_hp()

            pattern.append(random.randint(0, 3))
            pattern_len = len(pattern)

            print(f"  {C_YELLOW}Watch...{C_RESET}")
            time.sleep(0.5)

            for idx in pattern:
                clear_screen()
                print(f"\n  {C_MAGENTA}{C_BOLD}MEMORY PATTERN{C_RESET}\n")
                print(f"  {colors[idx]}████████{C_RESET}")
                print(f"  {colors[idx]}████████{C_RESET}")
                print(f"  {colors[idx]}████████{C_RESET}")
                print(f"  {C_CYAN}    {idx + 1}{C_RESET}")
                time.sleep(0.6)
                clear_screen()

            print(f"\n  {C_YELLOW}Your turn! Press keys 1-4 in order:{C_RESET}")
            for i, expected in enumerate(pattern):
                while True:
                    key = get_key()
                    if key in ["1", "2", "3", "4"]:
                        val = int(key) - 1
                        if val == expected:
                            print(f"  {C_GREEN}✓{C_RESET}", end=" ", flush=True)
                            break
                        else:
                            print(f"\n  {C_RED}Wrong! Take damage!{C_RESET}")
                            self.player_hp -= 10
                            time.sleep(1)
                            if self.player_hp <= 0:
                                return False
                            return True

            self.score += pattern_len * 50
            self.boss_hp -= 10
            print(f"\n  {C_GREEN}Pattern complete! +{pattern_len * 50}pts, boss -10HP{C_RESET}")
            time.sleep(1)
            round_num += 1

            if self.boss_hp <= 0:
                self.boss_hp = 0
                return True

        return self.player_hp > 0

    def _phase_reflex(self) -> bool:
        """Quick-time event style reflex challenge."""
        clear_screen()
        print(f"\n  {C_MAGENTA}{C_BOLD}PHASE 3: REFLEX CHALLENGE{C_RESET}")
        print(f"  {C_WHITE}Quick! React to the symbols on screen!{C_RESET}")
        print(f"  {C_WHITE}Press the matching key before time runs out!{C_RESET}\n")
        time.sleep(2)

        challenges = [
            ("Press SPACE when the bar fills!", " ", [0.5, 0.8, 1.2]),
            ("Type the letter: ", "hijklmnpqrtuvxyzw"),
            ("Hit ENTER on the count of 3!", "\r"),
        ]

        for round_num in range(8):
            clear_screen()
            print(f"\n  {C_MAGENTA}{C_BOLD}PHASE 3: REFLEX — Round {round_num + 1}/8{C_RESET}\n")
            self._show_hp()

            chall = random.choice(challenges)
            prompt = chall[0]

            if chall[1] == " ":
                print(f"  {C_YELLOW}{prompt}{C_RESET}")
                delay = random.uniform(1.0, 3.0)
                fill_chars = ["░", "▒", "▓", "█"]
                for i in range(20):
                    bar = fill_chars[-1] * i + "░" * (20 - i)
                    print(f"\r  {C_CYAN}[{bar}]{C_RESET}", end="", flush=True)
                    time.sleep(delay / 20)
                print()
                start = time.time()
                key = None
                while time.time() - start < 0.5:
                    k = get_key()
                    if k is not None:
                        key = k
                        break
                if key in [" ", "\r", "\n", "enter"]:
                    self.score += 150
                    print(f"  {C_GREEN}PERFECT! +150pts{C_RESET}")
                else:
                    self.player_hp -= 10
                    print(f"  {C_RED}Too slow! -10HP{C_RESET}")

            elif len(chall[1]) > 5:
                letter = random.choice(chall[1])
                print(f"  {C_YELLOW}{prompt}'{letter}'{C_RESET}")
                start = time.time()
                hit = False
                while time.time() - start < 1.5:
                    key = get_key()
                    if key and key.lower() == letter:
                        self.score += 120
                        print(f"  {C_GREEN}HIT! +120pts{C_RESET}")
                        hit = True
                        break
                if not hit:
                    self.player_hp -= 8
                    print(f"  {C_RED}Missed! -8HP{C_RESET}")

            else:
                print(f"  {C_YELLOW}{prompt}{C_RESET}")
                for i in range(3, 0, -1):
                    print(f"\r  {C_RED}{i}...{C_RESET}", end="", flush=True)
                    time.sleep(0.8)
                print(f"\r  {C_GREEN}NOW!{C_RESET}  ")
                start = time.time()
                hit = False
                while time.time() - start < 0.4:
                    key = get_key()
                    if key in ["\r", "\n", " ", "enter"]:
                        self.score += 200
                        print(f"  {C_GREEN}PERFECT TIMING! +200pts{C_RESET}")
                        hit = True
                        break
                if not hit:
                    self.player_hp -= 12
                    print(f"  {C_RED}Too slow! -12HP{C_RESET}")

            time.sleep(0.5)
            if self.player_hp <= 0:
                return False

            if round_num % 3 == 0:
                self.boss_hp -= 8
                if self.boss_hp <= 0:
                    self.boss_hp = 0
                    return True

        return self.player_hp > 0

    def _phase_final(self) -> bool:
        """Final phase — rapid-fire combined challenge."""
        clear_screen()
        print(f"\n  {C_RED}{C_BOLD}╔═══════════════════════════════════════╗{C_RESET}")
        print(f"  {C_RED}{C_BOLD}║       FINAL PHASE: ALL OUT!          ║{C_RESET}")
        print(f"  {C_RED}{C_BOLD}╚═══════════════════════════════════════╝{C_RESET}")
        print(f"  {C_YELLOW}No rules. No mercy. SURVIVE!{C_RESET}\n")
        time.sleep(2)

        final_attacks = [
            ("dodge", "up"),
            ("dodge", "down"),
            ("dodge", "left"),
            ("dodge", "right"),
            ("strike", "w"),
            ("strike", "a"),
            ("strike", "s"),
            ("strike", "d"),
            ("block", "b"),
            ("heal", "h"),
        ]

        for wave in range(15):
            clear_screen()
            print(f"\n  {C_RED}{C_BOLD}PHASE 4: FINAL ASSAULT — Wave {wave + 1}/15{C_RESET}\n")
            self._show_hp()

            attack_type, attack_key = random.choice(final_attacks)

            if attack_type == "dodge":
                dirs = {"up": "↑", "down": "↓", "left": "←", "right": "→"}
                print(f"  {C_RED}BOSS uses: {dirs.get(attack_key, '?')} LASER!{C_RESET}")
                print(f"  {C_YELLOW}Press OPPOSITE arrow to dodge!{C_RESET}")
                opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
                correct = opposites[attack_key]
            elif attack_type == "strike":
                print(f"  {C_RED}BOSS is open! Strike with '{attack_key.upper()}'!{C_RESET}")
                correct = attack_key
            elif attack_type == "block":
                print(f"  {C_RED}BOSS attacks! Press 'B' to block!{C_RESET}")
                correct = "b"
            else:
                print(f"  {C_GREEN}Heal opportunity! Press 'H' to recover!{C_RESET}")
                correct = "h"

            start = time.time()
            hit = False
            while time.time() - start < 1.2:
                key = get_key()
                if key and key.lower() == correct:
                    if attack_type == "heal":
                        self.player_hp = min(100, self.player_hp + 15)
                        self.score += 80
                        print(f"  {C_GREEN}HEALED! +15HP{C_RESET}")
                    elif attack_type == "block":
                        self.score += 100
                        print(f"  {C_GREEN}BLOCKED! +100pts{C_RESET}")
                    elif attack_type == "strike":
                        self.boss_hp -= 12
                        self.score += 150
                        print(f"  {C_GREEN}CRITICAL HIT! -12 Boss HP{C_RESET}")
                    else:
                        self.score += 80
                        print(f"  {C_GREEN}DODGED! +80pts{C_RESET}")
                    hit = True
                    break

            if not hit:
                self.player_hp -= 10
                print(f"  {C_RED}HIT! -10HP{C_RESET}")

            time.sleep(0.4)
            if self.player_hp <= 0:
                return False
            if self.boss_hp <= 0:
                self.boss_hp = 0
                return True

        return self.player_hp > 0


def play_boss_fight() -> dict:
    """Entry point for the secret boss fight."""
    return BossFight().play()
