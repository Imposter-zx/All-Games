# 👨‍💻 Development Guide - Quick Start

## Getting Started with Development

### 1. Environment Setup
```bash
cd "c:\Users\HASSA\Desktop\All Games"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Ensure dependencies installed
pip install -r terminal_games/requirements.txt
pip install pytest coverage black pylint
```

### 2. Run Current Project
```bash
python terminal_games/arcade.py
```

---

## Phase 1: Foundation Work (Start Here)

### Task 1.1: Create BaseGame Abstract Class

**File to create**: `terminal_games/base_game.py`

```python
from abc import ABC, abstractmethod
from arcade_utils import add_xp, update_stats

class BaseGame(ABC):
    """Abstract base class for all terminal games."""
    
    def __init__(self, game_name: str):
        self.game_name = game_name
        self.score = 0
        self.xp_earned = 0
        self.start_time = None
        self.end_time = None
    
    @abstractmethod
    def play(self) -> dict:
        """Main game loop. Must return final stats."""
        pass
    
    def add_xp(self, amount: int):
        """Award XP to player."""
        self.xp_earned += amount
        add_xp(amount)
    
    def save_stats(self, stats_dict: dict):
        """Save game stats to persistent storage."""
        update_stats(self.game_name, stats_dict)
    
    def get_duration_seconds(self) -> int:
        """Get game duration in seconds."""
        if self.start_time and self.end_time:
            return int(self.end_time - self.start_time)
        return 0
```

**What to do**:
1. Create the file with above code
2. Verify no syntax errors: `python -m py_compile terminal_games/base_game.py`

---

### Task 1.2: Refactor Snake Game

**File to modify**: `terminal_games/snake.py`

**Change imports** (add at top):
```python
from base_game import BaseGame
import time

class SnakeGame(BaseGame):
    def __init__(self):
        super().__init__("snake")
        self.board_width = 30
        self.board_height = 15
    
    def play(self):
        """Main snake game loop."""
        # Move existing play_snake() logic here
        # Add self.add_xp() calls when food is eaten
        # Return stats at end
        return {
            'high_score': self.score,
            'xp_earned': self.xp_earned
        }

# Keep old function for backward compatibility
def play_snake():
    game = SnakeGame()
    return game.play()
```

---

### Task 1.3: Create StatsManager

**File to create**: `terminal_games/stats_manager.py`

```python
import json
import os
from pathlib import Path

class StatsManager:
    """Centralized player statistics manager."""
    
    STATS_FILE = "terminal_games/player_stats.json"
    
    DEFAULT_STATS = {
        "player_name": "RETRO_MASTER",
        "total_xp": 0,
        "level": 1,
        "games_played": 0,
        "total_playtime": 0,
        "games": {}
    }
    
    def __init__(self):
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """Load stats from JSON file."""
        if os.path.exists(self.STATS_FILE):
            try:
                with open(self.STATS_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self.DEFAULT_STATS.copy()
        return self.DEFAULT_STATS.copy()
    
    def save(self):
        """Save stats to JSON file."""
        os.makedirs(os.path.dirname(self.STATS_FILE), exist_ok=True)
        with open(self.STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def update_game_stats(self, game_name: str, stats_dict: dict):
        """Update stats for a specific game."""
        if game_name not in self.stats['games']:
            self.stats['games'][game_name] = {}
        self.stats['games'][game_name].update(stats_dict)
        self.stats['games_played'] += 1
        self.save()
    
    def add_xp(self, amount: int):
        """Add XP to player."""
        self.stats['total_xp'] += amount
        self._update_level()
        self.save()
    
    def _update_level(self):
        """Calculate current level based on XP."""
        # Level formula: level = 1 + (total_xp / 500)
        self.stats['level'] = 1 + (self.stats['total_xp'] // 500)
    
    def get_stats(self, game_name: str = None) -> dict:
        """Get stats for a game or overall."""
        if game_name:
            return self.stats['games'].get(game_name, {})
        return self.stats

# Global instance
_manager = None

def get_stats_manager() -> StatsManager:
    """Get global stats manager instance."""
    global _manager
    if _manager is None:
        _manager = StatsManager()
    return _manager
```

