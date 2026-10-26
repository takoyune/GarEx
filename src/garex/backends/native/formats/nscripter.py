"""Pure-Python implementation of NScripter SAR and NSA archive formats.

References:
- SAR: https://github.com/morkt/GARbro/blob/master/ArcFormats/NScripter/ArcSAR.cs
- NSA: https://github.com/morkt/GARbro/blob/master/ArcFormats/NScripter/ArcNSA.cs
- Specification: docs/formats/NSCRIPTER.md
"""

from __future__ import annotations

import bz2
import io
import struct
from pathlib import Path
from typing import BinaryIO, ClassVar

from garex.backends.native.base import NativeFormat, register_format
from garex.backends.native.binary import BinaryReader
from garex.errors import CorruptArchiveError
from garex.models import ArchiveInfo, Entry


def _decode_name(raw: bytes) -> str:
    """Decode null-terminated CP932 / Shift-JIS entry name."""
    null_idx = raw.find(b"\x00")
    if null_idx != -1:
        raw = raw[:null_idx]
    try:
        return raw.decode("cp932")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


class MsbBitReader:
    """MSB-first bit reader for NScripter decompression."""

    __slots__ = ("_data", "_pos", "_bits", "_cached_bits")

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0
        self._bits = 0
        self._cached_bits = 0

    def get_bits(self, count: int) -> int:
        """Read count bits from MSB to LSB."""
        while self._cached_bits < count:
            if self._pos >= len(self._data):
                return -1
            b = self._data[self._pos]
            self._pos += 1
            self._bits = (self._bits << 8) | b
            self._cached_bits += 8
        mask = (1 << count) - 1
        self._cached_bits -= count
        return (self._bits >> self._cached_bits) & mask


def decompress_lzss(data: bytes, unpacked_size: int) -> bytes:
    """Decode Okumura LZSS compressed stream used by NScripter NSA."""
    ei = 8
    ej = 4
    p = 1
    n = 1 << ei  # 256
    f = (1 << ej) + p  # 17
    r = n - f  # 239

    reader = MsbBitReader(data)
    out = bytearray()
    decomp_buffer = bytearray(n * 2)

    while len(out) < unpacked_size:
        flag = reader.get_bits(1)
        if flag == -1:
            break
        if flag != 0:
            c = reader.get_bits(8)
            if c == -1:
                break
            out.append(c)
            decomp_buffer[r] = c
            r = (r + 1) & (n - 1)
        else:
            i = reader.get_bits(ei)
            if i == -1:
                break
            j = reader.get_bits(ej)
            if j == -1:
                break
            for k in range(j + 2):
                c = decomp_buffer[(i + k) & (n - 1)]
                out.append(c)
                decomp_buffer[r] = c
                r = (r + 1) & (n - 1)
                if len(out) == unpacked_size:
                    break

    return bytes(out)


def decompress_spb(data: bytes, unpacked_size: int) -> bytes:
    """Decode SPB (Special Picture Bitmap) compressed 24-bit image."""
    if len(data) < 4:
        return data

    width = (data[0] << 8) | data[1]
    height = (data[2] << 8) | data[3]

    width_pad = (4 - (width * 3) % 4) % 4
    stride = width * 3 + width_pad
    total_size = stride * height + 54

    out = bytearray(max(unpacked_size, total_size))

    # BMP Header
    out[0:2] = b"BM"
    struct.pack_into("<I", out, 2, total_size)
    out[10] = 54
    out[14] = 40
    struct.pack_into("<I", out, 18, width)
    struct.pack_into("<I", out, 22, height)
    struct.pack_into("<H", out, 26, 1)
    struct.pack_into("<H", out, 28, 24)

    reader = MsbBitReader(data[4:])
    decomp_buffer = bytearray(width * height * 4)

    for i in range(3):
        count = 0
        c = reader.get_bits(8)
        if c == -1:
            break
        decomp_buffer[count] = c
        count += 1

        while count < width * height:
            n = reader.get_bits(3)
            if n == -1:
                break
            if n == 0:
                for _ in range(4):
                    if count < width * height:
                        decomp_buffer[count] = c
                        count += 1
                continue

            m = reader.get_bits(1) + 1 if n == 7 else n + 2

            for _ in range(4):
                if count >= width * height:
                    break
                if m == 8:
                    c = reader.get_bits(8)
                else:
                    k = reader.get_bits(m)
                    if (k & 1) != 0:
                        c = (c + (k >> 1) + 1) & 0xFF
                    else:
                        c = (c - (k >> 1)) & 0xFF
                decomp_buffer[count] = c
                count += 1

        pbuf = stride * (height - 1) + i + 54
        psbuf = 0

        for j in range(height):
            if (j & 1) != 0:
                for _ in range(width):
                    if pbuf < len(out) and psbuf < len(decomp_buffer):
                        out[pbuf] = decomp_buffer[psbuf]
                        psbuf += 1
                    pbuf -= 3
                pbuf -= stride - 3
            else:
                for _ in range(width):
                    if pbuf < len(out) and psbuf < len(decomp_buffer):
                        out[pbuf] = decomp_buffer[psbuf]
                        psbuf += 1
                    pbuf += 3
                pbuf -= stride + 3

    return bytes(out[:total_size])


