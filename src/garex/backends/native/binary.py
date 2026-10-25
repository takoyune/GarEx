"""Safe binary reader helpers for native format decoders.

Provides bounds-checked integer, float, string, and buffer reading operations.
Raises CorruptArchiveError on truncated input or corrupt bounds.
"""

from __future__ import annotations

import io
import struct
from pathlib import Path
from typing import BinaryIO

from garex.errors import CorruptArchiveError


class BinaryReader:
    """A safe, bounds-checked binary reader wrapping a stream or byte buffer."""

    def __init__(self, stream_or_bytes: BinaryIO | bytes, name: str = "") -> None:
        self.name = name
        if isinstance(stream_or_bytes, bytes):
            self._stream: BinaryIO = io.BytesIO(stream_or_bytes)
        else:
            self._stream = stream_or_bytes

        # Calculate stream length if seekable
        try:
            current = self._stream.tell()
            self._stream.seek(0, io.SEEK_END)
            self._length = self._stream.tell()
            self._stream.seek(current, io.SEEK_SET)
        except (io.UnsupportedOperation, AttributeError, OSError):
            self._length = -1

    @classmethod
    def open_file(cls, path: Path | str) -> BinaryReader:
        """Open a file in binary read mode."""
        f = open(path, "rb")
        return cls(f, name=Path(path).name)

    @property
    def length(self) -> int:
        """Total size of stream in bytes, or -1 if not seekable."""
        return self._length

    def tell(self) -> int:
        """Current position within stream."""
        return self._stream.tell()

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        """Seek to a byte position in the stream."""
        if whence == io.SEEK_SET and offset < 0:
            raise CorruptArchiveError(f"Cannot seek to negative offset {offset} in '{self.name}'")
        if self._length >= 0:
            target = offset
            if whence == io.SEEK_CUR:
                target = self.tell() + offset
            elif whence == io.SEEK_END:
                target = self._length + offset
            if target < 0 or target > self._length:
                raise CorruptArchiveError(
                    f"Seek offset {target} out of bounds (file size {self._length}) in '{self.name}'"
                )
        return self._stream.seek(offset, whence)

    def remaining(self) -> int:
        """Remaining bytes available to read, or -1 if length unknown."""
        if self._length < 0:
            return -1
        return max(0, self._length - self.tell())

    def read(self, size: int) -> bytes:
        """Read exact number of bytes, raising CorruptArchiveError if truncated."""
        if size < 0:
            raise CorruptArchiveError(f"Negative read size {size} requested in '{self.name}'")
        if size == 0:
            return b""
        data = self._stream.read(size)
        if len(data) != size:
            raise CorruptArchiveError(
                f"Unexpected end of stream in '{self.name}': requested {size} bytes, got {len(data)}"
            )
        return data

    def read_exact(self, size: int) -> bytes:
        """Alias for read(size)."""
        return self.read(size)

    def read_bytes(self, size: int) -> bytes:
        """Alias for read(size)."""
        return self.read(size)

    # Convenient Little-Endian aliases (default for x86 visual novel formats)
    def read_u16(self) -> int:
        return self.read_u16_le()

    def read_i16(self) -> int:
        return self.read_i16_le()

    def read_u32(self) -> int:
        return self.read_u32_le()

    def read_i32(self) -> int:
        return self.read_i32_le()

    def read_u64(self) -> int:
        return self.read_u64_le()

    def read_i64(self) -> int:
        return self.read_i64_le()

    def peek(self, size: int) -> bytes:
        """Peek ahead by size bytes without advancing position."""
        pos = self.tell()
        try:
            data = self._stream.read(size)
            return data
        finally:
            self.seek(pos)

    # Integer reads - Little Endian
    def read_u8(self) -> int:
        """Read unsigned 8-bit integer."""
        return struct.unpack("<B", self.read(1))[0]

    def read_i8(self) -> int:
        """Read signed 8-bit integer."""
        return struct.unpack("<b", self.read(1))[0]

    def read_u16_le(self) -> int:
        """Read unsigned 16-bit little-endian integer."""
        return struct.unpack("<H", self.read(2))[0]

    def read_i16_le(self) -> int:
        """Read signed 16-bit little-endian integer."""
        return struct.unpack("<h", self.read(2))[0]

    def read_u32_le(self) -> int:
        """Read unsigned 32-bit little-endian integer."""
        return struct.unpack("<I", self.read(4))[0]

    def read_i32_le(self) -> int:
        """Read signed 32-bit little-endian integer."""
        return struct.unpack("<i", self.read(4))[0]

    def read_u64_le(self) -> int:
        """Read unsigned 64-bit little-endian integer."""
        return struct.unpack("<Q", self.read(8))[0]

    def read_i64_le(self) -> int:
        """Read signed 64-bit little-endian integer."""
        return struct.unpack("<q", self.read(8))[0]

    # Integer reads - Big Endian
    def read_u16_be(self) -> int:
        """Read unsigned 16-bit big-endian integer."""
        return struct.unpack(">H", self.read(2))[0]

    def read_i16_be(self) -> int:
        """Read signed 16-bit big-endian integer."""
        return struct.unpack(">h", self.read(2))[0]

    def read_u32_be(self) -> int:
        """Read unsigned 32-bit big-endian integer."""
        return struct.unpack(">I", self.read(4))[0]

    def read_i32_be(self) -> int:
        """Read signed 32-bit big-endian integer."""
        return struct.unpack(">i", self.read(4))[0]

    def read_u64_be(self) -> int:
        """Read unsigned 64-bit big-endian integer."""
        return struct.unpack(">Q", self.read(8))[0]

    def read_i64_be(self) -> int:
        """Read signed 64-bit big-endian integer."""
        return struct.unpack(">q", self.read(8))[0]

    # String reads
    def read_cstring(self, encoding: str = "cp932", max_length: int = 1024) -> str:
        """Read null-terminated string up to max_length."""
        chars = bytearray()
        while len(chars) < max_length:
            b = self.read(1)
            if b == b"\x00":
                break
            chars.extend(b)
        else:
            raise CorruptArchiveError(f"Null terminator not found within {max_length} bytes in '{self.name}'")
        return chars.decode(encoding, errors="replace")

    def read_fixed_string(self, length: int, encoding: str = "cp932", strip_nulls: bool = True) -> str:
        """Read fixed-length string buffer."""
        data = self.read(length)
        if strip_nulls:
            data = data.split(b"\x00", 1)[0]
        return data.decode(encoding, errors="replace")

    def sub_reader(self, offset: int, size: int) -> BinaryReader:
        """Create a child BinaryReader scoped to [offset, offset + size]."""
        pos = self.tell()
        self.seek(offset)
        chunk = self.read(size)
        self.seek(pos)
        return BinaryReader(chunk, name=f"{self.name}@[0x{offset:X}:0x{offset+size:X}]")

    def close(self) -> None:
        """Close underlying stream."""
        try:
            self._stream.close()
        except Exception:
            pass

    def __enter__(self) -> BinaryReader:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()
