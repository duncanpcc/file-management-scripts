#!/usr/bin/env python3
"""Execute the project scripts in a fixed, explicit order."""

from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_TO_RUN = [
    "10.move-files.py",
    "20.delete-old-files.py",
    "30.of-copy.py",
    "40.tifa-of-copy.py",
    "50.tifa-backup.py",
]


def main() -> int:
    scripts = [SCRIPT_DIR / script_name for script_name in SCRIPTS_TO_RUN]

    for script in scripts:
        if not script.is_file():
            print(f"Stopped: missing script '{script.name}'")
            return 1

    for script in scripts:
        print(f"Running: {script.name}")
        result = subprocess.run([sys.executable, str(script)], cwd=SCRIPT_DIR)
        if result.returncode != 0:
            print(f"Stopped: {script.name} failed with exit code {result.returncode}")
            return result.returncode

    print("Done. All numbered scripts completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())