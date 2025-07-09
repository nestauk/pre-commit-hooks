#!/usr/bin/env python3
import datetime
import os
import platform
import subprocess
import sys


def get_mtime(file: str) -> int | None:
    """Get the modification time of a file as a UNIX timestamp."""
    try:
        return int(os.stat(file).st_mtime)
    except Exception:
        return None


def set_mtime(file: str, timestamp: int) -> None:
    """Set the modification time of a file, cross-platform."""
    try:
        os.utime(file, (timestamp, timestamp))
    except Exception:
        # Fallback to shell command if os.utime fails (rare)
        try:
            if platform.system() == "Darwin":
                subprocess.run(
                    ["touch", "-t", datetime.datetime.fromtimestamp(timestamp).strftime("%Y%m%d%H%M.%S"), file],
                    check=True,
                )
            else:
                subprocess.run(["touch", "-d", f"@{timestamp}", file], check=True)
        except Exception:
            pass


def main() -> int:
    files = sys.argv[1:]
    return_code = 0

    for file in files:
        if file.endswith(".ipynb") and os.path.isfile(file):
            original_timestamp = get_mtime(file)

            # Check if there are outputs to strip
            result = subprocess.run(
                ["nbstripout", "--test", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
            )

            # If nbstripout detected outputs (returns non-zero), strip them
            if result.returncode != 0:
                print(f"❌ Stripping outputs from: {file}", file=sys.stderr)
                subprocess.run(["nbstripout", file], check=True)
                if original_timestamp is not None:
                    set_mtime(file, original_timestamp)
                print("✅ Outputs stripped, timestamp preserved", file=sys.stderr)
                return_code = 1

    return return_code


if __name__ == "__main__":
    sys.exit(main())
