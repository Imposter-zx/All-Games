"""Abstract base class for all terminal games."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from arcade_utils import (
    C_GREEN,
    C_RED,
    C_RESET,
    C_YELLOW,
    Renderer,
    beep,
    show_popup,
)
from stats_manager import get_stats_manager
from xp_config import get_xp_system

logger = logging.getLogger(__name__)


class BaseGame(ABC):
    """Abstract base class for all terminal games."""

    def __init__(self, game_name: str, difficulty: str = 'normal') -> None:
        self.game_name = game_name
        self.difficulty = difficulty
        self.score = 0
        self.xp_earned = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.game_over = False
        self.stats_manager = get_stats_manager()
        self.xp_system = get_xp_system(difficulty)
        self.renderer = Renderer(fps=20)

    @abstractmethod
    def play(self) -> Dict[str, Any]:
        """Main game loop. Must be implemented by subclasses."""
        ...

    def unlock_achievement(self, achievement_id: str, name: str) -> None:
        """Unlock an achievement and show popup."""
        if self.stats_manager.unlock_achievement(achievement_id):
            beep("achievement")
            show_popup(f"🏆 ACHIEVEMENT UNLOCKED: {name}", delay=1.5)

    def add_xp(self, amount: int) -> None:
        if amount < 0:
            logger.warning(f"Negative XP amount: {amount}")
            return
        self.xp_earned += amount
        self.stats_manager.add_xp(amount)
        logger.debug(f"Awarded {amount} XP in {self.game_name}")

    def award_xp_for_action(self, base_value: int) -> int:
        xp = self.xp_system.calculate_xp(self.game_name, base_value)
        self.add_xp(xp)
        return xp

    def save_stats(self, stats_dict: Dict[str, Any]) -> None:
        """Save game stats and record session. Clears saved state on completion."""
        try:
            self.stats_manager.update_game_stats(self.game_name, stats_dict)
            self.stats_manager.record_session(
                game_name=self.game_name,
                score=self.score,
                xp_earned=self.xp_earned,
                duration=self.get_duration_seconds(),
                difficulty=self.difficulty
            )
            self.stats_manager.record_telemetry('game_completed', self.game_name)
            self.stats_manager.delete_game_state(self.game_name)
            logger.debug(f"Saved stats for {self.game_name}: {stats_dict}")
        except Exception as e:
            logger.error(f"Failed to save stats for {self.game_name}: {e}")

    def get_duration_seconds(self) -> int:
        if self.start_time and self.end_time:
            return int(self.end_time - self.start_time)
        return 0

    def get_final_stats(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'xp_earned': self.xp_earned,
            'duration_seconds': self.get_duration_seconds()
        }

    def start_timer(self) -> None:
        self.start_time = time.time()

    def end_timer(self) -> None:
        self.end_time = time.time()

    def validate_score(self, score: int) -> bool:
        if not isinstance(score, int) or score < 0:
            logger.warning(f"Invalid score: {score}")
            return False
        return True

    def save_state_json(self) -> Dict[str, Any]:
        return {}

    def load_state_json(self, state: Dict[str, Any]) -> None:
        pass

    def has_saved_state(self) -> bool:
        return self.stats_manager.has_game_state(self.game_name)

    def _save_and_quit(self, key: str) -> bool:
        if key == 'q':
            state = self.save_state_json()
            if state:
                self.stats_manager.save_game_state(self.game_name, state)
            self.game_over = True
            return True
        return False

    def _pause_game(self) -> None:
        show_popup(f"{C_YELLOW}PAUSED{C_RESET} — Press {C_GREEN}P{C_RESET} to resume or {C_RED}Q{C_RESET} to quit",
                   delay=0.0)
        from input_handler import get_safe_input_handler
        ih = get_safe_input_handler()
        while True:
            k = ih.get_safe_key()
            if k == 'p':
                break
            if k and k.lower() == 'q':
                self._save_and_quit('q')
                self.game_over = True
                break
            if k == '?':
                show_popup("P = Resume  Q = Quit (saves progress)", delay=1.0)
            time.sleep(0.05)

    def _prompt_resume(self) -> bool:
        if self.has_saved_state():
            show_popup(f"{self.game_name.upper()}: Saved game found. Press ENTER to resume or Q for new game.",
                       delay=1.5)
            return True
        return False
