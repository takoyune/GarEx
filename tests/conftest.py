"""Shared pytest configuration and fixtures for garex test suites."""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

# Ensure src/ is on sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _has_bridge() -> bool:
    try:
        from garex.backends.bridge import find_bridge_exe
        find_bridge_exe()
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if not _has_bridge():
        skip_bridge = pytest.mark.skip(reason="Bridge binaries not present in this environment")
        for item in items:
            if "bridge" in item.keywords:
                item.add_marker(skip_bridge)
