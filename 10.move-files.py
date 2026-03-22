#!/usr/bin/env python3
"""Move and rename files in /mnt/truenas based on dash-separated parts."""

from pathlib import Path
import sys

ROOT = Path("/mnt/truenas")


def main() -> int:
    if not ROOT.exists():
        print(f"Error: {ROOT} does not exist.", file=sys.stderr)
        return 1

    if not ROOT.is_dir():
        print(f"Error: {ROOT} is not a directory.", file=sys.stderr)
        return 1

    entries = list(ROOT.iterdir())

    folders_by_second_part = {}
    for entry in entries:
        if not entry.is_dir():
            continue

        folder_parts = [part.strip() for part in entry.name.split("-")]
        if len(folder_parts) != 2 or not folder_parts[1]:
            continue

        folders_by_second_part.setdefault(folder_parts[1], []).append(entry.name)

    for path in entries:
        if not path.is_file():
            continue

        parts = [part.strip() for part in path.stem.split("-")]
        if len(parts) < 4:
            print(f"{path.name} -> [skipped: needs at least 4 dash-separated parts]")
            continue

        original_middle = parts[3]
        current_middle = original_middle
        new_name = f"{parts[0]} - {current_middle} - {parts[2]}{path.suffix}"
        matches = sorted(folders_by_second_part.get(parts[1], []))

        if len(matches) == 1:
            target_dir = ROOT / matches[0]
        elif len(matches) > 1:
            print(
                f"{path.name} -> [skipped: multiple matching folders for second part "
                f"'{parts[1]}': {', '.join(matches)}]"
            )
            continue
        else:
            new_folder = f"{parts[0]}-{parts[1]}"
            target_dir = ROOT / new_folder
            try:
                target_dir.mkdir(exist_ok=True)
            except OSError as exc:
                print(f"{path.name} -> [failed: could not create '{new_folder}': {exc}]")
                continue

            folders_by_second_part.setdefault(parts[1], []).append(new_folder)

        destination = target_dir / new_name
        while destination.exists():
            if not current_middle.isdigit():
                print(
                    f"{path.name} -> [skipped: destination exists and middle part is not numeric: "
                    f"'{destination.name}' in '{target_dir.name}']"
                )
                destination = None
                break

            current_middle = str(int(current_middle) + 1).zfill(len(current_middle))
            new_name = f"{parts[0]} - {current_middle} - {parts[2]}{path.suffix}"
            destination = target_dir / new_name

        if destination is None:
            continue

        try:
            path.rename(destination)
        except OSError as exc:
            print(f"{path.name} -> [failed: {exc}]")
            continue

        if current_middle != original_middle:
            print(
                f"{path.name} -> moved to '{target_dir.name}' as '{new_name}' "
                f"[deduped: middle value {original_middle} -> {current_middle}]"
            )
        else:
            print(f"{path.name} -> moved to '{target_dir.name}' as '{new_name}'")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
