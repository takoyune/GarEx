<!--
FILE CONTRACT
Purpose : Handoff log between AI sessions, so a new session knows exactly where to continue.
Status  : TEMPLATE. Append a new entry at the END of EVERY session. Never rewrite old entries.
Format  : See the template below.
-->

# Progress Log

## Current state (overwrite this block each session)

- Current phase: Phase 1 (Bridge + open/list)
- Last completed task: 0.9 in docs/04_TASKS.md (Phase 0 COMPLETED)
- Next task: 1.1 in docs/04_TASKS.md (Bridge spike for ADR-004)
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
- Next steps: Task 0.3 (document Windows build steps for upstream GARbro in `docs/BUILDING_UPSTREAM.md`).

