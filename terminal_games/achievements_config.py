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
}


def get_achievement(achievement_id: str) -> Optional[Dict[str, Any]]:
    """Look up an achievement definition by ID."""
    return ACHIEVEMENTS.get(achievement_id)
