"""Abstract base backend interface for garex.

Both BridgeBackend and NativeBackend implement this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from garex.models import ArchiveInfo, Entry, FormatInfo


class BaseBackend(ABC):
    """Abstract interface defining required backend capabilities."""

    @abstractmethod
    def probe(self, path: Path) -> dict[str, Any] | None:
        """Check whether the backend recognizes the format of the given path."""

    @abstractmethod
    def list_entries(self, path: Path) -> tuple[ArchiveInfo, list[Entry]]:
        """Open archive and list all entries."""

    @abstractmethod
    def supported_formats(self) -> list[FormatInfo]:
        """Return all resource formats supported by this backend."""

    @abstractmethod
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
        """Extract one or all entries from an archive into destination directory."""

    @abstractmethod
    def convert_image(
        self,
        path: Path,
        destination: Path,
        format: str = "PNG",
    ) -> dict[str, Any]:
        """Convert a standalone visual novel image to standard format."""

    @abstractmethod
    def convert_audio(
        self,
        path: Path,
        destination: Path,
        format: str = "WAV",
    ) -> dict[str, Any]:
        """Convert a standalone visual novel audio track to standard format."""


