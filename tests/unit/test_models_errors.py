"""Unit tests for models and error hierarchy."""

from __future__ import annotations

import dataclasses
import pytest

import garex
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


def test_entry_model_properties() -> None:
    e1 = Entry(name="script.ks", size=1024, offset=512, type="script")
    assert e1.name == "script.ks"
    assert e1.size == 1024
    assert e1.packed_size is None
    assert not e1.is_packed
    assert e1.offset == 512

    e2 = Entry(name="image.png", size=5000, packed_size=2000, offset=1024, type="image")
    assert e2.is_packed
    assert e2.size == 5000
    assert e2.packed_size == 2000


def test_models_immutability() -> None:
    e = Entry(name="test.txt", size=100)
    with pytest.raises(dataclasses.FrozenInstanceError):
        e.name = "changed.txt"  # type: ignore[misc]

    info = ArchiveInfo(format="XP3", description="KiriKiri", count=1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        info.format = "INT"  # type: ignore[misc]

    fmt = FormatInfo(tag="XP3", kind="archive", description="KiriKiri")
    with pytest.raises(dataclasses.FrozenInstanceError):
        fmt.tag = "INT"  # type: ignore[misc]


def test_error_hierarchy() -> None:
    assert issubclass(UnsupportedFormatError, GarexError)
    assert issubclass(CorruptArchiveError, GarexError)
    assert issubclass(EncryptedArchiveError, GarexError)
    assert issubclass(BridgeNotFoundError, GarexError)
    assert issubclass(BridgeError, GarexError)
    assert issubclass(BridgeTimeoutError, BridgeError)
    assert issubclass(UnsafePathError, GarexError)


def test_bridge_error_properties() -> None:
    err = BridgeError("TEST_CODE", "Something failed")
    assert err.code == "TEST_CODE"
    assert err.message == "Something failed"
    assert "[TEST_CODE] Something failed" in str(err)
