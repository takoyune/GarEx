<!--
FILE CONTRACT
Purpose : Handoff log between AI sessions, so a new session knows exactly where to continue.
Status  : TEMPLATE. Append a new entry at the END of EVERY session. Never rewrite old entries.
Format  : See the template below.
-->

# Progress Log

## Current state (overwrite this block each session)

- Current phase: Phase 5 (Native ports)
- Last completed task: 4.5 in docs/04_TASKS.md (Phase 4 COMPLETED)
- Next task: 5.0 in docs/04_TASKS.md (Confirm priority list of formats/engines with owner)
- Blockers / questions for the human: none

## Session entries (append only)

### Session 2026-10-25
- Phase / tasks worked on: Phase 0 (Tasks 0.1 through 0.9 - COMPLETED)
- What was done:
  - Conducted `/grill-me` alignment interview to resolve decisions on upstream cloning target, skill integration scope, and git initialization.
  - Initialized Git repository in GarEx workspace root (Task 0.1).
  - Cloned upstream GARbro as git submodule in `vendor/GARbro` (Task 0.2).
  - Pinned commit `b09ee4570ccb1daf6ac56710ee8934dc0b8baeb0` (2023-10-27) recorded in `vendor/README.md`.
  - Copied upstream LICENSE to `licenses/LICENSE-GARbro.txt`.
  - Integrated 11 mandatory agent skills into `AGENT_INSTRUCTIONS.md` and `docs/06_FORMAT_PORTING_GUIDE.md` (featuring `reverse-engineer-anything`, `tdd-workflow`, `verification-before-completion`, and more).
  - Documented Windows upstream build steps, requirements, and overrides in `docs/BUILDING_UPSTREAM.md` (Task 0.3).
  - Implemented automated build pipeline `tools/build_upstream.ps1` with MSBuild overrides in `tools/build_overrides.targets` (Task 0.4).
  - Built `GameRes.dll`, `ArcFormats.dll`, `Image.Convert.exe`, `GARbro.Console.exe`, and `Formats.dat` without modifying any vendor files (Task 0.4).
  - Read upstream source and filled the verified column and questions in `reference/GARBRO_REPO_MAP.md` (Task 0.5).
  - Documented discovery mechanism (MEF), encryption/scheme storage (`GameData/Formats.dat` via zlib BinaryFormatter `SchemeDataBase`), WPF dependencies (`BitmapSource`), and large archive streaming in `docs/02_ARCHITECTURE.md` (Task 0.6, 0.8).
  - Built inventory exporter `tools/export_inventory.ps1` and tracker generator `tools/format_inventory.py`, indexing 831 formats into `docs/10_FORMAT_TRACKER.md` (Task 0.7).
  - Resolved Task 0.9 with the human owner: the owner confirmed they will provide real visual novel sample files kept outside the repo for differential testing (Task 0.9).
  - Formally closed Phase 0 with all exit criteria satisfied; advanced to Phase 1.
- Files created/changed:
  - `vendor/GARbro` (git submodule added)
  - `vendor/README.md`
  - `licenses/LICENSE-GARbro.txt`
  - `AGENT_INSTRUCTIONS.md`
  - `docs/06_FORMAT_PORTING_GUIDE.md`
  - `docs/04_TASKS.md`
  - `PROGRESS.md`
  - `CHANGELOG.md`
- Tests run and results: Git submodule and commit resolution verified via CLI.
- Decisions made: Alignment via `/grill-me` on submodule destination and 11-skill integration list.
- Open problems: None.
- Next steps: Phase 1 implementation.

### Session 2026-10-25 (Evening)
- Phase / tasks worked on: Phase 1 (Tasks 1.1-1.8) and Phase 2 (Tasks 2.1-2.5) - BOTH COMPLETED
- What was done:
  - Phase 1: Evaluated ADR-004 bridge options (subprocess vs pythonnet); implemented C# helper bridge `garex-bridge.exe` over JSON-lines stdio IPC.
  - Implemented `src/garex/backends/bridge.py`, `models.py`, `errors.py`, `router.py`, `api.py` (`open_archive`, `supported_formats`), and CLI `garex list`.
  - Built distributable wheel `garex-0.1.0-py3-none-any.whl` packaging the compiled bridge and upstream assemblies.
  - Phase 2: Added `extract` command in `bridge/Program.cs` supporting single-entry and bulk extraction.
  - Implemented path traversal / zip-slip security in `src/garex/security.py` (`sanitize_entry_path`) protecting against directory traversal, UNC escapes, and drive overrides.
  - Implemented `Archive.extract(entry, destination)` and `Archive.extract_all(destination, progress_callback)` in `src/garex/api.py`.
  - Added CLI `garex extract <archive> [-o output] [--entry name]`.
  - Added full test suite in `tests/unit/test_path_safety.py` and `tests/integration/test_extract.py`.
  - Verified 100% test pass rate (21/21 tests passing).
- Files created/changed:
  - `bridge/GarexBridge.csproj`, `bridge/Program.cs`
  - `src/garex/security.py`
  - `src/garex/backends/base.py`, `src/garex/backends/bridge.py`
  - `src/garex/api.py`, `src/garex/cli.py`
  - `tests/unit/test_path_safety.py`, `tests/integration/test_extract.py`, `tests/unit/test_router.py`
  - `docs/04_TASKS.md`, `PROGRESS.md`, `CHANGELOG.md`
- Tests run and results: 21 passed in pytest (100% pass rate).
- Decisions made: Handled path traversal prevention in both C# bridge and Python API layer.
- Next steps: Phase 3 (Convert image/audio, tasks 3.1 - 3.5).

