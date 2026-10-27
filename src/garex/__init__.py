"""garex: Python library for browsing, extracting, converting, and repacking visual novel game resources."""

from __future__ import annotations

from garex.api import (
    Archive,
    convert_audio,
    convert_image,
    create_archive,
    open_archive,
    replace_entries,
    supported_formats,
)
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

__version__ = "0.1.1"

__all__ = [
    "__version__",
    "open_archive",
    "create_archive",
    "replace_entries",
    "supported_formats",
    "convert_image",
    "convert_audio",
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
