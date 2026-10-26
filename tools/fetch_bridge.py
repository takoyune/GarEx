#!/usr/bin/env python3
"""Developer utility: Fetch or verify the pre-built GarEx C# bridge assemblies.

This script ensures `src/garex/_bridge/` contains the necessary Windows assemblies
(`garex-bridge.exe`, `GameRes.dll`, `ArcFormats.dll`, `GameData/Formats.dat`, and dependencies)
without requiring developers to compile C# code manually.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_DIR = REPO_ROOT / "src" / "garex" / "_bridge"
LOCAL_BUILD_DIR = REPO_ROOT / "bridge" / "bin" / "Release"

REQUIRED_FILES = [
    "garex-bridge.exe",
    "GameRes.dll",
    "ArcFormats.dll",
]


def check_bridge_installed() -> bool:
    """Return True if all essential bridge binaries exist."""
    if not BRIDGE_DIR.is_dir():
        return False
    return all((BRIDGE_DIR / fname).is_file() for fname in REQUIRED_FILES)


def copy_from_local_build() -> bool:
    """Attempt to copy bridge binaries from a local MSBuild output."""
    if not LOCAL_BUILD_DIR.is_dir():
        return False

    exe = LOCAL_BUILD_DIR / "garex-bridge.exe"
    if not exe.is_file():
        return False

    print(f"[*] Copying pre-built bridge from {LOCAL_BUILD_DIR} -> {BRIDGE_DIR}...")
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    for item in LOCAL_BUILD_DIR.iterdir():
        dest = BRIDGE_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
    return check_bridge_installed()


def main() -> int:
    print("=== GarEx Bridge Setup Utility ===")

    if check_bridge_installed():
        print(f"[+] GarEx bridge is already installed and ready at: {BRIDGE_DIR}")
        return 0

    print("[*] Bridge binaries not found in src/garex/_bridge/.")

    # 1. Try local build directory
    if copy_from_local_build():
        print(f"[+] Successfully copied bridge binaries to: {BRIDGE_DIR}")
        return 0

    # 2. In a release environment, offer download instructions
    print("[-] No local bridge build found.")
    print(
        "    On Windows, you can build the bridge with:\n"
        "      msbuild bridge/GarexBridge.csproj /p:Configuration=Release\n"
        "    Or download the pre-built bridge release from:\n"
        "      https://github.com/TakoYune/GarEx/releases\n"
        "    and extract into: src/garex/_bridge/"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
