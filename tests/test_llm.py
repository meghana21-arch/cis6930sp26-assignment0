"""Tests for llm module. Mock external APIs; do not call live APIs."""

from unittest.mock import patch, MagicMock

import pytest
import requests

from assignment0.llm import (
    NavigatorAIError,
    _build_prompt,
    _get_api_key,
    summarize_with_navigator,
)


def test_build_prompt_includes_data():
    """Prompt includes Pokemon data and asks for analysis."""
    data = {"name": "pikachu", "types": ["electric"]}
    prompt = _build_prompt(data)
    assert "pikachu" in prompt
    assert "electric" in prompt
    assert "analysis" in prompt or "summarize" in prompt
    assert "reformat" in prompt or "not simply" in prompt


@patch("assignment0.llm.load_dotenv")
@patch.dict("os.environ", {"NAVIGATOR_TOOLKIT_API_KEY": "test-key-123"}, clear=False)
def test_get_api_key_from_env(_mock_load_dotenv):
    """API key is read from environment."""
    assert _get_api_key() == "test-key-123"


@patch("assignment0.llm.load_dotenv")
@patch.dict("os.environ", {}, clear=True)
def test_get_api_key_missing(_mock_load_dotenv):
    """Missing key raises NavigatorAIError."""
    with pytest.raises(NavigatorAIError, match="NAVIGATOR_TOOLKIT_API_KEY"):
        _get_api_key()


@patch("assignment0.llm.load_dotenv")
@patch.dict("os.environ", {"NAVIGATOR_TOOLKIT_API_KEY": "   "}, clear=False)
def test_get_api_key_empty(_mock_load_dotenv):
    """Empty/whitespace key raises NavigatorAIError."""
    with pytest.raises(NavigatorAIError, match="not set"):
        _get_api_key()


def test_summarize_with_navigator_success():
    """Successful LLM call returns content. Mocks NaviGator AI; no live call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "Pikachu is an iconic Electric-type Pokemon."}}
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("assignment0.llm.requests.post") as mock_post:
        with patch("assignment0.llm._get_api_key", return_value="fake-key"):
            mock_post.return_value = mock_response
            result = summarize_with_navigator({"name": "pikachu"})

    mock_post.assert_called_once()
    assert "Pikachu" in result


def test_summarize_with_navigator_http_error():
    """HTTP error from NaviGator raises NavigatorAIError. Mocks API; no live call."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)

    with patch("assignment0.llm.requests.post") as mock_post:
        with patch("assignment0.llm._get_api_key", return_value="fake-key"):
            mock_post.return_value = mock_response
            with pytest.raises(NavigatorAIError, match="NaviGator"):
                summarize_with_navigator({"name": "pikachu"})
    mock_post.assert_called_once()


def test_summarize_with_navigator_timeout():
    """Timeout raises NavigatorAIError. Mocks network; no live call."""
    with patch("assignment0.llm.requests.post") as mock_post:
        with patch("assignment0.llm._get_api_key", return_value="fake-key"):
            mock_post.side_effect = requests.exceptions.Timeout()
            with pytest.raises(NavigatorAIError, match="timed out"):
                summarize_with_navigator({"name": "pikachu"})
    mock_post.assert_called_once()


def test_summarize_with_navigator_empty_choices():
    """Response with no choices raises NavigatorAIError. Mocks API; no live call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": []}
    mock_response.raise_for_status = MagicMock()

    with patch("assignment0.llm.requests.post") as mock_post:
        with patch("assignment0.llm._get_api_key", return_value="fake-key"):
            mock_post.return_value = mock_response
            with pytest.raises(NavigatorAIError, match="no choices"):
                summarize_with_navigator({"name": "pikachu"})
    mock_post.assert_called_once()
