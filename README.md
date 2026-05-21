# 🕹️ Retro Terminal Arcade V2: The Production Release

A premium collection of 15 classic terminal games with a polished TUI, XP/Leveling system, procedural dungeons, and immersive visual effects. **Now with SQLite persistence, sound engine, AI opponents, full type safety, and CI/CD pipeline.**

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Tests](https://img.shields.io/badge/tests-41%2F41%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blueviolet)
![Version](https://img.shields.io/badge/version-2.0.0-blue)

## 🚀 Installation & Usage

```bash
pip install git+https://github.com/Imposter-zx/All-Games.git
retro-arcade
```

For local development:
```bash
git clone https://github.com/Imposter-zx/All-Games.git
cd "All Games"
pip install -e .
retro-arcade
```

## 🎮 Games Included

1.  **⚔️ Dungeon Crawler** — Roguelike exploration with procedural rooms, turn-based combat, loot.
2.  **🟡 Pac-Man** — Classic grid movement with ghost AI and powerups.
3.  **🐍 Snake** — High-speed survival with XP rewards.
4.  **🧱 Breakout** — Physics-based brick destruction with screen shake.
5.  **🧩 Tetris** — Modern implementation with line clear XP.
6.  **🚀 Space Shooter** — Fast-paced combat with particle effects.
7.  **💣 Minesweeper** — Classic logic-based mine detection.
8.  **♟️ Chess vs AI** — Stockfish engine or heuristic AI; configurable skill level.
9.  **🔢 Sudoku** — Logic puzzles with persistence bonuses.
10. **🔢 2048** — Merge tiles to reach 2048.
11. **🏓 Pong** — CPU opponent with ball trajectory prediction.
12. **☄️ Asteroids** — Vector shooter with space debris.
13. **🐸 Frogger** — Guide the frog across roads and rivers.
14. **🐦 Flappy Bird** — Navigate through pipes.
15. **🏎️ Racing** — Dodge oncoming cars at high speed.

## ✨ V2.0.0 Features

### Core Gaming
- **Global RPG Progression**: Gain XP across ALL games, level up, track achievements.
- **Difficulty Selection**: Easy (0.5x), Normal (1.0x), Hard (2.0x) — affects speed & XP.
- **Visual Juice**: Screen shakes, particles, ANSI-safe rendering.
- **AI Opponents**: Chess (Stockfish + heuristic), Pac-Man (4 ghost personalities), Pong (trajectory prediction).
- **Tutorial System**: Press `H` in any game for contextual help; option 17 in main menu for full tutorial.

### Infrastructure
- **SQLite Persistence**: Player stats, sessions, achievements, telemetry stored in `~/.retro_arcade/player.db`.
- **Sound Engine**: Synthesized WAV audio (sine/square/noise), background music, cross-platform playback.
- **Full Type Annotations**: mypy-compatible on all 20+ modules.
- **CI/CD Pipeline**: GitHub Actions — matrix test (3.8–3.11 × Linux/Windows), ruff lint, mypy, pytest with coverage, PyPI publish on release.
- **Telemetry & Analytics**: Session tracking, app start/stop events, game completions.

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Infrastructure | ✅ Complete | BaseGame, StatsManager (SQLite), Error Handlers, Input Validation |
| Testing | ✅ Complete | 41/41 tests passing |
| Game Migration | ✅ Complete | All 15 games refactored to BaseGame architecture |
| Difficulty System | ✅ Complete | Dynamic speed/XP scaling |
| XP Integration | ✅ Complete | Global progression synced across all modules |
| AI Opponents | ✅ Complete | Chess (Stockfish), Pac-Man (ghost personalities), Pong (prediction) |
| Sound Engine | ✅ Complete | Waveform synthesis, background music, cross-platform |
| Type Annotations | ✅ Complete | mypy-compatible across all modules |
| CI/CD Pipeline | ✅ Complete | GitHub Actions — lint, test, type-check, publish |
| Telemetry | ✅ Complete | Sessions, events, analytics |
| Tutorial System | ✅ Complete | In-game H key help, dedicated tutorial screen |
| Packaging & Dist | ✅ Complete | pip-installable via GitHub, `retro-arcade` CLI entry point |

## 🧪 Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=terminal_games
```

## 🛠️ Project Structure

```
All Games/
├── terminal_games/
│   ├── arcade.py              # Main launcher + tutorial screen
│   ├── base_game.py           # Abstract base class with session/telemetry
│   ├── stats_manager.py       # SQLite-backed stats, sessions, telemetry
│   ├── sound_engine.py        # WAV synthesis + background music
│   ├── error_handler.py       # Error handling wrapper
│   ├── input_handler.py       # Safe input handling
│   ├── xp_config.py           # XP calculation logic
│   ├── logger_setup.py        # Logging configuration
│   ├── arcade_utils.py        # ANSI-safe UI utilities
│   ├── achievements_config.py # Achievement definitions
│   ├── snake.py, pacman.py, breakout.py, tetris.py
│   ├── space_shooter.py, minesweeper.py, chess_game.py
│   ├── sudoku.py, dungeon.py, game_2048.py, pong.py
│   ├── asteroids.py, frogger.py, flappy.py, racing.py
│   └── requirements.txt
├── tests/
│   ├── test_base_game.py      # BaseGame tests
│   └── test_stats_manager.py  # StatsManager (SQLite) tests
├── .github/workflows/
│   ├── ci.yml                 # Matrix test + lint + typecheck + publish
│   └── lint.yml               # Black + ruff check
├── setup.py                   # v2.0.0 packaging
├── pyproject.toml              # Build/config
└── README.md
```

## 📈 Architecture

- **BaseGame**: Abstract class — `play()`, `_render()`, `_handle_input()`, `_update_game_state()` — auto-records sessions & telemetry.
- **StatsManager**: Singleton backed by SQLite — `add_xp()`, `record_session()`, `get_leaderboard()`, `record_telemetry()`.
- **SoundEngine**: Synthesizes WAV at runtime, falls back to terminal beep gracefully.
- **AI** — Chess: Stockfish auto-detection + skill levels. Pac-Man: Blinky/Pinky/Inky/Sue personalities. Pong: reaction delay + trajectory prediction.

## 📝 License

MIT License

## 👤 Author

Created and maintained by Imposter-zx

---

**Last Updated**: May 2026 | **Version**: 2.0.0
