# algo-snippets

Personal competitive programming study and review snippets.

This repository is intentionally lightweight: each file should be easy to read,
run, and revisit without package setup. The current focus is correctness and
review value over contest-template automation.

## Structure

- `data_structures/`: reusable data structure and range-query snippets.
- `mise.toml`: Python toolchain configuration.
- `AGENTS.md`: contributor and agent guidance for future edits.

Add new algorithms under the closest topic directory. If a topic grows beyond a
couple of files, create a concise plural directory such as `graphs/`, `strings/`,
or `number_theory/`.

## Environment

This repo uses `mise` to pin Python:

```sh
mise install
mise shell
```

The configured Python version is declared in `mise.toml`.

## Running Checks

Most snippets keep lightweight assertion checks in the same file under
`if __name__ == "__main__":`.

Run one module:

```sh
python data_structures/sparse_table.py
```

Run all current snippet checks:

```sh
for f in data_structures/*.py; do python "$f"; done
```
