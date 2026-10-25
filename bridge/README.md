<!--
FILE CONTRACT
Purpose : Home of the small C# shim ("garex-bridge") that exposes upstream GARbro to Python.
Status  : EMPTY PLACEHOLDER. Built in Phase 1 (tasks 1.1-1.2).
-->

# bridge/

WHAT THIS MUST BECOME: a C# project (`GarexBridge.csproj` + sources) that:
- references the UNMODIFIED upstream assemblies built from `vendor/GARbro`;
- builds `garex-bridge.exe`, a console program speaking JSON lines over stdin/stdout (spec in `docs/02_ARCHITECTURE.md`);
- implements commands phase by phase: `probe`, `list`, `formats` (P1) -> `extract` (P2) -> `convert_image`, `convert_audio` (P3) -> `create` (P4);
- never prints anything except protocol messages to stdout (logs go to stderr);
- returns structured errors, never crashes silently.

MUST NOT: contain format logic of its own, modify upstream behavior, or include a GUI.
