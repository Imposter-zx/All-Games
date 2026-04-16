"""Logger setup for the terminal games arcade."""

import logging
import os
from pathlib import Path


def setup_logger(name: str = 'arcade', level=logging.INFO) -> logging.Logger:
    """
    Setup logging for the arcade application.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    log_dir = Path("terminal_games")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "debug.log"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create file handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger (avoid duplicates)
        if not logger.handlers:
            logger.addHandler(file_handler)
    
    except IOError as e:
        print(f"Warning: Could not create log file: {e}")
    
    # Also add console handler for errors
    try:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            logger.addHandler(console_handler)
    
    except Exception as e:
        print(f"Warning: Could not setup console logging: {e}")
    
    return logger


# Initialize default logger
logger = setup_logger()
