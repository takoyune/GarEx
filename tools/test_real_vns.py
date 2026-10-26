"""Comprehensive Real Visual Novel Archive Test Suite using Unicode Path Discovery.

Tests both Native (Option A "Big 4": Ren'Py, KiriKiri, CatSystem2, NScripter)
and Bridge Extended Visual Novel engine archives (AliceSoft, YU-RIS, Circus, Waffle, Eushully, Marmalade).
"""

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
        # Native "Big 4" Formats
        "RPA (Ren'Py)": [],
        "XP3 (KiriKiri)": [],
        "NSA (NScripter)": [],
        "SAR (NScripter)": [],
        "INT (CatSystem2)": [],
        # Extended VN Engine Formats (via Bridge)
        "AFA (AliceSoft)": [],
        "ALD (AliceSoft)": [],
        "YPF (YU-RIS / CLOCKUP)": [],
        "PAK (Waffle / NekoSDK)": [],
        "PCK (Circus)": [],
        "ALF (Eushully)": [],
        "NOA (Marmalade / Entis)": [],
    }

    try:
        for p in VN_ROOT.rglob("*"):
            if not p.is_file():
                continue
            ext = p.suffix.lower()

            if ext == ".rpa" and len(discovered["RPA (Ren'Py)"]) < 2:
                discovered["RPA (Ren'Py)"].append(p)
            elif ext == ".xp3" and len(discovered["XP3 (KiriKiri)"]) < 2:
                discovered["XP3 (KiriKiri)"].append(p)
            elif ext == ".int" and len(discovered["INT (CatSystem2)"]) < 2:
                discovered["INT (CatSystem2)"].append(p)
            elif ext == ".nsa" and len(discovered["NSA (NScripter)"]) < 2:
                discovered["NSA (NScripter)"].append(p)
            elif ext == ".sar" and len(discovered["SAR (NScripter)"]) < 2:
                discovered["SAR (NScripter)"].append(p)
            elif ext == ".afa" and len(discovered["AFA (AliceSoft)"]) < 2:
                discovered["AFA (AliceSoft)"].append(p)
            elif ext == ".ald" and len(discovered["ALD (AliceSoft)"]) < 2:
                discovered["ALD (AliceSoft)"].append(p)
            elif ext == ".ypf" and len(discovered["YPF (YU-RIS / CLOCKUP)"]) < 2:
                discovered["YPF (YU-RIS / CLOCKUP)"].append(p)
            elif ext == ".pak" and "WAFFLE" in str(p) and len(discovered["PAK (Waffle / NekoSDK)"]) < 2:
                discovered["PAK (Waffle / NekoSDK)"].append(p)
            elif ext == ".pck" and "CIRCUS" in str(p) and len(discovered["PCK (Circus)"]) < 2:
                discovered["PCK (Circus)"].append(p)
            elif ext == ".alf" and "Eushully" in str(p) and len(discovered["ALF (Eushully)"]) < 2:
                discovered["ALF (Eushully)"].append(p)
            elif ext == ".noa" and len(discovered["NOA (Marmalade / Entis)"]) < 2:
                discovered["NOA (Marmalade / Entis)"].append(p)
    except Exception as e:
        print(f"[-] Error scanning: {e}")

    return {k: v for k, v in discovered.items() if v}


def test_archive(category: str, path: Path) -> None:
    print("\n" + "=" * 70)
    print(f"[{category}] Testing: {path.name}")
    print(f"Full Path: {path}")

    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"File Size: {size_mb:.2f} MB ({path.stat().st_size:,} bytes)")

    t0 = time.perf_counter()
    try:
        # 1. Open with GarEx (auto routing: Native-first with Bridge fallback)
        with garex.open_archive(path, backend="auto") as arc:
            t_open = time.perf_counter() - t0
            print(f"[+] SUCCESS! Opened with backend: {arc.info.backend.upper()} in {t_open:.3f}s")
            print(f"[+] Format Tag: {arc.info.format} | Description: {arc.info.description}")
            entries = arc.entries()
            print(f"[+] Entry Count: {len(entries):,} files inside")

            # Show first 3 entries
            for i, e in enumerate(entries[:3]):
                name_disp = e.name[:60] + "..." if len(e.name) > 60 else e.name
                print(f"    [{i}] {name_disp} (size: {e.size:,} bytes, offset: {e.offset:,})")
            if len(entries) > 3:
                print(f"    ... and {len(entries) - 3:,} more entries.")

            # Test extraction to dist/test_extract
            if entries:
                dest_dir = Path("dist/test_extract") / path.stem
                dest_dir.mkdir(parents=True, exist_ok=True)

                first = entries[0]
                t_ext = time.perf_counter()
                extracted_file = arc.extract(first, dest_dir)
                dt = time.perf_counter() - t_ext
                if extracted_file.is_file():
                    print(
                        f"[+] Raw extraction verified in {dt:.3f}s! "
                        f"File: {extracted_file.name} ({extracted_file.stat().st_size:,} bytes)"
                    )
                else:
                    print(f"[-] Extracted file not found at {extracted_file}")

                # Test on-the-fly image conversion if applicable (e.g. CRX)
                if first.name.lower().endswith(".crx"):
                    conv_dir = dest_dir / "converted"
                    t_c = time.perf_counter()
                    conv_file = arc.extract(first, conv_dir, convert=True)
                    dt_c = time.perf_counter() - t_c
                    if conv_file.is_file() and conv_file.suffix.lower() == ".png":
                        print(
                            f"[+] On-the-fly Image Conversion verified in {dt_c:.3f}s! "
                            f"Converted: {conv_file.name} ({conv_file.stat().st_size:,} bytes, PNG format)"
                        )

    except EncryptedArchiveError as enc_err:
        print(f"[!] ENCRYPTED ARCHIVE: Properly identified encryption scheme: {enc_err}")
    except Exception as exc:
        print(f"[-] FAILED with {type(exc).__name__}: {exc}")
        import traceback
        traceback.print_exc()


def main() -> None:
    samples = find_samples()
    print(f"\nDiscovered {sum(len(v) for v in samples.values())} archive files across {len(samples)} engine families.")
    for fmt, paths in samples.items():
        print(f"\n{'#' * 70}")
        print(f">>> Engine Category: {fmt} ({len(paths)} sampled)")
        print(f"{'#' * 70}")
        for path in paths:
            test_archive(fmt, path)


if __name__ == "__main__":
    main()
