"""BridgeBackend: communicates with garex-bridge.exe via JSON-lines stdio IPC.

Follows ADR-004 for crash isolation, portability, and process safety.
"""

from __future__ import annotations

import atexit
import json
import os
import subprocess
import threading
from pathlib import Path
from typing import Any

from garex.backends.base import BaseBackend
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


def find_bridge_exe() -> Path:
    """Locate the garex-bridge.exe executable within the package or environment."""
    # 1. Package directory (src/garex/_bridge/garex-bridge.exe)
    pkg_bridge = Path(__file__).resolve().parent.parent / "_bridge" / "garex-bridge.exe"
    if pkg_bridge.exists():
        return pkg_bridge

    # 2. Environment variable override
    env_bridge = os.environ.get("GAREX_BRIDGE_EXE")
    if env_bridge and Path(env_bridge).exists():
        return Path(env_bridge)

    # 3. Development local bridge build directory
    local_bridge = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "bridge"
        / "bin"
        / "Release"
        / "garex-bridge.exe"
    )
    if local_bridge.exists():
        return local_bridge

    raise BridgeNotFoundError(
        f"garex-bridge executable not found. Expected at {pkg_bridge}. "
        "Run 'python tools/fetch_bridge.py' to obtain pre-built bridge files."
    )


class BridgeClient:
    """Manages an active bridge process instance over stdio JSON-lines."""

    def __init__(self, bridge_path: Path | None = None) -> None:
        self.bridge_path = bridge_path or find_bridge_exe()
        self._proc: subprocess.Popen[str] | None = None
        self._lock = threading.Lock()
        self._seq = 0
        atexit.register(self.close)

    def _ensure_process(self) -> subprocess.Popen[str]:
        if self._proc is None or self._proc.poll() is not None:
            self._proc = subprocess.Popen(
                [str(self.bridge_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                text=True,
                bufsize=1,  # Line buffered
            )
        return self._proc

    def send_command(self, cmd: str, args: dict[str, Any] | None = None, timeout: float = 30.0) -> Any:
        """Send a JSON-lines command to the bridge and return the parsed result."""
        with self._lock:
            proc = self._ensure_process()
            self._seq += 1
            msg_id = str(self._seq)
            payload = json.dumps({"id": msg_id, "cmd": cmd, "args": args or {}}) + "\n"

            try:
                assert proc.stdin is not None
                proc.stdin.write(payload)
                proc.stdin.flush()
            except (BrokenPipeError, OSError) as ex:
                self.close()
                raise BridgeError("IPC_ERROR", f"Failed to send command to bridge: {ex}") from ex

            # Read response
            try:
                assert proc.stdout is not None
                line = proc.stdout.readline()
                if not line:
                    exit_code = proc.poll()
                    stderr_msg = proc.stderr.read() if proc.stderr else ""
                    self.close()
                    raise BridgeError(
                        "PROCESS_EXITED",
                        f"Bridge process terminated unexpectedly (exit code {exit_code}): {stderr_msg}",
                    )
            except Exception as ex:
                self.close()
                raise BridgeTimeoutError(f"Error reading bridge response: {ex}") from ex

            try:
                resp = json.loads(line)
            except json.JSONDecodeError as ex:
                raise BridgeError("INVALID_RESPONSE", f"Malformed JSON from bridge: {line.strip()}") from ex

            if not resp.get("ok"):
                err = resp.get("error", {})
                code = err.get("code", "UNKNOWN_ERROR")
                msg = err.get("message", "Unknown bridge error")
                self._raise_mapped_error(code, msg)

            return resp.get("result")

    def _raise_mapped_error(self, code: str, msg: str) -> None:
        if code in ("UNSUPPORTED_FORMAT", "UNKNOWN_FORMAT"):
            raise UnsupportedFormatError(msg)
        if code in ("CORRUPT_ARCHIVE", "INVALID_ARCHIVE"):
            raise CorruptArchiveError(msg)
        if code in ("ENCRYPTED_ARCHIVE", "PASSWORD_REQUIRED"):
            raise EncryptedArchiveError(msg)
        if code == "FILE_NOT_FOUND":
            raise FileNotFoundError(msg)
        if code == "ENTRY_NOT_FOUND":
            raise KeyError(msg)
        if code == "UNSAFE_PATH":
            raise UnsafePathError(msg)
        raise BridgeError(code, msg)

    def close(self) -> None:
        """Terminate the bridge process cleanly."""
        with self._lock:
            if self._proc is not None:
                try:
                    if self._proc.poll() is None:
                        assert self._proc.stdin is not None
                        self._proc.stdin.write(json.dumps({"id": "quit", "cmd": "quit", "args": {}}) + "\n")
                        self._proc.stdin.flush()
                        self._proc.wait(timeout=1.0)
                except Exception:
                    self._proc.kill()
                finally:
                    self._proc = None


class BridgeBackend(BaseBackend):
    """Bridge backend implementation interfacing with GARbro C# assemblies."""

    def __init__(self, client: BridgeClient | None = None) -> None:
        self.client = client or BridgeClient()

    def probe(self, path: Path) -> dict[str, Any] | None:
        abs_path = Path(path).resolve()
        res = self.client.send_command("probe", {"path": str(abs_path)})
        if res and res.get("recognized"):
            return res
        return None

    def list_entries(self, path: Path) -> tuple[ArchiveInfo, list[Entry]]:
        abs_path = Path(path).resolve()
        res = self.client.send_command("list", {"path": str(abs_path)})
        info = ArchiveInfo(
            format=res.get("format", ""),
            description=res.get("description", ""),
            count=res.get("count", 0),
            backend="bridge",
        )
        entries = [
            Entry(
                name=e.get("name", ""),
                size=int(e.get("size", 0)),
                packed_size=e.get("packed_size"),
                offset=int(e.get("offset", -1)),
                type=e.get("type", ""),
            )
            for e in res.get("entries", [])
        ]
        return info, entries

    def supported_formats(self) -> list[FormatInfo]:
        res = self.client.send_command("formats")
        formats = []
        for f in res.get("formats", []):
            formats.append(
                FormatInfo(
                    tag=f.get("tag", ""),
                    kind=f.get("kind", ""),
                    description=f.get("description", ""),
                    extensions=tuple(f.get("extensions", [])),
                    can_create=bool(f.get("can_create", False)),
                    status="bridge",
                )
            )
        return formats

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
        abs_path = Path(path).resolve()
        abs_dest = Path(destination).resolve()
        args: dict[str, Any] = {
            "path": str(abs_path),
            "destination": str(abs_dest),
            "convert": convert,
            "image_format": image_format.upper(),
            "audio_format": audio_format.upper(),
        }
        if entry is not None:
            args["entry"] = entry
        if scheme is not None:
            args["scheme"] = scheme
        return self.client.send_command("extract", args)

    def convert_image(
        self,
        path: Path,
        destination: Path,
        format: str = "PNG",
    ) -> dict[str, Any]:
        abs_path = Path(path).resolve()
        abs_dest = Path(destination).resolve()
        args = {
            "path": str(abs_path),
            "destination": str(abs_dest),
            "format": format.upper(),
        }
        return self.client.send_command("convert_image", args)

    def convert_audio(
        self,
        path: Path,
        destination: Path,
        format: str = "WAV",
    ) -> dict[str, Any]:
        abs_path = Path(path).resolve()
        abs_dest = Path(destination).resolve()
        args = {
            "path": str(abs_path),
            "destination": str(abs_dest),
            "format": format.upper(),
        }
        return self.client.send_command("convert_audio", args)

    def create_archive(
        self,
        path: Path,
        files: list[str],
        base_dir: Path | None = None,
        format: str | None = None,
    ) -> dict[str, Any]:
        abs_path = Path(path).resolve()
        args: dict[str, Any] = {
            "path": str(abs_path),
            "files": files,
        }
        if base_dir is not None:
            args["base_dir"] = str(Path(base_dir).resolve())
        if format is not None and format.lower() != "auto":
            args["format"] = format.upper()
        return self.client.send_command("create", args)

