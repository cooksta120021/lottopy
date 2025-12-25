from collections import Counter
from pathlib import Path
import random
import requests
from bs4 import BeautifulSoup  # type: ignore

from .games import get_game_config, GameConfig


def scrape_data(game: GameConfig, output_file: Path) -> None:
    response = requests.get(game.url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    rows = soup.select("table.large-only tbody tr")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        for row in rows:
            numbers, specials = game.parse_row(row)
            f.write(",".join(numbers + specials) + "\n")


def count_occurrences(game: GameConfig, input_file: Path, output_file: Path) -> None:
    with input_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    counts = Counter()
    for line in lines:
        parts = line.strip().split(",")
        numbers = parts[: game.numbers_per_draw]
        specials = parts[game.numbers_per_draw :]

        counts.update([f"{game.numbers_label},{n}" for n in numbers])
        for label, value in zip(game.special_labels, specials):
            counts.update([f"{label},{value}"])

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        for num, count in counts.items():
            f.write(f"{num},{count}\n")


def generate_suggestions(
    game: GameConfig,
    counts_file: Path,
    total_draws: int,
    output_file: Path,
    threshold_divisor: float = 31.0,
    suggestion_sets: int = 5,
) -> None:
    total_draws = max(1, total_draws)
    min_count = max(1, int(total_draws / threshold_divisor))

    winning_numbers = []
    specials = [[] for _ in game.special_labels]

    with counts_file.open("r", encoding="utf-8") as f:
        for line in f:
            category, num, count = line.strip().split(",")
            if int(count) < min_count:
                continue
            if category == game.numbers_label:
                winning_numbers.append(num)
            elif category in game.special_labels:
                idx = game.special_labels.index(category)
                specials[idx].append(num)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as out:
        for _ in range(suggestion_sets):
            if len(winning_numbers) < game.numbers_per_draw:
                break
            if any(len(s) == 0 for s in specials):
                break
            random_win_nums = random.sample(winning_numbers, game.numbers_per_draw)
            random_specials = [random.choice(s) for s in specials]
            out.write(f"{', '.join(random_win_nums + random_specials)}\n")


def run_game_flow(
    game_key: str,
    output_dir: Path,
    threshold_divisor: float = 31.0,
    suggestion_sets: int = 5,
) -> None:
    game = get_game_config(game_key)

    raw_file = output_dir / f"{game.key}_raw.csv"
    counts_file = output_dir / f"{game.key}_counts.csv"
    final_file = output_dir / f"{game.key}_suggestions.txt"

    scrape_data(game, raw_file)
    count_occurrences(game, raw_file, counts_file)

    total_draws = sum(1 for _ in raw_file.open("r", encoding="utf-8"))
    generate_suggestions(
        game,
        counts_file,
        total_draws,
        final_file,
        threshold_divisor,
        suggestion_sets,
    )