---

### Task 1.4: Unit Tests

**File to create**: `tests/test_base_game.py`

```python
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'terminal_games'))

from base_game import BaseGame

class TestGame(BaseGame):
    """Concrete implementation for testing."""
    def play(self):
        self.score = 100
        self.add_xp(50)
        return {'score': self.score, 'xp': self.xp_earned}

def test_base_game_initialization():
    """Test BaseGame initializes correctly."""
    game = TestGame("test")
    assert game.game_name == "test"
    assert game.score == 0
    assert game.xp_earned == 0

def test_base_game_add_xp():
    """Test XP addition."""
    game = TestGame("test")
    game.add_xp(100)
    assert game.xp_earned == 100

def test_base_game_play():
    """Test play method returns stats."""
    game = TestGame("test")
    stats = game.play()
    assert stats['score'] == 100
    assert stats['xp'] == 50
```

**Run tests**:
```bash
cd "c:\Users\HASSA\Desktop\All Games"
pytest tests/test_base_game.py -v
```

---

## Phase 2: Enhancement Work

### Task 2.1: Enhanced Input Handler

**File to create**: `terminal_games/input_handler.py`

```python
import time
from arcade_utils import get_key

class InputHandler:
    """Robust input handling with timeout and buffering."""
    
    def __init__(self):
        self.key_map = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        self.last_key = None
    
    def get_direction(self, timeout=0.05):
        """Get direction input with timeout."""
        key = get_key_with_timeout(timeout)
        if key in self.key_map:
            self.last_key = key
            return self.key_map[key]
        return None  # No valid input
    
    def get_yes_no(self) -> bool:
        """Get yes/no response."""
        while True:
            key = get_key()
            if key and key.lower() in ['y', 'yes', '1']:
                return True
            elif key and key.lower() in ['n', 'no', '0']:
                return False

def get_key_with_timeout(timeout=0.05):
    """Get key with timeout (non-blocking)."""
    import os
    import sys
    if os.name == 'nt':
        import msvcrt
        if msvcrt.kbhit():
            return get_key()
        time.sleep(timeout)
        return None
    else:
        # Unix implementation with timeout
        import select
        if select.select([sys.stdin], [], [], timeout)[0]:
            return get_key()
        return None
```

---

### Task 2.2: XP Configuration System

**File to create**: `terminal_games/xp_config.py`

```python
from dataclasses import dataclass

@dataclass
class GameXPConfig:
    """XP earning configuration per game."""
    name: str
    base_multiplier: float = 1.0
    difficulty_easy: float = 0.5
    difficulty_normal: float = 1.0
    difficulty_hard: float = 2.0

# Define XP rewards for each game
XP_CONFIGS = {
    'snake': GameXPConfig(
        name='Snake',
        base_multiplier=0.5  # points_scored * 0.5 = XP
    ),
    'tetris': GameXPConfig(
        name='Tetris',
        base_multiplier=1.0   # lines_cleared * 50 + score * 0.1
    ),
    'chess': GameXPConfig(
        name='Chess',
        base_multiplier=10.0  # win * 100 + pieces * 5
    ),
    'dungeon': GameXPConfig(
        name='Dungeon Crawler',
        base_multiplier=5.0   # room_cleared * 75 + combat * 25
    )
}

class XPSystem:
    """Dynamic XP earning system."""
    
    def __init__(self, difficulty='normal'):
        self.difficulty = difficulty
        self.multiplier = self._get_multiplier(difficulty)
    
    def _get_multiplier(self, difficulty) -> float:
        """Get difficulty multiplier."""
        multipliers = {
            'easy': 0.5,
            'normal': 1.0,
            'hard': 2.0
        }
        return multipliers.get(difficulty, 1.0)
    
    def calculate_xp(self, game_name: str, base_value: int) -> int:
        """Calculate XP earned."""
        if game_name in XP_CONFIGS:
            config = XP_CONFIGS[game_name]
            base_xp = int(base_value * config.base_multiplier)
            return int(base_xp * self.multiplier)
        return base_value
```

