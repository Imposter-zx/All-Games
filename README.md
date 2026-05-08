# 🕹️ Retro Terminal Arcade V5: The RPG Update

A premium collection of classic terminal games with a polished TUI, XP/Leveling system, procedural dungeons, and immersive visual effects. **Now with production-ready infrastructure, comprehensive testing, and clean architecture patterns.**

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Tests](https://img.shields.io/badge/tests-32%2F32%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blueviolet)

## 🎮 Games Included (All Refactored ✨)

1.  **⚔️ Dungeon Crawler**
    - Roguelike exploration with procedural rooms.
    - Turn-based combat, loot collection, and level progression.
2.  **🟡 Pac-Man**
    - Classic grid movement with ghost AI and powerups.
3.  **🐍 Snake**
    - High-speed survival with XP rewards for eating.
4.  **🧱 Breakout**
    - Physics-based brick destruction with screen shake and particles.
5.  **🧩 Tetris**
    - Modern implementation with line clears awarding massive XP.
6.  **🚀 Space Shooter**
    - Fast-paced combat with explosive particle effects.
7.  **💣 Minesweeper**
    - Classic logic-based mine detection with high XP on victory.
8.  **♟️ Chess vs AI**
    - Play against AI; XP for captures and wins.
9.  **🔢 Sudoku**
    - Logic puzzles with a persistence bonus.

## ✨ V5 Features: The RPG Update + Production Infrastructure (✅ Complete)

### Core Gaming Features
- **Global RPG Progression**: Gain XP across ALL games. Level up to see your rank grow on your persistent profile.
- **Difficulty Selection**: Choose between EASY, NORMAL, and HARD. Difficulty affects game speed and XP multipliers (Easy: 0.5x, Normal: 1.0x, Hard: 2.0x).
- **Visual Juice**: Immersive screen shakes and particle effects for combat, line clears, and explosions.
- **Enhanced Profile**: Sleek XP progress bar and level display in the main arcade menu.
- **ANSI-Safe Rendering**: Premium TUI alignment and design across all game modules.
- **Cross-Platform**: Optimized for Windows and Unix terminals.

### Production Infrastructure (✅ Complete)
- **Solid Architecture**: Abstract `BaseGame` class provides consistent interface for all 9 games.
- **Centralized Stats Management**: Singleton `StatsManager` handles all XP, levels, and game statistics.
- **XP Config System**: Dynamic XP calculation with difficulty-based multipliers.
- **Comprehensive Testing**: 32 automated unit tests with 100% pass rate.
- **Professional Error Handling**: Consistent exception handling and input validation via `safe_game_call`.
- **Safe Input Handler**: Robust, non-blocking input handling with direction validation.
- **Debug Logging**: Integrated logging system for troubleshooting.

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Infrastructure | ✅ Complete | BaseGame, StatsManager, Error Handlers, Input Validation |
| Testing | ✅ Complete | 32/32 tests passing (100% coverage of infrastructure) |
| Game Migration | ✅ Complete | All 9 games refactored to BaseGame architecture |
| Difficulty System | ✅ Complete | Dynamic speed/XP scaling based on player choice |
| XP Integration | ✅ Complete | Global progression synced across all modules |
| Code Quality | ✅ Improved | Fixed 50+ issues; standardized naming, exceptions, patterns |
| Documentation | ✅ Complete | 7+ comprehensive guides created |

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
│   ├── arcade.py              # Main launcher (Difficulty Selection)
│   ├── base_game.py           # Abstract base class
│   ├── stats_manager.py       # Centralized stats system
│   ├── error_handler.py       # Error handling wrapper
│   ├── input_handler.py       # Input validation & Safe key handling
│   ├── xp_config.py           # XP calculation logic (NEW)
│   ├── logger_setup.py        # Logging configuration
│   ├── arcade_utils.py        # ANSI-safe UI utilities
│   ├── snake.py               # Snake
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
├── SUMMARY.md                 # Completion summary
├── DEVELOPMENT_GUIDE.md       # Dev instructions
└── .gitignore
```

## 📈 Architecture & Design Patterns

### BaseGame Abstract Class
All 9 games inherit from `BaseGame` and implement a standardized loop:
- `play()` - Main game entry point
- `_render()` - Frame rendering
- `_handle_input()` - Input processing  
- `_update_game_state()` - Game logic

### StatsManager (Singleton)
Global stats management with XP/leveling system:
- `add_xp(amount)` - Award XP with level calculation
- `update_game_stats(game_name, stats_dict)` - Save game results
- `get_level_and_xp()` - Get progression info

### XP Config & Difficulty
XP is calculated dynamically based on game-specific metrics (points, lines, kills) and modified by the chosen difficulty level.

## 📋 Development Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Create BaseGame abstract class
- [x] Create StatsManager singleton
- [x] Setup error handling & input validation
- [x] Refactor Snake game & setup test suite

### Phase 2: Game Migration ✅ COMPLETE
- [x] Refactor Tetris, Breakout, Pac-Man, Space Shooter
- [x] Refactor Chess, Dungeon, Minesweeper, Sudoku
- [x] Ensure all games use standardized `high_score` field

### Phase 3: Advanced Features ✅ COMPLETE
- [x] Difficulty modes (Easy, Normal, Hard)
- [x] Global XP scaling integration
- [x] Enhanced Main Menu with Profile Stats

### Phase 4: Polish & Performance ⏳ IN PROGRESS
- [ ] Implement FPS limiter for smoother rendering
- [ ] Add more sound effects (beeps) for game events
- [ ] Optimize terminal clearing to reduce flicker
- [ ] Expand Achievements system

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Created and maintained by Imposter-zx

## 🔗 Links

- **GitHub**: https://github.com/Imposter-zx/All-Games
- **Documentation**: See [SUMMARY.md](SUMMARY.md) for detailed progress

---

**Last Updated**: May 2026 | **Current Status**: 🚀 Phase 2 & 3 Complete

