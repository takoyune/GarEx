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

### Changed
- Updated `vendor/README.md` recording pinned commit details.
- Updated `docs/06_FORMAT_PORTING_GUIDE.md` integrating reverse-engineering and TDD skills into the format porting steps.
- Updated `docs/04_TASKS.md` and `PROGRESS.md` reflecting completed status for tasks 0.1 and 0.2.
