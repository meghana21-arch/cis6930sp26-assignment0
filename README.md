# cis6930sp26-assignment0

CIS6930 Assignment 0: API data collection (PokeAPI) + NaviGator AI summary.

## Features

- **API**: Fetches Pokemon data from [PokeAPI](https://pokeapi.co/) (no API key required).
- **LLM**: Sends parsed data to [NaviGator AI](https://api.ai.it.ufl.edu) for a short analysis/summary (API key required).
- **CLI**: `--source`, `--no-llm`, `--timeout`, and positional `pokemon` (name or ID).

---

## Prerequisites

- **Python 3.10+**
- **uv** or **pip**

Install uv: https://docs.astral.sh/uv/getting-started/installation/

---

## Setup (for collaborators)

From the **project root** (`cis6930sp26-assignment0/`):

### 1. Install dependencies

**With uv (recommended):**

```bash
uv sync
```

**With pip:**

```bash
pip install -e .
```

### 2. NaviGator API key (required for LLM summary)

Get a key at https://api.ai.it.ufl.edu/ui

**Option A – Use a `.env` file (recommended)**

```bash
# Copy the example file
copy .env.example .env

# Then edit .env and set your key:
#   NAVIGATOR_TOOLKIT_API_KEY=your_actual_key_here
```

On macOS/Linux:

```bash
cp .env.example .env
# Edit .env and set NAVIGATOR_TOOLKIT_API_KEY=your_actual_key_here
```

**Option B – Set environment variable (current terminal only)**

PowerShell (Windows):

```powershell
$env:NAVIGATOR_TOOLKIT_API_KEY = "your_actual_key_here"
```

Bash (macOS/Linux):

```bash
export NAVIGATOR_TOOLKIT_API_KEY="your_actual_key_here"
```

---

## Running the application

All commands below are from the **project root**. Use `uv run` if you installed with uv, or `python -m` if you used pip.

### Default run (Pikachu + AI summary)

```bash
uv run python -m assignment0
```

With pip:

```bash
python -m assignment0
```

### Fetch a specific Pokemon (by name or ID)

```bash
uv run python -m assignment0 charizard
uv run python -m assignment0 ditto
uv run python -m assignment0 25
```

### Fetch data only (no LLM call; no API key needed)

```bash
uv run python -m assignment0 --no-llm bulbasaur
```

### Custom timeout (seconds)

```bash
uv run python -m assignment0 --timeout 30 mewtwo
```

### Show help and usage

```bash
uv run python -m assignment0 --help
```

### Summary of run options

| Command | Description |
|--------|-------------|
| `uv run python -m assignment0` | Default: Pikachu + NaviGator summary |
| `uv run python -m assignment0 <name_or_id>` | Fetch that Pokemon + summary |
| `uv run python -m assignment0 --no-llm <name_or_id>` | Fetch only; no LLM (no key needed) |
| `uv run python -m assignment0 --timeout 20 <name_or_id>` | Request timeout in seconds |
| `uv run python -m assignment0 --help` | Usage and options |

---

## Testing

From the **project root**. Tests mock external APIs (no live PokeAPI or NaviGator calls).

### Run all tests (verbose)

```bash
uv run pytest -v
```

With pip:

```bash
python -m pytest tests -v
```

### Run a specific test file

```bash
uv run pytest tests/test_api.py -v
uv run pytest tests/test_llm.py -v
uv run pytest tests/test_cli.py -v
```

### Run a specific test by name

```bash
uv run pytest tests/test_api.py::test_fetch_pokemon_success -v
uv run pytest tests/test_llm.py::test_summarize_with_navigator_success -v
```

### Run tests (short summary)

```bash
uv run pytest
```

---

## GitHub Actions (CI/CD) — mandatory for assignment

Tests run automatically on **every push** and **every pull request** via GitHub Actions.

### What runs

- Workflow file: **`.github/workflows/pytest.yml`**
- On each run: checkout repo → install uv → install Python 3.10 → `uv sync` → `uv run pytest -v`

### How to use it

1. **Trigger a run:** Push to any branch (e.g. `git push origin main`).
2. **See results:** Repo → **Actions** tab → open the latest run.
3. **Green checkmark** = all tests passed. **Red X** = fix the failing step (usually a test), then push again.

### Full guide

See **[GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)** for step-by-step setup, how to read logs, and how to fix failures.

---

## Project structure

```
cis6930sp26-assignment0/
├── .github/workflows/pytest.yml
├── assignment0/
│   ├── __init__.py
│   ├── __main__.py
│   ├── api.py      # PokeAPI fetch + parse
│   ├── llm.py      # NaviGator AI summary
│   └── cli.py      # argparse + main
├── tests/
│   ├── test_api.py
│   ├── test_llm.py
│   └── test_cli.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## License

See LICENSE.
