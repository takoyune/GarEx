"""Integration and differential tests for pure-Python KiriKiri XP3 port.

Verifies:
1. Native XP3 creation and extraction roundtrip.
2. Cross-backend compatibility: Native creates XP3 -> Bridge reads and extracts with 100% byte parity.
3. Cross-backend compatibility: Bridge creates XP3 -> Native reads and extracts with 100% byte parity.
4. Metadata parity (entry names, sizes).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import garex
from tools.difftest import difftest_archive


@pytest.fixture
def xp3_test_src(tmp_path: Path) -> Path:
    """Synthetic directory structure for XP3 tests."""
    src_dir = tmp_path / "xp3_src"
    src_dir.mkdir()

    (src_dir / "scenario").mkdir()
    (src_dir / "scenario" / "first.tjs").write_bytes(b"function test() { return 42; }\r\n" * 20)

    (src_dir / "bg").mkdir()
    (src_dir / "bg" / "title.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200 + b"IEND\xaeB`\x82")

    (src_dir / "audio").mkdir()
    (src_dir / "audio" / "se01.wav").write_bytes(b"RIFF" + b"\x00" * 150 + b"WAVEfmt ")

    (src_dir / "readme.txt").write_text("KiriKiri XP3 native port test with Unicode: 桜, 日本語", encoding="utf-8")
    return src_dir


def test_native_xp3_roundtrip(tmp_path: Path, xp3_test_src: Path) -> None:
    """Test pure native XP3 creation and native extraction."""
    arc_path = tmp_path / "test_native.xp3"

    garex.create_archive(arc_path, xp3_test_src, format="XP3", backend="native").close()
    assert arc_path.is_file()

    with garex.open_archive(arc_path, backend="native") as arc:
        assert arc.format == "XP3"
        entries = arc.entries()
        assert len(entries) == 4

        extract_dir = tmp_path / "native_extracted"
        arc.extract_all(extract_dir)

        assert (extract_dir / "scenario" / "first.tjs").read_bytes() == (xp3_test_src / "scenario" / "first.tjs").read_bytes()
        assert (extract_dir / "bg" / "title.png").read_bytes() == (xp3_test_src / "bg" / "title.png").read_bytes()
        assert (extract_dir / "audio" / "se01.wav").read_bytes() == (xp3_test_src / "audio" / "se01.wav").read_bytes()
        assert (extract_dir / "readme.txt").read_text(encoding="utf-8") == (xp3_test_src / "readme.txt").read_text(encoding="utf-8")


@pytest.mark.bridge
def test_native_xp3_bridge_verification(tmp_path: Path, xp3_test_src: Path) -> None:
    """Test that GARbro Bridge opens and extracts native-created XP3 with 100% parity."""
    arc_path = tmp_path / "test_for_bridge.xp3"

    garex.create_archive(arc_path, xp3_test_src, format="XP3", backend="native").close()

    # Differential test suite verification (GARbro Bridge vs Native)
    assert difftest_archive(arc_path, format_tag="XP3") is True

    # Open directly via bridge
    with garex.open_archive(arc_path, backend="bridge") as arc:
        assert arc.format == "XP3"
        ext_dir = tmp_path / "bridge_extracted"
        arc.extract_all(ext_dir)

        assert (ext_dir / "scenario" / "first.tjs").read_bytes() == (xp3_test_src / "scenario" / "first.tjs").read_bytes()
        assert (ext_dir / "readme.txt").read_text(encoding="utf-8") == (xp3_test_src / "readme.txt").read_text(encoding="utf-8")


@pytest.mark.bridge
def test_bridge_created_xp3_native_verification(tmp_path: Path, xp3_test_src: Path) -> None:
    """Test that Native opens and extracts bridge-created XP3 with 100% parity."""
    arc_path = tmp_path / "test_from_bridge.xp3"

    garex.create_archive(arc_path, xp3_test_src, format="XP3", backend="bridge").close()

    # Differential test suite
    assert difftest_archive(arc_path, format_tag="XP3") is True

    # Open directly via native
    with garex.open_archive(arc_path, backend="native") as arc:
        assert arc.format == "XP3"
        ext_dir = tmp_path / "native_from_bridge"
        arc.extract_all(ext_dir)

        assert (ext_dir / "scenario" / "first.tjs").read_bytes() == (xp3_test_src / "scenario" / "first.tjs").read_bytes()
        assert (ext_dir / "readme.txt").read_text(encoding="utf-8") == (xp3_test_src / "readme.txt").read_text(encoding="utf-8")
