# Repository Guidelines

## Project Structure & Module Organization

This repository contains standalone Python algorithm snippets. Current source files live in `data_structures/`, grouped by data structure or technique, for example `sparse_table.py`, `prefix_sum_2d.py`, and `monotonic_deque.py`. There is no separate package, application entry point, assets directory, or dedicated `tests/` directory yet.

Keep new snippets in the closest existing topic directory. If a new topic grows beyond one or two files, create a concise plural directory name such as `graphs/` or `strings/`. Prefer small, importable modules with examples or assertions under an `if __name__ == "__main__":` block.

## Build, Test, and Development Commands

- `mise install`: installs the Python version declared in `mise.toml`.
- `mise shell` or `mise activate`: uses the configured `.venv` and Python `3.14.3`.
- `python data_structures/sparse_table.py`: runs that module's built-in assertion checks.
- `for f in data_structures/*.py; do python "$f"; done`: runs all current snippet smoke tests.

There is no build step. The repository is source-only Python.

## Coding Style & Naming Conventions

Use idiomatic Python with 4-space indentation and type hints where they clarify the algorithm interface. Module and function names should be `snake_case`; classes should be `PascalCase`, as in `SparseTable` and `Rect`.

Keep implementations compact and focused on the algorithm. Avoid adding framework dependencies for snippets. Match the surrounding style in each file, including direct assertions for examples and short docstrings where behavior is not obvious.

## Testing Guidelines

Current tests are assertion-based checks embedded in modules. When adding or changing an algorithm, include representative cases in the same file: edge cases, single-element inputs, and brute-force comparisons where practical. Run the edited file directly, then run all files with:

```sh
for f in data_structures/*.py; do python "$f"; done
```

If a formal test suite is added later, place tests under `tests/` and name files `test_<module>.py`.

## Commit & Pull Request Guidelines

The Git history currently contains only `Initial commit`, so there is no established project-specific convention. Use concise imperative commit messages, for example `Add 2D prefix sum snippet` or `Fix sparse table range query`.

Pull requests should describe the algorithm or bug fix, list the commands run, and note any complexity changes such as preprocessing time, query time, or memory usage. Link related issues when available.

## Agent-Specific Instructions

Make surgical changes. Read nearby modules before editing, avoid unrelated refactors, and verify behavior with runnable assertions before reporting completion.