---

## Phase 3: Feature Work

### Task 3.1: Add Game Difficulty Selection

**File to modify**: `terminal_games/arcade.py`

Add this function at menu level:

```python
def select_game_difficulty():
    """Let player choose difficulty before game starts."""
    from arcade_utils import draw_retro_box, C_YELLOW, C_RESET
    
    difficulties = ['EASY', 'NORMAL', 'HARD']
    selection = 0
    
    while True:
        clear_screen()
        print(f"\n{C_YELLOW}Select Difficulty:{C_RESET}\n")
        
        for i, diff in enumerate(difficulties):
            marker = "→ " if i == selection else "  "
            print(f"{marker}{diff}")
        
        print("\n[UP/DOWN to select, ENTER to confirm, Q to quit]")
        
        key = get_key()
        if key == 'up':
            selection = (selection - 1) % len(difficulties)
        elif key == 'down':
            selection = (selection + 1) % len(difficulties)
        elif key == 'enter':
            return difficulties[selection].lower()
        elif key and key.lower() == 'q':
            return None
        
        time.sleep(0.1)
```

---

## Common Implementation Patterns

### Pattern 1: Game Structure
```python
from base_game import BaseGame
from arcade_utils import add_xp, update_stats

class YourGame(BaseGame):
    def __init__(self, difficulty='normal'):
        super().__init__("your_game_name")
        self.difficulty = difficulty
    
    def play(self):
        # Game logic here
        while not game_over:
            # Render
            # Get input
            # Update
            pass
        
        # Save final stats
        self.save_stats({
            'high_score': self.score,
            'xp_earned': self.xp_earned,
            'difficulty': self.difficulty
        })
        
        return {'score': self.score}
```

### Pattern 2: Error Handling
```python
def safe_game_wrapper(game_func):
    """Decorator to safely run any game with error handling."""
    def wrapper(*args, **kwargs):
        try:
            return game_func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nGame interrupted by player")
            return {}
        except Exception as e:
            print(f"\nError in game: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    return wrapper
```

---

## Testing Checklist

- [ ] Create tests directory: `mkdir tests`
- [ ] Create `tests/__init__.py`
- [ ] Write BaseGame tests
- [ ] Write StatsManager tests
- [ ] Write InputHandler tests
- [ ] Run all tests: `pytest tests/ -v`
- [ ] Check coverage: `pytest tests/ --cov=terminal_games/`

**Target**: >70% code coverage

---

## Git Workflow (Recommended)

```bash
# Create feature branch
git checkout -b feature/base-game-refactor

# Make changes, test locally
pytest tests/

# Commit
git add .
git commit -m "refactor: implement BaseGame abstract class"

# Merge when ready
git checkout main
git merge feature/base-game-refactor
```

---

## Performance Checklist

- [ ] Add FPS limiter to game loops (target 30 FPS)
- [ ] Profile code with `cProfile`
- [ ] Cache ANSI escape sequences
- [ ] Minimize screen clears
- [ ] Test on slow terminals

---

## Code Quality Tools

```bash
# Format code
black terminal_games/

# Check style
pylint terminal_games/ --disable=C0111,C0103

# Find issues
python -m py_compile terminal_games/*.py
```

---

## Debugging Tips

```python
# Add logging
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Input received: {key}")

# Print variable state
print(f"DEBUG: {self.score=}, {self.xp_earned=}")

# Use breakpoints (for IDEs)
breakpoint()
```

---

## Helpful VSCode Extensions

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Test Explorer (littlefoxteam.vscode-test-explorer)
- Better Comments (aaron-bond.better-comments)

---

## Resources

- [Python ABC Module](https://docs.python.org/3/library/abc.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [ANSI Color Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)

---

**Next Action**: Start with Task 1.1 - Create BaseGame class, then move to refactoring key games.
