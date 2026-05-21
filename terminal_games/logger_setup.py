"""Logger setup for the terminal games arcade."""

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logger(name: str = 'arcade', level: int = logging.INFO) -> logging.Logger:
    """Configure logging for the arcade application."""
    log_dir = Path.home() / ".retro_arcade"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "debug.log"

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        try:
            file_handler = logging.FileHandler(str(log_file))
            file_handler.setLevel(level)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        except IOError as e:
            print(f"Warning: Could not create log file: {e}")

        try:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        except Exception as e:
            print(f"Warning: Could not setup console logging: {e}")

    return logger


# Initialize default logger
logger: logging.Logger = setup_logger()