def decompress_nbz(data: bytes) -> bytes:
    """Decompress NBZ stream (4-byte header followed by bzip2 stream)."""
    if len(data) > 4:
        return bz2.decompress(data[4:])
    return bz2.decompress(data)


@register_format
class SarFormat(NativeFormat):
    """NScripter SAR standard resource archive decoder and creator."""

    tag: ClassVar[str] = "SAR"
    description: ClassVar[str] = "NScripter resource archive"
    extensions: ClassVar[tuple[str, ...]] = ("sar",)
    can_write: ClassVar[bool] = True

    def probe(self, reader: BinaryReader) -> bool:
        """Probe for NScripter SAR archive."""
        if reader.length < 16:
            return False
        try:
            reader.seek(0)
            raw = reader.read_bytes(6)
            num_of_files, base_offset = struct.unpack(">HI", raw)
            if num_of_files <= 0 or num_of_files > 65535:
                return False
            if base_offset >= reader.length or base_offset < 10 * num_of_files:
                return False

            cur_offset = 6
            for _ in range(num_of_files):
                if base_offset - cur_offset < 10:
                    return False
                reader.seek(cur_offset)
                name_len = 0
                while cur_offset + name_len < base_offset:
                    b = reader.read_bytes(1)
                    if not b or b == b"\x00":
                        break
                    name_len += 1
                if name_len == 0 or cur_offset + name_len >= base_offset:
                    return False
                cur_offset += name_len + 1

                if base_offset - cur_offset < 8:
                    return False
                reader.seek(cur_offset)
                file_offset, file_size = struct.unpack(">II", reader.read_bytes(8))
                cur_offset += 8
                if base_offset + file_offset + file_size > reader.length:
                    return False

            return cur_offset == base_offset
        except Exception:
            return False

    def list_entries(self, reader: BinaryReader, path: Path | None = None) -> tuple[ArchiveInfo, list[Entry]]:
        """List all entries in NScripter SAR archive."""
        reader.seek(0)
        num_of_files, base_offset = struct.unpack(">HI", reader.read_bytes(6))

        if num_of_files <= 0:
            raise CorruptArchiveError(f"Invalid SAR entry count {num_of_files}")
        if base_offset >= reader.length or base_offset < 10 * num_of_files:
            raise CorruptArchiveError("Invalid SAR base offset")

        cur_offset = 6
        entries: list[Entry] = []

        for _ in range(num_of_files):
            if base_offset - cur_offset < 10:
                raise CorruptArchiveError("Premature end of SAR directory")

            reader.seek(cur_offset)
            name_bytes = bytearray()
            while cur_offset < base_offset:
                b = reader.read_bytes(1)
                cur_offset += 1
                if not b or b == b"\x00":
                    break
                name_bytes.extend(b)

            if not name_bytes:
                raise CorruptArchiveError("Empty entry name in SAR archive")

            if base_offset - cur_offset < 8:
                raise CorruptArchiveError("Missing SAR offset/size header")

            reader.seek(cur_offset)
            file_offset, file_size = struct.unpack(">II", reader.read_bytes(8))
            cur_offset += 8

            actual_offset = base_offset + file_offset
            if actual_offset + file_size > reader.length:
                raise CorruptArchiveError(f"Entry {name_bytes!r} exceeds archive bounds")

            name = _decode_name(name_bytes)
            entries.append(
                Entry(
                    name=name,
                    size=file_size,
                    packed_size=None,
                    offset=actual_offset,
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
        """Extract uncompressed bytes from SAR archive."""
        reader.seek(entry.offset)
        return reader.read_bytes(entry.size)

    def create(
        self,
        output: BinaryIO,
        files: list[str],
        base_dir: Path | None = None,
    ) -> None:
        """Create a new standard NScripter SAR archive."""
        file_count = len(files)
        root = base_dir or Path.cwd()

        encoded_names: list[bytes] = []
        for rel_path in files:
            name = Path(rel_path).as_posix()
            try:
                encoded_names.append(name.encode("cp932"))
            except UnicodeEncodeError:
                encoded_names.append(name.encode("utf-8"))

        index_size = sum(len(name_b) + 1 + 8 for name_b in encoded_names)
        base_offset = 6 + index_size

        output.seek(0)
        output.seek(base_offset)

        file_offsets: list[int] = []
        file_sizes: list[int] = []

        for rel_path in files:
            full_path = root / rel_path
            data = full_path.read_bytes()
            curr_pos = output.tell()
            file_offsets.append(curr_pos - base_offset)
            file_sizes.append(len(data))
            output.write(data)

        # Write header and index at beginning
        output.seek(0)
        output.write(struct.pack(">HI", file_count, base_offset))

        for name_b, offset, size in zip(encoded_names, file_offsets, file_sizes):
            output.write(name_b)
            output.write(b"\x00")
            output.write(struct.pack(">II", offset, size))


@register_format
class NsaFormat(NativeFormat):
    """NScripter NSA compressed resource archive decoder and creator."""

    tag: ClassVar[str] = "NSA"
    description: ClassVar[str] = "NScripter compressed resource archive"
    extensions: ClassVar[tuple[str, ...]] = ("nsa", "dat")
    can_write: ClassVar[bool] = True

    def probe(self, reader: BinaryReader) -> bool:
        """Probe for NScripter NSA archive."""
        if reader.length < 18:
            return False
        try:
            reader.seek(0)
            first_word = struct.unpack(">H", reader.read_bytes(2))[0]
            if first_word == 0:
                count_bytes = reader.read_bytes(2)
                if len(count_bytes) < 2:
                    return False
                count = struct.unpack(">H", count_bytes)[0]
                base_offset = struct.unpack(">I", reader.read_bytes(4))[0] + 2
            else:
                count = first_word
                base_offset = struct.unpack(">I", reader.read_bytes(4))[0]

            if count <= 0 or count > 65535:
                return False
            if base_offset >= reader.length or base_offset < 15 * count:
                return False

            cur_offset = 8 if first_word == 0 else 6
            for _ in range(count):
                if base_offset - cur_offset < 15:
                    return False
                reader.seek(cur_offset)
                name_len = 0
                while cur_offset + name_len < base_offset:
                    b = reader.read_bytes(1)
                    if not b or b == b"\x00":
                        break
                    name_len += 1
                if name_len == 0 or cur_offset + name_len >= base_offset:
                    return False
                cur_offset += name_len + 1

                if base_offset - cur_offset < 13:
                    return False
                reader.seek(cur_offset)
                comp_type = reader.read_bytes(1)[0]
                if comp_type not in (0, 1, 2, 4):
                    return False
                file_offset, packed_size, unpacked_size = struct.unpack(">III", reader.read_bytes(12))
                cur_offset += 13
                if base_offset + file_offset + packed_size > reader.length:
                    return False

            return cur_offset == base_offset
        except Exception:
            return False

    def __init__(self) -> None:
        super().__init__()
        self._compression_map: dict[tuple[int, int], int] = {}

    def list_entries(self, reader: BinaryReader, path: Path | None = None) -> tuple[ArchiveInfo, list[Entry]]:
        """List all entries in NScripter NSA archive."""
        reader.seek(0)
        first_word = struct.unpack(">H", reader.read_bytes(2))[0]
        cur_offset = 6

        if first_word == 0:
            count = struct.unpack(">H", reader.read_bytes(2))[0]
            base_offset = struct.unpack(">I", reader.read_bytes(4))[0] + 2
            cur_offset = 8
        else:
            count = first_word
            base_offset = struct.unpack(">I", reader.read_bytes(4))[0]

        if count <= 0:
            raise CorruptArchiveError(f"Invalid NSA entry count {count}")
        if base_offset >= reader.length or base_offset < 15 * count:
            raise CorruptArchiveError("Invalid NSA base offset")

        entries: list[Entry] = []

        for _ in range(count):
            if base_offset - cur_offset < 15:
                raise CorruptArchiveError("Premature end of NSA directory")

            reader.seek(cur_offset)
            name_bytes = bytearray()
            while cur_offset < base_offset:
                b = reader.read_bytes(1)
                cur_offset += 1
                if not b or b == b"\x00":
                    break
                name_bytes.extend(b)

            if not name_bytes:
                raise CorruptArchiveError("Empty entry name in NSA archive")

            if base_offset - cur_offset < 13:
                raise CorruptArchiveError("Missing NSA metadata header")

            reader.seek(cur_offset)
            comp_type = reader.read_bytes(1)[0]
            file_offset, packed_size, unpacked_size = struct.unpack(">III", reader.read_bytes(12))
            cur_offset += 13

            actual_offset = base_offset + file_offset
            if actual_offset + packed_size > reader.length:
                raise CorruptArchiveError(f"Entry {name_bytes!r} exceeds archive bounds")

            name = _decode_name(name_bytes)
            entry = Entry(
                name=name,
                size=unpacked_size if comp_type != 0 else packed_size,
                packed_size=packed_size if comp_type != 0 else None,
                offset=actual_offset,
                type="audio" if name.lower().endswith(".nbz") else "unknown",
            )
            self._compression_map[(entry.offset, entry.size)] = comp_type
            entries.append(entry)

        info = ArchiveInfo(
            format=self.tag,
            description=self.description,
            count=len(entries),
            backend="native",
        )
        return info, entries

    def read_entry(self, reader: BinaryReader, entry: Entry) -> bytes:
        """Extract and decompress file entry from NSA archive."""
        reader.seek(entry.offset)
        raw_size = entry.packed_size if entry.packed_size is not None else entry.size
        data = reader.read_bytes(raw_size)

        comp_type = self._compression_map.get((entry.offset, entry.size), 0)

        if comp_type == 0:
            return data
        if comp_type == 1:
            return decompress_spb(data, entry.size)
        if comp_type == 2:
            return decompress_lzss(data, entry.size)
        if comp_type == 4 or entry.name.lower().endswith(".nbz"):
            if len(data) > 4:
                return bz2.decompress(data[4:])
            return bz2.decompress(data)

        return data

    def create(
        self,
        output: BinaryIO,
        files: list[str],
        base_dir: Path | None = None,
    ) -> None:
        """Create a new standard NScripter NSA archive."""
        file_count = len(files)
        root = base_dir or Path.cwd()

        encoded_names: list[bytes] = []
        for rel_path in files:
            name = Path(rel_path).as_posix()
            try:
                encoded_names.append(name.encode("cp932"))
            except UnicodeEncodeError:
                encoded_names.append(name.encode("utf-8"))

        index_size = sum(len(name_b) + 1 + 13 for name_b in encoded_names)
        base_offset = 6 + index_size

        output.seek(0)
        output.seek(base_offset)

        file_offsets: list[int] = []
        file_sizes: list[int] = []

        for rel_path in files:
            full_path = root / rel_path
            data = full_path.read_bytes()
            curr_pos = output.tell()
            file_offsets.append(curr_pos - base_offset)
            file_sizes.append(len(data))
            output.write(data)

        # Write header and index at beginning
        output.seek(0)
        output.write(struct.pack(">HI", file_count, base_offset))

        for name_b, offset, size in zip(encoded_names, file_offsets, file_sizes):
            output.write(name_b)
            output.write(b"\x00")
            output.write(b"\x00")  # compression_type = None (0)
            output.write(struct.pack(">III", offset, size, size))
