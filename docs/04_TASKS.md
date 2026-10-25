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
- [ ] 0.9 Ask the human to provide sample files per format (or confirm synthetic test generation). Record answer in PROGRESS.md.

## Phase 1 - Bridge + open/list
- [ ] 1.1 Bridge spike for ADR-004: implement `list` via helper exe AND via pythonnet; measure; decide; write ADR.
- [ ] 1.2 Implement `/bridge` C# project (references unmodified upstream assemblies) with commands `probe`, `list`, `formats`.
- [ ] 1.3 Implement `src/garex/backends/bridge.py` (process management, JSON-lines protocol, timeouts, error mapping).
- [ ] 1.4 Implement `models.py`, `errors.py`, `api.py` (`open_archive`, `Archive`, `supported_formats`).
- [ ] 1.5 Implement backend router with `backend="auto|bridge|native"`.
- [ ] 1.6 Write tests (see 08_TESTING.md): unit tests with a fake bridge + integration tests with real bridge.
- [ ] 1.7 Build wheel containing the bridge exe + upstream DLLs + license files; test install in a clean venv.
- [ ] 1.8 Minimal CLI: `garex list <file>`.

## Phase 2 - Extract
- [ ] 2.1 Bridge command `extract` (single + all), with progress events.
- [ ] 2.2 API: `Archive.extract`, `extract_all`, progress callback, cancellation.
- [ ] 2.3 Security: reject entry names that escape the destination (`..`, absolute paths, drive letters).
- [ ] 2.4 Handle encrypted archives: how upstream asks for a scheme/title; expose as `scheme=` parameter.
- [ ] 2.5 Tests + CLI `garex extract`.

## Phase 3 - Convert image/audio
- [ ] 3.1 Inventory convertible formats from upstream (image + audio) into the tracker.
- [ ] 3.2 Bridge commands `convert_image`, `convert_audio`.
- [ ] 3.3 API functions + `extract_all(convert=True)`.
- [ ] 3.4 Tests comparing output hashes/pixels against upstream outputs.
- [ ] 3.5 CLI `garex convert`.

## Phase 4 - Create / repack
- [ ] 4.1 Inventory which formats upstream can create.
- [ ] 4.2 Bridge command `create`.
- [ ] 4.3 API `create_archive`, plus helper to replace files inside an existing archive (copy-modify-write, never in place on the original).
- [ ] 4.4 Round-trip tests.
- [ ] 4.5 CLI `garex create`.

## Phase 5 - Native ports (repeat per format)
- [ ] 5.0 Ask the owner for the priority list of formats/engines.
- [ ] 5.1 Build native infrastructure: `backends/native/base.py`, registry, binary reader helpers, differential test harness `tools/difftest.py`.
- [ ] 5.2 Port first format end-to-end as a reference implementation (pick simplest from the tracker).
- [ ] 5.n Port further formats. One task per format; link to tracker row.

## Phase 6 - Release hardening
- [ ] 6.1 Docs/README quickstart verified on a clean machine.
- [ ] 6.2 Versioning scheme (SemVer) + CHANGELOG.
- [ ] 6.3 TestPyPI upload and install test.
- [ ] 6.4 License/credits audit.
- [ ] 6.5 PyPI release (owner must approve).
