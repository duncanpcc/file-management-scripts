#!/usr/bin/env python3

"""Copy files from /home/duncan/git/ofdl/data into /mnt/idata/of with renamed filenames."""

from pathlib import Path
import shutil


SOURCE_DIR = Path("/home/duncan/git/ofdl/data")
DEST_DIR = Path("/mnt/idata/of")


def build_new_name(path: Path, root: Path) -> str:
	"""Build the new filename as <top_level_folder>_<original_filename>."""
	relative_path = path.relative_to(root)
	top_level_folder = relative_path.parts[0] if len(relative_path.parts) > 1 else path.parent.name
	return f"{top_level_folder}_{path.name}"


def try_copy_file(source_path: Path, target_path: Path) -> tuple[bool, str]:
	"""Copy one file to destination path, returning success and reason when skipped."""
	try:
		shutil.copy2(source_path, target_path)
		return True, ""
	except OSError as error:
		return False, f"copy failed: {error}"


def copy_files(root: Path, destination_root: Path) -> tuple[int, int, int]:
	"""Copy files and return (total, copied_count, skip_count)."""
	file_count = 0
	copy_count = 0
	skip_count = 0
	planned_targets: set[Path] = set()

	for path in root.rglob("*"):
		if not path.is_file():
			continue

		new_name = build_new_name(path, root)
		target_path = destination_root / new_name
		target_exists = target_path.exists()
		duplicate_target = target_path in planned_targets

		if target_exists or duplicate_target:
			reason = "destination exists" if target_exists else "duplicate target in preview"
			print(f"SKIP: {path} -> {target_path} ({reason})")
			skip_count += 1
		else:
			planned_targets.add(target_path)
			destination_root.mkdir(parents=True, exist_ok=True)
			copied, reason = try_copy_file(path, target_path)
			if copied:
				print(f"COPIED: {path} -> {target_path}")
				copy_count += 1
			else:
				print(f"SKIP: {path} -> {target_path} ({reason})")
				skip_count += 1

		file_count += 1

	return file_count, copy_count, skip_count


def main() -> None:
	if not SOURCE_DIR.exists():
		raise FileNotFoundError(f"Directory not found: {SOURCE_DIR}")

	if not SOURCE_DIR.is_dir():
		raise NotADirectoryError(f"Not a directory: {SOURCE_DIR}")

	total_files, copy_count, skip_count = copy_files(SOURCE_DIR, DEST_DIR)
	print(
		f"Done. Processed files: {total_files}, copied: {copy_count}, skipped: {skip_count}"
	)


if __name__ == "__main__":
	try:
		main()
	except BrokenPipeError:
		pass
