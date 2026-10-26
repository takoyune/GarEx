<!--
FILE CONTRACT
Purpose : Technical design of GarEx: layers, interfaces, data models, dual-core architecture, and bridge distribution.
Status  : ACTIVE. Updated with owner approval for open-source pivot and decoupled bridge architecture.
-->

# Architecture

## 1. High-Level System Design

GarEx is built on a **dual-core architecture** designed by **TakoYune**:

```
                  +-----------------------------------------------+
                  |          Public API & CLI (src/garex)         |
                  +-----------------------------------------------+
                                          |
                                          v
                  +-----------------------------------------------+
                  |       Backend Router (src/garex/router.py)    |
                  +-----------------------------------------------+
                                   /             \
                   (Probe Match)  /               \  (Fallback)
                                 v                 v
            +---------------------------+   +---------------------------+
            |       NativeBackend       |   |       BridgeBackend       |
            |     (100% Pure Python)    |   |     (Headless C# Shim)    |
            |   Fast, Zero-Dependency   |   |   4,000+ Legacy Formats   |
            +---------------------------+   +---------------------------+
```

---

## 2. Public API (`src/garex/api.py`)

The public interface is modern, typed, context-manager friendly, and accepts `pathlib.Path` or string paths:

```python
import garex

# 1. Open and inspect archive
with garex.open_archive("data.xp3") as arc:
    for entry in arc.entries():
        print(entry.name, entry.size)
    
    # Extract specific file or all files
    arc.extract("scripts/start.ks", dest="unpacked/")
    arc.extract_all(dest="unpacked/", convert=True)  # auto-convert images/audio

# 2. Standalone media conversions
garex.convert_image("cg01.grp", "cg01.png")
garex.convert_audio("bgm01.wav2", "bgm01.ogg")

# 3. Create or repack archives
garex.create_archive("modded.xp3", files=["unpacked/scripts/start.ks"], format="xp3")
```

---

## 3. Backend Coexistence & Router

1. **NativeBackend** (`src/garex/backends/native/`):
   - 100% pure Python using `BinaryReader` and standard libraries (`zlib`, `struct`).
   - Cross-platform: runs anywhere Python 3.10+ runs (Windows, Linux, macOS, Steam Deck, Android).
   - Priority handling: The router probes the native registry first. If a native module claims the format, it extracts or creates with zero subprocess overhead.

2. **BridgeBackend** (`src/garex/backends/bridge.py`):
   - Fallback engine on Windows communicating via JSON-lines RPC over stdio with `garex-bridge.exe`.
   - References `GameRes.dll` and `ArcFormats.dll` to unlock the entire 4,000+ catalog from upstream GARbro.
   - Ground-truth oracle for differential testing (`tools/difftest.py`).

---

## 4. Decoupled Repository & Bridge Distribution Strategy

To keep the open-source GitHub repository lightweight (< 2MB) and eliminate binary bloat:
1. **Source Repository**: Contains 100% clean source code. No compiled `.dll` or `.exe` files and no 150MB `vendor/` submodules in Git history.
2. **For End Users (`pip install garex`)**:
   - GitHub Actions CI compiles the Windows bridge on a Windows runner and packages it directly into the wheel (`garex-0.1.0-py3-none-win_amd64.whl`).
   - Windows users installing via pip get full bridge support out of the box with zero compilation.
3. **For Developers Cloning the Repo**:
   - `python tools/fetch_bridge.py`: 1-line script that downloads the pre-built bridge binaries into `src/garex/_bridge/` in seconds.
   - Developers on Linux/macOS run all Native engines immediately with no bridge files required.

---

## 5. Security & Large Archive Handling
- **Path Sanitization**: All extract operations pass through `sanitize_entry_path` (`src/garex/security.py`), preventing directory traversal (Zip-Slip) attacks, absolute paths, UNC network paths, and drive escapes.
- **Streaming Operations**: Real visual novel archives range from 20MB to 8GB+. All extraction logic operates with chunked streams (64KB to 1MB) to prevent unbounded memory growth.
