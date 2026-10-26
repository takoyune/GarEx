"""Path safety and security sanitization utilities.

Protects against directory traversal (Zip Slip), UNC escapes, drive overrides,
absolute path injections, invalid filesystem characters, and filesystem length limits during extraction.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from garex.errors import UnsafePathError

# Characters invalid in Windows file and directory names, plus ASCII control characters
_INVALID_CHARS_RE = re.compile(r'[\<\>\:\"\/\\\|\?\*\x00-\x1f]')
_MAX_COMPONENT_LENGTH = 200


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

    # Split into components and sanitize each component
    raw_parts = [p for p in clean_name.split("/") if p and p != "."]
    sanitized_parts: list[str] = []

    for part in raw_parts:
        if part == "..":
            # Traversal attempt; preserved for safety check below
            sanitized_parts.append("..")
            continue

        # Replace invalid filesystem characters with underscore and strip trailing spaces/dots
        clean_part = _INVALID_CHARS_RE.sub("_", part).strip(". ")
        if not clean_part:
            clean_part = "_"

        # Truncate overly long path components to preserve NTFS/ext4 limits (<= 255 chars)
        if len(clean_part) > _MAX_COMPONENT_LENGTH:
            stem, ext = os.path.splitext(clean_part)
            clean_part = stem[: _MAX_COMPONENT_LENGTH - len(ext) - 1] + "_" + ext

        sanitized_parts.append(clean_part)

    safe_subpath = Path(*sanitized_parts) if sanitized_parts else Path("_")
    target_resolved = (dest_resolved / safe_subpath).resolve()

    try:
        is_safe = target_resolved.is_relative_to(dest_resolved)
    except AttributeError:
        # Fallback for older python or edge cases
        is_safe = str(target_resolved).startswith(str(dest_resolved))

    if not is_safe or target_resolved == dest_resolved:
        raise UnsafePathError(f"Archive entry path '{entry_name}' attempts to escape destination directory '{dest_resolved}'")

    return target_resolved

