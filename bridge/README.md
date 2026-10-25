<!--
FILE CONTRACT
Purpose : Home of the small C# shim ("garex-bridge") that exposes upstream GARbro to Python.
Status  : IMPLEMENTED (Phases 1-4). Speaks JSON lines over stdio.
-->

# bridge/

The `GarexBridge` is a lightweight C# console bridge (`garex-bridge.exe`) that links unmodified upstream GARbro assemblies (`GameRes.dll`, `ArcFormats.dll`) and exposes format operations to Python via standard I/O JSON-lines protocol.

## Implemented Commands

- `ping`: Liveness check and version query.
- `probe`: Probe a file with `FormatCatalog` to detect recognized format tag, kind, and description.
- `list`: Inspect archive headers and return metadata plus directory of entries (`name`, `size`, `offset`, `type`).
- `extract`: Streaming extract of one or all archive entries, with optional on-the-fly conversion of visual novel images and audio.
- `convert_image`: Convert standalone VN images (e.g. BMP/custom) to standard image formats (PNG/JPEG/BMP).
- `convert_audio`: Convert standalone VN audio (e.g. WAV/compressed) to standard audio formats (WAV).
- `create`: Create or repack visual novel game archives (e.g. ZIP, RPA, XP3, INT) from directory trees or file entry lists using copy-modify-write patterns.
- `formats`: Query full catalog of supported archive, image, audio, and script formats.

## Building the Bridge

To compile `garex-bridge.exe`:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_bridge.ps1
```

The compiled binary and its runtime dependencies are copied directly to `src/garex/_bridge/` and bundled inside the `garex` wheel.
