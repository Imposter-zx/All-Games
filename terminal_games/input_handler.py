"""
Input handling and validation utilities.
Provides safe, robust input handling with timeout support.
"""

import time
import os
import sys
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and maps input to game actions."""
    
    # Standard directional input mappings
    DIRECTION_MAP = {
        'up': {(-1, 0), 'up', 'w', 'W', 'a', 'A'},
        'down': {(1, 0), 'down', 's', 'S'},
        'left': {(0, -1), 'left', 'a', 'A'},
        'right': {(0, 1), 'right', 'd', 'D'}
    }
    
    def __init__(self, allow_wasd=True, allow_arrows=True, allow_numpad=False):
        """
        Initialize input validator.
        
        Args:
            allow_wasd: Allow WASD keys for movement
            allow_arrows: Allow arrow keys for movement
            allow_numpad: Allow numpad keys for movement
        """
        self.allow_wasd = allow_wasd
        self.allow_arrows = allow_arrows
        self.allow_numpad = allow_numpad
        self.last_direction = None
    
    def validate_direction(self, key) -> str:
        """
        Validate input as direction and return normalized direction.
        
        Args:
            key: Raw input from get_key()
            
        Returns:
            'up', 'down', 'left', 'right', or None if invalid
        """
        if key is None:
            return None
        
        key_str = str(key).lower()
        
        # Check each direction
        for direction, valid_keys in self.DIRECTION_MAP.items():
            if key_str in valid_keys or key in valid_keys:
                self.last_direction = direction
                return direction
        
        return None
    
    def validate_yes_no(self, key) -> bool:
        """
        Validate input as yes/no response.
        
        Args:
            key: Raw input from get_key()
            
        Returns:
            True for yes, False for no, None if invalid
        """
        if key is None:
            return None
        
        key_str = str(key).lower()
        
        if key_str in ['y', 'yes', '1', 'return', 'enter']:
            return True
        elif key_str in ['n', 'no', '0', 'escape']:
            return False
        
        return None
    
    def validate_selection(self, key, num_options: int) -> int:
        """
        Validate input as menu selection.
        
        Args:
            key: Raw input from get_key()
            num_options: Number of menu options
            
        Returns:
            Selection number (0-indexed), or None if invalid
        """
        if key is None:
            return None
        
        key_str = str(key).lower()
        
        # Try to parse as number
        try:
            idx = int(key)
            if 0 <= idx < num_options:
                return idx
        except (ValueError, TypeError):
            pass
        
        return None
    
    def validate_coordinate(self, key) -> tuple:
        """
        Validate input as coordinate (for chess-like games).
        
        Args:
            key: Raw input (e.g., 'a1', 'h8')
            
        Returns:
            Tuple of (file, rank) or None if invalid
        """
        if key is None:
            return None
        
        key_str = str(key).lower()
        
        if len(key_str) >= 2:
            file = ord(key_str[0]) - ord('a')  # 0-7 for a-h
            try:
                rank = int(key_str[1]) - 1  # 0-7 for 1-8
                if 0 <= file < 8 and 0 <= rank < 8:
                    return (file, rank)
            except ValueError:
                pass
        
        return None
    
    def is_quit(self, key) -> bool:
        """
        Check if input is a quit command.
        
        Args:
            key: Raw input from get_key()
            
        Returns:
            True if quit, False otherwise
        """
        if key is None:
            return False
        
        key_str = str(key).lower()
        return key_str in ['q', 'quit', 'escape', 'esc']


class SafeInputHandler:
    """Safe input handler with timeout and buffering."""
    
    def __init__(self, timeout=0.05):
        """
        Initialize safe input handler.
        
        Args:
            timeout: Input timeout in seconds
        """
        self.timeout = timeout
        self.validator = InputValidator()
    
    def get_safe_key(self) -> str:
        """
        Get a key with timeout (non-blocking).
        
        Returns:
            Key string or None if no input
        """
        from arcade_utils import get_key as get_key_func
        
        if os.name == 'nt':
            # Windows non-blocking input
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
            # Unix non-blocking input
            import select
            if select.select([sys.stdin], [], [], self.timeout)[0]:
                try:
                    return get_key_func()
                except Exception as e:
                    logger.warning(f"Error getting key: {e}")
                    return None
            return None
    
    def get_direction(self, timeout=None) -> str:
        """
        Get direction input safely.
        
        Args:
            timeout: Optional custom timeout
            
        Returns:
            'up', 'down', 'left', 'right', or None
        """
        old_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout
        
        key = self.get_safe_key()
        direction = self.validator.validate_direction(key)
        
        self.timeout = old_timeout
        return direction
    
    def get_yes_no(self) -> bool:
        """
        Get yes/no response from user.
        
        Returns:
            True/False or None if invalid
        """
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


# Global input validator and handler
_validator = None
_safe_handler = None


def get_input_validator() -> InputValidator:
    """Get global input validator instance."""
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator


def get_safe_input_handler() -> SafeInputHandler:
    """Get global safe input handler instance."""
    global _safe_handler
    if _safe_handler is None:
        _safe_handler = SafeInputHandler()
    return _safe_handler
