"""PokeAPI data collection and parsing"""

import json
import os
from typing import Any

import requests

POKEAPI_BASE = "https://pokeapi.co/api/v2"
DEFAULT_TIMEOUT = 15


class PokeAPIError(Exception):
    """Raised when PokeAPI request or parsing fails"""
    pass


def fetch_pokemon(name_or_id: str | int, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """
    Fetch a single Pokemon by name or ID from PokeAPI.

    Handles timeouts, connection errors, and HTTP errors.
    """
    url = f"{POKEAPI_BASE}/pokemon/{name_or_id}"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.Timeout as e:
        raise PokeAPIError(f"Request timed out after {timeout}s") from e
    except requests.exceptions.ConnectionError as e:
        raise PokeAPIError("Connection failed. Check network.") from e
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        raise PokeAPIError(f"HTTP error {status}: {e}") from e

    try:
        return resp.json()
    except json.JSONDecodeError as e:
        raise PokeAPIError("Invalid JSON response from API") from e


def parse_pokemon_response(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Extract relevant fields from PokeAPI Pokemon response.

    Returns a simplified dict suitable for display and LLM input.
    """
    if not isinstance(raw, dict):
        raise PokeAPIError("Expected a JSON object")

    name = raw.get("name")
    if name is None:
        raise PokeAPIError("Missing 'name' in response")

    pokemon_id = raw.get("id")
    height = raw.get("height")
    weight = raw.get("weight")
    base_experience = raw.get("base_experience")

    types = []
    for t in raw.get("types", []):
        type_obj = t.get("type")
        if isinstance(type_obj, dict) and type_obj.get("name"):
            types.append(type_obj["name"])
    types = types or ["unknown"]

    abilities = []
    for a in raw.get("abilities", []):
        ability_obj = a.get("ability")
        if isinstance(ability_obj, dict) and ability_obj.get("name"):
            abilities.append(ability_obj["name"])
    abilities = abilities or ["unknown"]

    stats = {}
    for s in raw.get("stats", []):
        stat_obj = s.get("stat")
        base = s.get("base_stat")
        if isinstance(stat_obj, dict) and stat_obj.get("name") is not None and base is not None:
            stats[stat_obj["name"]] = base

    return {
        "id": pokemon_id,
        "name": name,
        "height": height,
        "weight": weight,
        "base_experience": base_experience,
        "types": types,
        "abilities": abilities,
        "stats": stats,
    }


def get_pokemon_data(name_or_id: str | int, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """
    Fetch and parse Pokemon data from PokeAPI.

    Convenience function that fetches then parses.
    """
    raw = fetch_pokemon(name_or_id, timeout=timeout)
    return parse_pokemon_response(raw)
