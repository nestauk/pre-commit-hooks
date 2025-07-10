import hashlib
import os
import subprocess
import sys


def get_file_hash(filename: str) -> str | None:
    """Return MD5 hash of file contents, or None if not found."""
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    return None


def get_modified_files() -> set[str]:
    """Get the set of files Git considers modified."""
    result = subprocess.run(["git", "ls-files", "--modified"], stdout=subprocess.PIPE, text=True, check=True)
    return set(result.stdout.split())


def has_file_changed(file: str, original_hash: str | None, before_modified: set[str], after_modified: set[str]) -> bool:
    """Determine if file changed based on content or Git modification."""
    if not os.path.isfile(file):
        return False
    current_hash = get_file_hash(file)
    content_changed = original_hash is not None and current_hash != original_hash
    git_modified = file in after_modified and file not in before_modified
    return content_changed or git_modified


def collect_file_pairs(files: list[str]) -> set[tuple[str, str]]:
    """Return a set of (notebook, script) pairs based on input files."""
    pairs = set()
    for file in files:
        if file.endswith(".ipynb"):
            nb_file = file
            py_file = file[:-6] + ".py"
        elif file.endswith(".py"):
            py_file = file
            nb_file = file[:-3] + ".ipynb"
        else:
            continue

        if os.path.isfile(nb_file) and os.path.isfile(py_file):
            pairs.add((nb_file, py_file))
    return pairs


def main() -> int:
    return_code = 0
    files = sys.argv[1:]
    file_pairs = collect_file_pairs(files)

    # Precompute original hashes
    all_files = {f for pair in file_pairs for f in pair}
    original_hashes = {f: get_file_hash(f) for f in all_files if os.path.isfile(f)}

    # Snapshot git modified state before sync
    before_modified = get_modified_files()

    # Perform sync
    for _, py_file in file_pairs:
        subprocess.run(["jupytext", "--sync", py_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Snapshot git modified state after sync
    after_modified = get_modified_files()

    # Check for changes
    files_out_of_sync = []
    for nb_file, py_file in file_pairs:
        for file in (nb_file, py_file):
            if has_file_changed(file, original_hashes.get(file), before_modified, after_modified):
                files_out_of_sync.append(file)
                return_code = 1

    if len(files_out_of_sync) > 1:
        print("❌ The following files are out of sync with their paired files:", file=sys.stderr)
        print("\n".join(files_out_of_sync), file=sys.stderr)
        print("🔄 Syncing files", file=sys.stderr)
    else:
        print("❌ The following file is out of sync with its paired file:", file=sys.stderr)
        print("\n".join(files_out_of_sync), file=sys.stderr)
        print("🔄 Syncing file", file=sys.stderr)
    print(f"💡 Run: git add {' '.join(files_out_of_sync)}", file=sys.stderr)

    return return_code


if __name__ == "__main__":
    sys.exit(main())
