<!--
FILE CONTRACT
Purpose : Defines WHAT GarEx is, what success looks like, author attribution, and project scope.
Status  : ACTIVE. Updated with owner approval for Open-Source Pivot and GARbro legacy continuation.
-->

# Goals & Vision

## 1. Project Identity & Attribution
* **Project Name**: GarEx (Game Archive Extractor & Repacker)
* **Lead Developer & Maintainer**: **TakoYune**
* **Project Heritage**: Modern open-source successor and continuation of **GARbro** (originally created by `morkt`, 2011–2023).
* **License**: MIT License (preserving open-source freedom and upstream copyright attribution).
* **Repository**: Public GitHub Repository (`https://github.com/TakoYune/GarEx`) & PyPI (`pip install garex`).

---

## 2. Vision: Continuing the GARbro Legacy
For over a decade, GARbro served as the definitive tool for visual novel preservation. However, upstream development has ceased, leaving the project tied to a legacy Windows desktop GUI and .NET Framework 4.6.

Under **TakoYune's leadership**, GarEx evolves into the **modern, cross-platform continuation of the GARbro legacy**:
1. **Modern Python-First API & CLI**: Bring visual novel resource extraction, image/audio conversion, and repacking to Python automation, fan-translation pipelines, and game modders.
2. **Dual-Core Architecture**:
   - **Native Core (Pure Python)**: Instant startup, zero dependencies, cross-platform (Windows, Linux, macOS, Steam Deck).
   - **Universal Legacy Bridge**: Fallback access to the 4,000+ classic visual novel formats from upstream GARbro.
3. **Decoupled & Standalone**: Clean Git repository with no submodule bloat; references canonical upstream links directly.

---

## 3. Phased Goals

### Phase A: Core Library & Big 4 Native Engines (v0.1.0 Target - Active)
1. **Pip-Installable Everywhere**: `pip install garex` works out of the box.
2. **Top VN Engines in Pure Python**: Full read/create support for Ren'Py (`RPA`), KiriKiri (`XP3`), CatSystem2 (`INT`), and NScripter (`SAR`/`NSA`) with 100% byte parity against GARbro.
3. **Full Legacy Bridge**: Access to all 4,000+ formats on Windows via `garex-bridge.exe`.
4. **Clean GitHub Repository**: 100% source code in Git (< 2MB); no compiled binaries or submodule bloat in Git history.

### Phase B: Community & Expansion (v0.2.0+ Target)
1. **Modern Game Engines**: Support engines not in classic GARbro (Ren'Py 8 / Python 3, modern KiriKiri Z, Godot VNs, Unity Addressables).
2. **Fan-Translation & Modding Tools**: Specialized CLI commands for dumping text, scripts, and injecting translated dialog.
3. **Community Plugin Architecture**: Allow community contributors to add support for any engine by submitting a single Python file.

---

## 4. Non-Goals (Explicitly Out of Scope)
- Building a desktop GUI (GarEx is focused strictly on Python library and CLI automation).
- Cracking, DRM bypass, or pirating game assets.
- Distributing proprietary or copyrighted game data (all test suites use synthetic fixtures).

---

## 5. Definition of Done (v0.1.0)
- **Feature Done**: Public API (`open_archive`, `extract`, `create`, `convert`) documented and tested.
- **Format Ported**: Pure-Python native implementation passes 100% byte-parity differential testing against GARbro (`tools/difftest.py`).
- **Release Done**: `pip install` works in a clean virtual environment; README quickstart runs without errors.
