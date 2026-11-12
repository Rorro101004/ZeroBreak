# ZeroBreak

**English** | [Español](README.es.md)

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://docs.python.org/3/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-146%20passed-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](tests/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)

Spec-Driven Development (SDD) framework to **refactor Python without breaking contracts** (Zero Breakage philosophy). Canonical target: Python 3.12+, validated with `pytest`.

Every change follows a mandatory 5-phase cycle: contract analysis → `pytest` baseline → proposal → sandbox verification → human confirmation → **didactic backup** (`<module>_legacy_anotado.py`) → apply to disk. Nothing is persisted without a green test suite and explicit approval.

## Test cases (modular)

Each case lives isolated in `test_cases/<case_name>/`, with its code and its `test_*.py` suite side by side. One case is worked at a time.

## Quick start

```bash
pytest                       # run every case + the framework tests
pytest test_cases/tienda     # baseline and verification for one case
```

Full cycle from the agent:

```text
/refactor test_cases/tienda
```

## Command-line interface

The package ships a `zerobreak` CLI that enforces the **mechanical** part of the cycle (baseline, backup, guarded apply with automatic rollback). It is deterministic and does not use AI.

```bash
pip install -e ".[dev]"        # installs the CLI and the dev tools

zerobreak cases                                  # list cases under test_cases/
zerobreak new my_case                            # scaffold a new test case directory and templates

# High-level orchestrator (module + proposal auto-detected; interactive):
zerobreak run tienda                              # baseline + backup + diff + confirmation prompt
zerobreak run tienda --source propuesta.py        # use a specific proposal
zerobreak run tienda --lint                       # also lint the proposal with ruff/mypy if available
zerobreak run tienda --yes                        # skip the prompt (CI / scripts)

# Free-File Mode (any Python script outside test_cases/):
zerobreak run --target my_app/billing.py --tests tests/test_billing.py --source proposal.py

# Test Scaffolding & Differential Testing (Golden Master + Hypothesis):
zerobreak scaffold-tests legacy_module.py       # generate tests/test_autogen_legacy_module.py
zerobreak run --target legacy.py --scaffold-tests  # auto-scaffold if companion test suite is missing

# Granular control, one step at a time:
zerobreak baseline tienda                        # run pytest and record a green baseline
zerobreak snapshot tienda --module tienda.py     # create the didactic backup
zerobreak apply tienda --module tienda.py --source propuesta.py --yes    # apply
zerobreak verify tienda                          # run the tests
zerobreak bench tienda                           # compare performance: legacy vs current
zerobreak status                                 # show the recorded state
```

`run` auto-detects the module (a single implementation file, or `<case>.py` by convention) and, if `--source` is omitted, looks for a standard proposal at `propuestas/<case>_mejorado.py`. It validates the integrity guards, shows the diff and asks for confirmation interactively (Enter/y to apply, n to cancel); `--yes` skips the prompt for CI. With `--lint` it also runs `ruff`/`mypy` on the proposal if they are installed (otherwise it warns and continues). `apply` refuses to write unless there is a green baseline and the module hash matches, always creates the `<module>_legacy_anotado.py` backup first, and reverts automatically if the tests fail.

See [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) for a step-by-step tutorial and troubleshooting, [`docs/JUNIOR_ONBOARDING.md`](docs/JUNIOR_ONBOARDING.md) for developer onboarding and a hands-on lab, and [`docs/architecture.md`](docs/architecture.md) for a file-by-file technical deep dive. For a visual overview of the whole flow (conceptual + mechanical), see [`docs/flow.md`](docs/flow.md).

## Measurement

- **Coverage:** `pytest --cov=zerobreak --cov-report=term-missing` (currently 100%; enforced at ≥ 90% in CI).
- **Complexity:** `radon cc -s -a src test_cases` and `radon mi src test_cases`.
- **Lint & types:** `ruff check src tests` and `mypy src` (enforced in CI).
- **Performance:** `zerobreak bench tienda` compares the original vs the refactored code. Results in [`docs/benchmarks.md`](docs/benchmarks.md). The `buscar_productos_duplicados` refactor shows a measured O(n²) → O(n) improvement (up to ~670× at n=5000).

