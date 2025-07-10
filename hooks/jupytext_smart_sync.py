import hashlib
import os
import subprocess
import sys


def get_file_hash(filename):
    """Get a hash of the file contents to check for actual differences."""
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    return None


def get_modified_files() -> set[str]:
    result = subprocess.run(["git", "ls-files", "--modified"], stdout=subprocess.PIPE, text=True)
    return set(result.stdout.split())


def main() -> int:
    files = sys.argv[1:]
    processed = set()
    return_code = 0

    # Store initial hashes of all files before syncing
    file_hashes_before = {}
    for file in files:
        if file.endswith(".ipynb"):
            nb_file = file
            py_file = file[:-6] + ".py"
        elif file.endswith(".py"):
            py_file = file
            nb_file = file[:-3] + ".ipynb"
        else:
            continue

        if os.path.isfile(nb_file):
            file_hashes_before[nb_file] = get_file_hash(nb_file)
        if os.path.isfile(py_file):
            file_hashes_before[py_file] = get_file_hash(py_file)

    # Get Git's modified files list before making changes
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

        # Check for changes in file content after sync
        nb_changed = False
        py_changed = False

        # Check notebook content changes
        if os.path.isfile(nb_file):
            nb_hash_after = get_file_hash(nb_file)
            if nb_file in file_hashes_before and file_hashes_before[nb_file] != nb_hash_after:
                nb_changed = True

        # Check Python file content changes
        if os.path.isfile(py_file):
            py_hash_after = get_file_hash(py_file)
            if py_file in file_hashes_before and file_hashes_before[py_file] != py_hash_after:
                py_changed = True

        # Also check Git's status for additional confirmation
        modified_after = get_modified_files()
        git_nb_changed = nb_file in modified_after and nb_file not in modified_before
        git_py_changed = py_file in modified_after and py_file not in modified_before

        # Report changes appropriately
        changes_detected = False

        if py_changed or git_py_changed:
            print(f"⚠️ Python file out of sync: {py_file}", file=sys.stderr)
            print("✅ Files synced", file=sys.stderr)
            print(f'💡 Untracked modification from sync, run: git add "{py_file}"', file=sys.stderr)
            changes_detected = True

        if nb_changed or git_nb_changed:
            print(f"⚠️ Notebook out of sync: {nb_file}", file=sys.stderr)
            print("✅ Files synced", file=sys.stderr)
            print(f'💡 Untracked modification from sync, run: git add "{nb_file}"', file=sys.stderr)
            changes_detected = True

        if changes_detected:
            return_code = 1

    return return_code


if __name__ == "__main__":
    sys.exit(main())
