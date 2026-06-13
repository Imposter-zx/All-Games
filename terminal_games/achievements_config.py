"""Definitions for all arcade achievements."""

from typing import Any, Dict, Optional

ACHIEVEMENTS: Dict[str, Dict[str, Any]] = {
    # General
    "first_game": {"name": "First Steps", "description": "Play your first game", "xp": 100},
    "level_5": {"name": "Rising Star", "description": "Reach level 5", "xp": 500},
    "level_10": {"name": "Arcade Pro", "description": "Reach level 10", "xp": 1000},

    # Snake
    "snake_100": {"name": "Slither Master", "description": "Score 100 in Snake", "xp": 200},
    "snake_500": {"name": "Python King", "description": "Score 500 in Snake", "xp": 500},
    "snake_1000": {"name": "Anaconda", "description": "Score 1000 in Snake", "xp": 1000},

    # Tetris
    "tetris_1000": {"name": "Block Architect", "description": "Score 1000 in Tetris", "xp": 200},

    # Minesweeper
    "mines_win": {"name": "Demolition Expert", "description": "Clear a Minesweeper board", "xp": 300},

    # Sudoku
    "sudoku_win": {"name": "Logic Wizard", "description": "Complete a Sudoku puzzle", "xp": 300},

    # Pac-Man
    "pacman_clear": {"name": "Ghost Hunter", "description": "Clear a level in Pac-Man", "xp": 400},
    "pacman_10000": {"name": "Wakka Wizard", "description": "Score 10000 in Pac-Man", "xp": 600},
    "pacman_no_dot_left": {"name": "Clean Plate", "description": "Eat ALL dots in a Pac-Man level", "xp": 500},

    # Space Shooter
    "space_shooter_1000": {"name": "Space Ace", "description": "Score 1000 in Space Shooter", "xp": 300},
    "space_shooter_5000": {"name": "Galactic Lord", "description": "Score 5000 in Space Shooter", "xp": 800},
    "space_shooter_10000": {"name": "Universe Master", "description": "Score 10000 in Space Shooter", "xp": 2000},

    # Breakout
    "breakout_win": {"name": "Wall Breaker", "description": "Clear all bricks in Breakout", "xp": 400},
    "breakout_500": {"name": "Brick Layer", "description": "Score 500 in Breakout", "xp": 300},
    "breakout_no_death": {"name": "Untouchable",
                          "description": "Clear a Breakout level without losing a life", "xp": 800},

    # Chess
    "chess_win": {"name": "Grandmaster", "description": "Win a game of Chess", "xp": 500},

    # Dungeon
    "dungeon_escape": {"name": "Legendary Hero", "description": "Escape the dungeon level 5", "xp": 1000},
    "dungeon_level_10": {"name": "Immortal", "description": "Reach dungeon level 10", "xp": 2000},
    "dungeon_100_kills": {"name": "Slayer", "description": "Kill 100 monsters in Dungeon", "xp": 500},

    # 2048
    "2048_rookie": {"name": "Halfway There", "description": "Reach the 512 tile in 2048", "xp": 200},
    "2048_expert": {"name": "Millennial", "description": "Reach the 1024 tile in 2048", "xp": 500},
    "2048_master": {"name": "Ultimate Logic", "description": "Reach the 2048 tile in 2048", "xp": 1000},

    # Pong
    "pong_pro": {"name": "Pong Pro", "description": "Get 10 hits in Pong", "xp": 200},
    "pong_master": {"name": "Pong Master", "description": "Get 25 hits in Pong", "xp": 500},

    # Asteroids
    "asteroids_500": {"name": "Space Pilot", "description": "Score 500 in Asteroids", "xp": 300},
    "asteroids_1000": {"name": "Void Master", "description": "Score 1000 in Asteroids", "xp": 500},

    # Frogger
    "frogger_first": {"name": "Crosser", "description": "Reach the goal for the first time in Frogger", "xp": 200},
    "frogger_5": {"name": "Highway Hero", "description": "Reach the goal 5 times in one game", "xp": 500},
    "frogger_10": {"name": "Leap Master", "description": "Reach the goal 10 times in one game", "xp": 1000},

    # Flappy
    "flappy_10": {"name": "Birdie", "description": "Score 10 in Flappy Bird", "xp": 300},
    "flappy_50": {"name": "Ace Flyer", "description": "Score 50 in Flappy Bird", "xp": 1000},

    # Racing
    "racing_100": {"name": "Speedster", "description": "Score 100 in Racing", "xp": 200},
    "racing_500": {"name": "Pro Racer", "description": "Score 500 in Racing", "xp": 500},

    # Blackjack
    "blackjack_natural": {"name": "Natural Blackjack", "description": "Get 21 in your first two cards", "xp": 200},
    "blackjack_500": {"name": "Blackjack Pro", "description": "Score 500 total in Blackjack", "xp": 500},

    # Connect Four
    "connect_four_win": {"name": "Connect Four Champion", "description": "Win a game of Connect Four", "xp": 300},

    # Hangman
    "hangman_first_win": {"name": "Word Detective", "description": "Win a game of Hangman", "xp": 150},
    "hangman_streak": {"name": "Hangman Streak", "description": "Win 3 Hangman games in a row", "xp": 300},

    # Wordle
    "wordle_win": {"name": "Wordle Wizard", "description": "Guess the Wordle word correctly", "xp": 300},
    "wordle_first_try": {"name": "Lucky Guess", "description": "Get Wordle on the first try", "xp": 1000},
    "wordle_streak": {"name": "Wordle Streak", "description": "Win 3 Wordle rounds in a row", "xp": 500},

    # Tic-Tac-Toe
    "tictactoe_win": {"name": "Tic-Tac-Toe Champion", "description": "Win a game of Tic-Tac-Toe", "xp": 200},
    "tictactoe_perfect": {"name": "Perfect Game",
                          "description": "Win without the opponent making a single move", "xp": 500},
    "tictactoe_streak": {"name": "Tic-Tac-Toe Streak", "description": "Win 3 Tic-Tac-Toe games in a row", "xp": 300},
    "tictactoe_streak_5": {"name": "Unstoppable", "description": "Win 5 Tic-Tac-Toe games in a row", "xp": 1000},

    # Simon Says
    "simon_first_win": {"name": "Simon Says Champion",
                        "description": "Complete a round in Simon Says", "xp": 150},
    "simon_streak_3": {"name": "Simon Streak",
                       "description": "Win 3 Simon Says games in a row", "xp": 300},
    "simon_streak_5": {"name": "Memory Master",
                       "description": "Win 5 Simon Says games in a row", "xp": 800},

    # Trivia
    "trivia_first_win": {"name": "Trivia Novice",
                         "description": "Complete your first Trivia game", "xp": 100},
    "trivia_perfect": {"name": "Trivia Genius",
                       "description": "Answer every question correctly", "xp": 1000},
    "trivia_streak_3": {"name": "Trivia Streak",
                        "description": "Win 3 Trivia games in a row", "xp": 300},
    "trivia_streak_5": {"name": "Trivia Legend",
                        "description": "Win 5 Trivia games in a row", "xp": 1000},
    "trivia_grade_a": {"name": "Honor Student",
                       "description": "Score an A grade in Trivia", "xp": 500},

    # Slots
    "slots_first_spin": {"name": "First Spin",
                         "description": "Spin the slots for the first time", "xp": 50},
    "slots_jackpot": {"name": "Jackpot!",
                      "description": "Hit the jackpot (3 SEVENS)", "xp": 2000},
    "slots_100_spins": {"name": "Slot Addict",
                        "description": "Spin 100 times", "xp": 500},
    "slots_500_coins": {"name": "High Roller",
                        "description": "Accumulate 500 coins", "xp": 1000},

    # Memory
    "memory_first_win": {"name": "First Match",
                         "description": "Complete your first Memory game", "xp": 100},
    "memory_perfect": {"name": "Perfect Memory",
                       "description": "Complete a game with 0 extra attempts", "xp": 1500},
    "memory_streak_3": {"name": "Memory Streak",
                        "description": "Win 3 Memory games in a row", "xp": 300},
    "memory_streak_5": {"name": "Memory Legend",
                        "description": "Win 5 Memory games in a row", "xp": 1000},

    # Battleship
    "battleship_first_win": {"name": "First Blood",
                             "description": "Win your first Battleship game", "xp": 200},
    "battleship_perfect": {"name": "Perfect Victory",
                           "description": "Win without losing any ships", "xp": 2000},
    "battleship_streak_3": {"name": "Naval Commander",
                            "description": "Win 3 Battleship games in a row", "xp": 500},
    "battleship_fast_win": {"name": "Speed Demon",
                            "description": "Win in under 15 turns", "xp": 1000},

    # Crossword
    "crossword_first_win": {"name": "Word Wizard",
                            "description": "Complete your first Crossword", "xp": 200},
    "crossword_no_hints": {"name": "Pure Genius",
                           "description": "Complete a Crossword without hints", "xp": 1500},
    "crossword_streak_3": {"name": "Crossword Streak",
                           "description": "Win 3 Crossword games in a row", "xp": 500},

    # Tower of Hanoi
    "hanoi_first_win": {"name": "First Tower",
                        "description": "Solve your first Tower of Hanoi", "xp": 200},
    "hanoi_perfect": {"name": "Perfect Solution",
                      "description": "Solve in minimum moves", "xp": 2000},
    "hanoi_streak_3": {"name": "Hanoi Streak",
                       "description": "Solve 3 Hanoi puzzles in a row", "xp": 500},
    "hanoi_5_disks": {"name": "Master of Hanoi",
                      "description": "Solve with 5 disks", "xp": 1000},

    # Typer
    "typer_first_game": {"name": "First Typing Test",
                         "description": "Complete your first typing test", "xp": 100},
    "typer_wpm_50": {"name": "Fast Fingers",
                     "description": "Achieve 50 WPM", "xp": 500},
    "typer_wpm_80": {"name": "Speed Demon",
                     "description": "Achieve 80 WPM", "xp": 1500},
    "typer_accuracy_100": {"name": "Perfect Accuracy",
                           "description": "Complete a game with 100% accuracy", "xp": 2000},

    # Solitaire
    "solitaire_first_win": {"name": "First Solitaire",
                            "description": "Win your first Solitaire game", "xp": 300},
    "solitaire_fast_win": {"name": "Speed Dealer",
                           "description": "Win in under 100 moves", "xp": 1500},
    "solitaire_streak_3": {"name": "Solitaire Streak",
                           "description": "Win 3 Solitaire games in a row", "xp": 500},

    # RPSLS
    "rpsls_first_win": {"name": "First Blood",
                        "description": "Win your first RPSLS match", "xp": 100},
    "rpsls_perfect": {"name": "Perfect Match",
                      "description": "Win a match 5-0", "xp": 1000},
    "rpsls_streak_3": {"name": "RPSLS Streak",
                       "description": "Win 3 RPSLS matches in a row", "xp": 300},

    # Poker
    "poker_royal": {"name": "Royal Flush!",
                    "description": "Get a Royal Flush in Video Poker", "xp": 2000},
    "poker_500": {"name": "Poker High Roller",
                  "description": "Win 500+ total credits in Poker", "xp": 500},
    "poker_1000": {"name": "Poker Millionaire",
                   "description": "Reach 1000 credits in a Poker session", "xp": 1000},

    # Mastermind
    "mastermind_first_win": {"name": "First Crack",
                             "description": "Crack your first Mastermind code", "xp": 100},
    "mastermind_quick": {"name": "Quick Thinker",
                         "description": "Solve in 3 tries or fewer", "xp": 500},
    "mastermind_perfect": {"name": "Perfect Mind",
                           "description": "Solve in 1 try!", "xp": 2000},

    # Gomoku
    "gomoku_first_win": {"name": "First Five",
                         "description": "Win your first Gomoku game", "xp": 100},
    "gomoku_streak_3": {"name": "Gomoku Streak",
                        "description": "Win 3 Gomoku games in a row", "xp": 500},
}


def get_achievement(achievement_id: str) -> Optional[Dict[str, Any]]:
    """Look up an achievement definition by ID."""
    return ACHIEVEMENTS.get(achievement_id)
