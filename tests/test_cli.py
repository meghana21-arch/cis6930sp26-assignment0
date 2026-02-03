"""Tests for CLI. Mock external APIs; do not call live APIs."""

import sys
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest

from assignment0.cli import format_pokemon_display, main, parse_args


def test_parse_args_defaults():
    """Default source is pokeapi, default pokemon is pikachu."""
    args = parse_args([])
    assert args.source == "pokeapi"
    assert args.pokemon == "pikachu"
    assert args.no_llm is False


def test_parse_args_pokemon_positional():
    """Pokemon can be passed as positional arg."""
    args = parse_args(["charizard"])
    assert args.pokemon == "charizard"


def test_parse_args_source():
    """--source pokeapi is accepted."""
    args = parse_args(["--source", "pokeapi", "ditto"])
    assert args.source == "pokeapi"
    assert args.pokemon == "ditto"


def test_parse_args_no_llm():
    """--no-llm sets flag."""
    args = parse_args(["--no-llm", "mewtwo"])
    assert args.no_llm is True
    assert args.pokemon == "mewtwo"


def test_parse_args_timeout():
    """--timeout is parsed."""
    args = parse_args(["--timeout", "30", "snorlax"])
    assert args.timeout == 30


def test_parse_args_help():
    """--help exits without error (argparse behavior)."""
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--help"])
    assert exc_info.value.code == 0


def test_format_pokemon_display():
    """Display includes name, types, stats."""
    data = {
        "name": "squirtle",
        "id": 7,
        "types": ["water"],
        "height": 5,
        "weight": 90,
        "base_experience": 63,
        "abilities": ["torrent", "rain-dish"],
        "stats": {"hp": 44, "attack": 48},
    }
    out = format_pokemon_display(data)
    assert "squirtle" in out
    assert "7" in out
    assert "water" in out
    assert "torrent" in out
    assert "hp" in out or "44" in out


def test_main_success_with_llm():
    """Main fetches data, calls LLM, prints summary. Mocks APIs; no live calls."""
    mock_fetch_return = {
        "name": "eevee",
        "id": 133,
        "types": ["normal"],
        "height": 3,
        "weight": 65,
        "base_experience": 65,
        "abilities": ["run-away", "adaptability"],
        "stats": {},
    }
    mock_llm_return = "Eevee is a versatile Normal-type."

    with patch("assignment0.cli.get_pokemon_data") as mock_fetch:
        with patch("assignment0.cli.summarize_with_navigator") as mock_llm:
            mock_fetch.return_value = mock_fetch_return
            mock_llm.return_value = mock_llm_return
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main(["eevee"])

    assert exit_code == 0
    assert "eevee" in stdout.getvalue().lower()
    assert "Eevee is a versatile" in stdout.getvalue()
    mock_fetch.assert_called_once()
    mock_llm.assert_called_once()


def test_main_no_llm_flag():
    """With --no-llm, LLM is not called. Mocks PokeAPI only; no live calls."""
    mock_fetch_return = {
        "name": "mew",
        "id": 151,
        "types": ["psychic"],
        "height": 4,
        "weight": 40,
        "base_experience": 100,
        "abilities": ["synchronize"],
        "stats": {},
    }

    with patch("assignment0.cli.get_pokemon_data") as mock_fetch:
        with patch("assignment0.cli.summarize_with_navigator") as mock_llm:
            mock_fetch.return_value = mock_fetch_return
            with patch("sys.stdout", new_callable=StringIO):
                exit_code = main(["--no-llm", "mew"])

    assert exit_code == 0
    mock_llm.assert_not_called()


def test_main_api_error_returns_1():
    """PokeAPI error returns exit code 1. Mocks API error; no live call."""
    from assignment0.api import PokeAPIError

    with patch("assignment0.cli.get_pokemon_data") as mock_fetch:
        mock_fetch.side_effect = PokeAPIError("Not found")
        with patch("sys.stderr", new_callable=StringIO):
            exit_code = main(["invalid"])

    assert exit_code == 1
    mock_fetch.assert_called_once()
