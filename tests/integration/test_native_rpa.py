"""Differential tests and verification for Native RPA format decoder and creator.

Verifies 100% byte and metadata parity between NativeBackend and BridgeBackend.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import garex
from garex.backends.bridge import BridgeBackend
from garex.backends.native import NativeBackend
from garex.errors import CorruptArchiveError
from tools.difftest import difftest_archive


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.mark.bridge
def test_native_rpa_read_parity(tmp_path: Path) -> None:
    """Verify NativeBackend parses and extracts Bridge-generated RPA archive with 100% byte parity."""
    src_dir = tmp_path / "rpa_src"
    src_dir.mkdir()

    # Create various sample files: text, binary, short, long
    (src_dir / "script.rpy").write_text("label start:\n    'Hello World!'\n    return\n", encoding="utf-8")
    (src_dir / "small.txt").write_text("tiny", encoding="utf-8")
    (src_dir / "nested" / "deep").mkdir(parents=True)
    (src_dir / "nested" / "deep" / "data.bin").write_bytes(bytes(range(256)) * 8)

    archive_path = tmp_path / "bridge_generated.rpa"

    # 1. Create with bridge
    garex.create_archive(archive_path, src_dir, format="RPA", backend="bridge").close()

    # 2. Run differential test harness
    assert difftest_archive(archive_path, format_tag="RPA") is True

    # 3. Verify via public API with backend="native"
    with garex.open_archive(archive_path, backend="native") as arc:
        assert arc.format == "RPA"
        names = {e.name.replace("\\", "/") for e in arc.entries()}
        assert "script.rpy" in names
        assert "small.txt" in names
        assert "nested/deep/data.bin" in names

        extract_dir = tmp_path / "native_extracted"
        arc.extract_all(extract_dir)

        assert (extract_dir / "script.rpy").read_text(encoding="utf-8") == "label start:\n    'Hello World!'\n    return\n"
        assert (extract_dir / "small.txt").read_text(encoding="utf-8") == "tiny"
        assert (extract_dir / "nested" / "deep" / "data.bin").read_bytes() == bytes(range(256)) * 8


@pytest.mark.bridge
def test_native_rpa_creation_bridge_verification(tmp_path: Path) -> None:
    """Verify Native-created RPA archive can be opened and extracted by GARbro Bridge."""
    src_dir = tmp_path / "native_src"
    src_dir.mkdir()

    f1 = src_dir / "dialogue.rpy"
    f1.write_text("eileen 'Welcome to GarEx native RenPy!'\n", encoding="utf-8")
    f2 = src_dir / "random.bin"
    f2.write_bytes(b"\xca\xfe\xba\xbe" * 64)

    out_rpa = tmp_path / "native_created.rpa"

    # Create using NativeBackend
    native = NativeBackend()
    native.create_archive(out_rpa, ["dialogue.rpy", "random.bin"], base_dir=src_dir, format="RPA")

    # Verify with differential test
    assert difftest_archive(out_rpa, format_tag="RPA") is True

    # Open with BridgeBackend (GARbro oracle)
    with garex.open_archive(out_rpa, backend="bridge") as arc:
        assert arc.format == "RPA"
        ext_dir = tmp_path / "bridge_from_native"
        arc.extract_all(ext_dir)

        assert (ext_dir / "dialogue.rpy").read_text(encoding="utf-8") == "eileen 'Welcome to GarEx native RenPy!'\n"
        assert (ext_dir / "random.bin").read_bytes() == b"\xca\xfe\xba\xbe" * 64


def test_native_rpa_corrupt_signature(tmp_path: Path) -> None:
    """Ensure invalid signature raises CorruptArchiveError."""
    bad_file = tmp_path / "corrupt.rpa"
    bad_file.write_bytes(b"INVALID_HEADER_NOT_RPA_30" + b"\x00" * 30)

    native = NativeBackend()
    assert native.probe(bad_file) is None

    with pytest.raises(CorruptArchiveError):
        from garex.backends.native.binary import BinaryReader
        from garex.backends.native.formats.rpa import RpaFormat
        with BinaryReader.open_file(bad_file) as reader:
            RpaFormat().list_entries(reader, bad_file)
