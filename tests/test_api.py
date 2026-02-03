"""Tests for api module. Mock external APIs; do not call live APIs."""

import pytest
import requests
from unittest.mock import patch, MagicMock

from assignment0.api import (
    PokeAPIError,
    fetch_pokemon,
    get_pokemon_data,
    parse_pokemon_response,
)


def test_parse_pokemon_response_minimal():
    """Parse minimal valid response."""
    raw = {"name": "pikachu", "id": 25}
    out = parse_pokemon_response(raw)
    assert out["name"] == "pikachu"
    assert out["id"] == 25
    assert out["types"] == ["unknown"]
    assert out["abilities"] == ["unknown"]
    assert out["stats"] == {}


def test_parse_pokemon_response_full():
    """Parse full response with types, abilities, stats."""
    raw = {
        "name": "charizard",
        "id": 6,
        "height": 17,
        "weight": 905,
        "base_experience": 240,
        "types": [{"type": {"name": "fire"}}, {"type": {"name": "flying"}}],
        "abilities": [
            {"ability": {"name": "blaze"}},
            {"ability": {"name": "solar-power", "url": "x"}},
        ],
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 78},
            {"stat": {"name": "attack"}, "base_stat": 84},
        ],
    }
    out = parse_pokemon_response(raw)
    assert out["name"] == "charizard"
    assert out["height"] == 17
    assert out["weight"] == 905
    assert out["base_experience"] == 240
    assert out["types"] == ["fire", "flying"]
    assert out["abilities"] == ["blaze", "solar-power"]
    assert out["stats"] == {"hp": 78, "attack": 84}


def test_parse_pokemon_response_missing_name():
    """Missing name raises PokeAPIError."""
    with pytest.raises(PokeAPIError, match="name"):
        parse_pokemon_response({"id": 1})


def test_parse_pokemon_response_not_dict():
    """Non-dict raises PokeAPIError."""
    with pytest.raises(PokeAPIError, match="object"):
        parse_pokemon_response([])


def test_fetch_pokemon_success():
    """Successful fetch returns JSON. Mocks PokeAPI; no live call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "bulbasaur", "id": 1}
    mock_response.raise_for_status = MagicMock()

    with patch("assignment0.api.requests.get") as mock_get:
        mock_get.return_value = mock_response
        result = fetch_pokemon("bulbasaur")

    mock_get.assert_called_once()
    assert result["name"] == "bulbasaur"
    assert "id" in result


def test_fetch_pokemon_timeout():
    """Timeout raises PokeAPIError. Mocks network; no live call."""
    with patch("assignment0.api.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(PokeAPIError, match="timed out"):
            fetch_pokemon("pikachu", timeout=5)
    mock_get.assert_called_once()


def test_fetch_pokemon_connection_error():
    """Connection error raises PokeAPIError. Mocks network; no live call."""
    with patch("assignment0.api.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(PokeAPIError, match="Connection"):
            fetch_pokemon("pikachu")
    mock_get.assert_called_once()


def test_fetch_pokemon_http_404():
    """HTTP 404 raises PokeAPIError. Mocks PokeAPI response; no live call."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)

    with patch("assignment0.api.requests.get") as mock_get:
        mock_get.return_value = mock_response
        with pytest.raises(PokeAPIError, match="HTTP"):
            fetch_pokemon("nonexistent-pokemon-xyz")
    mock_get.assert_called_once()


def test_get_pokemon_data_calls_fetch_and_parse():
    """get_pokemon_data fetches then parses. Mocks PokeAPI; no live call."""
    mock_raw = {"name": "ditto", "id": 132, "types": [], "abilities": []}

    with patch("assignment0.api.fetch_pokemon") as mock_fetch:
        mock_fetch.return_value = mock_raw
        data = get_pokemon_data("ditto")

    mock_fetch.assert_called_once_with("ditto", timeout=15)
    assert data["name"] == "ditto"
    assert data["id"] == 132
