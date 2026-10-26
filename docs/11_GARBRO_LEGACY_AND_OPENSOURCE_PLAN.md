<!--
FILE CONTRACT
Purpose : Comprehensive strategic RFC and plan for transitioning GarEx to an Open-Source GitHub project,
          establishing TakoYune as author/lead developer, honoring morkt's original GARbro legacy,
          resolving bridge distribution cleanly without binary bloat, and defining strict v0.1.0 scope.
Status  : APPROVED RFC & ACTION PLAN.
-->

# RFC: GarEx — Open Source Pivot & The Continuation of the GARbro Legacy

## 1. Executive Summary & Author Attribution
* **Project Name**: GarEx (Game Archive Extractor & Repacker)
* **Lead Developer & Maintainer**: **TakoYune**
* **Project Heritage & Attribution**: 
  - GarEx is the modern open-source continuation and evolution of **GARbro**, originally created by **`morkt`** (2011–2023).
  - GarEx honors `morkt`'s pioneering reverse-engineering and preservation work with full attribution across `LICENSE`, `NOTICE.md`, and all documentation.
* **License**: MIT License (preserving open-source freedom for both original and new code).
* **Target Distribution**: Public GitHub Repository (`github.com/TakoYune/GarEx`) & PyPI (`pip install garex`).

---

## 2. Solutions to the 4 Quality Engineering (AQE) Guardrails

### Problem 1 Solution: Clean Git Repo (No Binary Bloat)
* **Decision**: Keep the Git repository 100% source code (< 2MB). Do **not** commit compiled `.dll` and `.exe` binaries into Git history.
* **How it works for regular users (`pip install garex`)**:
  - GitHub Actions CI builds the Windows Wheel (`.whl`) and bundles the compiled bridge assemblies automatically into the release package.
  - End users on Windows simply run `pip install garex` and get 100% full bridge functionality out of the box with zero compilation.
* **How it works for developers cloning the Git repo**:
  - A clean 1-line helper script (`python tools/fetch_bridge.py`) downloads the pre-built bridge release asset in 2 seconds into `src/garex/_bridge/` if needed.
  - Developers on Linux/macOS run all Native engines immediately with zero bridge files needed.

### Problem 2 Solution: Honorable Dual-Attribution
* **Decision**: Clear, transparent, and respectful copyright notices:
  - In `pyproject.toml`: `authors = [{ name = "TakoYune" }]`
  - In `NOTICE.md` and `README.md`:
    > **Credits & Heritage**  
    > GarEx is developed and maintained by **TakoYune**.  
    > This project continues the legacy of **GARbro**, originally created by **`morkt`** (Copyright © 2011–2023 morkt, MIT License). We extend our deepest gratitude to `morkt` and all contributors to the original GARbro project for over a decade of visual novel preservation work.

### Problem 3 Solution: Windows First Testing & Platform Isolation
* **Decision**: Windows remains the primary development and integration test environment.
  - Native tests (`RPA`, `XP3`, `INT`, `SAR`/`NSA`) are 100% cross-platform and run everywhere (Windows, Linux, macOS).
  - Bridge tests are strictly tagged with `@pytest.mark.bridge` and automatically skip gracefully if run in an environment without .NET / Windows bridge assemblies.

### Problem 4 Solution: Strict v0.1.0 Scope (Port First!)
* **Decision**: Avoid premature scope creep. Focus 100% on porting the core library first.
  - **v0.1.0 Milestone**:
    1. Complete the "Big 4" VN engines in Native pure Python (Ren'Py, KiriKiri, CatSystem2, NScripter).
    2. Solidify core Python API (`open_archive`, `extract`, `create`, `list`) and CLI.
    3. Remove `vendor/` submodule and replace references with upstream GitHub links.
    4. First public GitHub release under **TakoYune**.
  - **v0.2.0+ Future Milestones**: Modern engines (Godot/Unity), modding & fan-translation tools, community plugin system.

---

## 3. Decoupling `vendor/` & Link Migration Strategy

* `vendor/` is added to `.gitignore`. The submodule entry in `.gitmodules` is removed.
* All code docstrings and documentation citing `vendor/GARbro/...` are updated to canonical GitHub permalinks:
  `https://github.com/morkt/GARbro/blob/master/...`
* This keeps the repository completely standalone and self-contained.

---

## 4. Master Action Plan for Phase 5 & Open-Source Launch

| Step | Task | Details |
|:---:|:---|:---|
| **Step 1** | **Update Core Docs & pyproject.toml** | Update `01_GOALS.md`, `02_ARCHITECTURE.md`, `03_ROADMAP.md`, `04_TASKS.md`, `NOTICE.md`, `README.md`, and `pyproject.toml` with TakoYune attribution and the legacy continuation mission. |
| **Step 2** | **Decouple `vendor/`** | Remove submodule from `.gitmodules`, add `vendor/` to `.gitignore`, update references in code/docs to upstream GitHub links. |
| **Step 3** | **Add Bridge Fetch Script** | Add `tools/fetch_bridge.py` for repository developers who want to download the pre-built bridge without compiling. |
| **Step 4** | **Task 5.5: Port NScripter (`SAR`/`NSA`)** | Implement pure-Python NScripter decoder and creator in `src/garex/backends/native/formats/nscripter.py` with 100% differential parity. (Completes Option A!). |
| **Step 5** | **Phase 6: Release Hardening** | Verify clean `pip install`, generate distribution wheel, create GitHub Actions CI workflow, and prepare public GitHub release. |
