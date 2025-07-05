#!/usr/bin/env python3
"""agentic_refactorer.py

Command-line utility to scan an entire repository:
  • List all non-binary files
  • Detect mock/placeholder content
  • Detect exact duplicate files by content
  • Optional automatic cleanup (with backups)

Usage:
    python scripts/agentic_refactorer.py --path /path/to/project --deep --auto-fix
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import List, Tuple

# Keywords that indicate a file is likely mock / placeholder content
MOCK_KEYWORDS: list[str] = [
    "dummy",
    "placeholder",
    "mock",
    "test",
    "lorem",
]

# File extensions that can safely be skipped for textual analysis
IGNORED_EXTENSIONS: set[str] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".mp4",
    ".mov",
    ".pdf",
    ".docx",
}


def is_mock_file(path: Path) -> bool:
    """Return True if the file appears to be a mock/placeholder."""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            content_lower = f.read().lower()
            return any(keyword in content_lower for keyword in MOCK_KEYWORDS)
    except Exception:
        return False


def list_all_files(base_path: Path) -> List[Path]:
    """Walk directory tree and return a list of files excluding ignored extensions."""
    all_files: list[Path] = []
    for root, _dirs, files in os.walk(base_path):
        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext in IGNORED_EXTENSIONS:
                continue
            all_files.append(Path(root) / filename)
    return all_files


def detect_duplicates(files: List[Path]) -> List[Tuple[Path, Path]]:
    """Detect and return list of (duplicate_path, original_path) pairs."""
    duplicates: list[Tuple[Path, Path]] = []
    seen: dict[str, Path] = {}

    for file_path in files:
        try:
            with file_path.open("rb") as f:
                content_bytes = f.read()
            content_hash = hash(content_bytes)
        except Exception:
            # Skip unreadable files
            continue

        if content_hash in seen:
            duplicates.append((file_path, seen[content_hash]))
        else:
            seen[content_hash] = file_path

    return duplicates


def analyze_structure(base_path: Path):
    print("🔍  Menganalisis struktur direktori dan file…")
    files = list_all_files(base_path)
    mocks = [f for f in files if is_mock_file(f)]
    duplicates = detect_duplicates(files)

    print(f"\n📁  Total file terdeteksi: {len(files)}")
    print(f"🧪  File mock/placeholder: {len(mocks)}")
    print(f"📂  Duplikat file: {len(duplicates)}")

    return mocks, duplicates


def auto_fix(mocks: List[Path], duplicates: List[Tuple[Path, Path]], backup: bool = True):
    print("\n🛠  Melakukan auto-fix…")
    backup_dir = Path("refactor_backup")
    if backup:
        backup_dir.mkdir(exist_ok=True)

    for path in mocks:
        try:
            print(f"🗑️  Menghapus mock: {path}")
            if backup:
                shutil.copy2(path, backup_dir / path.name)
            path.unlink(missing_ok=True)
        except Exception as exc:
            print(f"  ⚠️  Gagal menghapus {path}: {exc}")

    for duplicate_path, original_path in duplicates:
        try:
            print(f"📛  Duplikat ditemukan: {duplicate_path} == {original_path}")
            if backup and duplicate_path.exists():
                shutil.copy2(duplicate_path, backup_dir / duplicate_path.name)
            duplicate_path.unlink(missing_ok=True)
        except Exception as exc:
            print(f"  ⚠️  Gagal menghapus {duplicate_path}: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🔧 Agentic Refactorer: Auto Cleanup Tool",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Direktori project yang ingin dianalisis",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Mode deep scan (saat ini placeholder)",
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Langsung perbaiki file mock & duplikat",
    )

    args = parser.parse_args()

    base_path = Path(args.path).resolve()
    if not base_path.is_dir():
        print("❌  Path tidak valid.")
        raise SystemExit(1)

    mock_files, duplicate_files = analyze_structure(base_path)

    if args.auto_fix:
        auto_fix(mock_files, duplicate_files)

    print("\n✅  Selesai. Seluruh analisa sudah ditampilkan.")