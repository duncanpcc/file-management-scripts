#!/usr/bin/env python3
"""Recursively back up /mnt/idata/files/Tifa into /mnt/truenas/model-backup/tifa."""

from pathlib import Path
import os
import shutil
import sys

SOURCE_DIR = Path("/mnt/idata/files/Tifa")
DEST_DIR = Path("/mnt/truenas/model-backup/tifa")


def copy_tree(source_root: Path, destination_root: Path) -> tuple[int, int, int, int, int]:
	"""Copy tree and return counts for dirs created/skipped and files copied/skipped/failed."""
	dirs_created = 0
	dirs_skipped = 0
	files_copied = 0
	files_skipped = 0
	files_failed = 0

	destination_root.mkdir(parents=True, exist_ok=True)

	for current_root, dir_names, file_names in os.walk(source_root):
		current_path = Path(current_root)
		relative_dir = current_path.relative_to(source_root)
		target_root = destination_root / relative_dir
		target_root.mkdir(parents=True, exist_ok=True)

		for dir_name in sorted(dir_names):
			source_dir_path = current_path / dir_name
			target_dir_path = target_root / dir_name
			if target_dir_path.exists():
				print(f"SKIP_DIR: {source_dir_path} -> {target_dir_path} (destination exists)")
				dirs_skipped += 1
			else:
				try:
					target_dir_path.mkdir(parents=True, exist_ok=False)
					print(f"MKDIR: {source_dir_path} -> {target_dir_path}")
					dirs_created += 1
				except OSError as exc:
					print(f"FAILED_DIR: {source_dir_path} -> {target_dir_path} ({exc})", file=sys.stderr)

		for file_name in sorted(file_names):
			source_file_path = current_path / file_name
			target_file_path = target_root / file_name

			if target_file_path.exists():
				print(f"SKIP_FILE: {source_file_path} -> {target_file_path} (destination exists)")
				files_skipped += 1
				continue

			try:
				shutil.copy2(source_file_path, target_file_path)
				print(f"COPIED: {source_file_path} -> {target_file_path}")
				files_copied += 1
			except OSError as exc:
				print(f"FAILED_FILE: {source_file_path} -> {target_file_path} ({exc})", file=sys.stderr)
				files_failed += 1

	return dirs_created, dirs_skipped, files_copied, files_skipped, files_failed


def main() -> int:
	if not SOURCE_DIR.exists():
		print(f"Error: {SOURCE_DIR} does not exist.", file=sys.stderr)
		return 1

	if not SOURCE_DIR.is_dir():
		print(f"Error: {SOURCE_DIR} is not a directory.", file=sys.stderr)
		return 1

	dirs_created, dirs_skipped, files_copied, files_skipped, files_failed = copy_tree(
		SOURCE_DIR,
		DEST_DIR,
	)
	print(
		"Done. "
		f"Directories created: {dirs_created}, "
		f"directories skipped: {dirs_skipped}, "
		f"files copied: {files_copied}, "
		f"files skipped: {files_skipped}, "
		f"files failed: {files_failed}."
	)
	return 1 if files_failed else 0


if __name__ == "__main__":
	raise SystemExit(main())
