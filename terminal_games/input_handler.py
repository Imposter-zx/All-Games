"""Input handling and validation utilities."""

import logging
import os
import sys
import time
from typing import Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and maps input to game actions."""

    DIRECTION_MAP: dict = {
        'up': {'up', 'w', 'W'},
        'down': {'down', 's', 'S'},
        'left': {'left', 'a', 'A'},
        'right': {'right', 'd', 'D'}
    }

    def __init__(self, allow_wasd: bool = True, allow_arrows: bool = True,
                 allow_numpad: bool = False) -> None:
        self.allow_wasd = allow_wasd
        self.allow_arrows = allow_arrows
        self.allow_numpad = allow_numpad
        self.last_direction: Optional[str] = None

    def validate_direction(self, key: Optional[str]) -> Optional[str]:
        if key is None:
            return None

        key_str = str(key).lower()

        for direction, valid_keys in self.DIRECTION_MAP.items():
            if key_str in valid_keys or key in valid_keys:
                self.last_direction = direction
                return direction

        return None

    def validate_yes_no(self, key: Optional[str]) -> Optional[bool]:
        if key is None:
            return None

        key_str = str(key).lower()

        if key_str in ['y', 'yes', '1', 'return', 'enter']:
            return True
        elif key_str in ['n', 'no', '0', 'escape']:
            return False

        return None

    def validate_selection(self, key: Optional[str], num_options: int) -> Optional[int]:
        if key is None:
            return None

        try:
            idx = int(key)
            if 0 <= idx < num_options:
                return idx
        except (ValueError, TypeError):
            pass

        return None

    def validate_coordinate(self, key: Optional[str]) -> Optional[tuple]:
        if key is None:
            return None

        key_str = str(key).lower()

        if len(key_str) >= 2:
            file_val = ord(key_str[0]) - ord('a')
            try:
                rank = int(key_str[1]) - 1
                if 0 <= file_val < 8 and 0 <= rank < 8:
                    return (file_val, rank)
            except ValueError:
                pass

        return None

    def is_quit(self, key: Optional[str]) -> bool:
        if key is None:
            return False

        key_str = str(key).lower()
        return key_str in ['q', 'quit', 'escape', 'esc']


class SafeInputHandler:
    """Safe input handler with timeout and buffering."""

    def __init__(self, timeout: float = 0.05) -> None:
        self.timeout = timeout
        self.validator = InputValidator()

    def get_safe_key(self) -> Optional[str]:
        from arcade_utils import get_key as get_key_func

        if os.name == 'nt':
            import msvcrt
            if msvcrt.kbhit():
                try:
                    return get_key_func()
                except Exception as e:
                    logger.warning(f"Error getting key: {e}")
                    return None
            time.sleep(self.timeout)
            return None
        else:
            import select
            if select.select([sys.stdin], [], [], self.timeout)[0]:
                try:
                    return get_key_func()
                except Exception as e:
                    logger.warning(f"Error getting key: {e}")
                    return None
            return None

    def get_direction(self, timeout: Optional[float] = None) -> Optional[str]:
        old_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout

        key = self.get_safe_key()
        direction = self.validator.validate_direction(key)

        self.timeout = old_timeout
        return direction

    def get_yes_no(self) -> Optional[bool]:
        from arcade_utils import get_key as get_key_func

        while True:
            try:
                key = get_key_func()
                result = self.validator.validate_yes_no(key)
                if result is not None:
                    return result
            except KeyboardInterrupt:
                return None
            except Exception as e:
                logger.warning(f"Input error: {e}")
                return None


# Global instances
_validator: Optional[InputValidator] = None
_safe_handler: Optional[SafeInputHandler] = None


def get_input_validator() -> InputValidator:
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator


def get_safe_input_handler() -> SafeInputHandler:
    global _safe_handler
    if _safe_handler is None:
        _safe_handler = SafeInputHandler()
    return _safe_handler
