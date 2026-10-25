"""garex: Python library for browsing, extracting, converting, and repacking visual novel game resources."""

from __future__ import annotations

from garex.api import Archive, open_archive, supported_formats
from garex.errors import (
    BridgeError,
    BridgeNotFoundError,
    BridgeTimeoutError,
    CorruptArchiveError,
    EncryptedArchiveError,
    GarexError,
    UnsafePathError,
    UnsupportedFormatError,
)
from garex.models import ArchiveInfo, Entry, FormatInfo

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "open_archive",
    "supported_formats",
    "Archive",
    "Entry",
    "ArchiveInfo",
    "FormatInfo",
    "GarexError",
    "UnsupportedFormatError",
    "CorruptArchiveError",
    "EncryptedArchiveError",
    "BridgeError",
    "BridgeNotFoundError",
    "BridgeTimeoutError",
    "UnsafePathError",
]
