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

    # New Game Specific Achievements
    "pacman_clear": {"name": "Ghost Hunter", "description": "Clear a level in Pac-Man", "xp": 400},
    "space_shooter_1000": {"name": "Space Ace", "description": "Score 1000 in Space Shooter", "xp": 300},
    "breakout_win": {"name": "Wall Breaker", "description": "Clear all bricks in Breakout", "xp": 400},
    "chess_win": {"name": "Grandmaster", "description": "Win a game of Chess", "xp": 500},
    "dungeon_escape": {"name": "Legendary Hero", "description": "Escape the dungeon level 5", "xp": 1000},
    
    # 2048 Achievements
    "2048_rookie": {"name": "Halfway There", "description": "Reach the 512 tile in 2048", "xp": 200},
    "2048_expert": {"name": "Millennial", "description": "Reach the 1024 tile in 2048", "xp": 500},
    "2048_master": {"name": "Ultimate Logic", "description": "Reach the 2048 tile in 2048", "xp": 1000},
    
    # Pong Achievements
    "pong_pro": {"name": "Pong Pro", "description": "Get 10 hits in Pong", "xp": 200},
    "pong_master": {"name": "Pong Master", "description": "Get 25 hits in Pong", "xp": 500},
    
    # Asteroids Achievements
    "asteroids_500": {"name": "Space Pilot", "description": "Score 500 in Asteroids", "xp": 300},
    "asteroids_1000": {"name": "Void Master", "description": "Score 1000 in Asteroids", "xp": 500},
}

def get_achievement(achievement_id):
    return ACHIEVEMENTS.get(achievement_id)
