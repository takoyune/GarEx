"""Integration tests for garex bridge open, list, and format discovery."""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

import garex
from garex.errors import UnsupportedFormatError


def test_bridge_supported_formats() -> None:
    formats = garex.supported_formats(backend="bridge")
    assert len(formats) >= 800

    tags = {f.tag for f in formats}
    # Check well-known engine archive formats
    assert "XP3" in tags  # KiriKiri
    assert "INT" in tags  # CatSystem2
    assert "ARC" in tags or "BURIKO ARC" in tags  # BGI / Ethornell

    # Check that kinds are correctly populated
    kinds = {f.kind for f in formats}
    assert "archive" in kinds
    assert "image" in kinds
    assert "audio" in kinds


def test_open_archive_nonexistent_file() -> None:
    with pytest.raises(FileNotFoundError):
        garex.open_archive(Path("non_existent_archive_12345.xp3"))


def test_open_archive_unsupported_file(tmp_path: Path) -> None:
    fake_file = tmp_path / "dummy.xyz"
    fake_file.write_text("This is not a visual novel archive.", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError):
        garex.open_archive(fake_file)
