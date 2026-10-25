"""Integration tests for image and audio conversion via garex bridge backend (Phase 3)."""

from __future__ import annotations

import struct
import wave
import zipfile
from pathlib import Path
import pytest

import garex
from garex.cli import main as cli_main
from garex.errors import UnsupportedFormatError


def create_sample_bmp() -> bytes:
    """Create a minimal 2x2 24bpp BMP byte array."""
    row = b"\xff\x00\x00\x00\xff\x00\x00\x00"  # 2 pixels BGR + 2 padding bytes
    pixels = row * 2
    file_size = 54 + len(pixels)
    header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54)
    dib = struct.pack("<IIIHHIIIIII", 40, 2, 2, 1, 24, 0, len(pixels), 2835, 2835, 0, 0)
    return header + dib + pixels


def create_sample_wav(path: Path) -> None:
    """Create a minimal 1-second mono PCM WAV file."""
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(b"\x00\x00" * 44100)


def test_convert_image_bmp_to_png(tmp_path: Path) -> None:
    bmp_path = tmp_path / "sample.bmp"
    png_path = tmp_path / "output.png"
    bmp_path.write_bytes(create_sample_bmp())

    result = garex.convert_image(bmp_path, png_path, format="png")
    assert result == png_path
    assert png_path.is_file()

    # Verify PNG header
    data = png_path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")


def test_convert_audio_wav(tmp_path: Path) -> None:
    in_wav = tmp_path / "input.wav"
    out_wav = tmp_path / "converted.wav"
    create_sample_wav(in_wav)

    result = garex.convert_audio(in_wav, out_wav, format="wav")
    assert result == out_wav
    assert out_wav.is_file()

    with wave.open(str(out_wav), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 44100


def test_extract_all_with_convert(tmp_path: Path) -> None:
    arc_path = tmp_path / "archive_with_media.zip"
    with zipfile.ZipFile(arc_path, "w") as zf:
        zf.writestr("notes.txt", "Plain text file content")
        zf.writestr("image.bmp", create_sample_bmp())

    out_dir = tmp_path / "extracted_converted"
    with garex.open_archive(arc_path) as arc:
        extracted = arc.extract_all(destination=out_dir, convert=True)

    assert len(extracted) == 2
    # Image was converted to PNG
    png_file = out_dir / "image.png"
    assert png_file.is_file()
    assert png_file.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    # Non-image kept original extension
    txt_file = out_dir / "notes.txt"
    assert txt_file.is_file()
    assert "Plain text file" in txt_file.read_text(encoding="utf-8")


def test_cli_convert_image(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bmp_path = tmp_path / "cli_input.bmp"
    png_path = tmp_path / "cli_output.png"
    bmp_path.write_bytes(create_sample_bmp())

    code = cli_main(["convert", str(bmp_path), "-o", str(png_path)])
    assert code == 0

    captured = capsys.readouterr()
    assert "Converted:" in captured.out
    assert png_path.is_file()
    assert png_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_cli_convert_audio(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    in_wav = tmp_path / "cli_audio_in.wav"
    out_wav = tmp_path / "cli_audio_out.wav"
    create_sample_wav(in_wav)

    code = cli_main(["convert", str(in_wav), "-o", str(out_wav)])
    assert code == 0

    captured = capsys.readouterr()
    assert "Converted:" in captured.out
    assert out_wav.is_file()


def test_convert_image_nonexistent_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        garex.convert_image(tmp_path / "missing.bmp", tmp_path / "out.png")
