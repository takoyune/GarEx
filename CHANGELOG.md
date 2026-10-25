<!--
FILE CONTRACT
Purpose : User-facing change history (Keep a Changelog format, SemVer).
Status  : TEMPLATE. Agent adds entries under "Unreleased" as features land.
-->

# Changelog

## [Unreleased]
### Added
- Git repository initialized for GarEx root workspace (Phase 0 Task 0.1).
- Pinned upstream GARbro as a git submodule in `vendor/GARbro` at commit `b09ee4570ccb1daf6ac56710ee8934dc0b8baeb0` (Phase 0 Task 0.2).
- Upstream GARbro MIT license copied to `licenses/LICENSE-GARbro.txt`.
- Mandatory toolchain section added to `AGENT_INSTRUCTIONS.md` defining 11 specialized agent skills (including `reverse-engineer-anything`, `tdd-workflow`, `verification-before-completion`, `systematic-debugging`, `code-simplification`, and more).
- Automated build pipeline `tools/build_upstream.ps1` and non-intrusive MSBuild overrides `tools/build_overrides.targets` (Phase 0 Task 0.4).
- Comprehensive Windows upstream build guide `docs/BUILDING_UPSTREAM.md` (Phase 0 Task 0.3).
- Format inventory tools `tools/export_inventory.ps1` and `tools/format_inventory.py` discovering 831 formats (Phase 0 Task 0.7).
- Generated format tracker `docs/10_FORMAT_TRACKER.md` with 831 format records.
- ADR-004 decision record: subprocess JSON-lines helper bridge over `pythonnet` (`DECISIONS.md`).
- C# helper executable bridge `garex-bridge.exe` referencing upstream GameRes & ArcFormats (`bridge/Program.cs`).
- Python core models and typed exceptions (`src/garex/models.py`, `src/garex/errors.py`).
- IPC bridge client with process lifecycle management (`src/garex/backends/bridge.py`).
- Router architecture supporting auto fallback between native and bridge backends (`src/garex/backends/router.py`).
- Public API `open_archive`, `Archive`, and `supported_formats` (`src/garex/api.py`).
- CLI tool `garex list`, `garex formats`, and `garex extract` (`src/garex/cli.py`).
- Path safety and directory traversal / Zip-Slip sanitization (`src/garex/security.py`).
- Archive extraction engine supporting single entry and bulk extraction with progress tracking (`Archive.extract`, `Archive.extract_all`).
- Comprehensive unit and integration test suite with 21 tests passing at 100% pass rate (`tests/`).
- Bridge commands `convert_image` and `convert_audio` supporting 293 image formats and 63 audio formats (`bridge/Program.cs`).
- On-the-fly conversion of visual novel images to PNG and audio to WAV during archive extraction (`Archive.extract(convert=True)`, `Archive.extract_all(convert=True)`).
- Public standalone conversion API functions `convert_image` and `convert_audio` in `src/garex/api.py`.
- CLI command `garex convert <file> -o <output>` and `garex extract --convert` flag in `src/garex/cli.py`.
- Integration tests in `tests/integration/test_convert.py` expanding test suite to 27 tests passing at 100% pass rate.
- Inventory of 19 creatable archive formats verified in upstream GARbro (`XP3`, `INT`, `SAR`, `NSA`, `RPA`, `YPF`, `YKC`, `ZIP`, `MAJIRO`, `NPK`, `NPA`, `NPA-SG`, `ARC/Will`, `ARC/WillV2`, `AMI`, `XFL`, `PD`, `DAT/EGO/1`, `PAK/HyPack`) (Phase 4 Task 4.1).
- Bridge command `create` in `bridge/Program.cs` supporting atomic archive creation and error handling (Phase 4 Task 4.2).
- Public archive creation API `garex.create_archive` accepting directory trees, file sequences, or entry mappings (Phase 4 Task 4.3).
- Safe copy-modify-write repacking API `garex.replace_entries`, strictly prohibiting in-place mutation of original archives (Phase 4 Task 4.3).
- Integration test suite `tests/integration/test_roundtrip.py` with 7 tests verifying roundtrip creation, extract-modify-repack, Ren'Py RPA format, and safe error handling (Phase 4 Task 4.4).
- CLI command `garex create <archive> <inputs...> [--format TAG] [--base-dir DIR]` in `src/garex/cli.py` (Phase 4 Task 4.5).
- Test suite expanded to 34 tests passing at 100% pass rate.

### Changed
- Updated `vendor/README.md` recording pinned commit details.
- Updated `docs/06_FORMAT_PORTING_GUIDE.md` integrating reverse-engineering and TDD skills into the format porting steps.
- Updated `reference/GARBRO_REPO_MAP.md` filling all verified repository facts and answering architectural questions (Phase 0 Task 0.5).
- Updated `docs/02_ARCHITECTURE.md` with answers regarding format discovery (MEF), encryption/scheme storage (`Formats.dat`), WPF dependencies, and archive sizes (Phase 0 Task 0.6, 0.8).
- Updated `docs/03_ROADMAP.md`, `docs/04_TASKS.md`, and `PROGRESS.md` reflecting completed status for Phase 0, Phase 1, Phase 2, Phase 3, and Phase 4.
- Updated `bridge/README.md` reflecting fully implemented bridge commands (`probe`, `list`, `formats`, `extract`, `convert_image`, `convert_audio`, `create`) and documenting build instructions.

