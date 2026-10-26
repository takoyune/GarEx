<!--
FILE CONTRACT
Purpose : Ordered phases with exit criteria. Defines what "done" means for each phase and release milestones.
Status  : ACTIVE. Updated with owner approval for open-source pivot, TakoYune attribution, and GARbro legacy continuation.
-->

# Roadmap

Rule: Finish a phase completely before starting the next. Detailed checklists are in `04_TASKS.md`.

---

## Phase 0 — Recon & Build  | Status: COMPLETED
Exit criteria: Upstream inventory complete, Windows build steps verified, format tracker generated.

## Phase 1 — Bridge + Open/List  | Status: COMPLETED
Exit criteria: `garex.open_archive()`, `Archive.entries()`, `garex.supported_formats()`, CLI `garex list`.

## Phase 2 — Extract & Safety  | Status: COMPLETED
Exit criteria: `Archive.extract()`, `extract_all()`, Zip-Slip / path traversal protection, CLI `garex extract`.

## Phase 3 — Convert Media  | Status: COMPLETED
Exit criteria: `convert_image()`, `convert_audio()`, and `extract_all(convert=True)` for visual novel images and audio.

## Phase 4 — Create & Repack  | Status: COMPLETED
Exit criteria: `garex.create_archive()`, `garex.replace_entries()`, atomic repack workflow, roundtrip tests passing.

---

## Phase 5 — Native Ports (Option A)  | Status: IN PROGRESS (75% Complete)
Goal: Pure Python implementations of the "Big 4" visual novel engines with 100% byte-parity against GARbro.
- [x] **Task 5.0**: Priority list selected (Option A: Ren'Py, KiriKiri, CatSystem2, NScripter; created `docs/ENGINE_STATUS.md`).
- [x] **Task 5.1**: Native infrastructure (`BinaryReader`, `NativeBackend`, registry, `tools/difftest.py`).
- [x] **Task 5.2**: Port Ren'Py (`RPA`) -> Complete (read + create, 100% parity).
- [x] **Task 5.3**: Port KiriKiri (`XP3`) -> Complete (read + create, 100% parity).
- [x] **Task 5.4**: Port CatSystem2 (`INT`) -> Complete (read + create, 100% parity).
- [ ] **Task 5.5**: Port NScripter (`SAR`/`NSA`) -> **CURRENT TASK** (read + create, 100% parity).

Exit criteria: All 4 engines passing 100% differential byte-parity against GARbro.

---

## Phase 6 — Open-Source Launch & Release Hardening (v0.1.0)  | Status: IN PROGRESS
Goal: Decouple `vendor/`, setup clean GitHub repo, add CI/CD, and release on GitHub & PyPI.
- [x] RFC approved (`docs/11_GARBRO_LEGACY_AND_OPENSOURCE_PLAN.md`).
- [x] Update documentation and `pyproject.toml` with **TakoYune** attribution and legacy continuation mission.
- [ ] Decouple `vendor/` from Git tracking and update references to canonical GitHub URLs.
- [ ] Implement `tools/fetch_bridge.py` developer download script.
- [ ] Create GitHub Actions CI workflow for automated testing on Windows & Ubuntu.
- [ ] Build distribution wheels and verify `pip install` in a clean environment.

---

## Phase 7 — Expansion & Community Ecosystem (v0.2.0+)  | Status: PLANNED
Goal: Expand beyond classic GARbro into modern visual novels and modding pipelines.
- **Modern Engines**: Support Ren'Py 8 / Python 3, modern KiriKiri Z, Godot VNs, and modern Unity Addressables.
- **Fan-Translation & Modding Tools**: Specialized CLI commands for dumping game text and repacking translated assets.
- **Community Plugin Architecture**: Single-file format contributions by the open-source community.
