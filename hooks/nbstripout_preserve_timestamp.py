import datetime
import json
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
    """Check if notebook has outputs that need stripping by inspecting the JSON content."""
    try:
        with open(file, "r") as f:
            notebook = json.load(f)

        # Check each cell for outputs
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") == "code" and len(cell.get("outputs", [])) > 0:
                return True

        # Check for execution count
        for cell in notebook.get("cells", []):
            if (
                cell.get("cell_type") == "code"
                and cell.get("execution_count") is not None
                and cell.get("execution_count") != 0
            ):
                return True

        return False
    except Exception as e:
        print(f"Error checking notebook {file}: {e}", file=sys.stderr)
        # If we can't parse the notebook, better safe than sorry - strip it
        return True


def main() -> int:
    files = sys.argv[1:]
    any_changes = False

    files_to_strip = []
    result_strings = []
    files_stripped = []
    for file in files:
        if file.endswith(".ipynb") and os.path.isfile(file):
            # Only process if the notebook actually has outputs
            if notebook_has_outputs(file):
                original_timestamp = get_mtime(file)

                files_to_strip.append(file)
                subprocess.run(["nbstripout", file], check=True)

                if original_timestamp is not None:
                    set_mtime(file, original_timestamp)
                    result_strings.append(f"✅ Outputs stripped from {file}, timestamp preserved")
                    files_stripped.append(file)
                else:
                    result_strings.append(f"⚠️ Could not preserve timestamp for {file}")
                any_changes = True

    print("❌ Stripping outputs from:", file=sys.stderr)
    print("\n".join(files_to_strip), file=sys.stderr)
    print("\n".join(result_strings), file=sys.stderr)
    print(f"💡 Run: git add {' '.join(files_stripped)}", file=sys.stderr)
    return 1 if any_changes else 0


if __name__ == "__main__":
    sys.exit(main())
