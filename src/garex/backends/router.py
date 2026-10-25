"""Backend router for selecting between native and bridge backends.

Implements the hybrid strategy: native-first with bridge fallback.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from garex.backends.base import BaseBackend
from garex.backends.bridge import BridgeBackend
from garex.errors import UnsupportedFormatError

if TYPE_CHECKING:
    from garex.models import ArchiveInfo, Entry, FormatInfo

BackendMode = Literal["auto", "bridge", "native"]

_DEFAULT_BRIDGE: BridgeBackend | None = None


def get_bridge_backend() -> BridgeBackend:
    """Return the shared default BridgeBackend instance."""
    global _DEFAULT_BRIDGE
    if _DEFAULT_BRIDGE is None:
        _DEFAULT_BRIDGE = BridgeBackend()
    return _DEFAULT_BRIDGE


def route_archive(
    path: Path,
    mode: BackendMode = "auto",
    bridge_backend: BaseBackend | None = None,
    native_backend: BaseBackend | None = None,
) -> tuple[BaseBackend, ArchiveInfo, list[Entry]]:
    """Determine the appropriate backend for the archive and retrieve its entries."""
    path = Path(path).resolve()
    bridge = bridge_backend or get_bridge_backend()

    if mode == "native":
        if native_backend is None:
            raise UnsupportedFormatError(f"No native format implementation available for '{path.name}'")
        res = native_backend.probe(path)
        if not res:
            raise UnsupportedFormatError(f"Native backend does not support '{path.name}'")
        info, entries = native_backend.list_entries(path)
        return native_backend, info, entries

    if mode == "bridge":
        info, entries = bridge.list_entries(path)
        return bridge, info, entries

    # mode == "auto": Native first, then bridge fallback
    if native_backend is not None:
        try:
            res = native_backend.probe(path)
            if res:
                info, entries = native_backend.list_entries(path)
                return native_backend, info, entries
        except Exception:
            pass  # Fall back to bridge

    info, entries = bridge.list_entries(path)
    return bridge, info, entries


def get_all_supported_formats(
    mode: BackendMode = "auto",
    bridge_backend: BaseBackend | None = None,
    native_backend: BaseBackend | None = None,
) -> list[FormatInfo]:
    """Return catalog of supported formats according to the selected mode."""
    bridge = bridge_backend or get_bridge_backend()

    if mode == "bridge":
        return bridge.supported_formats()

    if mode == "native":
        return native_backend.supported_formats() if native_backend else []

    # "auto": Combine native formats over bridge formats
    native_formats = native_backend.supported_formats() if native_backend else []
    native_tags = {f.tag for f in native_formats}

    bridge_formats = bridge.supported_formats()
    combined = list(native_formats)
    for bf in bridge_formats:
        if bf.tag not in native_tags:
            combined.append(bf)

    return combined
