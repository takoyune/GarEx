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

### Changed
- Updated `vendor/README.md` recording pinned commit details.
- Updated `docs/06_FORMAT_PORTING_GUIDE.md` integrating reverse-engineering and TDD skills into the format porting steps.
- Updated `reference/GARBRO_REPO_MAP.md` filling all verified repository facts and answering architectural questions (Phase 0 Task 0.5).
- Updated `docs/02_ARCHITECTURE.md` with answers regarding format discovery (MEF), encryption/scheme storage (`Formats.dat`), WPF dependencies, and archive sizes (Phase 0 Task 0.6, 0.8).
- Updated `docs/04_TASKS.md` and `PROGRESS.md` reflecting completed status for tasks 0.1 through 0.8.
