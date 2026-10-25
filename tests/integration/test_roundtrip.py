"""Integration tests for archive creation and round-trip repacking (Phase 4).

Tests:
1. create_archive with ZIP format (synthetic files)
2. create_archive from directory tree
3. replace_entries (copy-modify-write workflow)
4. create_archive with Ren'Py RPA format
5. Error handling for non-creatable / invalid formats
6. Safe rejection of in-place archive replacement (same path)
7. CLI command 'garex create'
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

import garex
from garex.errors import GarexError, UnsupportedFormatError


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


@pytest.mark.bridge
def test_create_archive_zip(tmp_path: Path) -> None:
    """Create a ZIP archive from a dict of files and verify with open_archive."""
    f1 = tmp_path / "hello.txt"
    f1.write_text("Hello, GarEx creation!", encoding="utf-8")

    f2 = tmp_path / "binary.dat"
    f2.write_bytes(bytes(range(256)))

    out_zip = tmp_path / "test_out.zip"
    files = {
        "hello.txt": f1,
        "nested/binary.dat": f2,
    }

    with garex.create_archive(out_zip, files, format="ZIP") as arc:
        assert arc.format == "ZIP"
        names = [e.name.replace("\\", "/") for e in arc.entries()]
        assert "hello.txt" in names
        assert "nested/binary.dat" in names

    # Reopen independently
    with garex.open_archive(out_zip) as arc:
        extract_dir = tmp_path / "extracted"
        arc.extract_all(extract_dir)

        ext_f1 = extract_dir / "hello.txt"
        ext_f2 = extract_dir / "nested" / "binary.dat"

        assert ext_f1.read_text(encoding="utf-8") == "Hello, GarEx creation!"
        assert ext_f2.read_bytes() == bytes(range(256))


@pytest.mark.bridge
def test_create_archive_from_directory(tmp_path: Path) -> None:
    """Create an archive pointing directly to a directory tree."""
    source_dir = tmp_path / "source_tree"
    sub_dir = source_dir / "scripts"
    sub_dir.mkdir(parents=True)

    (source_dir / "config.ini").write_text("[general]\nversion=1.0\n", encoding="utf-8")
    (sub_dir / "scene01.txt").write_text("Dialogue line 1\nDialogue line 2\n", encoding="utf-8")

    out_zip = tmp_path / "dir_archive.zip"
    with garex.create_archive(out_zip, source_dir, format="ZIP") as arc:
        entry_names = [e.name.replace("\\", "/") for e in arc.entries()]
        assert "config.ini" in entry_names
        assert "scripts/scene01.txt" in entry_names

    with garex.open_archive(out_zip) as arc:
        ext_dir = tmp_path / "ext_dir"
        arc.extract_all(ext_dir)
        assert (ext_dir / "config.ini").read_text(encoding="utf-8") == "[general]\nversion=1.0\n"
        assert (ext_dir / "scripts" / "scene01.txt").read_text(encoding="utf-8") == "Dialogue line 1\nDialogue line 2\n"


@pytest.mark.bridge
def test_replace_entries_roundtrip(tmp_path: Path) -> None:
    """Test copy-modify-write workflow with replace_entries."""
    orig_dir = tmp_path / "orig_files"
    orig_dir.mkdir()
    (orig_dir / "file1.txt").write_text("Original File 1", encoding="utf-8")
    (orig_dir / "file2.txt").write_text("Original File 2 (untouched)", encoding="utf-8")

    initial_zip = tmp_path / "initial.zip"
    garex.create_archive(initial_zip, orig_dir, format="ZIP").close()

    orig_hash = _sha256(initial_zip)

    # Prepare modification
    mod_file = tmp_path / "mod_file1.txt"
    mod_file.write_text("Updated File 1 Content - Repacked!", encoding="utf-8")

    repacked_zip = tmp_path / "repacked.zip"
    with garex.replace_entries(initial_zip, repacked_zip, {"file1.txt": mod_file}) as repacked_arc:
        assert repacked_arc.format == "ZIP"
        entry_map = {e.name.replace("\\", "/"): e for e in repacked_arc.entries()}
        assert "file1.txt" in entry_map
        assert "file2.txt" in entry_map

    # 1. Verify original archive was not modified
    assert _sha256(initial_zip) == orig_hash

    # 2. Verify repacked archive content
    ext_dir = tmp_path / "ext_repack"
    with garex.open_archive(repacked_zip) as arc:
        arc.extract_all(ext_dir)
        assert (ext_dir / "file1.txt").read_text(encoding="utf-8") == "Updated File 1 Content - Repacked!"
        assert (ext_dir / "file2.txt").read_text(encoding="utf-8") == "Original File 2 (untouched)"


@pytest.mark.bridge
def test_create_archive_rpa(tmp_path: Path) -> None:
    """Test creation and verification of Ren'Py RPA archive format."""
    rpa_dir = tmp_path / "rpa_input"
    rpa_dir.mkdir()
    (rpa_dir / "script.rpy").write_text('define s = Character("Alice")\n', encoding="utf-8")
    (rpa_dir / "data.bin").write_bytes(b"\xde\xad\xbe\xef" * 32)

    out_rpa = tmp_path / "game.rpa"
    with garex.create_archive(out_rpa, rpa_dir, format="RPA") as arc:
        assert arc.format == "RPA"
        names = [e.name.replace("\\", "/") for e in arc.entries()]
        assert "script.rpy" in names
        assert "data.bin" in names

    with garex.open_archive(out_rpa) as arc:
        ext_dir = tmp_path / "rpa_extracted"
        arc.extract_all(ext_dir)
        assert (ext_dir / "script.rpy").read_text(encoding="utf-8") == 'define s = Character("Alice")\n'
        assert (ext_dir / "data.bin").read_bytes() == b"\xde\xad\xbe\xef" * 32


def test_replace_entries_same_path_rejected(tmp_path: Path) -> None:
    """Ensure in-place mutation is rejected to prevent corrupting the original archive."""
    arc_path = tmp_path / "same.zip"
    arc_path.write_bytes(b"dummy")

    with pytest.raises(ValueError, match="must be different"):
        garex.replace_entries(arc_path, arc_path, {"x": tmp_path / "y"})


def test_create_archive_unsupported_format(tmp_path: Path) -> None:
    """Ensure invalid format tag raises UnsupportedFormatError or GarexError."""
    f = tmp_path / "sample.txt"
    f.write_text("test", encoding="utf-8")
    out = tmp_path / "out.xyz"

    with pytest.raises((UnsupportedFormatError, GarexError)):
        garex.create_archive(out, [f], format="NON_EXISTENT_FORMAT_TAG_999")


@pytest.mark.bridge
def test_cli_create(tmp_path: Path) -> None:
    """Test CLI command 'garex create'."""
    src_dir = tmp_path / "cli_src"
    src_dir.mkdir()
    (src_dir / "cli_file.txt").write_text("CLI create test content", encoding="utf-8")

    out_arc = tmp_path / "cli_out.zip"

    cmd = [
        sys.executable,
        "-m",
        "garex.cli",
        "create",
        str(out_arc),
        str(src_dir),
        "--format",
        "ZIP",
    ]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
    res = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    assert res.returncode == 0, f"CLI error: {res.stderr}"
    assert "Created ZIP archive" in res.stdout

    # Verify output archive exists and has the entry
    with garex.open_archive(out_arc) as arc:
        names = [e.name.replace("\\", "/") for e in arc.entries()]
        assert "cli_file.txt" in names
