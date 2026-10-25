<!--
FILE CONTRACT
Purpose : Handoff log between AI sessions, so a new session knows exactly where to continue.
Status  : TEMPLATE. Append a new entry at the END of EVERY session. Never rewrite old entries.
Format  : See the template below.
-->

# Progress Log

## Current state (overwrite this block each session)

- Current phase: Phase 3 (Convert image/audio)
- Last completed task: 2.5 in docs/04_TASKS.md (Phase 2 COMPLETED)
- Next task: 3.1 in docs/04_TASKS.md (Inventory convertible formats from upstream)
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

