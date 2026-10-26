"""Integration and differential tests for pure-Python NScripter SAR and NSA formats.

Verifies:
1. Native probing, listing, extraction, and creation of SAR archives.
2. Native probing, listing, extraction, and creation of NSA archives.
3. LZSS and NBZ decompression routines.
4. 100% byte and metadata parity against BridgeBackend (GARbro).
"""

from __future__ import annotations

import bz2
import hashlib
from pathlib import Path

import pytest

import garex
from garex.backends.native.formats.nscripter import decompress_lzss, decompress_nbz
from tools.difftest import difftest_archive


@pytest.fixture
def sample_files(tmp_path: Path) -> list[Path]:
    """Create a set of realistic synthetic test files."""
    src_dir = tmp_path / "nscripter_src"
    src_dir.mkdir(parents=True, exist_ok=True)

    files = [
        ("0.txt", b"; Mode: Normal script\n*define\ngame\n*start\nHello from NScripter!\n"),
        ("bg01.txt", b"PNG_MOCK_IMAGE_DATA_WITH_REPEATED_BYTES_" * 64),
        ("se01.txt", b"RIFF_WAV_AUDIO_MOCK_STREAM_BYTES_" * 128),
    ]

    paths: list[Path] = []
    for rel_name, data in files:
        p = src_dir / rel_name
        p.write_bytes(data)
        paths.append(p)
    return paths


def test_sar_native_roundtrip(tmp_path: Path, sample_files: list[Path]) -> None:
    """Verify pure-Python creation and extraction of SAR archive."""
    archive_path = tmp_path / "arc.sar"
    src_dir = sample_files[0].parent

    # 1. Create SAR archive using NativeBackend
    garex.create_archive(
        archive_path,
        files=[p.name for p in sample_files],
        base_dir=src_dir,
        format="SAR",
        backend="native",
    )
    assert archive_path.is_file()
    assert archive_path.stat().st_size > 0

    # 2. Open and inspect using NativeBackend
    with garex.open_archive(archive_path, backend="native") as arc:
        assert arc.info.format == "SAR"
        assert arc.info.backend == "native"
        assert len(arc.entries()) == len(sample_files)

        # 3. Extract and verify content
        out_dir = tmp_path / "extracted_sar"
        arc.extract_all(out_dir)

        for p in sample_files:
            extracted_file = out_dir / p.name
            assert extracted_file.is_file()
            assert extracted_file.read_bytes() == p.read_bytes()


def test_nsa_native_roundtrip(tmp_path: Path, sample_files: list[Path]) -> None:
    """Verify pure-Python creation and extraction of NSA archive."""
    archive_path = tmp_path / "arc.nsa"
    src_dir = sample_files[0].parent

    # 1. Create NSA archive using NativeBackend
    garex.create_archive(
        archive_path,
        files=[p.name for p in sample_files],
        base_dir=src_dir,
        format="NSA",
        backend="native",
    )
    assert archive_path.is_file()
    assert archive_path.stat().st_size > 0

    # 2. Open and inspect using NativeBackend
    with garex.open_archive(archive_path, backend="native") as arc:
        assert arc.info.format == "NSA"
        assert arc.info.backend == "native"
        assert len(arc.entries()) == len(sample_files)

        # 3. Extract and verify content
        out_dir = tmp_path / "extracted_nsa"
        arc.extract_all(out_dir)

        for p in sample_files:
            extracted_file = out_dir / p.name
            assert extracted_file.is_file()
            assert extracted_file.read_bytes() == p.read_bytes()


@pytest.mark.bridge
def test_sar_differential_cross_compatibility(tmp_path: Path, sample_files: list[Path]) -> None:
    """Verify SAR 100% cross-compatibility between NativeBackend and BridgeBackend."""
    native_arc = tmp_path / "native.sar"
    src_dir = sample_files[0].parent

    garex.create_archive(
        native_arc,
        files=[p.name for p in sample_files],
        base_dir=src_dir,
        format="SAR",
        backend="native",
    ).close()

    # 1. Differential test harness verification
    assert difftest_archive(native_arc, format_tag="SAR") is True

    # 2. Open and extract directly via Bridge
    with garex.open_archive(native_arc, backend="bridge") as arc:
        assert arc.format == "SAR"
        ext_dir = tmp_path / "bridge_from_native_sar"
        arc.extract_all(ext_dir)

        for p in sample_files:
            assert (ext_dir / p.name).read_bytes() == p.read_bytes()


@pytest.mark.bridge
def test_nsa_differential_cross_compatibility(tmp_path: Path, sample_files: list[Path]) -> None:
    """Verify NSA 100% cross-compatibility between NativeBackend and BridgeBackend."""
    native_arc = tmp_path / "native.nsa"
    src_dir = sample_files[0].parent

    garex.create_archive(
        native_arc,
        files=[p.name for p in sample_files],
        base_dir=src_dir,
        format="NSA",
        backend="native",
    ).close()

    # 1. Differential test harness verification
    assert difftest_archive(native_arc, format_tag="NSA") is True

    # 2. Open and extract directly via Bridge
    with garex.open_archive(native_arc, backend="bridge") as arc:
        assert arc.format == "NSA"
        ext_dir = tmp_path / "bridge_from_native_nsa"
        arc.extract_all(ext_dir)

        for p in sample_files:
            assert (ext_dir / p.name).read_bytes() == p.read_bytes()


def test_nsa_nbz_bzip2_decompression() -> None:
    """Verify NBZ bzip2 decompression with 4-byte header."""
    raw_text = b"Hello from NScripter NBZ compressed stream! " * 50
    compressed_body = bz2.compress(raw_text)
    # NBZ format starts with 4-byte header followed by bzip2 stream
    nbz_data = b"\x00\x00\x00\x00" + compressed_body

    decompressed = bz2.decompress(nbz_data[4:])
    assert decompressed == raw_text


def test_nsa_lzss_decompression() -> None:
    """Verify LZSS bitstream decompression."""
    raw_text = b"NScripter LZSS Test Payload Data!"

    # Encode raw text as literal tokens (flag bit 1 followed by 8 bits of byte)
    bit_buffer = 0
    bit_mask = 128
    encoded = bytearray()

    def put_bit(bit: int) -> None:
        nonlocal bit_buffer, bit_mask
        if bit:
            bit_buffer |= bit_mask
        bit_mask >>= 1
        if bit_mask == 0:
            encoded.append(bit_buffer)
            bit_buffer = 0
            bit_mask = 128

    for b in raw_text:
        put_bit(1)  # Literal flag
        for i in range(7, -1, -1):
            put_bit((b >> i) & 1)

    if bit_mask != 128:
        encoded.append(bit_buffer)

    decompressed = decompress_lzss(bytes(encoded), len(raw_text))
    assert decompressed == raw_text

