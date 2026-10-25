"""Unit tests for path safety and traversal protection (Task 2.3)."""

from __future__ import annotations

from pathlib import Path
import pytest

from garex.errors import UnsafePathError
from garex.security import sanitize_entry_path


def test_sanitize_entry_path_normal(tmp_path: Path) -> None:
    dest = tmp_path / "output"
    dest.mkdir()

    safe_target = sanitize_entry_path(dest, "images/sprite_01.png")
    assert safe_target == (dest / "images" / "sprite_01.png").resolve()


def test_sanitize_entry_path_rejects_parent_traversal(tmp_path: Path) -> None:
    dest = tmp_path / "output"
    dest.mkdir()

    with pytest.raises(UnsafePathError, match="escape destination"):
        sanitize_entry_path(dest, "../evil.exe")

    with pytest.raises(UnsafePathError, match="escape destination"):
        sanitize_entry_path(dest, "sub/../../evil.exe")


def test_sanitize_entry_path_rejects_absolute_path(tmp_path: Path) -> None:
    dest = tmp_path / "output"
    dest.mkdir()

    with pytest.raises(UnsafePathError, match="escape destination"):
        sanitize_entry_path(dest, "C:/Windows/System32/cmd.exe")

    with pytest.raises(UnsafePathError, match="escape destination"):
        sanitize_entry_path(dest, "/etc/shadow")


def test_sanitize_entry_path_rejects_unc_and_drive_letters(tmp_path: Path) -> None:
    dest = tmp_path / "output"
    dest.mkdir()

    with pytest.raises(UnsafePathError, match="escape destination"):
        sanitize_entry_path(dest, r"\\server\share\file.txt")

    with pytest.raises(UnsafePathError, match="escape destination"):
        sanitize_entry_path(dest, r"D:\test.txt")
