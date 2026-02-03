"""Command-line interface for assignment0."""

import argparse
import sys

from assignment0.api import PokeAPIError, get_pokemon_data
from assignment0.llm import NavigatorAIError, summarize_with_navigator


def format_pokemon_display(data: dict) -> str:
    """Format parsed Pokemon data for terminal output."""
    lines = [
        f"Name: {data.get('name', '?')} (#{data.get('id', '?')})",
        f"Types: {', '.join(data.get('types', []))}",
        f"Height: {data.get('height', '?')} | Weight: {data.get('weight', '?')}",
        f"Base experience: {data.get('base_experience', '?')}",
        f"Abilities: {', '.join(data.get('abilities', []))}",
        "Stats: " + ", ".join(f"{k}: {v}" for k, v in (data.get("stats") or {}).items()),
    ]
    return "\n".join(lines)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="assignment0",
        description="Fetch Pokemon data from PokeAPI and get an AI summary via NaviGator.",
    )
    parser.add_argument(
        "--source",
        default="pokeapi",
        choices=["pokeapi"],
        help="Data source/API to use (default: pokeapi)",
    )
    parser.add_argument(
        "pokemon",
        nargs="?",
        default="pikachu",
        help="Pokemon name or ID (default: pikachu)",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Only fetch and print Pokemon data; do not call NaviGator AI",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        metavar="SECS",
        help="Request timeout in seconds (default: 15)",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Entry point: fetch Pokemon, optionally get LLM summary, print result."""
    parsed = parse_args(args)

    if parsed.source != "pokeapi":
        print("Only 'pokeapi' source is supported.", file=sys.stderr)
        return 1

    try:
        data = get_pokemon_data(parsed.pokemon, timeout=parsed.timeout)
    except PokeAPIError as e:
        print(f"PokeAPI error: {e}", file=sys.stderr)
        return 1

    print(format_pokemon_display(data))
    print()

    if parsed.no_llm:
        return 0

    try:
        summary = summarize_with_navigator(data, timeout=60)
        print("--- AI Summary (NaviGator) ---")
        print(summary)
    except NavigatorAIError as e:
        print(f"NaviGator AI error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
