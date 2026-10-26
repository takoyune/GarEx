"""CatSystem2 INT archive format implementation (Pure Python).

Reference:
- Upstream: https://github.com/morkt/GARbro/blob/master/ArcFormats/CatSystem/ArcINT.cs
- Specification: docs/formats/INT.md
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import BinaryIO, ClassVar

from garex.backends.native.base import NativeFormat, register_format
from garex.backends.native.binary import BinaryReader
from garex.errors import CorruptArchiveError
from garex.models import ArchiveInfo, Entry

INT_SIGNATURE = b"KIF\x00"  # 0x0046494B


def _decode_name(raw: bytes) -> str:
    """Decode null-terminated CP932 / Shift-JIS entry name."""
    null_idx = raw.find(b"\x00")
    if null_idx != -1:
        raw = raw[:null_idx]
    try:
        return raw.decode("cp932")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


@register_format
class IntFormat(NativeFormat):
    """CatSystem2 INT archive decoder and creator."""

    tag: ClassVar[str] = "INT"
    description: ClassVar[str] = "CatSystem2 engine resource archive"
    extensions: ClassVar[tuple[str, ...]] = ("int",)
    can_write: ClassVar[bool] = True

    def probe(self, reader: BinaryReader) -> bool:
        """Probe for CatSystem2 INT archive signature."""
        if reader.length < 8:
            return False
        try:
            reader.seek(0)
            sig = reader.read_bytes(4)
            if sig != INT_SIGNATURE:
                return False
            count = reader.read_i32()
            if count <= 0 or count > 500000:
                return False
            # Check whether directory table fits within the archive
            dir_size_64 = 8 + count * 0x48
            dir_size_32 = 8 + count * 0x28
            return dir_size_64 <= reader.length or dir_size_32 <= reader.length
        except Exception:
            return False

    def list_entries(self, reader: BinaryReader, path: Path | None = None) -> tuple[ArchiveInfo, list[Entry]]:
        """List all entries in the CatSystem2 INT archive."""
        reader.seek(0)
        sig = reader.read_bytes(4)
        if sig != INT_SIGNATURE:
            raise CorruptArchiveError("Invalid CatSystem2 INT signature")

        count = reader.read_i32()
        if count <= 0:
            raise CorruptArchiveError(f"Invalid entry count {count} in CatSystem2 archive")

        # CatSystem uses either 0x40 (standard v2) or 0x20 (legacy v1) name buffer length
        for name_len in (0x40, 0x20):
            record_len = name_len + 8
            if 8 + count * record_len > reader.length:
                continue

            entries: list[Entry] = []
            valid = True

            reader.seek(8)
            for _ in range(count):
                name_bytes = reader.read_bytes(name_len)
                offset = reader.read_u32()
                size = reader.read_u32()

                name = _decode_name(name_bytes)
                if not name or offset + size > reader.length:
                    valid = False
                    break

                entries.append(
                    Entry(
                        name=name,
                        size=size,
                        packed_size=None,
                        offset=offset,
                        type="unknown",
                    )
                )

            if valid and len(entries) == count:
                info = ArchiveInfo(
                    format=self.tag,
                    description=self.description,
                    count=len(entries),
                    backend="native",
                )
                return info, entries

        raise CorruptArchiveError("Failed to parse CatSystem2 directory entries")

    def read_entry(self, reader: BinaryReader, entry: Entry) -> bytes:
        """Extract and return entry bytes from CatSystem2 INT archive."""
        reader.seek(entry.offset)
        return reader.read_bytes(entry.size)

    def create(
        self,
        output: BinaryIO,
        files: list[str],
        base_dir: Path | None = None,
    ) -> None:
        """Create a new standard CatSystem2 INT archive."""
        file_count = len(files)
        output.seek(0)
        output.write(INT_SIGNATURE)
        output.write(struct.pack("<i", file_count))

        # 1. Write directory placeholder with 64-byte name buffers
        for rel_path in files:
            name = Path(rel_path).name
            try:
                name_bytes = name.encode("cp932")
            except UnicodeEncodeError:
                name_bytes = name.encode("utf-8")
            name_padded = name_bytes[:64].ljust(64, b"\x00")
            output.write(name_padded)
            output.write(b"\x00" * 8)  # Placeholder for uint32 offset and uint32 size

        # 2. Write file payloads consecutively
        entry_positions: list[tuple[int, int]] = []
        for rel_path in files:
            full_path = (base_dir / rel_path) if base_dir else Path(rel_path)
            data = full_path.read_bytes()
            offset = output.tell()
            output.write(data)
            size = len(data)
            entry_positions.append((offset, size))

        # 3. Rewind to directory table and write offsets and sizes
        for i, (offset, size) in enumerate(entry_positions):
            entry_dir_pos = 8 + i * 0x48 + 0x40
            output.seek(entry_dir_pos)
            output.write(struct.pack("<II", offset, size))
