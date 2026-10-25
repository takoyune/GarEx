"""Native format abstract interface and registry.

Defines the contract for pure Python visual novel archive, image, and audio decoders.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, ClassVar, Type

if TYPE_CHECKING:
    from garex.backends.native.binary import BinaryReader
    from garex.models import ArchiveInfo, Entry, FormatInfo


class NativeFormat(ABC):
    """Abstract base class for a native pure-Python format implementation."""

    tag: ClassVar[str] = ""
    description: ClassVar[str] = ""
    extensions: ClassVar[tuple[str, ...]] = ()
    kind: ClassVar[str] = "archive"
    can_write: ClassVar[bool] = False

    @abstractmethod
    def probe(self, reader: BinaryReader) -> bool:
        """Probe the stream to check if it matches this format's magic or structure."""

    @abstractmethod
    def list_entries(self, reader: BinaryReader, path: Path) -> tuple[ArchiveInfo, list[Entry]]:
        """Parse directory/index table and return archive metadata and entries."""

    @abstractmethod
    def read_entry(self, reader: BinaryReader, entry: Entry) -> bytes:
        """Extract and decompress/decrypt a single entry's bytes."""

    def create(
        self,
        output: BinaryIO,
        files: list[str],
        base_dir: Path | None = None,
    ) -> None:
        """Create an archive. Raises NotImplementedError if not supported."""
        raise NotImplementedError(f"Native creation is not implemented for format {self.tag}")


_FORMAT_REGISTRY: dict[str, NativeFormat] = {}


def register_format(cls: Type[NativeFormat]) -> Type[NativeFormat]:
    """Decorator to register a native format class."""
    instance = cls()
    _FORMAT_REGISTRY[cls.tag.upper()] = instance
    return cls


def get_native_format(tag: str) -> NativeFormat | None:
    """Retrieve a registered native format by tag."""
    return _FORMAT_REGISTRY.get(tag.upper())


def list_native_formats() -> list[NativeFormat]:
    """Return all registered native format instances."""
    return list(_FORMAT_REGISTRY.values())


def probe_native_format(reader: BinaryReader) -> NativeFormat | None:
    """Probe all registered native formats against a binary reader."""
    for fmt in _FORMAT_REGISTRY.values():
        pos = reader.tell()
        try:
            if fmt.probe(reader):
                return fmt
        except Exception:
            pass
        finally:
            reader.seek(pos)
    return None
