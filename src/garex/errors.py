"""Typed exceptions for garex.

All exceptions inherit from GarexError.
"""

from __future__ import annotations


class GarexError(Exception):
    """Base exception for all errors raised by garex."""


class UnsupportedFormatError(GarexError):
    """Raised when a file or stream format is not recognized or unsupported."""


class CorruptArchiveError(GarexError):
    """Raised when an archive has corrupted headers, tables, or payload data."""


class EncryptedArchiveError(GarexError):
    """Raised when an archive is encrypted and requires a passphrase or scheme."""


class BridgeNotFoundError(GarexError):
    """Raised when the garex-bridge executable or runtime assemblies cannot be located."""


class BridgeError(GarexError):
    """Raised when the C# bridge returns an error response or fails."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


class BridgeTimeoutError(BridgeError):
    """Raised when a command sent to the bridge times out."""

    def __init__(self, message: str = "Bridge process timed out") -> None:
        super().__init__("TIMEOUT", message)


class UnsafePathError(GarexError):
    """Raised when an archive entry contains paths that escape the target directory."""
