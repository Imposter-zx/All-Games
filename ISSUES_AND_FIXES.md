# 🐛 Issues & Quick Fixes

## Critical Issues Found

### Issue 1: Bare Except Clauses (Code Quality Risk)
**Severity**: MEDIUM  
**Files Affected**: arcade_utils.py, chess_game.py, sudoku.py, minesweeper.py, tetris.py

**Problem**:
```python
try:
    # code
except:  # ❌ Catches ALL exceptions, even KeyboardInterrupt
    pass
```

**Fix** (QUICK - 15 min):
```python
try:
    # code
except (ValueError, IndexError, OSError) as e:  # ✅ Specific exceptions
    logger.warning(f"Expected error: {e}")
```

**Files to Fix**:
1. `arcade_utils.py` - Line 64-65, 72, 92-95, 184-186
2. `chess_game.py` - Line 26-30, 37-38
3. `sudoku.py` - Line 44-45, 58-59
4. `minesweeper.py` - Line 38-39
5. `tetris.py` - Line 29

---

### Issue 2: Missing Dependency Documentation
**Severity**: MEDIUM  
**Problem**: `requirements.txt` only lists `python-chess` but code imports other modules  

**Current `requirements.txt`**:
```
python-chess==1.10.0
```

**Should Be** (QUICK - 5 min):
```
python-chess==1.10.0
colorama==0.4.6      # For better Windows ANSI support (optional)
pytest==7.4.0        # For testing (optional)
coverage==7.3.0      # For test coverage (optional)
```

**Fix**: Update `terminal_games/requirements.txt`

---

### Issue 3: Bare Terminal Size Exception Handling
**Severity**: LOW  
**Files**: Multiple (arcade.py, chess_game.py, sudoku.py, minesweeper.py)

**Current (Bad)**:
```python
try: term_width = os.get_terminal_size().columns
except: pass  # Ignores all errors
```

**Fix** (QUICK - 10 min):
```python
try:
    term_width = os.get_terminal_size().columns
except (OSError, ValueError):
    term_width = 80  # Sensible default
```

---

### Issue 4: No Input Validation
**Severity**: HIGH  
**Problem**: Game crashes on unexpected input

**Current**:
```python
key = get_key()
if key == 'up':  # ❌ What if key is None?
    direction = (-1, 0)
```

**Fix**:
```python
key = get_key()
if key and key in ['up', 'w', 'W']:  # ✅ Safe check
    direction = (-1, 0)
```

---

### Issue 5: Missing Game State Validation
**Severity**: MEDIUM  
**Problem**: No checks for corrupted save files

**Current**:
```python
def load_stats():
    with open(STATS_FILE) as f:
        return json.load(f)  # ❌ Can crash on bad JSON
```

**Fix**:
```python
def load_stats():
    try:
        if not os.path.exists(STATS_FILE):
            return DEFAULT_STATS.copy()
        with open(STATS_FILE) as f:
            data = json.load(f)
            # Validate required fields
            if not isinstance(data, dict):
                return DEFAULT_STATS.copy()
            return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load stats: {e}")
        return DEFAULT_STATS.copy()
```

---

### Issue 6: No Game Timeout
**Severity**: MEDIUM  
**Problem**: `get_key()` can block indefinitely on some systems

**Current**: 
```python
def get_key():
    # Could block forever waiting for input
```

**Fix**:
```python
import signal

def get_key_with_timeout(timeout=0.05):
    """Get key with timeout to prevent blocking."""
    if os.name == 'nt':
        import msvcrt
        start = time.time()
        while time.time() - start < timeout:
            if msvcrt.kbhit():
                return get_key()
            time.sleep(0.01)
        return None
```

---

### Issue 7: Inconsistent Score/Stats Field Names
**Severity**: MEDIUM  
**Problem**: Different games use different field names

**Current**:
```
snake: "high_score"
tetris: "best_score"
space_shooter: "high_score"
breakout: "best_score"  # ❌ Inconsistent names!
```

**Fix**: Standardize all to `"high_score"`

**Games to Fix**:
1. `breakout.py` - Change "best_score" → "high_score"
2. `tetris.py` - Change "best_score" → "high_score"

---

### Issue 8: No Game Performance Monitoring
**Severity**: LOW  
**Problem**: Can't tell if games are lagging

**Quick Fix** (Add to game loops):
```python
import time

FPS_TARGET = 30
FRAME_TIME = 1.0 / FPS_TARGET

frame_start = time.time()
# ... game logic ...
frame_elapsed = time.time() - frame_start
sleep_time = FRAME_TIME - frame_elapsed
if sleep_time > 0:
    time.sleep(sleep_time)
```

---

### Issue 9: Error Message Not User-Friendly
**Severity**: LOW

**Current** (in arcade.py):
```python
print(f"\n{C_RED} Error: python-chess not found!{C_RESET}")
```

