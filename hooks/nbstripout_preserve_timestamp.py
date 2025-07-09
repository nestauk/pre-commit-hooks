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


def notebook_has_outputs(file: str) -> bool:
    """Check if notebook has outputs that need stripping."""
    # Based on nbstripout's test mode:
    # - Returns 0 if notebook doesn't need stripping (no outputs)
    # - Returns 1 if notebook needs stripping (has outputs)
    result = subprocess.run(["nbstripout", "--test", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.returncode != 0


def main() -> int:
    files = sys.argv[1:]
    return_code = 0

    for file in files:
        if file.endswith(".ipynb") and os.path.isfile(file):
            # Only process if the notebook actually has outputs
            if notebook_has_outputs(file):
                original_timestamp = get_mtime(file)

                print(f"❌ Stripping outputs from: {file}", file=sys.stderr)
                subprocess.run(["nbstripout", file], check=True)

                if original_timestamp is not None:
                    set_mtime(file, original_timestamp)

                print("✅ Outputs stripped, timestamp preserved", file=sys.stderr)
                return_code = 1
            else:
                print(f"✅ No outputs to strip in: {file}", file=sys.stderr)

    return return_code


if __name__ == "__main__":
    sys.exit(main())
