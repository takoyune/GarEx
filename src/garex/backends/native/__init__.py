"""Native backend package for pure-Python format decoders.

Discovers and registers all format modules under `formats/` and provides
the BaseBackend implementation for native operations.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Any

from garex.backends.base import BaseBackend
from garex.backends.native.base import (
    NativeFormat,
    get_native_format,
    list_native_formats,
    probe_native_format,
)
from garex.backends.native.binary import BinaryReader
from garex.errors import (
    CorruptArchiveError,
    GarexError,
    UnsupportedFormatError,
)
from garex.models import ArchiveInfo, Entry, FormatInfo
from garex.security import sanitize_entry_path


_FORMATS_LOADED = False


def _ensure_formats_loaded() -> None:
    """Dynamically import all modules in formats/ to trigger @register_format."""
    global _FORMATS_LOADED
    if _FORMATS_LOADED:
        return
    _FORMATS_LOADED = True

    formats_dir = Path(__file__).parent / "formats"
    if not formats_dir.is_dir():
        return

    for _, modname, ispkg in pkgutil.iter_modules([str(formats_dir)]):
        if not ispkg and not modname.startswith("_"):
            importlib.import_module(f"garex.backends.native.formats.{modname}")


class NativeBackend(BaseBackend):
    """Pure Python backend dispatching to registered NativeFormat decoders."""

    def __init__(self) -> None:
        _ensure_formats_loaded()

    def probe(self, path: Path) -> dict[str, Any] | None:
        """Probe the file with native decoders."""
        abs_path = Path(path).resolve()
        if not abs_path.is_file():
            return None

        with BinaryReader.open_file(abs_path) as reader:
            fmt = probe_native_format(reader)
            if fmt is not None:
                return {
                    "recognized": True,
                    "format": fmt.tag,
                    "kind": fmt.kind,
                    "description": fmt.description,
                    "backend": "native",
                }
        return None

    def list_entries(self, path: Path) -> tuple[ArchiveInfo, list[Entry]]:
        """List entries using the matched native format."""
        abs_path = Path(path).resolve()
        with BinaryReader.open_file(abs_path) as reader:
            fmt = probe_native_format(reader)
            if fmt is None:
                raise UnsupportedFormatError(f"No native format recognized '{abs_path.name}'")
            return fmt.list_entries(reader, abs_path)

    def supported_formats(self) -> list[FormatInfo]:
        """Return all formats implemented natively."""
        _ensure_formats_loaded()
        return [
            FormatInfo(
                tag=f.tag,
                kind=f.kind,
                description=f.description,
                extensions=f.extensions,
                can_create=f.can_write,
                status="native",
            )
            for f in list_native_formats()
        ]

    def extract(
        self,
        path: Path,
        destination: Path,
        entry: str | None = None,
        scheme: str | None = None,
        convert: bool = False,
        image_format: str = "PNG",
        audio_format: str = "WAV",
    ) -> dict[str, Any]:
        """Extract one or all entries using native format decoder."""
        abs_path = Path(path).resolve()
        dest_dir = Path(destination).resolve()
        dest_dir.mkdir(parents=True, exist_ok=True)

        with BinaryReader.open_file(abs_path) as reader:
            fmt = probe_native_format(reader)
            if fmt is None:
                raise UnsupportedFormatError(f"No native format recognized '{abs_path.name}'")

            info, entries = fmt.list_entries(reader, abs_path)

            targets = entries
            if entry is not None:
                norm_entry = entry.replace("\\", "/").lower()
                targets = [e for e in entries if e.name.replace("\\", "/").lower() == norm_entry]
                if not targets:
                    raise KeyError(f"Entry '{entry}' not found in archive '{abs_path.name}'")

            extracted_count = 0
            total_bytes = 0

            for e in targets:
                target_path = sanitize_entry_path(dest_dir, e.name)
                target_path.parent.mkdir(parents=True, exist_ok=True)

                data = fmt.read_entry(reader, e)
                target_path.write_bytes(data)

                extracted_count += 1
                total_bytes += len(data)

            return {
                "extracted_count": extracted_count,
                "total_bytes": total_bytes,
                "destination": str(dest_dir),
            }

    def convert_image(
        self,
        path: Path,
        destination: Path,
        format: str = "PNG",
    ) -> dict[str, Any]:
        raise NotImplementedError("Native standalone image conversion not yet ported")

    def convert_audio(
        self,
        path: Path,
        destination: Path,
        format: str = "WAV",
    ) -> dict[str, Any]:
        raise NotImplementedError("Native standalone audio conversion not yet ported")

    def create_archive(
        self,
        path: Path,
        files: list[str],
        base_dir: Path | None = None,
        format: str | None = None,
    ) -> dict[str, Any]:
        if format is None:
            raise UnsupportedFormatError("Format tag must be specified for native creation")
        fmt = get_native_format(format)
        if fmt is None or not fmt.can_write:
            raise UnsupportedFormatError(f"Native creation not supported for format: {format}")

        dest_path = Path(path).resolve()
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dest_path, "wb") as out_f:
            fmt.create(out_f, files, base_dir=base_dir)

        return {
            "format": fmt.tag,
            "path": str(dest_path),
            "entries_count": len(files),
        }
