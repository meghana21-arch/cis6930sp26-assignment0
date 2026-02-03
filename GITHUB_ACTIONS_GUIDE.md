# GitHub Actions Guide — CIS6930 Assignment 0

This guide explains how GitHub Actions is set up for this project and how to use it for the assignment.

---

## What is GitHub Actions?

GitHub Actions runs **automated workflows** (e.g. tests) when you **push** or open a **pull request**. For this assignment, the workflow:

1. Runs on every **push** to any branch and on every **pull request**.
2. Uses **Ubuntu**.
3. Installs **uv** and **Python 3.10**.
4. Installs project dependencies with **uv sync**.
5. Runs **pytest** with `uv run pytest -v`.

If all tests pass → workflow is **green** (success).  
If any test fails → workflow is **red** (failure).

---

## Step 1: Make Sure the Workflow File Is in Your Repo

The workflow file **must** be at:

```
.github/workflows/pytest.yml
```

**Check locally:**

1. Open your project folder.
2. Go to `.github/workflows/`.
3. You should see `pytest.yml`.

**Check on GitHub after pushing:**

1. Open your repo: `https://github.com/YOUR_USERNAME/cis6930sp26-assignment0`
2. Click the **Code** tab.
3. Navigate to `.github/workflows/pytest.yml`.
4. You should see the YAML content (name, on, jobs, steps).

If the file is missing, add it and push:

```bash
git add .github/workflows/pytest.yml
git commit -m "Add GitHub Actions workflow for pytest"
git push origin main
```

---

## Step 2: Trigger the Workflow (Push Code)

The workflow runs automatically when you:

- **Push** to any branch (e.g. `main`, `master`).
- Open or update a **pull request**.

**To trigger it:**

1. Make sure you’re in the project root.
2. Commit and push:

```bash
cd "C:\Users\saime\OneDrive\Desktop\Projects\Data Engineering Help\cis6930sp26-assignment0"

git add .
git status
git commit -m "Your message"
git push origin main
```

(Use `master` instead of `main` if that’s your default branch.)

After the push, GitHub starts the workflow. No extra step needed.

---

## Step 3: View Workflow Runs and Results

1. Open your repo on GitHub.
2. Click the **Actions** tab (top menu).
3. You’ll see a list of **workflow runs** (e.g. “pytest”).
4. Click the **latest run** (top of the list).
5. You’ll see the **job** (e.g. “test”) and its **steps**:
   - Checkout
   - Install uv
   - Set up Python
   - Install dependencies
   - Run pytest

**Success:** The run and the “Run pytest” step show a **green checkmark**.  
**Failure:** The run or a step shows a **red X**. Click the failed step to see the log (e.g. which test failed).

---

## Step 4: Understand the Workflow (pytest.yml)

| Section | Purpose |
|--------|---------|
| `name: pytest` | Name shown in the Actions tab. |
| `on: push / pull_request` | When the workflow runs (every push and every PR). |
| `branches: ["*"]` | All branches (you can change to e.g. `["main"]` if you want). |
| `runs-on: ubuntu-latest` | Runner OS (Linux). |
| `actions/checkout@v4` | Clones your repo. |
| `astral-sh/setup-uv@v4` | Installs **uv**. |
| `uv python install 3.10` | Installs **Python 3.10**. |
| `uv sync` | Installs dependencies from `pyproject.toml`. |
| `uv run pytest -v` | Runs tests (same as locally). |

No secrets or API keys are needed for tests (they use mocks).

---

## Step 5: If the Workflow Fails (Red X)

1. In the **Actions** tab, open the **failed run**.
2. Click the **failed job** (e.g. “test”).
3. Click the **failed step** (often “Run pytest”).
4. Read the log at the bottom (error and traceback).

**Typical causes:**

- **Test failure:** Fix the test or the code locally, then commit and push again.
- **Missing dependency:** Add it to `pyproject.toml` under `dependencies`, then push.
- **Wrong Python version:** Workflow uses 3.10; your code must be compatible (e.g. 3.10+).
- **Path/import error:** Ensure `pyproject.toml` has `[tool.pytest.ini_options]` with `pythonpath = ["."]` so `assignment0` is importable.

**After fixing locally:**

```bash
# Run tests locally first
uv run pytest -v

# If all pass:
git add .
git commit -m "Fix failing tests"
git push origin main
```

Then check the **Actions** tab again; the new run should be green.

---

## Step 6: Assignment Requirements Checklist

For the “CI/CD Setup” part of the assignment, you need:

| Requirement | Done? |
|-------------|--------|
| Workflow file at `.github/workflows/pytest.yml` | Yes |
| Workflow runs on every push | Yes (`on: push`) |
| Workflow runs tests (e.g. pytest) | Yes (`uv run pytest -v`) |
| Workflow is triggered and visible under Actions | You verify after push |
| Latest run is successful (green) | You verify after push |

---

## Quick Reference Commands

```bash
# 1. Ensure workflow file is tracked and pushed
git add .github/workflows/pytest.yml
git status

# 2. Push to trigger the workflow
git commit -m "Add or update GitHub Actions workflow"
git push origin main

# 3. Run the same tests locally before pushing
uv run pytest -v
```

---

## Summary

- **What:** GitHub Actions runs `uv run pytest -v` on every push and pull request.
- **Where:** Workflow file is `.github/workflows/pytest.yml`.
- **How to trigger:** Push to any branch (or open a PR).
- **How to check:** Repo → **Actions** tab → open latest run → see green (pass) or red (fail) and logs.
- **If it fails:** Fix the failing step (usually tests or dependencies), push again, and re-check Actions.

Once the workflow file is in the repo and you’ve pushed at least once, you’ve satisfied the CI/CD part of the assignment. Keep the latest run **green** before you tag and submit (e.g. `v1.0`).
