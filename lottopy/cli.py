import argparse
from pathlib import Path

from .pipeline import run_game_flow, get_game_config


def main() -> None:
    parser = argparse.ArgumentParser(description="LottoPy - scrape and suggest lottery numbers.")
    parser.add_argument(
        "--game",
        default="mega_millions",
        help="Game key to run (available: mega_millions, texas_two_step).",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory to store outputs (raw, counts, suggestions).",
    )
    parser.add_argument(
        "--threshold-divisor",
        type=float,
        default=31.0,
        help="Divisor used to compute frequency threshold (total_draws / divisor).",
    )
    parser.add_argument(
        "--suggestion-sets",
        type=int,
        default=5,
        help="Number of suggestion sets to generate.",
    )

    args = parser.parse_args()

    game = get_game_config(args.game)
    print(f"Running {game.name} pipeline...")
    run_game_flow(
        game_key=game.key,
        output_dir=Path(args.output_dir),
        threshold_divisor=args.threshold_divisor,
        suggestion_sets=args.suggestion_sets,
    )
    print("Done.")


if __name__ == "__main__":
    main()
