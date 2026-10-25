"""Integration and differential tests for pure-Python CatSystem2 INT port.

Verifies:
1. Native INT creation and extraction roundtrip.
2. Cross-backend compatibility: Native creates INT -> Bridge reads and extracts with 100% byte parity.
3. Cross-backend compatibility: Bridge creates INT -> Native reads and extracts with 100% byte parity.
4. Metadata parity (entry names, sizes).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import garex
from tools.difftest import difftest_archive


@pytest.fixture
def int_test_src(tmp_path: Path) -> Path:
    """Synthetic directory structure for CatSystem2 INT tests."""
    src_dir = tmp_path / "int_src"
    src_dir.mkdir()

    (src_dir / "scene01.cst").write_bytes(b"CatSystem2 Script Content\r\n" * 25)
    (src_dir / "title.hg3").write_bytes(b"HG-3" + b"\x00" * 300)
    (src_dir / "bgm01.ogg").write_bytes(b"OggS" + b"\x00" * 250)
    (src_dir / "system.txt").write_text("CatSystem2 INT native test: 戯画, フロントウイング", encoding="utf-8")
    return src_dir


def test_native_int_roundtrip(tmp_path: Path, int_test_src: Path) -> None:
    """Test pure native INT creation and native extraction."""
    arc_path = tmp_path / "test_native.int"

    garex.create_archive(arc_path, int_test_src, format="INT", backend="native").close()
    assert arc_path.is_file()

    with garex.open_archive(arc_path, backend="native") as arc:
        assert arc.format == "INT"
        entries = arc.entries()
        assert len(entries) == 4

        extract_dir = tmp_path / "native_extracted"
        arc.extract_all(extract_dir)

        assert (extract_dir / "scene01.cst").read_bytes() == (int_test_src / "scene01.cst").read_bytes()
        assert (extract_dir / "title.hg3").read_bytes() == (int_test_src / "title.hg3").read_bytes()
        assert (extract_dir / "bgm01.ogg").read_bytes() == (int_test_src / "bgm01.ogg").read_bytes()
        assert (extract_dir / "system.txt").read_text(encoding="utf-8") == (int_test_src / "system.txt").read_text(encoding="utf-8")


@pytest.mark.bridge
def test_native_int_bridge_verification(tmp_path: Path, int_test_src: Path) -> None:
    """Test that GARbro Bridge opens and extracts native-created INT with 100% parity."""
    arc_path = tmp_path / "test_for_bridge.int"

    garex.create_archive(arc_path, int_test_src, format="INT", backend="native").close()

    # Differential test suite verification (GARbro Bridge vs Native)
    assert difftest_archive(arc_path, format_tag="INT") is True

    # Open directly via bridge
    with garex.open_archive(arc_path, backend="bridge") as arc:
        assert arc.format == "INT"
        ext_dir = tmp_path / "bridge_extracted"
        arc.extract_all(ext_dir)

        assert (ext_dir / "scene01.cst").read_bytes() == (int_test_src / "scene01.cst").read_bytes()
        assert (ext_dir / "system.txt").read_text(encoding="utf-8") == (int_test_src / "system.txt").read_text(encoding="utf-8")


@pytest.mark.bridge
def test_bridge_created_int_native_verification(tmp_path: Path, int_test_src: Path) -> None:
    """Test that Native opens and extracts bridge-created INT with 100% parity."""
    arc_path = tmp_path / "test_from_bridge.int"

    garex.create_archive(arc_path, int_test_src, format="INT", backend="bridge").close()

    # Differential test suite
    assert difftest_archive(arc_path, format_tag="INT") is True

    # Open directly via native
    with garex.open_archive(arc_path, backend="native") as arc:
        assert arc.format == "INT"
        ext_dir = tmp_path / "native_from_bridge"
        arc.extract_all(ext_dir)

        assert (ext_dir / "scene01.cst").read_bytes() == (int_test_src / "scene01.cst").read_bytes()
        assert (ext_dir / "system.txt").read_text(encoding="utf-8") == (int_test_src / "system.txt").read_text(encoding="utf-8")
