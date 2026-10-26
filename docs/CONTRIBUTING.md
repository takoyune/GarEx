# Contributing to GarEx

Thank you for your interest in contributing to **GarEx**! GarEx is an open-source visual novel resource extraction, browsing, and repacking library. We welcome contributions ranging from adding new native Python formats to improving performance, documentation, and tooling.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/TakoYune/GarEx.git
cd GarEx
```

### 2. Set Up Development Environment

Python 3.10 or higher is required. Create a virtual environment and install the development dependencies:

```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux / macOS:
source .venv/bin/activate

# Install GarEx in editable mode with development dependencies
pip install -e ".[dev]"
```

### 3. Run the Test Suite

Verify that your environment runs the test suite cleanly:

```bash
python -m pytest tests/
```

---

## Adding a Native Archive Format

GarEx's primary mission is to expand cross-platform pure-Python format decoders that run everywhere (Windows, Linux, macOS, Steam Deck) without external runtime dependencies.

Here is the step-by-step workflow for implementing a new native format.

### Step 1: Research the Format Layout

1. Identify the engine and target archive format (e.g. extension, magic bytes, structure).
2. If the format exists in classic GARbro C# source code, inspect its implementation in `vendor/GARbro/ArcFormats/`.
3. Document the format's binary structure (magic, header, directory table, compression algorithm, and endianness) in `docs/formats/<FORMAT>.md`.

### Step 2: Implement the Format Module

Create a new file under `src/garex/backends/native/formats/<format_name>.py`:

```python
"""<Format Name> archive support for GarEx."""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, Sequence

from garex.backends.native.base import NativeArchive, NativeFormat, register_format
from garex.backends.native.binary import read_exact, read_u32_le
from garex.core.archive import ArchiveEntry
from garex.core.errors import CorruptArchiveError, InvalidSignatureError


@register_format
class MyFormatOpener(NativeFormat):
    """Opener and unpacker for <Format Name> archives."""

    format_tag = "MYFORMAT"
    extensions = ("arc", "dat")
    description = "<Format Name> resource archive"

    def probe(self, stream: BinaryIO) -> bool:
        """Quickly check if the file matches this format's magic signature."""
        stream.seek(0)
        magic = stream.read(4)
        return magic == b"MAGIC"

    def open(self, stream: BinaryIO, path: str | Path | None = None) -> NativeArchive:
        """Parse the archive directory table and return a NativeArchive."""
        if not self.probe(stream):
            raise InvalidSignatureError("Not a valid <Format Name> archive.")

        # Read directory table, validate bounds, and build ArchiveEntry list
        entries: list[ArchiveEntry] = []
        ...
        return MyArchive(stream=stream, entries_list=entries, format_tag=self.format_tag)
```

### Step 3: Implement Archive Reading & Extraction

Subclass `NativeArchive` to handle entry extraction:

```python
class MyArchive(NativeArchive):
    """Archive reader for <Format Name>."""

    def open_entry(self, entry: ArchiveEntry) -> BinaryIO:
        """Return a readable stream containing the uncompressed file data."""
        self._stream.seek(entry.offset)
        raw_data = read_exact(self._stream, entry.packed_size)

        # Decompress if compressed (e.g. zlib, lzss, bzip2)
        unpacked_data = decompress_payload(raw_data)
        return io.BytesIO(unpacked_data)
```

### Step 4: Follow Safety & Robustness Guidelines

- **Safe Path Sanitization**: Always sanitize extracted paths to prevent directory traversal (Zip-Slip) attacks. GarEx includes path sanitization utilities in `garex.security`.
- **Bounds Checking**: Never assume file offsets or packed sizes in archive headers are trustworthy. Verify that all offsets fit within the file size. If corrupt data is encountered, raise `CorruptArchiveError`.
- **Type Annotations**: GarEx uses strict Python type hinting. Ensure all functions and class methods have type annotations.
- **Memory Efficiency**: Prefer streaming or zero-copy memoryview slicing over duplicating large memory buffers.

### Step 5: Add Tests & Verify Differential Parity

1. Add unit tests in `tests/test_native_<format>.py` testing:
   - Header probing and signature validation.
   - Archive listing and entry metadata.
   - Entry extraction and byte contents.
   - Error handling on truncated or corrupt input.
2. If comparing against GARbro bridge output, verify that extracted files match byte-for-byte (SHA-256 parity).

---

## Coding Standards

- **Python Version**: Python 3.10+.
- **Formatting & Linting**: We use `ruff` and `black` standards:
  - Line length: 100 characters.
  - Descriptive, unambiguous variable and function names.
- **No External Runtime Dependencies**: Native formats must rely exclusively on Python standard library modules (`zlib`, `bz2`, `lzma`, `struct`, `io`, `pathlib`).

---

## Submitting Pull Requests

1. Create a feature branch: `git checkout -b feature/my-new-format`
2. Ensure all tests pass: `python -m pytest tests/`
3. Commit your changes with clear, conventional commit messages:
   - `feat(formats): add native support for XYZ archive`
   - `fix(security): handle invalid path characters on Windows`
   - `docs: update engine support guide`
4. Push your branch and open a Pull Request on GitHub.
