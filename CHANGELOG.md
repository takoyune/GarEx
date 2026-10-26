<!--
FILE CONTRACT
Purpose : User-facing change history (Keep a Changelog format, SemVer).
Status  : TEMPLATE. Agent adds entries under "Unreleased" as features land.
-->

# Changelog

## [Unreleased]
### Added
- Comprehensive strategic RFC and action plan for transitioning GarEx to open-source GitHub project, establishing TakoYune as lead developer, honoring morkt's original GARbro legacy, resolving bridge distribution without binary bloat, and defining strict v0.1.0 scope (`docs/11_GARBRO_LEGACY_AND_OPENSOURCE_PLAN.md`).
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
- Visual novel engine implementation status tracker in `docs/ENGINE_STATUS.md` recording all supported engines, formats, bridge status, and native status (Task 5.0).
- Pure-Python native infrastructure in `src/garex/backends/native/`: `BinaryReader` with safe bounds-checked reads in `binary.py`, `NativeFormat` base class and format registry in `base.py`, and `NativeBackend` implementing `BaseBackend` (Task 5.1).
- Differential testing tool `tools/difftest.py` comparing native vs bridge metadata and SHA-256 byte parity (Task 5.1).
- Ported first native format end-to-end: Ren'Py (`RPA`) archive decoder and creator in `src/garex/backends/native/formats/rpa.py` with 100% byte parity against GARbro (Task 5.2).
- Technical format specification `docs/formats/RPA.md` based on reverse-engineered upstream source `vendor/GARbro/ArcFormats/RenPy/ArcRPA.cs`.
- Integration and differential tests in `tests/integration/test_native_rpa.py` expanding test suite to 37 tests passing at 100% pass rate.
- Ported second native format: KiriKiri 2 / KAG3 (`XP3`) decoder and creator in `src/garex/backends/native/formats/xp3.py` with 100% byte and metadata parity against GARbro (Task 5.3).
- Technical format specification `docs/formats/XP3.md` based on reverse-engineered `vendor/GARbro/ArcFormats/KiriKiri/ArcXP3.cs`.
- Integration and differential test suite in `tests/integration/test_native_xp3.py` expanding test suite to 40 tests passing at 100% pass rate.
- Ported third native format: CatSystem2 (`INT`) decoder and creator in `src/garex/backends/native/formats/int.py` with 100% byte and metadata parity against GARbro (Task 5.4).
- Technical format specification `docs/formats/INT.md` based on reverse-engineered `vendor/GARbro/ArcFormats/CatSystem/ArcINT.cs`.
- Integration and differential test suite in `tests/integration/test_native_int.py` expanding test suite to 43 tests passing at 100% pass rate.
- Ergonomic aliases added to `BinaryReader`: `read_bytes`, `read_u16`, `read_i16`, `read_u32`, `read_i32`, `read_u64`, `read_i64`.
- Auto-loading of native formats upon any registry access via `ensure_formats_loaded()`.

### Changed
- Updated `vendor/README.md` recording pinned commit details.
- Updated `docs/06_FORMAT_PORTING_GUIDE.md` integrating reverse-engineering and TDD skills into the format porting steps.
- Updated `reference/GARBRO_REPO_MAP.md` filling all verified repository facts and answering architectural questions (Phase 0 Task 0.5).
- Updated `docs/02_ARCHITECTURE.md` with answers regarding format discovery (MEF), encryption/scheme storage (`Formats.dat`), WPF dependencies, and archive sizes (Phase 0 Task 0.6, 0.8).
- Updated `docs/03_ROADMAP.md`, `docs/04_TASKS.md`, `docs/ENGINE_STATUS.md`, and `PROGRESS.md` reflecting completed status for Task 5.3 (XP3) and Task 5.4 (INT).
- Updated `docs/10_FORMAT_TRACKER.md` setting status of `XP3` and `INT` to `native`.
- Updated `bridge/README.md` reflecting fully implemented bridge commands (`probe`, `list`, `formats`, `extract`, `convert_image`, `convert_audio`, `create`) and documenting build instructions.
- Configured `garex.create_archive` to dynamically route creation to `NativeBackend` when a native format with write capability is available.

### Fixed
- Fixed subprocess `PYTHONPATH` inheritance in `test_cli_create` integration test.
- Registered `FormatCatalog.Instance.ParametersRequest` handler in bridge helper to prevent `OperationCanceledException` during parameter queries.
- Configured `RetainDirs = true` on `Xp3Options` in bridge helper to preserve directory structures during XP3 creation.
- Disabled `ForceEncryptionQuery` on `Xp3Opener` for unencrypted archives in bridge helper.

