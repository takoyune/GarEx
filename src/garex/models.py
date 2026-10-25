"""Data models for garex.

All models are frozen dataclasses for immutability and thread safety.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    """Represents a single file or resource entry inside an archive."""

    name: str
    size: int
    packed_size: int | None = None
    offset: int = -1
    type: str = ""

    @property
    def is_packed(self) -> bool:
        """Whether the entry is compressed inside the archive."""
        return self.packed_size is not None and self.packed_size != self.size


@dataclass(frozen=True)
class ArchiveInfo:
    """Metadata describing an opened archive."""

    format: str
    description: str
    count: int
    backend: str = "bridge"


@dataclass(frozen=True)
class FormatInfo:
    """Describes a recognized resource format."""

    tag: str
    kind: str  # "archive", "image", "audio", "script"
    description: str
    extensions: tuple[str, ...] = ()
    can_create: bool = False
    status: str = "bridge"  # "bridge", "native", "native-partial"
