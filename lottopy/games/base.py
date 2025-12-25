from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from bs4 import BeautifulSoup  # type: ignore

ParseResult = Tuple[List[str], List[str]]


@dataclass(frozen=True)
class GameConfig:
    key: str
    name: str
    url: str
    numbers_per_draw: int
    numbers_label: str
    special_labels: List[str]
    parse_row: Callable[[BeautifulSoup], ParseResult]


_REGISTRY: Dict[str, GameConfig] = {}


def register_game(config: GameConfig) -> None:
    _REGISTRY[config.key] = config


def get_game_config(game_key: str) -> GameConfig:
    key = game_key.lower()
    if key not in _REGISTRY:
        raise ValueError(f"Unsupported game '{game_key}'. Available: {', '.join(_REGISTRY.keys())}")
    return _REGISTRY[key]


def available_games() -> List[str]:
    return sorted(_REGISTRY.keys())
