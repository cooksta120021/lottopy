from .base import GameConfig, ParseResult, register_game, get_game_config, available_games

# Import built-in games to register them on package import
from . import mega_millions  # noqa: F401
from . import texas_two_step  # noqa: F401

__all__ = [
    "GameConfig",
    "ParseResult",
    "register_game",
    "get_game_config",
    "available_games",
]
