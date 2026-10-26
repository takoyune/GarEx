"""Pure Python implementation of Ren'Py RPA archive format.

Supports reading and creating RPA-3.0 archives with full byte parity.
Ported from upstream GARbro: https://github.com/morkt/GARbro/blob/master/ArcFormats/RenPy/ArcRPA.cs
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import Any, BinaryIO, ClassVar

from garex.backends.native.base import NativeFormat, register_format
from garex.backends.native.binary import BinaryReader
from garex.errors import CorruptArchiveError
from garex.models import ArchiveInfo, Entry


def _extract_prefix(val: Any) -> bytes:
    """Safely convert header prefix to bytes regardless of Python 2/3 pickle representation."""
    if not val:
        return b""
    if isinstance(val, (bytes, bytearray)):
        return bytes(val)
    if isinstance(val, str):
        return val.encode("latin1")
    return bytes(val)


def _serialize_rpa_index(entries: list[tuple[str, int, int, bytes]]) -> bytes:
    """Serialize RPA index into pickle opcodes compatible with GARbro's custom Pickle parser."""
    out = bytearray()
    out.extend(b"\x80\x02}")  # PROTO 2, EMPTY_DICT

    def put_int(val: int) -> None:
        if val <= 0xFF:
            out.extend(struct.pack("<BB", 0x4B, val))  # BININT1
        elif val <= 0xFFFF:
            out.extend(struct.pack("<BH", 0x4D, val))  # BININT2
        elif val <= 0xFFFFFFFF:
            out.extend(struct.pack("<BI", 0x4A, val))  # BININT
        else:
            out.extend(b"I" + str(val).encode("ascii") + b"\n")

    def put_string(s: bytes | str) -> None:
        b = s.encode("utf-8") if isinstance(s, str) else s
        if len(b) < 256:
            out.extend(struct.pack("<BB", 0x55, len(b)) + b)  # SHORT_BINSTRING
        else:
            out.extend(struct.pack("<BI", 0x54, len(b)) + b)  # BINSTRING

    for name, offset, size, header in entries:
        put_string(name)
        out.append(0x5D)  # EMPTY_LIST ']'
        put_int(offset)
        put_int(size)
        if header:
            put_string(header)
            out.append(0x87)  # TUPLE3
        else:
            out.append(0x86)  # TUPLE2
        out.append(0x61)  # APPEND 'a'
        out.append(0x73)  # SETITEM 's'

    out.append(0x2E)  # STOP '.'
    return bytes(out)


