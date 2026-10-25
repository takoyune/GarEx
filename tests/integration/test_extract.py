"""Integration tests for archive extraction via garex bridge backend (Phase 2)."""

from __future__ import annotations

import zipfile
from pathlib import Path
import pytest

import garex
from garex.cli import main as cli_main


@pytest.fixture
def sample_archive(tmp_path: Path) -> Path:
    """Create a multi-file synthetic archive supported by GARbro."""
    arc_path = tmp_path / "sample_test.zip"
    with zipfile.ZipFile(arc_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("script.txt", "Script line 1\nScript line 2\n")
        zf.writestr("data/config.ini", "[Settings]\nResolution=1920x1080\n")
        zf.writestr("bg/scene_01.dat", b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
    return arc_path


def test_extract_all(sample_archive: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "extracted_all"
    progress_records: list[tuple[int, int, str]] = []

    with garex.open_archive(sample_archive, backend="bridge") as arc:
        assert len(arc) == 3

        def on_progress(current: int, total: int, entry: garex.models.Entry) -> None:
            progress_records.append((current, total, entry.name))

        extracted_paths = arc.extract_all(destination=output_dir, progress_callback=on_progress)

        assert len(extracted_paths) == 3
        assert len(progress_records) == 3
        assert progress_records[-1][0] == 3
        assert progress_records[-1][1] == 3

    # Verify extracted files on disk
    script_file = output_dir / "script.txt"
    assert script_file.is_file()
    assert "Script line 1" in script_file.read_text(encoding="utf-8")

    config_file = output_dir / "data" / "config.ini"
    assert config_file.is_file()
    assert "Resolution=1920x1080" in config_file.read_text(encoding="utf-8")

    bg_file = output_dir / "bg" / "scene_01.dat"
    assert bg_file.is_file()
    assert bg_file.read_bytes().startswith(b"\x89PNG")


def test_extract_single_entry(sample_archive: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "extracted_single"

    with garex.open_archive(sample_archive, backend="bridge") as arc:
        target = arc.extract("script.txt", destination=output_dir)
        assert target == (output_dir / "script.txt").resolve()
        assert target.is_file()
        assert "Script line 1" in target.read_text(encoding="utf-8")

        # Verify other files were NOT extracted
        assert not (output_dir / "data" / "config.ini").exists()


def test_extract_nonexistent_entry(sample_archive: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "out"

    with garex.open_archive(sample_archive, backend="bridge") as arc:
        with pytest.raises(KeyError, match="not found"):
            arc.extract("does_not_exist.bin", destination=output_dir)


def test_extract_closed_archive(sample_archive: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "out"
    arc = garex.open_archive(sample_archive, backend="bridge")
    arc.close()

    with pytest.raises(ValueError, match="closed Archive"):
        arc.extract("script.txt", destination=output_dir)

    with pytest.raises(ValueError, match="closed Archive"):
        arc.extract_all(destination=output_dir)


def test_cli_extract_all(sample_archive: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output_dir = tmp_path / "cli_out"
    code = cli_main(["extract", str(sample_archive), "-o", str(output_dir), "--backend", "bridge"])
    assert code == 0

    captured = capsys.readouterr()
    assert "Extraction complete" in captured.out
    assert (output_dir / "script.txt").is_file()
    assert (output_dir / "data" / "config.ini").is_file()


def test_cli_extract_single(sample_archive: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output_dir = tmp_path / "cli_single"
    code = cli_main(["extract", str(sample_archive), "-o", str(output_dir), "--entry", "script.txt"])
    assert code == 0

    captured = capsys.readouterr()
    assert "Extracted:" in captured.out
    assert (output_dir / "script.txt").is_file()
    assert not (output_dir / "data" / "config.ini").exists()
