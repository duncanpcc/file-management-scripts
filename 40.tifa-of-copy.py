#!/usr/bin/env python3

"""Copy tifatuesdays_ files into the Tifa Onlyfans folder."""

from pathlib import Path
import shutil


SOURCE_DIR = Path("/mnt/idata/of")
DEST_DIR = Path("/mnt/idata/files/Tifa/Onlyfans")
PREFIX = "tifatuesdays_"


def copy_files(source_root: Path, destination_root: Path, prefix: str) -> tuple[int, int, int]:
	"""Copy matching files and return (matched, copy_count, skip_count)."""
	matched_count = 0
	copy_count = 0
	skip_count = 0
	destination_root.mkdir(parents=True, exist_ok=True)

	for path in source_root.iterdir():
		if not path.is_file() or not path.name.startswith(prefix):
			continue

		matched_count += 1
		target_path = destination_root / path.name

		if target_path.exists():
			print(f"SKIP: {path} -> {target_path} (destination exists)")
			skip_count += 1
		else:
			shutil.copy2(path, target_path)
			print(f"COPIED: {path} -> {target_path}")
			copy_count += 1

	return matched_count, copy_count, skip_count


def main() -> None:
	if not SOURCE_DIR.exists():
		raise FileNotFoundError(f"Directory not found: {SOURCE_DIR}")

	if not SOURCE_DIR.is_dir():
		raise NotADirectoryError(f"Not a directory: {SOURCE_DIR}")

	matched_count, copy_count, skip_count = copy_files(SOURCE_DIR, DEST_DIR, PREFIX)
	print(
		f"Done. Matched files: {matched_count}, copied: {copy_count}, skipped: {skip_count}"
	)


if __name__ == "__main__":
	try:
		main()
	except BrokenPipeError:
		pass
