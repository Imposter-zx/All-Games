"""
Definitions for all arcade achievements.
"""

ACHIEVEMENTS = {
    # General Achievements
    "first_game": {"name": "First Steps", "description": "Play your first game", "xp": 100},
    "level_5": {"name": "Rising Star", "description": "Reach level 5", "xp": 500},
    "level_10": {"name": "Arcade Pro", "description": "Reach level 10", "xp": 1000},
    
    # Snake Achievements
    "snake_100": {"name": "Slither Master", "description": "Score 100 in Snake", "xp": 200},
    "snake_500": {"name": "Python King", "description": "Score 500 in Snake", "xp": 500},
    
    # Tetris Achievements
    "tetris_1000": {"name": "Block Architect", "description": "Score 1000 in Tetris", "xp": 200},
    
    # Minesweeper Achievements
    "mines_win": {"name": "Demolition Expert", "description": "Clear a Minesweeper board", "xp": 300},
    
    # Sudoku Achievements
    "sudoku_win": {"name": "Logic Wizard", "description": "Complete a Sudoku puzzle", "xp": 300},
}

def get_achievement(achievement_id):
    return ACHIEVEMENTS.get(achievement_id)
