"""KiriKiri / TVP XP3 archive format implementation (Pure Python).

Reference:
- Upstream: vendor/GARbro/ArcFormats/KiriKiri/ArcXP3.cs
- Specification: docs/formats/XP3.md
"""

from __future__ import annotations

import io
import struct
import zlib
from pathlib import Path
from typing import BinaryIO, ClassVar

from garex.backends.native.base import NativeFormat, register_format
from garex.backends.native.binary import BinaryReader
from garex.errors import CorruptArchiveError
from garex.models import ArchiveInfo, Entry

XP3_MAGIC = b"XP3\r\n \n\x1a\x8bg\x01"  # 11 bytes
SEC_FILE = 0x656C6946  # "File"
SEC_INFO = 0x6F666E69  # "info"
SEC_SEGM = 0x6D676573  # "segm"
SEC_ADLR = 0x726C6461  # "adlr"


def _read_index_buffer(reader: BinaryReader) -> bytes:
    """Read and decompress the XP3 index block."""
    reader.seek(0)
    magic = reader.read_bytes(11)
    if magic != XP3_MAGIC:
        raise CorruptArchiveError("Invalid XP3 signature")

    dir_offset = reader.read_i64()
    if dir_offset < 19 or dir_offset >= reader.length:
        raise CorruptArchiveError(f"XP3 index offset out of bounds: {dir_offset}")

    reader.seek(dir_offset)
    flag_or_magic = reader.read_u32()
    reader.seek(dir_offset)

    if flag_or_magic == 0x80:
        reader.seek(dir_offset + 9)
        dir_offset = reader.read_i64()
        if dir_offset < 19 or dir_offset >= reader.length:
            raise CorruptArchiveError(f"XP3 redirected index offset invalid: {dir_offset}")
        reader.seek(dir_offset)

    header_type = reader.read_u8()
    if header_type == 0:
        header_size = reader.read_i64()
        return reader.read_bytes(header_size)
    if header_type == 1:
        packed_size = reader.read_i64()
        _unpacked_size = reader.read_i64()
        compressed = reader.read_bytes(packed_size)
        try:
            return zlib.decompress(compressed)
        except Exception as exc:
            raise CorruptArchiveError(f"Corrupted XP3 compressed index: {exc}") from exc

    raise CorruptArchiveError(f"Unsupported XP3 index compression type: {header_type}")


def _parse_file_entry(
    reader: BinaryReader,
    chunk_limit: int,
) -> tuple[Entry, list[tuple[int, int, int, bool]]] | None:
    """Parse a single 'File' container chunk from the XP3 index."""
    entry_name = ""
    unpacked_size = 0
    packed_size = 0
    segments: list[tuple[int, int, int, bool]] = []

    while reader.tell() + 12 <= chunk_limit:
        sec_sig = reader.read_u32()
        sec_size = reader.read_i64()
        sec_next = reader.tell() + sec_size

        if sec_sig == SEC_INFO:
            _flags = reader.read_u32()
            unpacked_size = reader.read_i64()
            packed_size = reader.read_i64()
            name_len = reader.read_u16()
            name_bytes = reader.read_bytes(name_len * 2)
            entry_name = name_bytes.decode("utf-16le", errors="replace").replace("\\", "/")
        elif sec_sig == SEC_SEGM:
            seg_count = sec_size // 28
            for _ in range(seg_count):
                is_comp = reader.read_i32() != 0
                offset = reader.read_i64()
                size = reader.read_i64()
                psz = reader.read_i64()
                segments.append((offset, size, psz, is_comp))
        elif sec_sig == SEC_ADLR:
            _hash = reader.read_u32()

        reader.seek(sec_next)

    if not entry_name or not segments:
        return None

    first_offset = segments[0][0]
    entry_info = Entry(
        name=entry_name,
        size=unpacked_size,
        packed_size=packed_size if packed_size != unpacked_size else None,
        offset=first_offset,
        type="unknown",
    )
    return entry_info, segments


def _build_file_chunk(
    name: str,
    offset: int,
    unpacked_size: int,
    packed_size: int,
    is_compressed: bool,
    checksum: int,
) -> bytes:
    """Build serialized 'File' container chunk for XP3 index."""
    encoded_name = name.encode("utf-16le")
    name_len = len(name)

    info_payload = struct.pack(
        "<IqqH",
        0,
        unpacked_size,
        packed_size,
        name_len,
    ) + encoded_name
    info_sec = struct.pack("<Iq", SEC_INFO, len(info_payload)) + info_payload

    segm_payload = struct.pack(
        "<Iqqq",
        1 if is_compressed else 0,
        offset,
        unpacked_size,
        packed_size,
    )
    segm_sec = struct.pack("<Iq", SEC_SEGM, len(segm_payload)) + segm_payload

    adlr_payload = struct.pack("<I", checksum)
    adlr_sec = struct.pack("<Iq", SEC_ADLR, len(adlr_payload)) + adlr_payload

    payload = info_sec + segm_sec + adlr_sec
    return struct.pack("<Iq", SEC_FILE, len(payload)) + payload


