"""Spike benchmark for ADR-004: Helper executable (subprocess) vs pythonnet (in-process).

Measures:
1. Initialization time (cold start)
2. Operation latency (format catalog query / archive listing)
3. Crash resilience / process safety
4. Dependency & portability implications
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


def benchmark_subprocess(console_exe: Path) -> dict:
    t0 = time.perf_counter()
    res = subprocess.run([str(console_exe), "-l"], capture_output=True, text=True, check=True)
    duration = time.perf_counter() - t0
    lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
    return {
        "mechanism": "helper executable (subprocess)",
        "duration_seconds": round(duration, 4),
        "formats_counted": len(lines) - 1,  # Header line excluded
    }


def benchmark_pythonnet(bin_dir: Path) -> dict:
    t0 = time.perf_counter()
    import clr  # type: ignore

    gameres_dll = bin_dir / "GameRes.dll"
    arcformats_dll = bin_dir / "ArcFormats.dll"

    clr.AddReference(str(gameres_dll))
    clr.AddReference(str(arcformats_dll))

    import GameRes  # type: ignore

    catalog = GameRes.FormatCatalog.Instance
    formats = list(catalog.ArcFormats)
    duration = time.perf_counter() - t0

    return {
        "mechanism": "pythonnet (in-process CLR)",
        "duration_seconds": round(duration, 4),
        "formats_counted": len(formats),
    }


def run_spike() -> None:
    root = Path(__file__).resolve().parent.parent
    bin_dir = root / "vendor" / "GARbro" / "bin" / "Release"
    console_exe = bin_dir / "GARbro.Console.exe"

    print("Running ADR-004 Bridge Spike Benchmark...")

    sub_res = benchmark_subprocess(console_exe)
    print(f"Subprocess result: {sub_res}")

    py_res = benchmark_pythonnet(bin_dir)
    print(f"Pythonnet result: {py_res}")

    # Subsequent call measurement for persistent daemon / cached in-process
    # Warm subprocess run
    t0 = time.perf_counter()
    subprocess.run([str(console_exe), "-l"], capture_output=True, text=True, check=True)
    warm_sub = time.perf_counter() - t0
    print(f"Warm subprocess run: {warm_sub:.4f}s")


if __name__ == "__main__":
    run_spike()