## Tech stack & tools

- **Core & Runtime (Zero External Dependencies):**
  - **Python 3.12+ Standard Library:**
    - `ast`: Static syntax tree parsing, public signature extraction, and docstring/typing contract inspection without running untrusted code.
    - `hashlib`: Cryptographic SHA-256 digests ensuring filesystem state integrity and detecting out-of-band modifications.
    - `difflib`: Generation of unified diffs for terminal inspection prior to confirmation.
    - `timeit`: High-precision micro-benchmarks with `autorange` and noise reduction (minimum execution time).
    - `importlib`: Dynamic, sandboxed module execution in isolated namespaces without polluting `sys.modules`.
    - `argparse`: Standard, dependency-free command-line interface.
    - `os.replace`: Atomic filesystem replacement guarantees.
- **Testing & Safety Harness:**
  - `pytest`: Modular test discovery, test isolation via root `conftest.py` (`collect_ignore_glob`), and test fixtures.
  - `pytest-cov`: Strict statement and branch coverage tracking (100% coverage, enforced ≥90% in CI).
  - `hypothesis`: Automatic differential property-based testing (`@given`) synthesized via `testgen.py`.
  - `mutmut`: Mutation testing to audit test suite robustness and eliminate false-positive "green" tests.
- **Static Analysis & Quality Assurance:**
  - `ruff`: Ultra-fast linting (PEP 8, pyflakes, pycodestyle).
  - `mypy`: Static type validation according to PEP 484, 585, and 604.
  - `radon`: Cyclomatic complexity (`radon cc`) and maintainability index (`radon mi`) quality gates.
- **Build & Packaging:**
  - `hatchling`: Modern PEP 517/621 build backend.
- **Developer Tooling & Graph-First:**
  - `codegraph-mcp`: Model Context Protocol server enabling semantic AST graph navigation for agentic pair-programming.

## Structure

| Path | Purpose |
|------|---------|
| `AGENTS.md` | Operational rules (SSOT; in Spanish) |
| `specs/constitution.md` | Mission, scope and stack |
| `specs/features/001-safe-refactor-loop.md` | Detailed per-phase process |
| `specs/features/002-differential-and-golden-testing.md` | Golden Master and Differential Testing specification |
| `src/zerobreak/` | CLI package (mechanical guard) |
| `src/zerobreak/testgen.py` | Test scaffolding and differential test generator |
| `tests/` | Tests for the framework itself |
| `docs/USER_GUIDE.md` | End-to-end user guide, `.venv` setup and troubleshooting |
| `docs/JUNIOR_ONBOARDING.md` | Junior developer onboarding, SDD philosophy and hands-on lab |
| `docs/architecture.md` | Internal architecture of the CLI package (deep dive) |
| `docs/flow.md` | Flow diagram (SVG) with the SDD cycle and the safety guards |
| `docs/benchmarks.md` | Measured results (legacy vs refactored) |
| `.opencode/` | Agent skills, commands and subagent |
| `conftest.py` | Test isolation (excludes `*_legacy_anotado.py`) |
| `test_cases/<case>/` | Isolated cases: code + `test_*.py` |
| `test_cases/<case>/<module>_legacy_anotado.py` | Didactic backup of the original code (not a test) |
| `PROGRESS.md` | Change log |

> Operational documents (`AGENTS.md`, `specs/`, `.opencode/`) are written in Spanish; the public entry points and the code are bilingual-friendly (English README, Spanish docstrings).

## Configuration

- `opencode.json`: writing under `test_cases/**` requires approval (`edit: ask`), enforcing Phase 5.
- `pyproject.toml`: packaging, the `zerobreak` entry point, dev dependencies, `testpaths` and coverage settings.

## Acknowledgements

Developed with the assistance of **Antigravity** (Google DeepMind) and **DeepSeek** as AI pair-programming companions.

## License

MIT — see [LICENSE](LICENSE).
