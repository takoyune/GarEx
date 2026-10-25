"""Path safety and security sanitization utilities.

Protects against directory traversal (Zip Slip), UNC escapes, drive overrides,
and absolute path injections during extraction.
"""

from __future__ import annotations

import os
from pathlib import Path

from garex.errors import UnsafePathError


def sanitize_entry_path(destination: str | Path, entry_name: str) -> Path:
    """Validate and resolve an archive entry path against a target destination.

    Args:
        destination: Root directory where the archive is being extracted.
        entry_name: Raw entry filename or relative path stored in the archive.

    Returns:
        Absolute Path safely residing within the destination directory.

    Raises:
        UnsafePathError: If the entry attempts to escape destination directory,
                         contains drive letters, UNC prefixes, or absolute paths.
    """
    if not entry_name or not entry_name.strip():
        raise UnsafePathError("Empty archive entry name is not allowed")

    clean_name = entry_name.replace("\\", "/").strip()

    # Reject absolute paths, UNC paths, and drive letters
    if clean_name.startswith("/") or clean_name.startswith("//"):
        raise UnsafePathError(f"Archive entry path '{entry_name}' attempts to escape destination: absolute or UNC path")

    if ":" in clean_name.split("/")[0]:
        raise UnsafePathError(f"Archive entry path '{entry_name}' attempts to escape destination: drive specifier detected")

    dest_resolved = Path(destination).resolve()
    target_resolved = (dest_resolved / clean_name).resolve()

    try:
        is_safe = target_resolved.is_relative_to(dest_resolved)
    except AttributeError:
        # Fallback for older python or edge cases
        is_safe = str(target_resolved).startswith(str(dest_resolved))

    if not is_safe or target_resolved == dest_resolved:
        raise UnsafePathError(f"Archive entry path '{entry_name}' attempts to escape destination directory '{dest_resolved}'")

    return target_resolved
