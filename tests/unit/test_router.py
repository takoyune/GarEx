"""Unit tests for backend router using fake backends."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import pytest

from garex.backends.base import BaseBackend
from garex.backends.router import get_all_supported_formats, route_archive
from garex.errors import UnsupportedFormatError
from garex.models import ArchiveInfo, Entry, FormatInfo


class FakeBackend(BaseBackend):
    def __init__(self, name: str, recognized_files: list[str]) -> None:
        self.name = name
        self.recognized_files = set(recognized_files)

    def probe(self, path: Path) -> dict[str, Any] | None:
        if path.name in self.recognized_files:
            return {"recognized": True, "format": "FAKE", "description": f"Fake by {self.name}"}
        return None

    def list_entries(self, path: Path) -> tuple[ArchiveInfo, list[Entry]]:
        if path.name not in self.recognized_files:
            raise UnsupportedFormatError(f"{self.name} cannot open {path.name}")
        info = ArchiveInfo(format="FAKE", description=f"Fake by {self.name}", count=1, backend=self.name)
        entries = [Entry(name="file.txt", size=100, offset=0, type="text")]
        return info, entries

    def supported_formats(self) -> list[FormatInfo]:
        return [FormatInfo(tag=f"FAKE-{self.name.upper()}", kind="archive", description="Fake")]

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
        return {"extracted_count": 1, "total_bytes": 100, "destination": str(destination)}

    def convert_image(
        self,
        path: Path,
        destination: Path,
        format: str = "PNG",
    ) -> dict[str, Any]:
        return {"width": 100, "height": 100, "bpp": 32, "target_format": format.upper()}

    def convert_audio(
        self,
        path: Path,
        destination: Path,
        format: str = "WAV",
    ) -> dict[str, Any]:
        return {"sample_rate": 44100, "channels": 2, "target_format": format.upper()}




def test_router_auto_prefers_native() -> None:
    native = FakeBackend("native", ["claimed.arc"])
    bridge = FakeBackend("bridge", ["claimed.arc", "fallback.arc"])

    backend, info, entries = route_archive(
        Path("claimed.arc"),
        mode="auto",
        native_backend=native,
        bridge_backend=bridge,
    )
    assert backend is native
    assert info.backend == "native"
    assert len(entries) == 1


def test_router_auto_falls_back_to_bridge() -> None:
    native = FakeBackend("native", ["claimed.arc"])
    bridge = FakeBackend("bridge", ["claimed.arc", "fallback.arc"])

    backend, info, entries = route_archive(
        Path("fallback.arc"),
        mode="auto",
        native_backend=native,
        bridge_backend=bridge,
    )
    assert backend is bridge
    assert info.backend == "bridge"


def test_router_explicit_modes() -> None:
    native = FakeBackend("native", ["claimed.arc"])
    bridge = FakeBackend("bridge", ["claimed.arc"])

    # Force bridge on claimed.arc
    backend, info, _ = route_archive(
        Path("claimed.arc"),
        mode="bridge",
        native_backend=native,
        bridge_backend=bridge,
    )
    assert backend is bridge

    # Force native on unsupported file raises
    with pytest.raises(UnsupportedFormatError):
        route_archive(
            Path("other.arc"),
            mode="native",
            native_backend=native,
            bridge_backend=bridge,
        )


def test_router_formats_merging() -> None:
    native = FakeBackend("native", [])
    bridge = FakeBackend("bridge", [])

    formats = get_all_supported_formats(mode="auto", native_backend=native, bridge_backend=bridge)
    tags = {f.tag for f in formats}
    assert "FAKE-NATIVE" in tags
    assert "FAKE-BRIDGE" in tags
