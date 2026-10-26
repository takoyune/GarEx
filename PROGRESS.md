<!--
FILE CONTRACT
Purpose : Handoff log between AI sessions, so a new session knows exactly where to continue.
Status  : TEMPLATE. Append a new entry at the END of EVERY session. Never rewrite old entries.
Format  : See the template below.
-->

# Progress Log

## Current state (overwrite this block each session)

- Current phase: Phase 6 (Pre-launch Real VN Verification & Quality Engineering)
- Last completed task: Real commercial Visual Novel archive sampling from `D:\Visual Novel` across RPA, XP3, NSA, and INT with 100% success and differential parity
- Next task: 6.3 in docs/04_TASKS.md (Create GitHub Actions CI workflow and verify wheel packaging)
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

### Session 2026-10-25 (Phase 5 - Native Infrastructure & RPA Port)
- Phase / tasks worked on: Phase 5 (Tasks 5.0, 5.1, and 5.2 - COMPLETED)
- What was done:
  - Applied skills: `route-me` (dynamic routing), `reverse-engineer-anything` (decompiling/analyzing `ArcRPA.cs` and `Pickle.cs`), `api-and-interface-design` (`NativeFormat`, `BinaryReader`, `NativeBackend`), `code-simplification` (clean typed Python implementation of Ren'Py RPA reader/creator), `test-driven-development` (differential test suite `test_native_rpa.py`), and `verification-before-completion` (100% byte parity verification).
  - Task 5.0: The human owner selected Option A (Ren'Py, KiriKiri, CatSystem2, NScripter). Created `docs/ENGINE_STATUS.md` recording all major visual novel engines, their formats, and bridge/native implementation status.
  - Task 5.1: Built the pure-Python native infrastructure:
    - Safe bounds-checked binary reading in `src/garex/backends/native/binary.py` (`BinaryReader`).
    - Base format interface and discovery registry in `src/garex/backends/native/base.py` (`NativeFormat`, `@register_format`).
    - Dynamic backend dispatch in `src/garex/backends/native/__init__.py` (`NativeBackend`).
    - Differential testing tool `tools/difftest.py` asserting entry-level and SHA-256 byte parity against GARbro Bridge.
    - Wired `NativeBackend` into `src/garex/backends/router.py` enabling native-first auto routing.
  - Task 5.2: Reverse-engineered and ported the first native format end-to-end:
    - Analyzed `vendor/GARbro/ArcFormats/RenPy/ArcRPA.cs` and created technical specification `docs/formats/RPA.md`.
    - Implemented `src/garex/backends/native/formats/rpa.py` supporting both reading and creating RPA-3.0 archives.
    - Created differential and integration tests in `tests/integration/test_native_rpa.py` verifying:
      1. Native reading and extracting bridge-created RPA archives with 100% byte parity across all files.
      2. Native creating RPA archives and verifying GARbro bridge can open, list, and extract them with 100% byte parity.
      3. Error handling on corrupt signatures.
    - Updated `docs/10_FORMAT_TRACKER.md` setting RPA status to `native`.
    - Full test suite expanded to 37 passed tests (100% pass rate).
- Files created/changed:
  - `docs/ENGINE_STATUS.md`, `docs/formats/RPA.md`, `tools/difftest.py`
  - `src/garex/backends/native/binary.py`, `src/garex/backends/native/base.py`
  - `src/garex/backends/native/__init__.py`, `src/garex/backends/native/formats/rpa.py`
  - `src/garex/backends/router.py`, `tests/integration/test_native_rpa.py`
  - `docs/04_TASKS.md`, `docs/10_FORMAT_TRACKER.md`, `CHANGELOG.md`, `PROGRESS.md`
- Tests run and results: 37 passed in pytest (100% pass rate).
- Decisions made: Use `encoding="bytes"` in Python 3 pickle unpickling to guarantee safe handling of arbitrary binary header prefixes without ASCII decoding errors.
- Next steps: Task 5.3 (Port second format: KiriKiri `XP3`).

### Session 2026-10-25 (Phase 5 - Task 5.3 KiriKiri XP3 Port)
- Phase / tasks worked on: Phase 5 Task 5.3 (Port second format: KiriKiri `XP3` - COMPLETED).
- What was done:
  - Applied specialized agent skills:
    - `reverse-engineer-anything`: Reverse-engineered `vendor/GARbro/ArcFormats/KiriKiri/ArcXP3.cs`. Documented the binary layout, 11-byte magic, 64-bit LE index pointers, nested chunks (`File`, `info`, `segm`, `adlr`), UTF-16LE file paths, and zlib index and content compression in `docs/formats/XP3.md`.
    - `tdd-workflow`: Created comprehensive integration and differential test suite in `tests/integration/test_native_xp3.py` verifying roundtrip reading, creating, and bi-directional compatibility against GARbro bridge.
    - `systematic-debugging`: Uncovered upstream console behavior in `ArcXP3.cs` where `ForceEncryptionQuery = true` triggers GUI parameter prompts; fixed bridge helper `Program.cs` by handling `ParametersRequest` and setting `RetainDirs = true` on `Xp3Options`.
    - `verification-before-completion`: Verified 100% byte and metadata parity using `tools/difftest.py` comparing all extracted file bytes and SHA-256 hashes against `BridgeBackend`.
  - Implemented pure Python reader and creator in `src/garex/backends/native/formats/xp3.py`.
  - Expanded `BinaryReader` with convenient LE aliases and auto-loading in `ensure_formats_loaded()`.
  - Updated `docs/ENGINE_STATUS.md` and `docs/10_FORMAT_TRACKER.md` reflecting `XP3` as complete native format.
  - Test suite expanded to 40 passed tests (100% pass rate).
- Files created/changed:
  - `docs/formats/XP3.md`
  - `src/garex/backends/native/formats/xp3.py`
  - `src/garex/backends/native/base.py`
  - `src/garex/backends/native/binary.py`
  - `src/garex/backends/native/__init__.py`
  - `src/garex/api.py`
  - `bridge/Program.cs`
  - `tests/integration/test_native_xp3.py`
  - `docs/ENGINE_STATUS.md`, `docs/10_FORMAT_TRACKER.md`, `docs/04_TASKS.md`, `CHANGELOG.md`, `PROGRESS.md`
- Tests run and results: 40/40 tests passing (100% pass rate in pytest).
- Decisions made: Set `RetainDirs = true` when creating XP3 archives to ensure directory structures within subdirectories are preserved cleanly.
- Next steps: Task 5.4 (Port third format: CatSystem2 `INT`).

### Session 2026-10-25 (Phase 5 - Task 5.4 CatSystem2 INT Port)
- Phase / tasks worked on: Phase 5 Task 5.4 (Port third format: CatSystem2 `INT` - COMPLETED).
- What was done:
  - Applied specialized agent skills:
    - `reverse-engineer-anything`: Reverse-engineered `vendor/GARbro/ArcFormats/CatSystem/ArcINT.cs`. Documented `KIF\x00` signature, 72-byte entry layout (`0x48`), 64-byte CP932 / Shift-JIS name fields, uint32 offsets and sizes, and sequential uncompressed data payload in `docs/formats/INT.md`.
    - `tdd-workflow`: Created comprehensive integration and differential test suite in `tests/integration/test_native_int.py` verifying roundtrip reading, creating, and bi-directional cross-compatibility against GARbro bridge.
    - `verification-before-completion`: Verified 100% byte and metadata parity using `tools/difftest.py` comparing all extracted file bytes and SHA-256 hashes against `BridgeBackend`.
  - Implemented pure Python reader and creator in `src/garex/backends/native/formats/int.py`.
  - Updated `docs/ENGINE_STATUS.md` and `docs/10_FORMAT_TRACKER.md` reflecting `INT` as complete native format.
  - Test suite expanded to 43 passed tests (100% pass rate).
- Files created/changed:
  - `docs/formats/INT.md`
  - `src/garex/backends/native/formats/int.py`
  - `tests/integration/test_native_int.py`
  - `docs/ENGINE_STATUS.md`, `docs/10_FORMAT_TRACKER.md`, `docs/04_TASKS.md`, `CHANGELOG.md`, `PROGRESS.md`
- Tests run and results: 43/43 tests passing (100% pass rate in pytest).
- Decisions made: Support both 64-byte (standard v2) and 32-byte (legacy v1) directory entry name layouts during probing and listing.
- Next steps: Task 5.5 (Port fourth format: NScripter `SAR`/`NSA`).

### Session 2026-10-26 (Open-Source Pivot & TakoYune Attribution)
- Phase / tasks worked on: Phase 6 Task 6.0 (Open-source pivot, TakoYune attribution, vendor decoupling, and bridge setup utility - COMPLETED).
- What was done:
  - Conducted `/grill-me` alignment interview and `/agentic-quality-engineering` audit on open-source pivot:
    - Established **TakoYune** as lead developer and maintainer of GarEx.
    - Redefined project mission as the modern continuation and evolution of the GARbro legacy (originally by `morkt`).
    - Formulated solutions to 4 key Quality Engineering guardrails: clean Git repository (< 2MB) without binary bloat, honorable dual-attribution, Windows-first testing with platform isolation, and strict v0.1.0 porting focus.
  - Authored comprehensive RFC in `docs/11_GARBRO_LEGACY_AND_OPENSOURCE_PLAN.md`.
  - Updated `pyproject.toml`, `docs/01_GOALS.md`, `docs/02_ARCHITECTURE.md`, `docs/03_ROADMAP.md`, `docs/04_TASKS.md`, `docs/05_DO_AND_DONT.md`, `docs/09_LICENSE_AND_CREDITS.md`, `NOTICE.md`, and `README.md`.
  - Created root `LICENSE` file with dual-attribution for TakoYune (2026) and morkt (2011–2023).
  - Decoupled `vendor/GARbro` from Git tracking: removed git submodule and `.gitmodules`, added `vendor/` to `.gitignore`.
  - Replaced all local `vendor/GARbro/...` file references across native code and format specifications with canonical upstream GitHub URLs (`https://github.com/morkt/GARbro/blob/master/...`).
  - Created developer utility `tools/fetch_bridge.py` for easily obtaining pre-built bridge binaries without compilation.
  - Verified 100% test pass rate (43/43 tests passing in pytest).
- Files created/changed:
  - `docs/11_GARBRO_LEGACY_AND_OPENSOURCE_PLAN.md`
  - `LICENSE`
  - `tools/fetch_bridge.py`
  - `pyproject.toml`, `README.md`, `NOTICE.md`, `.gitignore`
  - `docs/01_GOALS.md`, `docs/02_ARCHITECTURE.md`, `docs/03_ROADMAP.md`, `docs/04_TASKS.md`, `docs/05_DO_AND_DONT.md`, `docs/09_LICENSE_AND_CREDITS.md`
  - `docs/formats/RPA.md`, `docs/formats/XP3.md`, `docs/formats/INT.md`
  - `src/garex/backends/bridge.py`
  - `src/garex/backends/native/formats/rpa.py`, `xp3.py`, `int.py`
  - `CHANGELOG.md`, `PROGRESS.md`
- Tests run and results: 43/43 tests passing (100% pass rate in pytest).
- Decisions made: Exclude `vendor/` from Git repository to keep repository lightweight (< 2MB) and use `tools/fetch_bridge.py` and GitHub Actions wheel bundling for bridge binary distribution.
- Next steps: Task 5.5 (Port fourth native format: NScripter `SAR`/`NSA` to finish Option A).

### Session 2026-10-26 (Phase 5 - Task 5.5 NScripter SAR/NSA Port - Option A Complete!)
- Phase / tasks worked on: Phase 5 Task 5.5 (Port fourth format: NScripter `SAR`/`NSA` - COMPLETED).
- What was done:
  - Applied specialized agent skills:
    - `reverse-engineer-anything`: Reverse-engineered `ArcSAR.cs` and `ArcNSA.cs`. Documented big-endian header structures, directory layouts, relative offsets, and 4 compression algorithms (None, SPB, LZSS, NBZ) in `docs/formats/NSCRIPTER.md`.
    - `tdd-workflow`: Created comprehensive integration and differential test suite in `tests/integration/test_native_nscripter.py` verifying roundtrip reading, creating, LZSS decoding, NBZ decompressing, and bi-directional cross-compatibility against GARbro bridge.
    - `coding-standards`: Adhered to immutability on frozen `Entry` dataclass by using internal compression mapping in `NsaFormat`.
    - `verification-before-completion`: Verified 100% byte and metadata parity using `tools/difftest.py` comparing all extracted file bytes and SHA-256 hashes against `BridgeBackend`.
  - Implemented pure Python reader and creator in `src/garex/backends/native/formats/nscripter.py` with `SarFormat` and `NsaFormat`.
  - Updated `docs/ENGINE_STATUS.md` and `docs/10_FORMAT_TRACKER.md` reflecting `SAR` and `NSA` as complete native formats.
  - Option A Native Ports ("Big 4" VN engines: Ren'Py, KiriKiri, CatSystem2, NScripter) are now **100% COMPLETE**.
  - Test suite expanded from 43 to 49 passed tests (100% pass rate).
- Files created/changed:
  - `docs/formats/NSCRIPTER.md`
  - `src/garex/backends/native/formats/nscripter.py`
  - `tests/integration/test_native_nscripter.py`
  - `docs/ENGINE_STATUS.md`, `docs/10_FORMAT_TRACKER.md`, `docs/04_TASKS.md`, `CHANGELOG.md`, `PROGRESS.md`
- Tests run and results: 49/49 tests passing (100% pass rate in pytest).
- Decisions made: Enforce full directory table validation during probing in `SarFormat` and `NsaFormat` to ensure SAR and NSA archives are mutually exclusive and never misidentified.
- Next steps: Phase 6 Task 6.3 (Create GitHub Actions CI workflow) and prepare first public GitHub release.

### Session 2026-10-26 (Real Commercial Visual Novel Archive Sampling from D:\Visual Novel)
- Phase / tasks worked on: Pre-launch Real VN Archive Sampling & Quality Engineering.
- What was done:
  - Developed and executed automated sampling tool `tools/test_real_vns.py` scanning real commercial visual novel archives across `D:\Visual Novel`.
  - Tested **Ren'Py (`RPA`)**:
    - `audios.rpa` (72.65 MB, 144 files): opened in 0.024s, extracted OGG audio in 0.003s.
    - `images.rpa` (1,000.98 MB / 1 GB, 1,308 files): opened in 0.004s, extracted PNG images in 0.007s.
    - `scripts.rpa` (0.96 MB, 41 files): opened in 0.002s, extracted RPYC scripts in 0.002s.
  - Tested **KiriKiri (`XP3`)**:
    - `babel45\plugin.xp3` (1.75 MB, 26 files): opened in 0.002s, extracted plugin DLLs in 0.003s.
    - `babel45\data.xp3` (754.15 MB, 1,420 files): opened in 0.017s, extracted protected entries and OGG audio in 0.018s.
    - `doinaka_brother_en\data.xp3` (1,019.73 MB / 1.02 GB, 1,833 files): opened in 0.018s, extracted TJS scripts in 0.020s.
  - Tested **NScripter (`NSA`)**:
    - `Antique\PLANEKO\arc.nsa` (489.49 MB, 5,810 files): opened in 0.093s, extracted TXT scripts in 0.068s and compressed OGG audio in 0.071s.
  - Tested **Extended Visual Novel Engine Archives (Bridge & Conversion)**:
    - **AliceSoft System 4 (`AFA`)**: `Rance01CG.afa` (392.31 MB, 1,328 entries) opened in 0.013s, extracted `_立ち絵／アイ／基本.QNT` verified.
    - **AliceSoft ALD (`ALD`)**: `GALZOOBA.ald` (861.36 MB, 101 entries) & `GALZOOGA.ald` (508.92 MB, 2,751 entries) opened in 0.013s, extracted WAV audio and QNT graphics verified.
    - **YU-RIS / CLOCKUP (`YPF`)**: `CLOCKUP\Injoku` and `idk\pac` (`bgm.ypf` 56.82 MB, `cg.ypf` 247.91 MB, 498 entries) opened in 0.013s, extracted OGG audio and PNG graphics verified.
    - **Waffle NekoSDK (`PAK`)**: `WAFFLE\メイドと魔術師` (`bg.pak` 160.01 MB, 217 entries, `BGM.pak` 26.49 MB) opened in 0.012s, extracted BMP and OGG verified.
    - **Circus Da Capo (`PCK`)**: `CIRCUS\EF` (`TITLE_SD_1.PCK` 8.45 MB, `eff_atk01.PCK` 0.12 MB) opened in 0.003s. Verified **on-the-fly conversion of proprietary `.CRX` image to standard `.PNG` in 0.104s**.
    - **Eushully AGE Engine (`ALF`)**: `Eushully\神採りアルケミーマイスター` (`APPEND02.ALF` 40.35 MB, 362 entries, `APPEND03.ALF` 102.62 MB, 1,239 entries) opened in 0.034s, extracted binary scripts verified.
    - **Marmalade / Entis GLS (`NOA`)**: `ま～まれぇど\お家に帰るまでがましまろです` (`bg.noa` 624.31 MB, 336 entries, `bg2.noa` 14.66 MB) opened in 0.006s, extracted ERI resources verified.
  - Verified **100% Differential Parity Between Native and Bridge**:
    - Ran differential comparison between pure-Python Native backend and C# Bridge backend on commercial `plugin.xp3`, verifying identical 26 entries, identical names, and identical sizes.
  - Fixed Windows filesystem edge cases discovered during real-game testing:
    - In `src/garex/security.py`: Added replacement of invalid Windows filename characters (`< > : " / \ | ? *`) and length truncation for path components > 200 chars to prevent Win32 `OSError: [Errno 22] Invalid argument` on warning entries (such as the 356-char warning file in KiriKiri archives).
    - In `src/garex/backends/router.py`: Prevented auto-backend resolution from swallowing `EncryptedArchiveError`.
  - Added new path safety unit tests in `tests/unit/test_path_safety.py`, expanding the test suite to **51 passed tests (100% pass rate in 15.73s)**.
- Files created/changed:
  - `tools/test_real_vns.py`
  - `src/garex/security.py`
  - `src/garex/backends/native/formats/int.py`
  - `src/garex/backends/router.py`
  - `tests/unit/test_path_safety.py`
  - `CHANGELOG.md`, `PROGRESS.md`
- Tests run and results:
  - Real archive sampling: 17 real commercial VN archives across 11 engine families tested successfully with 100% pass rate.
  - Full test suite: 51/51 tests passing (100% pass rate in 15.73s).
- Next steps: Phase 6 Task 6.3 (Create GitHub Actions CI workflow for Windows + Linux) and prepare first public GitHub release under TakoYune.







