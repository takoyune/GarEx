<!--
FILE CONTRACT
Purpose : Technical design of garex: layers, interfaces, data models, how bridge and native backends coexist.
Status  : DRAFT (skeleton below is the owner-approved direction). Agent REFINES it in Phase 0-1 after reading the real GARbro source; mark every refinement with "(refined YYYY-MM-DD)".
Must end up containing : final class/function signatures, error model, backend selection algorithm, bridge protocol spec.
-->

# Architecture

## Layers

```
user code
   |
garex public API  (src/garex/api.py)           <- stable, typed
   |
Backend router    (src/garex/backends/router.py)
   |-- NativeBackend  (backends/native/*)      <- pure Python, per-format modules
   '-- BridgeBackend  (backends/bridge.py)     <- talks to bundled GARbro C# shim
```

## Public API (draft, refine in Phase 1)

```python
import garex

with garex.open_archive("data.xp3") as arc:       # returns Archive
    for entry in arc.entries():                    # Entry: name, size, packed_size, offset, type
        ...
    arc.extract("script/main.ks", dest="out/")
    arc.extract_all(dest="out/", convert=True)     # convert images/audio to png/wav/ogg etc.

garex.convert_image("in.grp", "out.png")           # phase 3
garex.convert_audio("in.wav2", "out.ogg")          # phase 3
garex.create_archive("out.xp3", files=[...], format="xp3")   # phase 4
garex.supported_formats()                          # list with status native/bridge
```

Rules: context-manager support, `pathlib.Path` accepted everywhere, no global mutable state,
full type hints, typed exceptions (`garex.errors`).

## Data models (`src/garex/models.py`)
`Entry`, `ArchiveInfo`, `FormatInfo`. Dataclasses, frozen where possible.

## Backend router
For a given file: ask NativeBackend `probe(path)`; if a native format claims it, use it.
Else ask BridgeBackend. If neither: raise `UnsupportedFormatError`.
User can force a backend: `garex.open_archive(path, backend="bridge" | "native" | "auto")`.

## Bridge protocol (refine in Phase 1; default = helper exe, see DECISIONS ADR-004)
- Executable `garex-bridge.exe` (built from `/bridge`, references unmodified GARbro DLLs).
- Python spawns it, exchanges **JSON lines** over stdin/stdout.
- Commands (minimum): `probe`, `list`, `extract`, `convert_image`, `convert_audio`, `create`, `formats`.
- Binary payloads are never sent inline; the bridge writes to a temp/target path and returns the path.
- Every response: `{"ok": true, ...}` or `{"ok": false, "error": {"code":..., "message":...}}`.

## Native format module contract
Each native format is one module in `src/garex/backends/native/formats/` exposing a class that
implements `NativeFormat` (see `backends/native/base.py`): `probe`, `open`, `read_entry`,
and optionally `create`. Registered via a registry decorator. Details: `06_FORMAT_PORTING_GUIDE.md`.

## Encryption / game keys
GARbro stores game-specific schemes/keys in its own scheme database. Phase 0 must determine
how it is stored; native ports reuse the same data exported to JSON in `src/garex/data/`.
Do not add keys that are not in upstream GARbro.

## Open questions for Phase 0-1 (agent must answer here)
- Do GARbro DLLs require WPF types for image conversion? (affects bridge design)
- How are formats registered/discovered in upstream (verify the plugin mechanism)?
- How large are real archives? Do we need streaming extraction?
