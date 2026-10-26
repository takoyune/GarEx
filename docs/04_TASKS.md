<!--
FILE CONTRACT
Purpose : Detailed checklist of tasks per phase. The agent ticks boxes as it works and may ADD sub-tasks (never delete tasks).
Status  : TEMPLATE (checklists pre-filled). Task IDs are stable; reference them in PROGRESS.md.
-->

# Tasks

## Phase 0 - Recon and setup
- [x] 0.1 Create git repo structure; add `.gitignore`; init `pyproject.toml` skeleton (see 07_PACKAGING.md).
- [x] 0.2 Add upstream GARbro to `vendor/GARbro` as a git submodule (or pinned clone); record commit hash in `vendor/README.md`.
- [x] 0.3 Document the Windows build steps for `GameRes`, `ArcFormats`, `Image.Convert`, `Console` (what SDK/Visual Studio/MSBuild is needed). Put in `docs/BUILDING_UPSTREAM.md`.
- [x] 0.4 Build upstream successfully; record any build errors and fixes (without editing vendor files; use build flags/overrides).
- [x] 0.5 Read upstream source and fill the VERIFIED column in `reference/GARBRO_REPO_MAP.md`.
- [x] 0.6 Find how upstream registers formats (plugin discovery) and how game schemes/keys are stored. Answer in `02_ARCHITECTURE.md`.
- [x] 0.7 Write `tools/format_inventory.py` (or C# tool) that lists every archive/image/audio/script format upstream supports; generate `docs/10_FORMAT_TRACKER.md`.
- [x] 0.8 Check whether upstream image conversion requires WPF; document consequences.
- [x] 0.9 Ask the human to provide sample files per format (or confirm synthetic test generation). Record answer in PROGRESS.md.

## Phase 1 - Bridge + open/list
- [x] 1.1 Bridge spike for ADR-004: implement `list` via helper exe AND via pythonnet; measure; decide; write ADR.
- [x] 1.2 Implement `/bridge` C# project (references unmodified upstream assemblies) with commands `probe`, `list`, `formats`.
- [x] 1.3 Implement `src/garex/backends/bridge.py` (process management, JSON-lines protocol, timeouts, error mapping).
- [x] 1.4 Implement `models.py`, `errors.py`, `api.py` (`open_archive`, `Archive`, `supported_formats`).
- [x] 1.5 Implement backend router with `backend="auto|bridge|native"`.
- [x] 1.6 Write tests (see 08_TESTING.md): unit tests with a fake bridge + integration tests with real bridge.
- [x] 1.7 Build wheel containing the bridge exe + upstream DLLs + license files; test install in a clean venv.
- [x] 1.8 Minimal CLI: `garex list <file>`.

## Phase 2 - Extract
- [x] 2.1 Bridge command `extract` (single + all), with progress events.
- [x] 2.2 API: `Archive.extract`, `extract_all`, progress callback, cancellation.
- [x] 2.3 Security: reject entry names that escape the destination (`..`, absolute paths, drive letters).
- [x] 2.4 Handle encrypted archives: how upstream asks for a scheme/title; expose as `scheme=` parameter.
- [x] 2.5 Tests + CLI `garex extract`.

## Phase 3 - Convert image/audio
- [x] 3.1 Inventory convertible formats from upstream (image + audio) into the tracker.
- [x] 3.2 Bridge commands `convert_image`, `convert_audio`.
- [x] 3.3 API functions + `extract_all(convert=True)`.
- [x] 3.4 Tests comparing output hashes/pixels against upstream outputs.
- [x] 3.5 CLI `garex convert`.

## Phase 4 - Create / repack
- [x] 4.1 Inventory which formats upstream can create.
- [x] 4.2 Bridge command `create`.
- [x] 4.3 API `create_archive`, plus helper to replace files inside an existing archive (copy-modify-write, never in place on the original).
- [x] 4.4 Round-trip tests.
- [x] 4.5 CLI `garex create`.

## Phase 5 - Native ports (repeat per format)
- [x] 5.0 Ask the owner for the priority list of formats/engines (Owner selected Option A: Ren'Py, KiriKiri, CatSystem2, NScripter; created docs/ENGINE_STATUS.md).
- [x] 5.1 Build native infrastructure: `backends/native/base.py`, registry, binary reader helpers, differential test harness `tools/difftest.py`.
- [x] 5.2 Port first format end-to-end as a reference implementation (Ported Ren'Py RPA-3.0 in `backends/native/formats/rpa.py`, 100% byte parity verified).
- [x] 5.3 Port second format: KiriKiri (`XP3`) (Pure Python decoder and creator in `backends/native/formats/xp3.py`, 100% byte and metadata parity verified in differential tests against GARbro bridge).
- [x] 5.4 Port third format: CatSystem2 (`INT`) (Pure Python decoder and creator in `backends/native/formats/int.py`, 100% byte and metadata parity verified in differential tests against GARbro bridge).
- [x] 5.5 Port fourth format: NScripter (`SAR`/`NSA`) (Pure Python decoders and creators in `backends/native/formats/nscripter.py` with 100% differential parity against GARbro bridge). Option A 100% complete!
- [ ] 5.n Port further formats. One task per format; link to tracker row.

## Phase 6 - Open-Source Launch & Release Hardening
- [x] 6.0 Open-source pivot RFC approved (`docs/11_GARBRO_LEGACY_AND_OPENSOURCE_PLAN.md`); set TakoYune author and legacy continuation mission.
- [x] 6.1 Decouple `vendor/` from Git tracking; replace code/doc references with canonical upstream GitHub URLs.
- [x] 6.2 Implement `tools/fetch_bridge.py` developer helper script for downloading bridge release assets.
- [ ] 6.3 Add GitHub Actions CI workflow (`.github/workflows/ci.yml`) for automated Windows & Linux testing.
- [ ] 6.4 Docs and README quickstart verified on a clean environment.
- [ ] 6.5 Versioning scheme (SemVer) + CHANGELOG.
- [ ] 6.6 License and credits audit (`licenses/LICENSE-GARbro.txt`, `NOTICE.md`, `README.md`).
- [ ] 6.7 Publish public GitHub repository and PyPI release package.
