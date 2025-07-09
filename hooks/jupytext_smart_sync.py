#!/usr/bin/env python3
import os
import subprocess
import sys


def get_modified_files() -> set[str]:
    result = subprocess.run(["git", "ls-files", "--modified"], stdout=subprocess.PIPE, text=True)
    return set(result.stdout.split())


def main(files: list[str]) -> None:
    processed = set()
    for file in files:
        if file.endswith(".ipynb"):
            nb_file = file
            py_file = file[:-6] + ".py"
        elif file.endswith(".py"):
            py_file = file
            nb_file = file[:-3] + ".ipynb"
        else:
            continue
        pair_key = f"{nb_file}:{py_file}"
        if pair_key in processed:
            continue
        processed.add(pair_key)
        if os.path.isfile(nb_file) and os.path.isfile(py_file):
            print("❌ Files are out of sync, syncing via jupytext...", file=sys.stderr)
            subprocess.run(["jupytext", "--sync", py_file], check=True)
            print("✅ Files synced", file=sys.stderr)
            modified = get_modified_files()
            if py_file in modified:
                print(f'💡 Untracked modification from sync, run: git add "{py_file}"', file=sys.stderr)
            elif nb_file in modified:
                print(f'💡 Untracked modification from sync, run: git add "{nb_file}"', file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
