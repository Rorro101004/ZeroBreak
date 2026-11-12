# Contributing to ZeroBreak

**English** | [Español](CONTRIBUTING.es.md)

## The five-phase cycle

Every change to a case under `test_cases/<case>/` follows the Safe Refactor Loop:

1. **Contract analysis** — read the code and its `test_*.py`; inventory the public API (names, signatures, exceptions, returns).
2. **`pytest` baseline** — must be 100% green before touching anything.
3. **Proposal** — design the improvement (performance, PEP 484/585/604, docstrings) without applying it.
4. **Sandbox verification** — validate the change without writing to disk.
5. **Human confirmation** — then create the didactic backup and apply to disk.

Steps 1–4 never write to disk. Only step 5 persists changes.

## Adding a new case

1. Create the folder `test_cases/<case_name>/`.
2. Add the implementation module (e.g. `mycase.py`).
3. Add the suite `test_mycase.py` next to it; it imports `from mycase import ...`.
4. Run `pytest test_cases/<case_name>` until green.

## Running the tests

```bash
pytest                          # every case + the framework tests (tests/)
pytest test_cases/<case_name>   # one case
```

## Command-line interface

The `zerobreak` CLI enforces the mechanical part of the cycle:

```bash
pip install -e ".[dev]"
zerobreak baseline <case>
zerobreak apply <case> --module <module>.py --source proposed.py --yes
```

It refuses to apply without a green baseline, creates the didactic backup first, and rolls back automatically if the tests fail.

## Didactic backups

When a refactor is applied, the original code is preserved as
`<module>_legacy_anotado.py` in the same folder, annotated inline with the
exact smell, why it hurts, and the applied solution. These files are **not
tests** and are excluded from collection via `conftest.py` and `python_files`.

## Style

- Python 3.12+.
- PEP 8, type hints (PEP 484 / 585 / 604), Google-style docstrings.
- Prefer the standard library (`itertools`, `collections`, `functools`).
- Never modify public names/signatures or existing test assertions.

## License

By contributing, you agree that your contributions are licensed under the MIT License (see `LICENSE`).
