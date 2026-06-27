# Retro Terminal Arcade

```


                   ____  _  _  ____  _   _  _____  _   _  
                  |  _ \| || ||_  _|| | | ||  _  || \ | | 
                  |  __/| \/ |  ||  | |_| || |_| ||  \| | 
                  |_|    \__/   |_|  \___/ |_| |_||_|\__| 
                   _____  ____  ____  __  ____  ____  ____
                  |  _  ||  _ \|  _ \|  ||  _ \|  __||_  _|
                  | |_| ||  _/| |  | \__/|  _/|  __|  ||  
                  |_| |_||_|  |_|__| |__| |_|  |____| |_| 
                                                          
                        --- RETRO ARCADE SYSTEM ---       
```

A collection of **36 classic terminal games** with XP progression, achievements, AI opponents, and an online leaderboard.

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![Tests](https://img.shields.io/badge/tests-126%2F126%20passing-brightgreen)
![Lint](https://img.shields.io/badge/lint-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blueviolet)

## Quick Start

```bash
git clone https://github.com/Imposter-zx/All-Games.git
cd "All Games"
pip install -e .
python -m terminal_games.arcade
```

## Screenshots

### Main Menu

```
                ╔════════════════════════════════════════════════╗
                ║                 👤 RETRO_MASTER                 ║
                ╠════════════════════════════════════════════════╣
                ║   LV:4 [★★★★] XP:1500 [░░░░░░░░░░░░░░░░░░░░]   ║
                ║    🏆 2ach  🎯 1162pts  🕹️ 24plays  ⏱️ 11m29s    ║
                ║         ══════════════════════════════         ║
                ║               🐍    100   0pl  0s               ║
                ║               🧱      0   0pl  0s               ║
                ║               ...                               ║
                ║               📦      0   0pl  0s               ║
                ║         ══════════════════════════════         ║
                ║          RECENT: Speedster, Pro Racer          ║
                ╚════════════════════════════════════════════════╝


                         ╔════════════════════════════╗
                         ║        🕹️ GAME MENU        ║
                         ╠════════════════════════════╣
                         ║  ►  1. 🐍 Snake             ║
                         ║     2. 🧱 Breakout          ║
                         ║     3. 🚀 Space Shooter     ║
                         ║     4. 🧩 Tetris            ║
                         ║     5. 🟡 Pacman            ║
                         ║     L. 🏆 Leaderboard       ║
                         ║     S. ⚙️ Settings         ║
                         ║     H. Tutorial            ║
                         ║     Q. 🚪 Quit              ║
                         ╚════════════════════════════╝

                      Use Arrows to navigate, Enter to play
```

### Game Previews

| Snake | Tetris | Chess | Pong |
|-------|--------|-------|------|
| <pre lang="text">╔═════════╗<br>║  SNAKE  ║<br>╚═════════╝</pre> | <pre lang="text">╔══════════╗<br>║  TETRIS  ║<br>╚══════════╝</pre> | <pre lang="text">╔═════════╗<br>║  CHESS  ║<br>╚═════════╝</pre> | <pre lang="text">╔════════╗<br>║  PONG  ║<br>╚════════╝</pre> |

## Games (36)

| # | Game | Description |
|---|------|-------------|
| 1 | Snake | High-speed survival |
| 2 | Breakout | Break bricks with paddle |
| 3 | Space Shooter | Combat with enemies |
| 4 | Tetris | Classic line-clear puzzle |
| 5 | Pac-Man | Maze chase with ghost AI |
| 6 | Dungeon Crawler | Roguelike dungeon explorer |
| 7 | Minesweeper | Logic mine detection |
| 8 | Chess | Chess vs AI with multiple skill levels |
| 9 | Sudoku | Number logic puzzles |
| 10 | 2048 | Merge tiles to 2048 |
| 11 | Pong | Table tennis vs CPU |
| 12 | Asteroids | Vector asteroid shooter |
| 13 | Frogger | Cross roads and rivers |
| 14 | Flappy Bird | Navigate through pipes |
| 15 | Racing | Dodge oncoming traffic |
| 16 | Blackjack | Card game vs dealer |
| 17 | Connect Four | Drop 4 in a row vs AI |
| 18 | Hangman | Guess the word |
| 19 | Wordle | Guess the 5-letter word |
| 20 | Tic-Tac-Toe | 3-in-a-row vs AI or 2-player |
| 21 | Simon Says | Memory sequence game |
| 22 | Trivia | Quiz with 7 categories |
| 23 | Slots | 3-reel slot machine |
| 24 | Memory | Card matching concentration |
| 25 | Battleship | Naval combat vs AI |
| 26 | Crossword | Puzzle with 3 difficulties |
| 27 | Tower of Hanoi | Disk stacking puzzle |
| 28 | Typer | Typing speed / WPM game |
| 29 | Solitaire | Klondike solitaire |
| 30 | RPSLS | Rock Paper Scissors Lizard Spock |
| 31 | Video Poker | 5-card draw with payouts |
| 32 | Mastermind | Code-breaking logic game |
| 33 | Gomoku | 5-in-a-row on 15x15 board |
| 34 | Othello | Reversi board game vs AI |
| 35 | Nonograms | Picross picture puzzle |
| 36 | Sokoban | Warehouse box-pushing puzzle |

## Features

- **XP & Leveling** — Gain XP across all games, level up, track progress
- **Achievements** — Unlock over 80 achievements for milestones
- **Difficulty** — Easy / Normal / Hard per game affects speed and XP
- **Visual Themes** — 8 color themes (classic, neon, retro, monochrome, matrix, cyberpunk, sunset, forest)
- **AI Opponents** — Chess, Pac-Man, Pong, Connect Four, Gomoku, Othello, and more
- **Online Leaderboard** — Submit and compare scores globally
- **Save & Resume** — Quit any game and resume later
- **Sound** — Synthesized sound effects and background music
- **Keyboard Navigation** — Arrow keys, number shortcuts, WASD support

### 🥚 Hidden Features

- **Konami Code** — Press ↑↑↓↓←→←→BA on main menu to unlock a secret developer menu
- **Marathon Mode** — Play all 36 games in one session with cumulative score and limited lives
- **Chaos Mutators** — Random game-altering effects (speed surges, screen shake, inverted controls, color flashes)
- **Secret Boss Fight** — A 4-phase meta-boss combining mechanics from multiple games
- **Rhythm Game** — Full terminal rhythm game with 3 songs and difficulty scaling
- **Easter Egg OS** — Hidden fake terminal with filesystem, secrets, and hidden messages

## Stats

| Metric | Value |
|--------|-------|
| Games | 36 |
| Hidden Modes | Marathon, Boss Fight, Rhythm, Chaos |
| Tests | 126 passing |
| Achievements | 80+ |
| Visual Themes | 8 |
| Python Support | 3.6+ |

## Tests

```bash
pytest tests/ -v
```

## Project Structure

```
terminal_games/
├── arcade.py              # Main launcher and menu
├── base_game.py           # Abstract base class
├── arcade_utils.py        # UI utilities and themes
├── stats_manager.py       # SQLite-backed persistence
├── sound_engine.py        # WAV synthesis engine
├── xp_config.py           # XP calculation
├── achievements_config.py # Achievement definitions
├── error_handler.py       # Error handling
├── input_handler.py       # Safe keyboard input
├── online_leaderboard.py  # REST API client
├── logger_setup.py        # Logging configuration
├── chaos_mutator.py       # Random game-altering effects
├── secret_menu.py         # Konami code easter egg menu
├── boss_fight.py          # Secret 4-phase boss fight
├── marathon.py            # 36-game marathon mode
├── rhythm.py              # Terminal rhythm game
├── game*.py               # 36 individual game modules
server/
├── main.py                # FastAPI leaderboard server
├── Dockerfile
└── requirements.txt
tests/
├── test_*.py              # 9 test modules
```

## Architecture

Each game extends `BaseGame` which provides scoring, XP, timers, save/load, and achievements. The `StatsManager` singleton (SQLite-backed) persists all player data. Games follow a uniform `play_X(difficulty) -> dict` pattern for seamless integration.

## License

MIT

---

**Last Updated**: June 2026 | **Version**: 2.1.0