@register_format
class RpaFormat(NativeFormat):
    """Native decoder and creator for Ren'Py RPA-3.0 archives."""

    tag: ClassVar[str] = "RPA"
    description: ClassVar[str] = "Ren'Py game engine archive"
    extensions: ClassVar[tuple[str, ...]] = ("rpa",)
    kind: ClassVar[str] = "archive"
    can_write: ClassVar[bool] = True

    MAGIC: ClassVar[bytes] = b"RPA-3.0 "

    def probe(self, reader: BinaryReader) -> bool:
        if reader.length >= 0 and reader.length < 34:
            return False
        return reader.peek(8) == self.MAGIC

    def _load_index(self, reader: BinaryReader, path: Path | None = None) -> tuple[int, dict[str, Any]]:
        """Parse RPA header, decompress index, and return (key, index_dict)."""
        cached = getattr(reader, "_rpa_index_cache", None)
        if cached is not None:
            return cached

        name = path.name if path else reader.name
        pos = reader.tell()
        try:
            reader.seek(0)
            header_line = reader.read(34)
            if not header_line.startswith(self.MAGIC):
                raise CorruptArchiveError(f"Invalid RPA signature in '{name}'")

            try:
                parts = header_line.decode("ascii").strip().split()
                index_offset = int(parts[1], 16)
                key = int(parts[2], 16)
            except (ValueError, IndexError) as ex:
                raise CorruptArchiveError(f"Malformed RPA header in '{name}': {ex}") from ex

            if reader.length >= 0 and (index_offset < 0 or index_offset >= reader.length):
                raise CorruptArchiveError(
                    f"RPA index offset 0x{index_offset:X} exceeds file size {reader.length} in '{name}'"
                )

            reader.seek(index_offset)
            compressed = reader.read(reader.remaining() if reader.remaining() >= 0 else -1)

            try:
                raw_index = zlib.decompress(compressed)
            except zlib.error as ex:
                raise CorruptArchiveError(f"Failed to decompress RPA index in '{name}': {ex}") from ex

            import pickle

            try:
                index_dict = pickle.loads(raw_index, encoding="bytes")
            except Exception as ex:
                raise CorruptArchiveError(f"Failed to parse RPA pickle index in '{name}': {ex}") from ex

            if not isinstance(index_dict, dict):
                raise CorruptArchiveError(f"RPA index is not a dictionary in '{name}'")

            # Normalize keys to str
            norm_dict: dict[str, Any] = {}
            for k, val in index_dict.items():
                if isinstance(k, bytes):
                    k_str = k.decode("utf-8", errors="replace")
                else:
                    k_str = str(k)
                norm_dict[k_str.replace("\\", "/")] = val

            result = (key, norm_dict)
            setattr(reader, "_rpa_index_cache", result)
            return result
        finally:
            reader.seek(pos)

    def list_entries(self, reader: BinaryReader, path: Path) -> tuple[ArchiveInfo, list[Entry]]:
        key, index_dict = self._load_index(reader, path)
        entries: list[Entry] = []

        for name, segments in index_dict.items():
            if not segments or not isinstance(segments, (list, tuple)):
                continue

            # First segment contains (offset ^ key, size ^ key, optional_prefix)
            seg = segments[0]
            if len(seg) < 2:
                continue

            offset = int(seg[0]) ^ key
            unpacked_size = int(seg[1]) ^ key

            prefix_len = 0
            if len(seg) > 2 and seg[2]:
                prefix_len = len(_extract_prefix(seg[2]))

            stored_size = unpacked_size - prefix_len

            entries.append(
                Entry(
                    name=name,
                    size=unpacked_size,
                    packed_size=stored_size if prefix_len > 0 else None,
                    offset=offset,
                    type="unknown",
                )
            )

        info = ArchiveInfo(
            format=self.tag,
            description=self.description,
            count=len(entries),
            backend="native",
        )
        return info, entries

    def read_entry(self, reader: BinaryReader, entry: Entry) -> bytes:
        key, index_dict = self._load_index(reader)
        norm_name = entry.name.replace("\\", "/")

        seg_list = index_dict.get(norm_name)
        if not seg_list or not isinstance(seg_list, (list, tuple)):
            raise KeyError(f"Entry '{entry.name}' not found in RPA index")

        seg = seg_list[0]
        offset = int(seg[0]) ^ key
        unpacked_size = int(seg[1]) ^ key

        prefix = _extract_prefix(seg[2]) if len(seg) > 2 else b""

        body_len = unpacked_size - len(prefix)
        pos = reader.tell()
        try:
            reader.seek(offset)
            body = reader.read(body_len) if body_len > 0 else b""
            return prefix + body
        finally:
            reader.seek(pos)

    def create(
        self,
        output: BinaryIO,
        files: list[str],
        base_dir: Path | None = None,
    ) -> None:
        key = 0x42424242
        data_offset = 34  # length of header line
        output.seek(data_offset)

        entries_meta: list[tuple[str, int, int, bytes]] = []

        for rel_path in files:
            norm_name = rel_path.replace("\\", "/").lstrip("/")
            disk_path = (Path(base_dir) / rel_path) if base_dir else Path(rel_path)
            data = disk_path.read_bytes()

            size = len(data)
            header_size = min(size, 16)
            header_bytes = data[:header_size]
            body_bytes = data[header_size:]

            offset = output.tell()
            output.write(body_bytes)

            entries_meta.append(
                (norm_name, offset ^ key, size ^ key, header_bytes)
            )

        index_pos = output.tell()
        pickled = _serialize_rpa_index(entries_meta)
        compressed_index = zlib.compress(pickled, level=9)
        output.write(compressed_index)

        output.seek(0)
        header_str = f"RPA-3.0 {index_pos:016x} {key:08x}\n"
        output.write(header_str.encode("ascii"))