**Better**:
```python
error_message = [
    "⚠️  Chess Game Not Available",
    "",
    "Missing dependency: python-chess",
    "",
    "Install with:",
    "  pip install python-chess==1.10.0"
]
draw_retro_box(50, "ERROR", error_message, color=C_RED)
```

---

### Issue 10: No Logging System
**Severity**: MEDIUM  
**Problem**: Errors disappear into the void, can't debug

**Quick Fix** (Create `terminal_games/logger.py`):
```python
import logging
import os

def setup_logger():
    """Setup basic logging."""
    log_file = 'terminal_games/debug.log'
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logger()
```

---

## Quick Wins (4-Hour Sprint)

### QW1: Fix All Bare Except Clauses (45 min)
**Files**: 5 files  
**Action**: Replace `except:` with `except (ValueError, OSError) as e:`

### QW2: Update requirements.txt (5 min)
**Action**: Add comments and optional dependencies

### QW3: Add Input Validation (30 min)
**Action**: Add `if key and key in [...]` checks in all games

### QW4: Create Simple Logger (20 min)
**Action**: Create logger.py, import in arcade_utils.py

### QW5: Standardize Score Field Names (20 min)
**Action**: 
- Search for "best_score" → "high_score" 
- Update in: breakout.py, tetris.py, arcade.py

### QW6: Add Default Terminal Width (15 min)
**Action**: Replace bare `except` with proper exception handling + default

### QW7: Add Frame Rate Limiting (30 min)
**Action**: Add to all game loops

### QW8: Fix Error Messages (15 min)
**Action**: Use `draw_retro_box()` for error displays

---

## Implementation Priority

### MUST FIX (Bugs that cause crashes)
1. ✅ Standardize exception handling
2. ✅ Add field name consistency
3. ✅ Input validation

### SHOULD FIX (Code quality improvement)
1. ✅ Update requirements.txt
2. ✅ Add logging system
3. ✅ Improve error messages

### NICE TO HAVE (Performance/Polish)
1. ✅ Frame rate limiting
2. ✅ Terminal size defaults
3. ✅ Input timeout handling

---

## Testing the Fixes

### Test Exception Handling
```bash
cd terminal_games
python -c "import json; json.load(open('nonexistent.json'))" # Should handle gracefully
```

### Test Input Validation
```python
# In any game, press random keys - should not crash
```

### Test Stats Loading
```bash
# Delete player_stats.json, run game - should create fresh stats
rm player_stats.json
python arcade.py
```

---

## Code Review Checklist

Before committing fixes:
- [ ] No bare `except:` clauses remain
- [ ] All file operations have try-catch
- [ ] All input has validation
- [ ] requirements.txt is up-to-date
- [ ] Logger imported where needed
- [ ] Score field names are consistent
- [ ] Error messages use draw_retro_box()
- [ ] No new linting warnings

---

## Metrics After Fixes

| Metric | Before | After |
|--------|--------|-------|
| Bare except clauses | 20+ | 0 |
| Field name consistency | 60% | 100% |
| Exception coverage | ~30% | ~80% |
| Error message quality | Poor | Good |
| Code defects | ~10+ | <3 |

---

## Step-by-Step Fix Implementation

### Step 1: Create Exception Handler Wrapper (10 min)
Create `terminal_games/error_handler.py`:
```python
import logging

logger = logging.getLogger(__name__)

def safe_game_call(game_func, game_name):
    """Safely execute game function with error handling."""
    try:
        return game_func()
    except KeyboardInterrupt:
        logger.info(f"Player quit {game_name}")
        return {}
    except Exception as e:
        logger.error(f"Error in {game_name}: {e}", exc_info=True)
        from arcade_utils import draw_retro_box, C_RED
        draw_retro_box(
            60,
            "GAME ERROR",
            [f"Error: {str(e)}", "", "Check debug.log for details"],
            color=C_RED
        )
        return {}
```

### Step 2: Fix arcade.py (20 min)
Replace game calls:
```python
# OLD:
elif selection == 0: play_snake()

# NEW:
elif selection == 0: safe_game_call(play_snake, "Snake")
```

### Step 3: Fix Requirements (5 min)
Update `requirements.txt`

### Step 4: Add Input Checks (30 min)
Add validation in each game

### Step 5: Test All Games (30 min)
Play 2 minutes of each, check logs

---

## Total Time Commitment

- **Critical Fixes**: 2 hours
- **Quality Improvements**: 2 hours  
- **Testing**: 1 hour
- **Documentation**: 0.5 hours

**Total: ~5.5 hours for production-ready code**

---

Next Steps:
1. Run through the "Quick Wins (4-Hour Sprint)" section
2. Test each fix in the games
3. Check debug.log for error patterns
4. Move to Phase 1 of DEVELOPMENT_GUIDE.md
