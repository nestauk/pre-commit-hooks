# Nesta `pre-commit` hooks

To use these hooks, you need to have `pre-commit` installed. You can then edit the `.pre-commit-config.yaml` file in your project root to include the hooks defined in this directory. Currently, we have one group of hooks that are designed to run in the following sequence:

1. `nbstripout-preserve-timestamp`: Strips output from Jupyter notebooks while preserving the original file timestamp to facilitate smooth interoperation with `jupytext --sync` type functionality (which relies on the file timestamp).

2. `jupytext-enforce-pairing`: Ensures every Jupyter notebook has a corresponding Python (.py) file that is tracked by `git`. Automatically generates missing paired files.

3. `jupytext-smart-sync`: Synchronises content between Jupyter notebooks and their paired Python files when either is modified, maintaining consistency between the two formats, relies on underlying file timestamps and `jupytext --sync` to determine the correct direction of sync; identifies pairs based on the file name and extension and only runs on one of the two files (not both).

To use all three of these hooks, you can add the following to your `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/nestauk/pre-commit-hooks
    rev: v1.1.1
    hooks:
      - id: nbstripout-preserve-timestamp
      - id: jupytext-enforce-pairing
      - id: jupytext-smart-sync
```

There are two suggested ways to use these hooks:

1. All three hooks together fora full workflow, or
2. `jupytext-enforce-pairing` on its own if you only need pairing

## Development

### Setup

This project uses [`uv`](https://docs.astral.sh/uv/) for virtual environment management. If you are new to `uv`, you can find the [quickstart guide here](https://docs.astral.sh/uv/getting-started/).

We also utilise `direnv` via the `.envrc` file to automatically:

- Import your environment variables from `.env`
- Activate your virtual environment (_only if you comment out the relevant lines in `.envrc`_)

After installing `direnv` and `uv` on your system (we recommend doing this via [`brew`](https://brew.sh/) on macOS), you **must** run the following commands in your terminal to set up the project:

```bash
direnv allow
uv sync
```

## Contributor guidelines

[Technical and working style guidelines](https://github.com/nestauk/ds-cookiecutter/blob/master/GUIDELINES.md)

---

<small><p>Project based on <a target="_blank" href="https://github.com/nestauk/ds-cookiecutter">Nesta's data science project template</a>
(<a href="http://nestauk.github.io/ds-cookiecutter">Read the docs here</a>).
</small>
