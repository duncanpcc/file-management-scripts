#!/usr/bin/env python3
"""Delete files in /mnt/truenas that match deletion criteria: older than 30 days, contain 'public', and meet other filters."""

from datetime import datetime, timedelta
import os
from pathlib import Path
import re
import sys

ROOT = Path("/mnt/truenas")
AGE_DAYS = 14
REQUIRED_TERM = "public"
EXCLUDED_TERMS = ("private", "club", "group")
EXCLUDED_FOLDERS = [
    "lea_amano-42661270",
    "StellarLoving-18285697",
    "Vivixxeve-46600786",
    "Miss_emiko-38039457",
    "AnaMei-12724963",
    "daisii-41430045",
    "eggytiff-27142268",
    "BadGalAri-22991483",
    "SendTacoMoney-16331881",
    "KateNova-30649472",
    "AlexaBlancOh-22431493",
    "SandraGPopa-33690890",
    "AmeliaRussso-46468377",
    "SykoSadBby-46783507",
    "LunaHayes-34510886",
    "Stephanie-21723980",
    "noPumpkinface-10938464",
    "Lemontea-10938464",
    "SweetSamxo-46439888"
]
FOLDER_NAME_PATTERN = re.compile(r"^[^-]+-\d+$")


def main() -> int:
    if not ROOT.exists():
        print(f"Error: {ROOT} does not exist.", file=sys.stderr)
        return 1

    if not ROOT.is_dir():
        print(f"Error: {ROOT} is not a directory.", file=sys.stderr)
        return 1

    cutoff = datetime.now() - timedelta(days=AGE_DAYS)
    deleted_count = 0
    failed_count = 0
    excluded_folder_names = {name.lower() for name in EXCLUDED_FOLDERS}

    for current_root, dir_names, file_names in os.walk(ROOT):
        current_path = Path(current_root)

        if current_path == ROOT:
            invalid_dirs = sorted(
                dir_name
                for dir_name in dir_names
                if not FOLDER_NAME_PATTERN.fullmatch(dir_name)
            )
            for dir_name in invalid_dirs:
                print(f"[ignored folder] {current_path / dir_name}: does not match Text-number")

            dir_names[:] = [
                dir_name
                for dir_name in dir_names
                if FOLDER_NAME_PATTERN.fullmatch(dir_name)
            ]

        ignored_dirs = sorted(
            dir_name
            for dir_name in dir_names
            if dir_name.lower() in excluded_folder_names
        )
        for dir_name in ignored_dirs:
            print(f"[ignored folder] {current_path / dir_name}")

        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if dir_name.lower() not in excluded_folder_names
        ]

        for file_name in sorted(file_names):
            path = current_path / file_name

            try:
                modified_at = datetime.fromtimestamp(path.stat().st_mtime)
            except OSError as exc:
                print(f"[skipped] {path}: could not read file metadata: {exc}", file=sys.stderr)
                continue

            if modified_at >= cutoff:
                continue

            normalized_name = path.name.lower()
            if REQUIRED_TERM not in normalized_name:
                continue

            if any(term in normalized_name for term in EXCLUDED_TERMS):
                continue

            try:
                path.unlink()
                deleted_count += 1
                print(f"[deleted] {path}")
            except OSError as exc:
                failed_count += 1
                print(f"[failed to delete] {path}: {exc}", file=sys.stderr)

    print(f"\nDeleted {deleted_count} file(s)", end="")
    if failed_count > 0:
        print(f" ({failed_count} failed)", end="")
    print(".")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())