#!/usr/bin/env python3
import os
import subprocess
import sys


def is_tracked_by_git(file: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0


def main() -> int:
    files = sys.argv[1:]
    return_code = 0

    for nb in files:
        if not nb.endswith(".ipynb"):
            continue

        py = nb[:-6] + ".py"

        # Check if paired file exists
        if not os.path.isfile(py):
            print(f"⚠️ Missing paired file: {py} - generating it using jupytext...", file=sys.stderr)
            subprocess.run(["jupytext", "--set-formats", "ipynb,py:percent", nb], check=True)

            if not os.path.isfile(py):
                print(f"❌ Paired file {py} still missing after generation attempt.", file=sys.stderr)
                return_code = 1
            else:
                print("✅ Paired file generated", file=sys.stderr)
                print(f'💡 Run: git add "{py}" "{nb}"', file=sys.stderr)
                return_code = 1

        # Check if paired file is tracked by git
        elif not is_tracked_by_git(py):
            print(f"⚠️ Paired file exists but is not tracked by git: {py}", file=sys.stderr)
            print(f'💡 Run: git add "{py}" "{nb}"', file=sys.stderr)
            return_code = 1

    return return_code


if __name__ == "__main__":
    sys.exit(main())
