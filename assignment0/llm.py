"""NaviGator AI integration for summarizing/analyzing API data."""

import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# Load .env from project root (parent of assignment0 package) or current working directory
_load_dotenv_done = False


def _load_env() -> None:
    global _load_dotenv_done
    if _load_dotenv_done:
        return
    # Try project root: .../cis6930sp26-assignment0/.env
    try:
        pkg_dir = Path(__file__).resolve().parent
        project_root = pkg_dir.parent
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        else:
            load_dotenv()  # fallback: cwd
    except Exception:
        load_dotenv()
    _load_dotenv_done = True


NAVIGATOR_BASE = "https://api.ai.it.ufl.edu/v1"
NAVIGATOR_MODEL = "llama-3.1-8b-instruct"
DEFAULT_TIMEOUT = 60


class NavigatorAIError(Exception):
    """Raised when NaviGator AI request or response fails."""

    pass


def _get_api_key() -> str:
    """Get NaviGator API key from environment or .env file. Never hardcode."""
    _load_env()
    key = os.environ.get("NAVIGATOR_TOOLKIT_API_KEY")
    if not key or not key.strip():
        raise NavigatorAIError(
            "NAVIGATOR_TOOLKIT_API_KEY is not set. "
            "Export it or add to .env (see .env.example)."
        )
    return key.strip()


def _build_prompt(pokemon_data: dict[str, Any]) -> str:
    """Build a prompt that asks for meaningful analysis, not just reformatting."""
    data_str = json.dumps(pokemon_data, indent=2)
    return (
        "Below is structured data about a Pokemon from the PokeAPI.\n\n"
        "Data:\n"
        f"{data_str}\n\n"
        "Provide a short, meaningful analysis: "
        "summarize what makes this Pokemon notable (types, stats, abilities), "
        "and give a 2–3 sentence assessment of its strengths or character. "
        "Do not simply repeat or reformat the data."
    )


def summarize_with_navigator(pokemon_data: dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Send Pokemon data to NaviGator AI and return a summary/analysis.

    Uses chat completions endpoint. Handles missing key and API errors.
    """
    api_key = _get_api_key()
    url = f"{NAVIGATOR_BASE}/chat/completions"
    payload = {
        "model": NAVIGATOR_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that analyzes Pokemon data."},
            {"role": "user", "content": _build_prompt(pokemon_data)},
        ],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.Timeout as e:
        raise NavigatorAIError(f"NaviGator request timed out after {timeout}s") from e
    except requests.exceptions.ConnectionError as e:
        raise NavigatorAIError("Connection to NaviGator AI failed.") from e
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        body = ""
        if e.response is not None:
            try:
                body = e.response.text[:500]
            except Exception:
                pass
        raise NavigatorAIError(f"NaviGator HTTP {status}: {body}") from e

    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        raise NavigatorAIError("Invalid JSON from NaviGator AI") from e

    choices = data.get("choices")
    if not choices or not isinstance(choices, list):
        raise NavigatorAIError("Unexpected NaviGator response: no choices")

    first = choices[0]
    if not isinstance(first, dict):
        raise NavigatorAIError("Unexpected NaviGator response: choice not an object")

    message = first.get("message")
    if not isinstance(message, dict):
        raise NavigatorAIError("Unexpected NaviGator response: no message")

    content = message.get("content")
    if content is None:
        raise NavigatorAIError("Unexpected NaviGator response: empty content")

    return content.strip() if isinstance(content, str) else str(content)
