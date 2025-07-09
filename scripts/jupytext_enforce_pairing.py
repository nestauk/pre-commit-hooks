#!/usr/bin/env python3
import os
import subprocess
import sys


def is_tracked_by_git(file: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0


def main(files: list[str]) -> None:
    failed = 0
    for nb in files:
        py = nb[:-6] + ".py" if nb.endswith(".ipynb") else None
        if nb.endswith(".ipynb") and not os.path.isfile(py):
            print(f"⚠️  Missing paired file: {py} - generating it using jupytext...", file=sys.stderr)
            subprocess.run(["jupytext", "--set-formats", "ipynb,py:percent", nb], check=True)
            if not os.path.isfile(py):
                print(f"❌ Paired file {py} still missing after generation attempt.", file=sys.stderr)
                failed = 1
            else:
                print("✅ Paired file generated", file=sys.stderr)
        if py and not is_tracked_by_git(py):
            print(f"❌ Paired file exists but is not tracked by git: {py}", file=sys.stderr)
            print(f'💡 Run: git add "{py}" "{nb}"', file=sys.stderr)
            failed = 1
    sys.exit(failed)


if __name__ == "__main__":
    main(sys.argv[1:])
