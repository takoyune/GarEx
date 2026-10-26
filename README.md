# GarEx

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Steam%20Deck-informational.svg)](https://github.com/TakoYune/GarEx)

**GarEx** is a fast, modern visual novel archive extractor, browser, and repacker for Python and the command line.

It is the open-source continuation of **[GARbro](https://github.com/morkt/GARbro)**, developed and maintained by **[TakoYune](https://github.com/TakoYune)**.

---

## Installation

```bash
pip install garex
```

---

## Quickstart

### Command Line (CLI)

Browse, extract, or repack game archives directly from your terminal:

```bash
# List all files inside an archive
garex list game.xp3

# Extract an archive to a destination folder
garex extract game.xp3 -o ./unpacked/

# Extract only a single specific file
garex extract game.xp3 --entry "scripts/scene01.ks" -o ./unpacked/

# Create or repack an archive from a folder
garex create patch.xp3 ./unpacked_scripts/ --format XP3
```

### Python API

Use GarEx in your Python modding, translation, or asset pipelines:

```python
import garex

# Open and browse any supported archive
with garex.open_archive("game.xp3") as arc:
    print(f"Format: {arc.format} | Files: {len(arc.entries())}")

    # Print first few files
    for entry in arc.entries()[:5]:
        print(f" - {entry.name} ({entry.size:,} bytes)")

    # Extract all files
    arc.extract_all("./output_folder/")
```

Repack or create new archives:

```python
from pathlib import Path
import garex

# Create a new archive from a folder of files
garex.create_archive(
    "patch.xp3",
    files=Path("modded_scripts/"),
    format="XP3",
)
```

---

## Supported Engines & Formats

GarEx supports mainstream visual novel engines natively in pure Python (cross-platform with zero external dependencies), with fallback access to the 800+ legacy format catalog from classic GARbro:

| Engine | Format Tag | Extension | Example Visual Novels |
| :--- | :--- | :--- | :--- |
| **Ren'Py** | `RPA` | `.rpa` | *Doki Doki Literature Club*, *Slay the Princess* |
| **KiriKiri 2 / TVP** | `XP3` | `.xp3` | *Fate/stay night*, *Fate/hollow ataraxia*, *Tsukihime* |
| **NScripter** | `SAR` / `NSA` | `.sar`, `.nsa` | *Higurashi When They Cry*, *Umineko*, *Narcissu* |
| **CatSystem2** | `INT` | `.int` | *Grisaia no Kajitsu* series |
| **AliceSoft** | `AFA`, `ALD` | `.afa`, `.ald` | *Rance* series, *Evenicle*, *Galzoo Island* |
| **CIRCUS** | `PCK` | `.pck` | *D.C. ~Da Capo~* series |
| **YU-RIS** | `YPF` | `.ypf` | *CLOCKUP* visual novels |
| **Eushully** | `ALF` | `.alf` | *Kamidori Alchemy Meister*, AGE Engine titles |
| **Waffle** | `PAK` | `.pak` | *NekoSDK* visual novels |
| **Marmalade** | `NOA` | `.noa` | *Entis GLS* visual novels |
| **800+ Legacy Engines** | *Various* | *Various* | Nitroplus, Leaf, Key/VisualArts, Innocent Grey, and more |

*See [docs/ENGINE_STATUS.md](docs/ENGINE_STATUS.md) for the full engine catalog.*

---

## Credits & Heritage

- **Lead Developer**: **[TakoYune](https://github.com/TakoYune)**
- **Heritage**: GarEx is the open-source continuation of **[GARbro](https://github.com/morkt/GARbro)** by **`morkt`** (Copyright © 2011–2023 morkt, MIT License).

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
