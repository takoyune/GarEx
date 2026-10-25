"""Public high-level Python API for garex.

Provides typed, context-managed archive operations and format inspection.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterator, Literal, overload

from garex.backends.router import BackendMode, get_all_supported_formats, route_archive
from garex.models import Entry
from garex.security import sanitize_entry_path

if TYPE_CHECKING:
    from garex.backends.base import BaseBackend
    from garex.models import ArchiveInfo, FormatInfo


class Archive:
    """Represents an opened game resource archive."""

    def __init__(
        self,
        path: Path,
        info: ArchiveInfo,
        entries: list[Entry],
        backend: BaseBackend,
    ) -> None:
        self.path = Path(path).resolve()
        self.info = info
        self._entries = entries
        self._backend = backend
        self._closed = False

    @property
    def format(self) -> str:
        """The tag of the archive format (e.g. 'XP3', 'INT', 'PAC')."""
        return self.info.format

    @property
    def description(self) -> str:
        """A human-readable description of the format."""
        return self.info.description

    def entries(self) -> list[Entry]:
        """Return the list of all entries contained within this archive."""
        self._ensure_open()
        return list(self._entries)

    def close(self) -> None:
        """Close the archive and release associated backend resources."""
        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise ValueError(f"Operation on closed Archive '{self.path.name}'")

    def __enter__(self) -> Archive:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[Entry]:
        self._ensure_open()
        return iter(self._entries)

    def __getitem__(self, index_or_name: int | str) -> Entry:
        self._ensure_open()
        if isinstance(index_or_name, int):
            return self._entries[index_or_name]
        for e in self._entries:
            if e.name.lower() == index_or_name.lower():
                return e
        raise KeyError(f"Entry '{index_or_name}' not found in archive '{self.path.name}'")

    def __repr__(self) -> str:
        return f"<Archive format='{self.format}' path='{self.path.name}' entries={len(self._entries)}>"

    def extract(
        self,
        entry_or_name: Entry | str,
        destination: str | Path = ".",
        convert: bool = False,
        image_format: str = "png",
        audio_format: str = "wav",
    ) -> Path:
        """Extract a single archive entry to destination directory.

        Args:
            entry_or_name: Entry instance or entry filename string.
            destination: Target directory to extract to.
            convert: Automatically convert images/audio to standard formats.
            image_format: Target image format (default: 'png').
            audio_format: Target audio format (default: 'wav').

        Returns:
            Path to the extracted file.

        Raises:
            KeyError: If entry does not exist.
            UnsafePathError: If entry name contains directory traversal.
        """
        self._ensure_open()
        entry_name = entry_or_name.name if isinstance(entry_or_name, Entry) else str(entry_or_name)
        _ = self[entry_name]
        dest_path = Path(destination).resolve()
        safe_target = sanitize_entry_path(dest_path, entry_name)
        dest_path.mkdir(parents=True, exist_ok=True)
        res = self._backend.extract(
            self.path,
            dest_path,
            entry=entry_name,
            convert=convert,
            image_format=image_format,
            audio_format=audio_format,
        )
        if res and res.get("entries"):
            return dest_path / res["entries"][0].replace("\\", "/")
        return safe_target

    def extract_all(
        self,
        destination: str | Path = ".",
        convert: bool = False,
        image_format: str = "png",
        audio_format: str = "wav",
        progress_callback: Callable[[int, int, Entry], None] | None = None,
    ) -> list[Path]:
        """Extract all entries contained within this archive to destination.

        Args:
            destination: Target directory to extract to.
            convert: Automatically convert images/audio to standard formats.
            image_format: Target image format (default: 'png').
            audio_format: Target audio format (default: 'wav').
            progress_callback: Optional callback receiving (index, total, entry).

        Returns:
            List of extracted file Paths.

        Raises:
            UnsafePathError: If any entry name contains directory traversal.
        """
        self._ensure_open()
        dest_path = Path(destination).resolve()
        dest_path.mkdir(parents=True, exist_ok=True)

        for entry in self._entries:
            sanitize_entry_path(dest_path, entry.name)

        res = self._backend.extract(
            self.path,
            dest_path,
            entry=None,
            convert=convert,
            image_format=image_format,
            audio_format=audio_format,
        )
        extracted: list[Path] = []
        if res and res.get("entries"):
            for e_name in res["entries"]:
                extracted.append(dest_path / e_name.replace("\\", "/"))
        else:
            for entry in self._entries:
                target = dest_path / entry.name.replace("\\", "/")
                extracted.append(target)

        if progress_callback:
            for i, entry in enumerate(self._entries):
                progress_callback(i + 1, len(self._entries), entry)
        return extracted




def open_archive(
    path: str | Path,
    backend: BackendMode = "auto",
) -> Archive:
    """Open a game resource archive and inspect its directory.

    Args:
        path: Path to the visual novel archive file.
        backend: Backend selection ('auto', 'bridge', or 'native').

    Returns:
        Archive object implementing context management.

    Raises:
        FileNotFoundError: If the file does not exist.
        UnsupportedFormatError: If the format is not recognized.
        CorruptArchiveError: If the archive header or structure is invalid.
    """
    resolved_path = Path(path).resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"Archive file not found: {resolved_path}")

    selected_backend, info, entries = route_archive(resolved_path, mode=backend)
    return Archive(resolved_path, info, entries, selected_backend)


def supported_formats(backend: BackendMode = "auto") -> list[FormatInfo]:
    """Retrieve the catalog of all supported archive, image, audio, and script formats.

    Args:
        backend: Backend selection ('auto', 'bridge', or 'native').

    Returns:
        List of FormatInfo objects describing tags, extensions, and capabilities.
    """
    return get_all_supported_formats(mode=backend)


def convert_image(
    path: str | Path,
    destination: str | Path,
    format: str = "png",
    backend: BackendMode = "auto",
) -> Path:
    """Convert a visual novel image to standard format (PNG, BMP, JPEG, etc.).

    Args:
        path: Path to source image file.
        destination: Path to write the converted image file.
        format: Target format extension or tag (default: 'png').
        backend: Backend mode ('auto', 'bridge', or 'native').

    Returns:
        Path to the converted image.
    """
    from garex.backends.bridge import BridgeBackend

    src_path = Path(path).resolve()
    if not src_path.is_file():
        raise FileNotFoundError(f"Source image not found: {src_path}")
    dest_path = Path(destination).resolve()
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    b = BridgeBackend()
    b.convert_image(src_path, dest_path, format=format)
    return dest_path


def convert_audio(
    path: str | Path,
    destination: str | Path,
    format: str = "wav",
    backend: BackendMode = "auto",
) -> Path:
    """Convert a visual novel audio file to standard format (WAV).

    Args:
        path: Path to source audio file.
        destination: Path to write the converted audio file.
        format: Target format extension or tag (default: 'wav').
        backend: Backend mode ('auto', 'bridge', or 'native').

    Returns:
        Path to the converted audio.
    """
    from garex.backends.bridge import BridgeBackend

    src_path = Path(path).resolve()
    if not src_path.is_file():
        raise FileNotFoundError(f"Source audio not found: {src_path}")
    dest_path = Path(destination).resolve()
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    b = BridgeBackend()
    b.convert_audio(src_path, dest_path, format=format)
    return dest_path


def create_archive(
    path: str | Path,
    files: Sequence[str | Path] | Mapping[str, str | Path] | str | Path,
    format: str = "auto",
    backend: BackendMode = "auto",
    base_dir: str | Path | None = None,
) -> Archive:
    """Create a new game resource archive containing the specified files.

    Args:
        path: Destination path for the new archive.
        files: Files to include in the archive. Can be:
            - A directory path: all files inside are recursively packed preserving relative subpaths.
            - A list or sequence of file paths.
            - A mapping of {entry_name_in_archive: source_file_path_on_disk}.
        format: Target archive format tag (e.g. 'ZIP', 'RPA', 'XP3', 'INT').
            Defaults to 'auto' (inferred from destination file extension).
        backend: Backend selection ('auto', 'bridge', or 'native').
        base_dir: Optional base directory to resolve relative file paths against.

    Returns:
        Opened Archive instance for the newly created archive.
    """
    import shutil
    import tempfile
    from collections.abc import Mapping, Sequence
    if backend == "native":
        from garex.backends.native import NativeBackend
        b = NativeBackend()
    elif backend == "bridge":
        from garex.backends.bridge import BridgeBackend
        b = BridgeBackend()
    else:
        from garex.backends.native.base import get_native_format
        fmt = get_native_format(format) if format != "auto" else None
        if fmt and fmt.can_write:
            from garex.backends.native import NativeBackend
            b = NativeBackend()
        else:
            from garex.backends.bridge import BridgeBackend
            b = BridgeBackend()

    dest_path = Path(path).resolve()
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Case 1: A directory path was provided
    if isinstance(files, (str, Path)):
        src_dir = Path(files).resolve()
        if not src_dir.is_dir():
            raise FileNotFoundError(f"Source directory not found: {src_dir}")
        entry_list = [
            str(p.relative_to(src_dir)).replace("\\", "/")
            for p in src_dir.rglob("*")
            if p.is_file()
        ]
        b.create_archive(dest_path, entry_list, base_dir=src_dir, format=format)
        return open_archive(dest_path, backend=backend)

    # Case 2: A mapping of entry_name -> source_file was provided
    if isinstance(files, Mapping):
        with tempfile.TemporaryDirectory() as stage_dir:
            stage_path = Path(stage_dir)
            entry_list = []
            for entry_name, src_file in files.items():
                norm_name = entry_name.replace("\\", "/").lstrip("/")
                target = stage_path / norm_name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(Path(src_file), target)
                entry_list.append(norm_name)

            b.create_archive(dest_path, entry_list, base_dir=stage_path, format=format)
        return open_archive(dest_path, backend=backend)

    # Case 3: A sequence of file paths
    file_list = list(files)
    if not file_list:
        raise ValueError("Cannot create an archive with an empty file list")

    if base_dir is not None:
        effective_base = Path(base_dir).resolve()
        entry_list = [
            str(Path(p).resolve().relative_to(effective_base)).replace("\\", "/")
            if Path(p).is_absolute()
            else str(p).replace("\\", "/")
            for p in file_list
        ]
        b.create_archive(dest_path, entry_list, base_dir=effective_base, format=format)
    else:
        # Stage into temp directory to ensure uniform structure
        with tempfile.TemporaryDirectory() as stage_dir:
            stage_path = Path(stage_dir)
            entry_list = []
            for item in file_list:
                item_path = Path(item).resolve()
                if not item_path.is_file():
                    raise FileNotFoundError(f"Source file not found: {item_path}")
                norm_name = item_path.name
                target = stage_path / norm_name
                shutil.copyfile(item_path, target)
                entry_list.append(norm_name)

            b.create_archive(dest_path, entry_list, base_dir=stage_path, format=format)

    return open_archive(dest_path, backend=backend)


def replace_entries(
    source_archive: str | Path,
    output_archive: str | Path,
    replacements: Mapping[str, str | Path],
    backend: BackendMode = "auto",
) -> Archive:
    """Repack an archive by replacing specific entries (copy-modify-write workflow).

    Enforces safe file operations: NEVER modifies the source archive in place;
    always creates a new output archive.

    Args:
        source_archive: Path to the original source archive.
        output_archive: Path to the new repacked archive.
        replacements: Mapping of {entry_name_in_archive: path_to_replacement_file}.
        backend: Backend selection ('auto', 'bridge', or 'native').

    Returns:
        Opened Archive instance for the newly repacked archive.
    """
    import shutil
    import tempfile

    src_path = Path(source_archive).resolve()
    out_path = Path(output_archive).resolve()

    if src_path == out_path:
        raise ValueError("output_archive must be different from source_archive (copy-modify-write)")
    if not src_path.is_file():
        raise FileNotFoundError(f"Source archive not found: {src_path}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 1. Extract all existing entries into temporary staging directory
        with open_archive(src_path, backend=backend) as src_arc:
            arc_format = src_arc.format
            src_arc.extract_all(tmp_path)

        # 2. Apply replacements
        for entry_name, rep_path in replacements.items():
            rep_file = Path(rep_path).resolve()
            if not rep_file.is_file():
                raise FileNotFoundError(f"Replacement file not found: {rep_file}")
            target_entry = sanitize_entry_path(tmp_path, entry_name)
            target_entry.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(rep_file, target_entry)

        # 3. Create output archive from staged files
        return create_archive(out_path, tmp_path, format=arc_format, backend=backend)

