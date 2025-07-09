#!/usr/bin/env python3
import hashlib
import os
import subprocess
import sys
import time


def get_file_hash(filename):
    """Get a hash of the file contents to check for actual differences."""
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    return None


def get_modified_files() -> set[str]:
    result = subprocess.run(["git", "ls-files", "--modified"], stdout=subprocess.PIPE, text=True)
    return set(result.stdout.split())


def main(files: list[str]) -> None:
    print(f"DEBUG: Script invoked with files: {files}", file=sys.stderr)

    processed = set()
    for file in files:
        if file.endswith(".ipynb"):
            nb_file = file
            py_file = file[:-6] + ".py"
            print(f"DEBUG: Processing notebook file: {nb_file}, paired with: {py_file}", file=sys.stderr)
        elif file.endswith(".py"):
            py_file = file
            nb_file = file[:-3] + ".ipynb"
            print(f"DEBUG: Processing Python file: {py_file}, paired with: {nb_file}", file=sys.stderr)
        else:
            print(f"DEBUG: Skipping unsupported file: {file}", file=sys.stderr)
            continue

        pair_key = f"{nb_file}:{py_file}"
        if pair_key in processed:
            print(f"DEBUG: Skipping already processed pair: {pair_key}", file=sys.stderr)
            continue

        processed.add(pair_key)

        if os.path.isfile(nb_file) and os.path.isfile(py_file):
            nb_hash_before = get_file_hash(nb_file)
            py_hash_before = get_file_hash(py_file)

            print(f"DEBUG: Both files exist. Running jupytext sync on {py_file}", file=sys.stderr)

            # Run jupytext and capture its output
            result = subprocess.run(
                ["jupytext", "--sync", py_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
            )

            print(f"DEBUG: jupytext exit code: {result.returncode}", file=sys.stderr)
            print(f"DEBUG: jupytext stdout: {result.stdout}", file=sys.stderr)
            print(f"DEBUG: jupytext stderr: {result.stderr}", file=sys.stderr)

            nb_hash_after = get_file_hash(nb_file)
            py_hash_after = get_file_hash(py_file)

            if nb_hash_before != nb_hash_after or py_hash_before != py_hash_after:
                print("❌ Files were out of sync, syncing via jupytext...", file=sys.stderr)
                print("✅ Files synced", file=sys.stderr)

                # Give the file system a moment to register changes
                time.sleep(0.5)

                modified = get_modified_files()
                print(f"DEBUG: Modified files according to git: {modified}", file=sys.stderr)

                if py_file in modified:
                    print(f'💡 Untracked modification from sync, run: git add "{py_file}"', file=sys.stderr)
                elif nb_file in modified:
                    print(f'💡 Untracked modification from sync, run: git add "{nb_file}"', file=sys.stderr)
            else:
                print("DEBUG: No changes detected in files after sync", file=sys.stderr)
        else:
            missing = []
            if not os.path.isfile(nb_file):
                missing.append(nb_file)
            if not os.path.isfile(py_file):
                missing.append(py_file)
            print(f"DEBUG: Missing files: {missing}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
