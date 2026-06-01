import logging
import random
import time
from typing import List, Tuple

from arcade_utils import (
    BG_DARK,
    BG_GREEN,
    BG_RED,
    BG_YELLOW,
    C_CYAN,
    C_GREEN,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    beep,
    clear_screen,
    draw_retro_box,
    show_popup,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

WORD_POOL = [
    "apple", "crane", "brain", "stone", "flame", "grape", "heart", "juice",
    "knife", "lemon", "mango", "night", "ocean", "piano", "queen", "river",
    "snake", "tiger", "ultra", "vapor", "waste", "xenon", "yacht", "zebra",
    "about", "above", "abuse", "actor", "acute", "admit", "adopt", "adult",
    "after", "again", "agent", "agree", "ahead", "alarm", "album", "alert",
    "alien", "align", "alive", "allow", "alone", "along", "alter", "angel",
    "anger", "angle", "angry", "apart", "apple", "apply", "arena", "argue",
    "arise", "array", "aside", "asset", "avoid", "award", "aware", "badly",
    "baker", "bases", "basic", "basis", "beach", "began", "begin", "being",
    "below", "bench", "billy", "birth", "black", "blade", "blame", "blank",
    "blast", "blaze", "bleed", "blend", "bless", "blind", "blink", "bliss",
    "block", "blood", "blown", "board", "bonus", "boost", "bound", "brain",
    "brand", "brave", "bread", "break", "breed", "brief", "bring", "broad",
    "broke", "brown", "build", "bunch", "burst", "cabin", "candy", "cargo",
    "carry", "catch", "cause", "cease", "chain", "chair", "chalk", "champ",
    "chaos", "charm", "chart", "chase", "cheap", "check", "cheek", "cheer",
    "chess", "chest", "chief", "child", "chill", "choir", "chord", "civic",
    "civil", "claim", "class", "clean", "clear", "clerk", "click", "climb",
    "cling", "clock", "close", "cloth", "cloud", "coach", "coast", "color",
    "comet", "coral", "count", "court", "cover", "crack", "craft", "crane",
    "crash", "crazy", "cream", "crest", "crime", "crisp", "cross", "crowd",
    "crown", "cruel", "crush", "cubic", "curve", "cycle", "daily", "dance",
    "debut", "decay", "decor", "decoy", "delay", "delta", "demon", "dense",
    "depth", "derby", "desk", "devil", "diary", "dirty", "ditch", "dizzy",
    "dodge", "donor", "doubt", "dough", "draft", "drain", "drake", "drama",
    "drank", "drawn", "dread", "dream", "dress", "dried", "drift", "drill",
    "drink", "drive", "drone", "drool", "drops", "drove", "drums", "drunk",
    "dryer", "eager", "eagle", "early", "earth", "eight", "elder", "elect",
    "elite", "embed", "ember", "empty", "enemy", "enjoy", "enter", "entry",
    "equal", "equip", "error", "essay", "event", "every", "evict", "exact",
    "exert", "exile", "exist", "extra", "fable", "facet", "faint", "fairy",
    "faith", "false", "fancy", "fatal", "fault", "feast", "fence", "ferry",
    "fetch", "fever", "fiber", "field", "fiery", "fifth", "fifty", "fight",
    "final", "first", "fixed", "flame", "flash", "fleet", "flesh", "float",
    "flock", "flood", "floor", "flora", "flour", "fluid", "flush", "flute",
    "focal", "focus", "force", "forge", "forth", "forum", "found", "frame",
    "frank", "fraud", "fresh", "front", "frost", "froze", "fruit", "fully",
    "ghost", "giant", "given", "glass", "glide", "globe", "gloom", "glory",
    "glove", "going", "grace", "grade", "grain", "grand", "grant", "grape",
    "graph", "grasp", "grass", "grave", "great", "green", "greet", "grief",
    "grill", "grind", "gripe", "gross", "group", "grove", "grown", "guard",
    "guess", "guest", "guide", "guild", "guilt", "gulch", "gully", "hairy",
    "harsh", "haste", "hasty", "haven", "heart", "heavy", "hedge", "height",
    "hello", "henry", "herbs", "heron", "hobby", "honey", "honor", "horse",
    "hotel", "house", "hover", "human", "humor", "hurry", "ideal", "image",
    "imply", "index", "indie", "infer", "inner", "input", "ivory", "jewel",
    "joint", "joker", "judge", "juice", "jumbo", "kayak", "kebab", "knack",
    "kneel", "knock", "known", "label", "labor", "laker", "lapse", "large",
    "laser", "later", "laugh", "layer", "learn", "lease", "leave", "legal",
    "lemon", "level", "light", "limit", "linen", "liver", "local", "logic",
    "lodge", "lofty", "loose", "lover", "lower", "loyal", "lucky", "lunar",
    "lunch", "lying", "macro", "magic", "major", "maker", "manor", "maple",
    "march", "marry", "match", "mayor", "media", "mercy", "merge", "merit",
    "merry", "metal", "meter", "might", "minor", "minus", "mirth", "model",
    "money", "month", "moral", "motor", "mount", "mouse", "mouth", "movie",
    "music", "naive", "nanny", "nasal", "naval", "nerve", "never", "night",
    "noble", "noise", "north", "noted", "novel", "nurse", "nylon", "oasis",
    "occur", "ocean", "offer", "often", "olive", "onset", "opera", "orbit",
    "order", "other", "outer", "overt", "owner", "oxide", "ozone", "paint",
    "panel", "panic", "paper", "party", "pasta", "patch", "pause", "peace",
    "pearl", "penny", "phase", "phone", "photo", "piano", "piece", "pilot",
    "pinch", "pixel", "pizza", "place", "plain", "plane", "plant", "plate",
    "plaza", "plead", "pluck", "plumb", "plume", "plump", "plush", "poem",
    "poet", "point", "polar", "pound", "power", "press", "price", "pride",
    "prime", "prince", "print", "prior", "prism", "prize", "probe", "proof",
    "proud", "prove", "proxy", "pulse", "pupil", "purse", "queen", "quest",
    "queue", "quick", "quiet", "quote", "radar", "radio", "raise", "rally",
    "ranch", "range", "rapid", "ratio", "reach", "react", "ready", "realm",
    "rebel", "refer", "reign", "relax", "reply", "rider", "ridge", "rifle",
    "right", "rigid", "ripen", "risen", "risky", "rival", "river", "robin",
    "robot", "rocky", "rogue", "roman", "rouge", "rough", "round", "route",
    "royal", "rugby", "ruler", "rural", "sadly", "saint", "salad", "sauce",
    "scale", "scare", "scene", "scent", "scope", "score", "scout", "scrap",
    "sense", "serve", "setup", "seven", "shade", "shaft", "shake", "shall",
    "shame", "shape", "share", "shark", "sharp", "sheep", "sheer", "sheet",
    "shelf", "shell", "shift", "shine", "shirt", "shock", "shore", "short",
    "shout", "sight", "sigma", "since", "sixth", "sixty", "skate", "skill",
    "skull", "slate", "slave", "sleep", "slice", "slide", "slope", "small",
    "smart", "smell", "smile", "smoke", "snack", "snake", "solid", "solve",
    "sorry", "sound", "south", "space", "spare", "spark", "speak", "speed",
    "spend", "spice", "spill", "spine", "spite", "split", "spoke", "spoon",
    "sport", "spray", "squad", "stack", "staff", "stage", "stain", "stake",
    "stale", "stall", "stamp", "stand", "stark", "start", "state", "stays",
    "steal", "steam", "steel", "steep", "steer", "stern", "stick", "stiff",
    "still", "stock", "stone", "stood", "store", "storm", "story", "stout",
    "stove", "strap", "straw", "strip", "stuck", "study", "stuff", "style",
    "sugar", "suite", "sunny", "super", "surge", "swamp", "swarm", "swear",
    "sweep", "sweet", "swept", "swift", "swing", "swirl", "sword", "syrup",
    "table", "taste", "teach", "teeth", "temple", "terms", "theme", "there",
    "thick", "thief", "thing", "think", "third", "thorn", "those", "three",
    "threw", "throw", "thumb", "tiger", "tight", "timer", "tired", "title",
    "toast", "today", "token", "topic", "total", "touch", "tough", "tower",
    "toxic", "trace", "track", "trade", "trail", "train", "trait", "trash",
    "treat", "trend", "trial", "tribe", "trick", "tried", "troop", "truck",
    "truly", "trump", "trunk", "trust", "truth", "tumor", "twice", "twist",
    "ultra", "uncle", "under", "unfair", "union", "unite", "unity", "until",
    "upper", "upset", "urban", "usage", "usual", "utter", "valid", "value",
    "valve", "vault", "venue", "verse", "video", "vigor", "viral", "virus",
    "visit", "vital", "vivid", "vocal", "vodka", "voice", "voter", "vouch",
    "wagon", "waist", "waste", "watch", "water", "weave", "weigh", "weird",
    "whale", "wheat", "wheel", "where", "which", "while", "whine", "white",
    "whole", "whose", "wider", "widow", "width", "wield", "witch", "woman",
    "world", "worry", "worse", "worst", "worth", "would", "wound", "wrath",
    "write", "wrong", "wrote", "yacht", "yield", "young", "youth", "zebra",
]

WORD_LENGTH = 5
WORD_POOL = [w for w in WORD_POOL if len(w) == WORD_LENGTH]


def _daily_seed() -> int:
    import datetime
    import hashlib
    today = datetime.date.today().isoformat()
    return int(hashlib.md5(today.encode()).hexdigest()[:8], 16)


def _daily_word() -> str:
    rng = random.Random(_daily_seed())
    return rng.choice(WORD_POOL).upper()


class WordleGame(BaseGame):
    def __init__(self, difficulty: str = 'normal', daily: bool = False) -> None:
        super().__init__('wordle', difficulty)
        self.daily = daily
        self.target = _daily_word() if daily else random.choice(WORD_POOL).upper()
        self.attempts: List[str] = []
        self.max_attempts = 6
        self.used_letters: dict = {}
        self.round = 1

    def _check_guess(self, guess: str) -> List[Tuple[str, str]]:
        result: List[Tuple[str, str]] = [(c, 'gray') for c in guess]
        remaining = list(self.target)

        for i, c in enumerate(guess):
            if c == self.target[i]:
                result[i] = (c, 'green')
                remaining[i] = None

        for i, c in enumerate(guess):
            if result[i][1] == 'green':
                continue
            if c in remaining:
                idx = remaining.index(c)
                result[i] = (c, 'yellow')
                remaining[idx] = None

        return result

    def save_state_json(self) -> dict:
        return {
            'target': self.target,
            'attempts': list(self.attempts),
            'used_letters': dict(self.used_letters),
            'score': self.score,
            'round': self.round,
        }

    def load_state_json(self, state: dict) -> None:
        self.target = state.get('target', random.choice(WORD_POOL).upper())
        self.attempts = list(state.get('attempts', []))
        self.used_letters = dict(state.get('used_letters', {}))
        self.score = state.get('score', 0)
        self.round = state.get('round', 1)

    def _render_grid(self, current_word: str = "") -> None:
        for row_idx in range(self.max_attempts):
            line = "  "
            if row_idx < len(self.attempts):
                guess = self.attempts[row_idx]
                result = self._check_guess(guess)
                for char, color in result:
                    bg = BG_GREEN if color == 'green' else (BG_YELLOW if color == 'yellow' else BG_RED)
                    line += f"{bg}{C_WHITE} {char} {C_RESET}"
            elif row_idx == len(self.attempts) and current_word:
                for char in current_word:
                    line += f"{BG_DARK}{C_WHITE} {char} {C_RESET}"
                padding = WORD_LENGTH - len(current_word)
                if padding > 0:
                    line += f"{BG_DARK}{C_WHITE}" + " ." * padding + f" {C_RESET}"
            else:
                line += f"{BG_DARK}{C_WHITE} . . . . . {C_RESET}"
            print(line)

    def _render_alphabet(self) -> None:
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for row in rows:
            line = "   "
            for c in row:
                color = C_RESET
                if c in self.used_letters:
                    status = self.used_letters[c]
                    if status == 'green':
                        color = C_GREEN
                    elif status == 'yellow':
                        color = C_YELLOW
                    else:
                        color = C_RED
                line += f"{color}{c}{C_RESET} "
            print(line)

    def _render(self) -> None:
        title = "DAILY WORDLE" if self.daily else f"WORDLE ({WORD_LENGTH} LETTERS)"
        subtitle = ""
        if self.daily:
            import datetime
            subtitle = f"{C_YELLOW}Daily Puzzle — {datetime.date.today().strftime('%b %d, %Y')}{C_RESET}"
        else:
            subtitle = f"{C_CYAN}ROUND {self.round}{C_RESET}   DIFFICULTY: {self.difficulty.upper()}"
        lines: list = [subtitle, ""]
        draw_retro_box(30, title, lines, color=C_GREEN)

    def play(self) -> dict:
        self.start_timer()
        if self.has_saved_state():
            saved = self.stats_manager.load_game_state(self.game_name)
            if saved:
                self.load_state_json(saved)
        input_handler = get_safe_input_handler()

        try:
            current_word: List[str] = []

            while not self.game_over:
                clear_screen()
                print("\n" * 1)
                self._render()
                self._render_grid("".join(current_word))
                print()
                self._render_alphabet()
                hint = "".join(current_word) if current_word else "_" * WORD_LENGTH
                print(f"\n{C_WHITE}Word: {C_GREEN}{hint}{C_RESET}")
                print(f"{C_WHITE}[A-Z] Type  [ENTER] Submit  [BACKSPACE] Delete  [Q] Quit  [?] Help{C_RESET}")

                if len(self.attempts) >= self.max_attempts:
                    show_popup(f"GAME OVER! The word was {self.target}", C_RED, delay=2.0)
                    self.award_xp_for_action(10)
                    if self.daily:
                        self.game_over = True
                        break
                    self.round += 1
                    self.target = random.choice(WORD_POOL).upper()
                    self.attempts = []
                    self.used_letters = {}
                    current_word = []
                    continue

                if self.attempts and self.attempts[-1] == self.target:
                    remaining = self.max_attempts - len(self.attempts) + 1
                    xp = 50 + remaining * 30
                    self.score += 100 + xp
                    self.award_xp_for_action(xp)
                    beep("win")
                    show_popup(f"CORRECT! The word was {self.target}", C_GREEN, delay=1.5)
                    self.unlock_achievement("wordle_win", "Wordle Wizard")
                    if self.daily:
                        self.game_over = True
                        break
                    self.round += 1
                    self.target = random.choice(WORD_POOL).upper()
                    self.attempts = []
                    self.used_letters = {}
                    current_word = []
                    continue

                key = input_handler.get_safe_key()
                if not key:
                    time.sleep(0.05)
                    continue

                if self._save_and_quit(key.lower()):
                    break
                if key == '?':
                    show_popup(
                        "WORDLE: Guess the {0}-letter word in {1} tries. "
                        "{2}GREEN{3} = correct letter & position, "
                        "{2}YELLOW{3} = correct letter, wrong position, "
                        "{2}RED{3} = letter not in word.".format(
                            WORD_LENGTH, self.max_attempts,
                            C_GREEN, C_RESET
                        ),
                        C_GREEN, delay=2.0,
                    )
                    continue

                # Backspace
                if key in ['\b', '\x7f', 'backspace', 'delete']:
                    if current_word:
                        current_word.pop()
                        beep("correct")
                    continue

                # Enter to submit
                if key in ['\r', '\n', 'enter']:
                    guess = "".join(current_word).upper()
                    if len(guess) != WORD_LENGTH:
                        show_popup(f"Word must be {WORD_LENGTH} letters!", C_RED, delay=0.8)
                        continue
                    if guess in self.attempts:
                        show_popup("Already guessed!", C_RED, delay=0.8)
                        continue

                    self.attempts.append(guess)
                    result = self._check_guess(guess)
                    for char, status in result:
                        existing = self.used_letters.get(char)
                        if status == 'green' or (status == 'yellow' and existing != 'green'):
                            self.used_letters[char] = status
                        elif char not in self.used_letters:
                            self.used_letters[char] = 'gray'

                    self.score += 10
                    current_word = []
                    beep("correct")
                    continue

                # Letter input
                if key and key.isalpha() and len(key) == 1:
                    if len(current_word) < WORD_LENGTH:
                        current_word.append(key.upper())
                        beep("correct")
                    continue

                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats


def _select_wordle_mode() -> str:
    from arcade_utils import C_CYAN, C_RESET, C_WHITE, C_YELLOW, beep, clear_screen, draw_retro_box, get_key
    options = ["Normal (endless rounds)", "Daily Puzzle (one per day)"]
    sel = 0
    while True:
        clear_screen()
        print("\n" * 2)
        lines = []
        for i, opt in enumerate(options):
            m = f"{C_YELLOW}►{C_RESET} " if i == sel else "  "
            s = f"{C_YELLOW}" if i == sel else f"{C_WHITE}"
            lines.append(f"{m}{s}{opt}{C_RESET}")
        draw_retro_box(34, "WORDLE MODE", lines, color=C_CYAN)
        print(f"\n  {C_WHITE}[UP/DOWN] Select  [ENTER] Confirm  [Q] Back{C_RESET}")
        key = get_key()
        if key == "up":
            sel = (sel - 1) % len(options)
            beep("move")
        elif key == "down":
            sel = (sel + 1) % len(options)
            beep("move")
        elif key in ["\r", "\n", " ", "enter"]:
            beep("win")
            return "daily" if sel == 1 else "normal"
        elif key and key.lower() == "q":
            return ""


def play_wordle(difficulty: str = 'normal') -> dict:
    mode = _select_wordle_mode()
    if not mode:
        return {"score": 0, "xp_earned": 0, "duration_seconds": 0, "high_score": 0}
    daily = mode == "daily"
    game = WordleGame(difficulty, daily=daily)
    return game.play()
