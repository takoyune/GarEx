# GarEx (Game Archive Extractor & Repacker)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 100% Pass](https://img.shields.io/badge/tests-43%2F43%20passed-brightgreen.svg)](tests/)

**GarEx** is a modern visual novel resource management library and command-line utility for Python. 

Developed and maintained by **[TakoYune](https://github.com/TakoYune)**, GarEx is the **modern open-source continuation and evolution of [GARbro](https://github.com/morkt/GARbro)** (originally created by `morkt`).

---

## Key Features

* **Python-First API**: Open, browse, extract, convert, and repack visual novel archives in 3 lines of Python.
* **Dual-Core Architecture**:
  * **Native Core (100% Pure Python)**: Zero external dependencies. Instant startup. Fully cross-platform (Windows, Linux, macOS, Steam Deck).
  * **Universal Legacy Bridge**: Fallback access to the complete 4,000+ visual novel engine catalog from classic GARbro.
* **Bit-for-Bit Verified**: Every native format port is verified with automated differential tests asserting 100% SHA-256 byte parity against upstream GARbro.
* **Safe Extraction**: Built-in Zip-Slip and path traversal protection preventing directory escapes.
* **Rich CLI**: Modern command-line interface for listing, extracting, converting, and repacking assets.

---

## Quickstart

### Installation

```bash
pip install garex
```

### Python API

```python
import garex

# 1. Open and browse an archive
with garex.open_archive("data.xp3") as arc:
    for entry in arc.entries():
        print(f"{entry.name} ({entry.size} bytes)")
    
    # Extract specific file or all files
    arc.extract("scripts/start.ks", dest="unpacked/")
    arc.extract_all(dest="unpacked/", convert=True)  # auto-convert images to PNG and audio to WAV

# 2. Standalone image and audio conversion
garex.convert_image("cg01.grp", "cg01.png")
garex.convert_audio("bgm01.wav2", "bgm01.ogg")

# 3. Create or repack archives
garex.create_archive("modded.xp3", files=["unpacked/scripts/start.ks"], format="xp3")
```

### Command Line Interface (CLI)

```bash
# List archive contents
garex list game.xp3

# Extract archive
garex extract game.xp3 -o ./unpacked/

# Extract with automatic image/audio conversion
garex extract game.xp3 -o ./unpacked/ --convert

# Create a new archive
garex create patch.xp3 ./unpacked/scripts/ --format xp3
```

---

## Supported Engines (Native Pure-Python)

| Engine | Format Tag | Extension | Status | Verification |
|:---|:---|:---|:---:|:---:|
| **Ren'Py** | `RPA` | `.rpa` | Complete | 100% Byte Parity |
| **KiriKiri / TVP** | `XP3` | `.xp3` | Complete | 100% Byte Parity |
| **CatSystem2** | `INT` | `.int` | Complete | 100% Byte Parity |
| **NScripter** | `SAR` / `NSA` | `.sar`, `.nsa` | In Queue (Task 5.5) | In Progress |
| **4,000+ Legacy Formats** | *Various* | *Various* | Complete (via Bridge) | Upstream Verified |

For the full catalog of 50+ engine families, see [docs/ENGINE_STATUS.md](docs/ENGINE_STATUS.md).

---

## Credits & Heritage

* **Author & Lead Developer**: **TakoYune** (https://github.com/TakoYune)
* **Heritage**: GarEx is the successor to **[GARbro](https://github.com/morkt/GARbro)**, originally created by **`morkt`** (Copyright © 2011–2023 morkt, MIT License). We extend our deepest gratitude to `morkt` and the GARbro community for over a decade of dedication to visual novel preservation.

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md) for full details.
