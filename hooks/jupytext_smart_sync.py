import os
import subprocess
import sys


def get_modified_files() -> set[str]:
    result = subprocess.run(["git", "ls-files", "--modified"], stdout=subprocess.PIPE, text=True)
    return set(result.stdout.split())


def main() -> int:
    files = sys.argv[1:]
    processed = set()
    return_code = 0

    # Get the list of modified files before making any changes
    modified_before = get_modified_files()

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

        # Only proceed if both files exist
        if not (os.path.isfile(nb_file) and os.path.isfile(py_file)):
            continue

        # Run jupytext sync
        subprocess.run(["jupytext", "--sync", py_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check which files were modified by comparing with initial state
        modified_after = get_modified_files()

        # If either file is now in the modified list but wasn't before, report it
        if py_file in modified_after and py_file not in modified_before:
            print(f"⚠️ Python file out of sync: {py_file}", file=sys.stderr)
            print("✅ Files synced", file=sys.stderr)
            print(f'💡 Untracked modification from sync, run: git add "{py_file}"', file=sys.stderr)
            return_code = 1

        if nb_file in modified_after and nb_file not in modified_before:
            print(f"⚠️ Notebook out of sync: {nb_file}", file=sys.stderr)
            print("✅ Files synced", file=sys.stderr)
            print(f'💡 Untracked modification from sync, run: git add "{nb_file}"', file=sys.stderr)
            return_code = 1

    return return_code


if __name__ == "__main__":
    sys.exit(main())
