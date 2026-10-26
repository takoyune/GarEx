"""Backend router for selecting between native and bridge backends.

Implements the hybrid strategy: native-first with bridge fallback.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from garex.backends.base import BaseBackend
from garex.errors import BridgeNotFoundError, EncryptedArchiveError, UnsupportedFormatError

if TYPE_CHECKING:
    from garex.backends.bridge import BridgeBackend
    from garex.models import ArchiveInfo, Entry, FormatInfo

BackendMode = Literal["auto", "bridge", "native"]

_DEFAULT_BRIDGE: BridgeBackend | None = None
_DEFAULT_NATIVE: BaseBackend | None = None
_BRIDGE_TRIED: bool = False


def get_bridge_backend() -> BridgeBackend | None:
    """Return the shared default BridgeBackend instance, or None if unavailable."""
    global _DEFAULT_BRIDGE, _BRIDGE_TRIED
    if not _BRIDGE_TRIED:
        _BRIDGE_TRIED = True
        try:
            from garex.backends.bridge import BridgeBackend
            _DEFAULT_BRIDGE = BridgeBackend()
        except (BridgeNotFoundError, Exception):
            _DEFAULT_BRIDGE = None
    return _DEFAULT_BRIDGE


def get_native_backend() -> BaseBackend:
    """Return the shared default NativeBackend instance."""
    global _DEFAULT_NATIVE
    if _DEFAULT_NATIVE is None:
        from garex.backends.native import NativeBackend
        _DEFAULT_NATIVE = NativeBackend()
    return _DEFAULT_NATIVE


def route_archive(
    path: Path,
    mode: BackendMode = "auto",
    bridge_backend: BaseBackend | None = None,
    native_backend: BaseBackend | None = None,
) -> tuple[BaseBackend, ArchiveInfo, list[Entry]]:
    """Determine the appropriate backend for the archive and retrieve its entries."""
    path = Path(path).resolve()

    if mode == "native":
        native = native_backend or get_native_backend()
        res = native.probe(path)
        if not res:
            raise UnsupportedFormatError(f"Native backend does not support '{path.name}'")
        info, entries = native.list_entries(path)
        return native, info, entries

    if mode == "bridge":
        bridge = bridge_backend or get_bridge_backend()
        if bridge is None:
            raise BridgeNotFoundError(
                f"Bridge backend is not available to open '{path.name}'. "
                "The C# bridge requires Windows with compiled bridge assemblies."
            )
        res = bridge.probe(path)
        if not res:
            raise UnsupportedFormatError(f"Bridge backend does not support '{path.name}'")
        info, entries = bridge.list_entries(path)
        return bridge, info, entries

    # mode == "auto": Native first, then bridge fallback
    native = native_backend or get_native_backend()
    try:
        res = native.probe(path)
        if res:
            info, entries = native.list_entries(path)
            return native, info, entries
    except EncryptedArchiveError:
        raise
    except Exception:
        pass  # Fall back to bridge if native listing fails

    bridge = bridge_backend or get_bridge_backend()
    if bridge is not None:
        try:
            res = bridge.probe(path)
            if res:
                info, entries = bridge.list_entries(path)
                return bridge, info, entries
        except Exception:
            pass

    raise UnsupportedFormatError(f"Unsupported visual novel archive format: '{path.name}'")


def get_all_supported_formats(
    mode: BackendMode = "auto",
    bridge_backend: BaseBackend | None = None,
    native_backend: BaseBackend | None = None,
) -> list[FormatInfo]:
    """Return catalog of supported formats according to the selected mode."""
    native = native_backend or get_native_backend()
    native_formats = native.supported_formats()

    if mode == "native":
        return native_formats

    bridge = bridge_backend or get_bridge_backend()
    if mode == "bridge":
        return bridge.supported_formats() if bridge is not None else []

    # "auto": Combine native formats over bridge formats if bridge is available
    if bridge is None:
        return native_formats

    native_tags = {f.tag for f in native_formats}
    bridge_formats = bridge.supported_formats()
    combined = list(native_formats)
    for bf in bridge_formats:
        if bf.tag not in native_tags:
            combined.append(bf)

    return combined
