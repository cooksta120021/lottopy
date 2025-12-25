"""
Deprecated: kept for backward compatibility. Game configs now live in lottopy.games.*
"""

from .games.mega_millions import MEGA_MILLIONS  # noqa: F401
from .games.texas_two_step import TEXAS_TWO_STEP  # noqa: F401

GAME_CONFIGS = {
    "mega_millions": MEGA_MILLIONS,
    "texas_two_step": TEXAS_TWO_STEP,
}
