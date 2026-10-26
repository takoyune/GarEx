"""Comprehensive Real Visual Novel Archive Test Suite using Unicode Path Discovery."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

import garex
from garex.errors import EncryptedArchiveError

VN_ROOT = Path(r"D:\Visual Novel")


def find_samples() -> dict[str, list[Path]]:
    """Discover real samples across D:/Visual Novel using Unicode filesystem APIs."""
    print(f"[*] Scanning {VN_ROOT} for real game archive samples...")
    discovered: dict[str, list[Path]] = {
        "RPA": [],
        "XP3": [],
        "INT": [],
        "NSA": [],
        "SAR": [],
    }

    try:
        for p in VN_ROOT.rglob("*"):
            ext = p.suffix.lower()
            if ext == ".rpa" and len(discovered["RPA"]) < 3:
                discovered["RPA"].append(p)
            elif ext == ".xp3" and len(discovered["XP3"]) < 3:
                discovered["XP3"].append(p)
            elif ext == ".int" and len(discovered["INT"]) < 3:
                discovered["INT"].append(p)
            elif ext == ".nsa" and len(discovered["NSA"]) < 3:
                discovered["NSA"].append(p)
            elif ext == ".sar" and len(discovered["SAR"]) < 3:
                discovered["SAR"].append(p)
    except Exception as e:
        print(f"[-] Error scanning: {e}")

    return discovered


def test_archive(path: Path) -> None:
    print("\n" + "=" * 70)
    print(f"Testing Real Archive: {path.name} (Format ext: {path.suffix})")
    print(f"Full Path: {path}")

    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"File Size: {size_mb:.2f} MB ({path.stat().st_size:,} bytes)")

    t0 = time.perf_counter()
    try:
        # 1. Open with GarEx
        with garex.open_archive(path, backend="auto") as arc:
            t_open = time.perf_counter() - t0
            print(f"[+] SUCCESS! Opened with backend: {arc.info.backend} in {t_open:.3f}s")
            print(f"[+] Format Tag: {arc.info.format} | Description: {arc.info.description}")
            entries = arc.entries()
            print(f"[+] Entry Count: {len(entries):,} files inside")

            # Show first 3 entries
            for i, e in enumerate(entries[:3]):
                name_disp = e.name[:60] + "..." if len(e.name) > 60 else e.name
                print(f"    [{i}] {name_disp} (size: {e.size:,} bytes, offset: {e.offset:,})")
            if len(entries) > 3:
                print(f"    ... and {len(entries) - 3:,} more entries.")

            # Test extracting up to 2 entries to verify decompression & disk write
            if entries:
                dest_dir = Path("dist/test_extract") / path.stem
                dest_dir.mkdir(parents=True, exist_ok=True)

                test_candidates = [entries[0]]
                if len(entries) > 1:
                    # Pick a second entry from the middle
                    test_candidates.append(entries[len(entries) // 2])

                for cand in test_candidates:
                    t_ext = time.perf_counter()
                    extracted_file = arc.extract(cand, dest_dir)
                    dt = time.perf_counter() - t_ext
                    if extracted_file.is_file():
                        print(
                            f"[+] Extraction verified in {dt:.3f}s! "
                            f"File: {extracted_file.name} ({extracted_file.stat().st_size:,} bytes)"
                        )
                    else:
                        print(f"[-] Extracted file not found at {extracted_file}")

    except EncryptedArchiveError as enc_err:
        print(f"[!] ENCRYPTED ARCHIVE: Properly identified encryption scheme: {enc_err}")
    except Exception as exc:
        print(f"[-] FAILED with {type(exc).__name__}: {exc}")
        import traceback
        traceback.print_exc()


def main() -> None:
    samples = find_samples()
    for fmt, paths in samples.items():
        print(f"\n{'#' * 70}")
        print(f">>> Category: {fmt} ({len(paths)} found)")
        print(f"{'#' * 70}")
        for path in paths:
            test_archive(path)


if __name__ == "__main__":
    main()
