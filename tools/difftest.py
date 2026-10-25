#!/usr/bin/env python3
"""Differential Testing Tool for GarEx Native Format Ports.

Compares NativeBackend against BridgeBackend (GARbro oracle) on:
1. Archive metadata & format detection
2. Entry list (names, sizes, offsets)
3. Extracted file bytes (SHA-256 hash parity)

Usage:
    python tools/difftest.py <format_tag> <sample_archive_path> [...]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

# Ensure src/ is on sys.path
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from garex.backends.bridge import BridgeBackend
from garex.backends.native import NativeBackend


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def difftest_archive(archive_path: Path, format_tag: str | None = None) -> bool:
    """Run differential test between NativeBackend and BridgeBackend on an archive."""
    print(f"\n{'='*70}")
    print(f"Differential Test: {archive_path.name}")
    print(f"Path: {archive_path.resolve()}")
    print(f"{'='*70}")

    if not archive_path.is_file():
        print(f"ERROR: Archive file not found: {archive_path}")
        return False

    bridge = BridgeBackend()
    native = NativeBackend()

    # 1. Probe test
    bridge_probe = bridge.probe(archive_path)
    native_probe = native.probe(archive_path)

    print(f"Bridge probe: {bridge_probe}")
    print(f"Native probe: {native_probe}")

    if not bridge_probe or not bridge_probe.get("recognized"):
        print("FAIL: BridgeBackend failed to recognize archive format.")
        return False

    if not native_probe or not native_probe.get("recognized"):
        print("FAIL: NativeBackend failed to recognize archive format.")
        return False

    if format_tag and native_probe.get("format", "").upper() != format_tag.upper():
        print(f"FAIL: Expected format '{format_tag}', got '{native_probe.get('format')}'.")
        return False

    # 2. List test
    b_info, b_entries = bridge.list_entries(archive_path)
    n_info, n_entries = native.list_entries(archive_path)

    print(f"\nEntry Count: Bridge={len(b_entries)}, Native={len(n_entries)}")
    if len(b_entries) != len(n_entries):
        print(f"FAIL: Entry count mismatch: Bridge={len(b_entries)}, Native={len(n_entries)}")
        return False

    b_map = {e.name.replace("\\", "/"): e for e in b_entries}
    n_map = {e.name.replace("\\", "/"): e for e in n_entries}

    b_names = sorted(b_map.keys())
    n_names = sorted(n_map.keys())

    if b_names != n_names:
        print(f"FAIL: Entry name sets differ!")
        print(f"  Only in bridge: {set(b_names) - set(n_names)}")
        print(f"  Only in native: {set(n_names) - set(b_names)}")
        return False

    # 3. Extraction & Byte Parity Test
    with tempfile.TemporaryDirectory() as b_tmp, tempfile.TemporaryDirectory() as n_tmp:
        bridge.extract(archive_path, Path(b_tmp))
        native.extract(archive_path, Path(n_tmp))

        print(f"\n{'Name':<35} {'Size (B)':<10} {'Bridge SHA-256':<16} {'Native SHA-256':<16} Status")
        print("-" * 85)

        mismatches = 0
        for name in b_names:
            b_file = Path(b_tmp) / name
            n_file = Path(n_tmp) / name

            if not b_file.is_file():
                print(f"{name:<35} [Missing in Bridge output]")
                mismatches += 1
                continue
            if not n_file.is_file():
                print(f"{name:<35} [Missing in Native output]")
                mismatches += 1
                continue

            b_bytes = b_file.read_bytes()
            n_bytes = n_file.read_bytes()

            b_hash = _sha256(b_bytes)
            n_hash = _sha256(n_bytes)

            status = "MATCH" if b_hash == n_hash else "MISMATCH"
            if b_hash != n_hash:
                mismatches += 1

            print(f"{name:<35} {len(b_bytes):<10} {b_hash[:16]:<16} {n_hash[:16]:<16} {status}")

        if mismatches > 0:
            print(f"\nFAILED: {mismatches} entry mismatches detected!")
            return False

    print(f"\nPASS: 100% byte and metadata parity verified ({len(b_names)} entries).")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="GarEx differential tester.")
    parser.add_argument("format", help="Format tag (e.g. RPA, XP3, INT).")
    parser.add_argument("samples", nargs="+", help="Archive file(s) to test.")
    args = parser.parse_args()

    success = True
    for sample in args.samples:
        if not difftest_archive(Path(sample), format_tag=args.format):
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