@register_format
class Xp3Format(NativeFormat):
    """KiriKiri 2 / KAG3 XP3 archive decoder and creator."""

    tag: ClassVar[str] = "XP3"
    description: ClassVar[str] = "KiriKiri engine resource archive"
    extensions: ClassVar[tuple[str, ...]] = ("xp3",)
    can_write: ClassVar[bool] = True

    def __init__(self) -> None:
        self._segments_cache: dict[tuple[int, str], list[tuple[int, int, int, bool]]] = {}

    def probe(self, reader: BinaryReader) -> bool:
        """Probe for KiriKiri XP3 archive signature."""
        if reader.length < 19:
            return False
        try:
            reader.seek(0)
            magic = reader.read_bytes(11)
            if magic != XP3_MAGIC:
                return False
            dir_offset = reader.read_i64()
            return 19 <= dir_offset < reader.length
        except Exception:
            return False

    def list_entries(self, reader: BinaryReader, path: Path | None = None) -> tuple[ArchiveInfo, list[Entry]]:
        """List all entries in the XP3 archive."""
        index_bytes = _read_index_buffer(reader)
        idx_reader = BinaryReader(io.BytesIO(index_bytes))

        entries: list[Entry] = []
        cache_key_prefix = id(reader)

        while idx_reader.tell() + 12 <= idx_reader.length:
            chunk_sig = idx_reader.read_u32()
            chunk_size = idx_reader.read_i64()
            chunk_next = idx_reader.tell() + chunk_size

            if chunk_sig == SEC_FILE:
                parsed = _parse_file_entry(idx_reader, chunk_next)
                if parsed is not None:
                    entry, segments = parsed
                    entries.append(entry)
                    self._segments_cache[(cache_key_prefix, entry.name)] = segments

            idx_reader.seek(chunk_next)

        info = ArchiveInfo(
            format=self.tag,
            description=self.description,
            count=len(entries),
            backend="native",
        )
        return info, entries

    def read_entry(self, reader: BinaryReader, entry: Entry) -> bytes:
        """Extract and decompress entry bytes from XP3 archive."""
        cache_key = (id(reader), entry.name)
        segments = self._segments_cache.get(cache_key)

        if not segments:
            # Fallback single segment assumption if cache misses
            is_comp = entry.packed_size is not None and entry.packed_size != entry.size
            read_len = entry.packed_size if is_comp else entry.size
            reader.seek(entry.offset)
            raw = reader.read_bytes(read_len)
            return zlib.decompress(raw) if is_comp else raw

        chunks: list[bytes] = []
        for offset, size, packed_size, is_compressed in segments:
            reader.seek(offset)
            if is_compressed:
                raw_chunk = reader.read_bytes(packed_size)
                chunks.append(zlib.decompress(raw_chunk))
            else:
                chunks.append(reader.read_bytes(size))

        return b"".join(chunks)

    def create(
        self,
        output: BinaryIO,
        files: list[str],
        base_dir: Path | None = None,
    ) -> None:
        """Create a new standard compressed XP3 archive."""
        output.seek(0)
        output.write(XP3_MAGIC)
        output.write(b"\x00" * 8)  # Placeholder for index offset

        meta_list: list[tuple[str, int, int, int, bool, int]] = []

        for rel_path in files:
            clean_name = rel_path.replace("\\", "/").lstrip("/")
            full_path = (base_dir / rel_path) if base_dir else Path(rel_path)
            data = full_path.read_bytes()

            unpacked_size = len(data)
            adler = zlib.adler32(data) & 0xFFFFFFFF

            compressed = zlib.compress(data, level=9)
            if len(compressed) < unpacked_size:
                is_comp = True
                payload = compressed
            else:
                is_comp = False
                payload = data

            offset = output.tell()
            output.write(payload)
            packed_size = len(payload)

            meta_list.append((clean_name, offset, unpacked_size, packed_size, is_comp, adler))

        index_pos = output.tell()
        output.seek(11)
        output.write(struct.pack("<q", index_pos))
        output.seek(index_pos)

        # Build index chunks
        index_chunks = [
            _build_file_chunk(name, off, usz, psz, icomp, adl)
            for name, off, usz, psz, icomp, adl in meta_list
        ]
        raw_index = b"".join(index_chunks)
        comp_index = zlib.compress(raw_index, level=9)

        output.write(b"\x01")  # Compressed index
        output.write(struct.pack("<qq", len(comp_index), len(raw_index)))
        output.write(comp_index)
