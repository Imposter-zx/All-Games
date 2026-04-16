# 🕹️ Retro Terminal Arcade V5: The RPG Update

A premium collection of classic terminal games with a polished TUI, XP/Leveling system, procedural dungeons, and immersive visual effects. **Now with production-ready infrastructure, comprehensive testing, and clean architecture patterns.**

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Tests](https://img.shields.io/badge/tests-32%2F32%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blueviolet)

## 🎮 Games Included

1.  **⚔️ Dungeon Crawler**
    - Roguelike exploration with procedural rooms.
    - Turn-based combat, loot collection, and level progression.
2.  **🟡 Pac-Man**
    - Classic grid movement with ghost AI and powerups.
3.  **🐍 Snake** (Refactored ✨)
    - High-speed survival with XP rewards for eating.
    - Now uses clean BaseGame architecture.
4.  **🧱 Breakout**
    - Physics-based brick destruction with screen shake and particles.
5.  **🧩 Tetris**
    - Modern implementation with line clears awarding massive XP.
6.  **🚀 Space Shooter**
    - Fast-paced combat with explosive particle effects.
7.  **💣 Minesweeper**
    - Classic logic-based mine detection with high XP on victory.
8.  **♟️ Chess vs AI**
    - Play against Stockfish; XP for captures and wins.
9.  **🔢 Sudoku**
    - Logic puzzles with a persistence bonus.

## ✨ V5 Features: The RPG Update + Production Infrastructure (Phase 1 ✅)

### Core Gaming Features
- **Global RPG Progression**: Gain XP across ALL games. Level up to see your rank grow on your persistent profile.
- **Visual Juice**: Immersive screen shakes and particle effects for combat, line clears, and explosions.
- **Enhanced Profile**: Sleek XP progress bar and level display in the main arcade menu.
- **ANSI-Safe Rendering**: Premium TUI alignment and design across all game modules.
- **Cross-Platform**: Optimized for Windows and Unix terminals.

### Phase 1: Production Infrastructure (✅ Complete)
- **Solid Architecture**: Abstract `BaseGame` class provides consistent interface for all games
- **Centralized Stats Management**: Singleton `StatsManager` handles all XP, levels, and game statistics
- **Comprehensive Testing**: 32 automated unit tests with 100% pass rate
- **Professional Error Handling**: Consistent exception handling and input validation
- **Debug Logging**: Integrated logging system for troubleshooting
- **Code Quality**: 50+ code quality improvements and bug fixes

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Infrastructure | ✅ Complete | BaseGame, StatsManager, Error Handlers, Input Validation |
| Testing | ✅ Complete | 32/32 tests passing (100% coverage of infrastructure) |
| Snake Game | ✅ Refactored | Using new BaseGame architecture, production-ready |
| Other Games | ⏳ Pending | Phase 2 - Will refactor remaining 8 games using Snake model |
| Code Quality | ✅ Improved | Fixed 50+ issues; standardized naming, exceptions, patterns |
| Documentation | ✅ Complete | 7 comprehensive guides created |

## 🚀 Installation & Usage

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Imposter-zx/All-Games.git
    cd All-Games
    ```

2.  **Create and activate virtual environment (recommended)**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    
    # Linux/Mac
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r terminal_games/requirements.txt
    ```

4.  **Run the Arcade**
    ```bash
    cd terminal_games
    python arcade.py
    ```

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_base_game.py -v

# Run with coverage
python -m pytest tests/ --cov=terminal_games
```

## 🛠️ Project Structure

```
All Games/
├── terminal_games/
│   ├── arcade.py              # Main launcher
│   ├── base_game.py           # Abstract base class (NEW)
│   ├── stats_manager.py       # Centralized stats system (NEW)
│   ├── error_handler.py       # Error handling wrapper (NEW)
│   ├── input_handler.py       # Input validation (NEW)
│   ├── logger_setup.py        # Logging configuration (NEW)
│   ├── arcade_utils.py        # ANSI-safe UI utilities
│   ├── snake.py               # Snake (refactored ✨)
│   ├── pacman.py              # Pac-Man
│   ├── breakout.py            # Breakout
│   ├── tetris.py              # Tetris
│   ├── space_shooter.py       # Space Shooter
│   ├── minesweeper.py         # Minesweeper
│   ├── chess_game.py          # Chess vs AI
│   ├── sudoku.py              # Sudoku
│   ├── dungeon.py             # Dungeon Crawler
│   ├── player_stats.json      # Player progression (persisted)
│   └── requirements.txt       # Dependencies
├── tests/
│   ├── test_base_game.py      # BaseGame tests (14 tests)
│   └── test_stats_manager.py  # StatsManager tests (18 tests)
├── README.md                  # This file
├── PHASE1_COMPLETE.md         # Phase 1 completion details
├── IMPLEMENTATION_COMPLETE.md # Detailed implementation notes
└── .gitignore
```

## 📈 Architecture & Design Patterns

### Phase 1 Infrastructure

#### BaseGame Abstract Class
All games inherit from `BaseGame` and implement:
- `play()` - Main game loop
- `_render()` - Frame rendering
- `_handle_input()` - Input processing  
- `_update_game_state()` - Game logic

```python
class SnakeGame(BaseGame):
    def play(self):
        self.start_timer()
        try:
            # Your game loop
            pass
        finally:
            self.end_timer()
        return self.get_final_stats()
```

#### StatsManager (Singleton)
Global stats management with XP/leveling system:
- `add_xp(amount)` - Award XP with level calculation
- `update_game_stats(game_name, stats_dict)` - Save game results
- `get_level_and_xp()` - Get progression info
- `get_high_score(game_name)` - Retrieve best scores

#### Error Handling
Consistent exception handling with `safe_game_call()`:
- Catches and logs all exceptions
- Handles KeyboardInterrupt gracefully
- Displays user-friendly error messages

#### Input Validation
Centralized input validation with `InputValidator`:
- `validate_direction()` - Movement input
- `validate_yes_no()` - Binary choices
- `validate_selection()` - Menu choices
- Non-blocking input with timeout

## 📋 Development Roadmap

### Phase 1: ✅ COMPLETE
- [x] Create BaseGame abstract class
- [x] Create StatsManager singleton
- [x] Setup error handling infrastructure
- [x] Setup input validation framework
- [x] Setup logging system
- [x] Fix exception handling (50+ issues)
- [x] Standardize field names
- [x] Refactor Snake game
- [x] Create comprehensive test suite (32 tests)
- [x] Fix sudoku.py indentation error

### Phase 2: ⏳ PENDING
- [ ] Refactor Tetris using BaseGame
- [ ] Refactor Breakout using BaseGame
- [ ] Refactor Pac-Man using BaseGame
- [ ] Refactor Space Shooter using BaseGame
- [ ] Refactor Chess using BaseGame
- [ ] Refactor Dungeon using BaseGame
- [ ] Refactor Minesweeper using BaseGame
- [ ] Refactor Sudoku using BaseGame
- [ ] Expand test coverage to all games

### Phase 3: 📋 PLANNED
- [ ] Difficulty modes implementation
- [ ] Achievements/badges system
- [ ] Theme customization
- [ ] Multiplayer support (network)
- [ ] New game additions

## 🐛 Known Issues & Fixes

| Issue | Status | Solution |
|-------|--------|----------|
| Bare except clauses (50+ instances) | ✅ Fixed | Replaced with specific exceptions |
| Field name inconsistency | ✅ Fixed | Standardized to 'high_score' |
| No architecture pattern | ✅ Fixed | Implemented BaseGame abstract class |
| No test coverage | ✅ Fixed | Created 32-test suite (100% pass) |
| No centralized stats | ✅ Fixed | Implemented StatsManager singleton |
| Missing error handler | ✅ Fixed | Added safe_game_call wrapper |

## 🤝 Contributing

### Code Quality Standards
1. All new code must inherit from `BaseGame`
2. Use specific exception types (no bare `except:`)
3. Add comprehensive docstrings
4. Run test suite: `pytest tests/ -v`
5. Follow existing code style

### Testing Requirements
- All new features must have unit tests
- Target: 100% pass rate on test suite
- No regressions in existing games

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Created and maintained by Imposter-zx

## 🔗 Links

- **GitHub**: https://github.com/Imposter-zx/All-Games
- **Documentation**: See [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) for detailed progress
- **Implementation Notes**: See [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

---

**Last Updated**: April 2026 | **Phase 1 Status**: ✅ Complete and Verified