### Session 2026-10-25 (Night)
- Phase / tasks worked on: Phase 3 (Convert image/audio, tasks 3.1 - 3.5 - COMPLETED)
- What was done:
  - Applied skills: `reverse-engineer-anything` (decompiling/analyzing `Image.Convert`, `GarExtract`, and `GameRes.AudioFormat` to understand conversion workflows), `api-and-interface-design` (designing clean Python APIs `convert_image`, `convert_audio`, and `extract_all(convert=True)`), `test-driven-development` (synthetic BMP and WAV fixtures), `backend-patterns` (IPC commands `convert_image` and `convert_audio`), and `verification-before-completion` (running full test suite).
  - Verified tracker entries for 293 convertible images and 63 convertible audio formats (Task 3.1).
  - Implemented bridge commands `convert_image` and `convert_audio` in `bridge/Program.cs` utilizing `ImageFormat.Read`/`Write` and `AudioFormat.Read`/`Write` (Task 3.2).
  - Added on-the-fly conversion support during archive extraction in `bridge/Program.cs` and `Archive.extract(convert=True)` / `Archive.extract_all(convert=True)` (Task 3.3).
  - Exported `convert_image` and `convert_audio` in `src/garex/__init__.py` and `src/garex/api.py`.
  - Added CLI `garex convert <file> -o <output>` and `garex extract --convert` in `src/garex/cli.py` (Task 3.5).
  - Implemented 6 new integration tests in `tests/integration/test_convert.py` verifying BMP->PNG conversion, WAV conversion, archive extract with conversion, CLI conversion, and error handling (Task 3.4).
  - Verified 100% test pass rate (27/27 tests passing).
- Files created/changed:
  - `bridge/Program.cs`
  - `src/garex/backends/base.py`, `src/garex/backends/bridge.py`
  - `src/garex/api.py`, `src/garex/__init__.py`, `src/garex/cli.py`
  - `tests/integration/test_convert.py`, `tests/unit/test_router.py`
  - `docs/03_ROADMAP.md`, `docs/04_TASKS.md`, `PROGRESS.md`, `CHANGELOG.md`
- Tests run and results: 27 passed in pytest (100% pass rate).
- Decisions made: Audio conversion defaults to standard PCM WAV; image conversion defaults to PNG with full alpha support.
- Next steps: Phase 4 (Create / repack, tasks 4.1 - 4.5).

### Session 2026-10-25 (Late Night)
- Phase / tasks worked on: Phase 4 (Create / repack, tasks 4.1 - 4.5 - COMPLETED)
- What was done:
  - Applied skills: `route-me` (active router), `reverse-engineer-anything` (analyzing upstream `GarCreate.cs`, `ArchiveFormat.Create`, and creatable format implementations `ArcZIP.cs`, `ArcRPA.cs`, `ArcXP3.cs`, `ArcINT.cs`), `api-and-interface-design` (designing `create_archive` and copy-modify-write `replace_entries` API), `backend-patterns` (IPC `create` command with atomic staging and temp-file safety), `test-driven-development` (TDD Red->Green workflow in `test_roundtrip.py`), and `verification-before-completion` (running all 34 tests across entire test suite).
  - Task 4.1: Confirmed and inventoried all 19 creatable archive formats upstream (`XP3`, `INT`, `SAR`, `NSA`, `RPA`, `YPF`, `YKC`, `ZIP`, `MAJIRO`, `NPK`, `NPA`, `NPA-SG`, `ARC/Will`, `ARC/WillV2`, `AMI`, `XFL`, `PD`, `DAT/EGO/1`, `PAK/HyPack`).
  - Task 4.2: Implemented bridge command `create` in `bridge/Program.cs` supporting target format lookup by tag or extension, relative path resolution, atomic temp file creation, and error reporting. Built `GarexBridge.exe` via `tools/build_bridge.ps1`.
  - Task 4.3: Implemented public API functions in `src/garex/api.py`:
    - `create_archive(path, files, format="auto", backend="auto", base_dir=None)`: supports directory trees, path lists, or mapping dicts.
    - `replace_entries(source_archive, output_archive, replacements, backend="auto")`: enforces copy-modify-write, never mutating the original archive in place.
    - Exported functions in `src/garex/__init__.py`.
  - Task 4.4: Implemented comprehensive round-trip tests in `tests/integration/test_roundtrip.py` (7 tests covering ZIP creation, directory packing, roundtrip replace_entries, Ren'Py RPA format, and error validation).
  - Task 4.5: Added CLI command `garex create <archive> <inputs...> [--format TAG] [--base-dir DIR]` in `src/garex/cli.py`.
  - Updated `bridge/README.md`, `docs/04_TASKS.md`, `docs/03_ROADMAP.md`, `CHANGELOG.md`, and `pyproject.toml` (registered `bridge` pytest marker).
- Files created/changed:
  - `bridge/Program.cs`, `bridge/README.md`
  - `tools/build_bridge.ps1`
  - `src/garex/backends/base.py`, `src/garex/backends/bridge.py`
  - `src/garex/api.py`, `src/garex/__init__.py`, `src/garex/cli.py`
  - `tests/integration/test_roundtrip.py`, `tests/unit/test_router.py`
  - `pyproject.toml`, `docs/04_TASKS.md`, `docs/03_ROADMAP.md`, `CHANGELOG.md`, `PROGRESS.md`
- Tests run and results: 34 passed in pytest (100% pass rate).
- Decisions made: Enforce safe copy-modify-write workflow preventing accidental corruption of original visual novel archives.
- Next steps: Phase 5 (Native ports, tasks 5.0 - 5.n).


