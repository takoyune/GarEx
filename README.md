<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Steam%20Deck-2ea44f.svg?style=for-the-badge)](https://github.com/TakoYune/GarEx)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg?style=for-the-badge)](tests/)

</div>

<!-- PROJECT HEADER -->
<br />
<div align="center">
  <h1 align="center">GarEx</h1>

  <p align="center">
    <strong>A modern, high-performance visual novel archive extractor, browser, and repacker.</strong>
    <br />
    Pure Python for mainstream engines &middot; 800+ commercial formats via universal bridge
    <br />
    <br />
    <a href="docs/ENGINE_STATUS.md"><strong>Explore Supported Engines »</strong></a>
    <br />
    <br />
    <a href="docs/CONTRIBUTING.md">How to Contribute</a>
    &middot;
    <a href="https://github.com/TakoYune/GarEx/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/TakoYune/GarEx/issues/new?labels=enhancement">Request Format</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li><a href="#installation">Installation</a></li>
    <li>
      <a href="#quickstart">Quickstart</a>
      <ul>
        <li><a href="#command-line-interface-cli">Command Line Interface (CLI)</a></li>
        <li><a href="#python-api">Python API</a></li>
      </ul>
    </li>
    <li><a href="#supported-engines">Supported Engines</a></li>
    <li><a href="#advanced-capabilities">Advanced Capabilities</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#credits--license">Credits & License</a></li>
  </ol>
</details>

---

<!-- ABOUT THE PROJECT -->
## About The Project

Visual novel preservation, translation, and modding often run into proprietary archive formats, platform-locked tools, or discontinued legacy utilities. 

**GarEx** is the open-source continuation of **[GARbro](https://github.com/morkt/GARbro)**, developed and maintained by **[TakoYune](https://github.com/TakoYune)**. It bridges visual novel game archiving with the modern cross-platform Python ecosystem:

- **100% Pure Python** for mainstream visual novel engines (runs everywhere without C extensions or external binaries).
- **Universal Bridge** providing seamless access to the classic 800+ commercial format catalog.
- **On-the-Fly Conversion** for proprietary visual novel images and audio to standard PNG/WAV.
- **Enterprise Path Safety** protecting against Zip-Slip path traversal and invalid filesystem characters.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

### Key Features

- ⚡ **Cross-Platform**: Tested and verified on Windows, Linux, macOS, and Steam Deck.
- 📦 **Read, Extract & Repack**: Browse file tables, extract single entries or entire archives, and create new packages.
- 🖼️ **On-The-Fly Conversion**: Auto-convert proprietary image formats (`.crx`, `.tlg`, `.g00`, `.abm`) to `.png` during extraction.
- 🛡️ **Hardened Security**: Prevents directory traversal (`../../`) and sanitizes Windows-illegal path characters.
- 🎯 **Differential Parity**: Verified byte-for-byte SHA-256 equivalence against upstream GARbro.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Installation

Install GarEx from PyPI:

```bash
pip install garex
```

Or install with development dependencies:

```bash
git clone https://github.com/TakoYune/GarEx.git
cd GarEx
pip install -e ".[dev]"
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Quickstart

### Command Line Interface (CLI)

```bash
# List all files inside an archive
garex list game.xp3

# Extract an archive to an output folder
garex extract game.xp3 -o ./unpacked/

# Extract and convert proprietary images/audio to PNG and WAV on the fly
garex extract game.pck --convert -o ./unpacked/

# Extract only a specific file
garex extract game.xp3 --entry "scripts/scene01.ks" -o ./unpacked/

# Repack or create a new archive from a folder
garex create patch.xp3 ./modded_files/ --format XP3
```

### Python API

#### Browsing and Extracting Archives
```python
import garex

# Open and inspect any supported archive
with garex.open_archive("game.xp3") as arc:
    print(f"Format: {arc.format} | Total Files: {len(arc.entries())}")

    # Inspect entries
    for entry in arc.entries()[:5]:
        print(f"  • {entry.name} ({entry.size:,} bytes)")

    # Extract all assets
    arc.extract_all("./output_folder/")
```

#### Streaming a Single File to Memory
```python
with garex.open_archive("script.rpa") as arc:
    # Read directly as a binary stream without extracting to disk
    with arc.open_entry("story/chapter1.rpy") as stream:
        content = stream.read().decode("utf-8")
```

#### Repacking & Creating Archives
```python
from pathlib import Path
import garex

# Build an archive from a folder
garex.create_archive(
    "patch.xp3",
    files=Path("modded_scripts/"),
    format="XP3",
)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Supported Engines

GarEx combines native pure-Python format decoders with a universal bridge to cover both modern and classic visual novel engines:

| Engine | Format Tag | Primary Ext | Status | Prominent Visual Novels |
| :--- | :--- | :---: | :---: | :--- |
| **Ren'Py** | `RPA` | `.rpa` | Native (Pure Python) | *Doki Doki Literature Club*, *Slay the Princess* |
| **KiriKiri 2 / TVP** | `XP3` | `.xp3` | Native (Pure Python) | *Fate/stay night*, *Fate/hollow ataraxia*, *Tsukihime* |
| **CatSystem2** | `INT` | `.int` | Native (Pure Python) | *Grisaia no Kajitsu*, *Chrono Clock*, Frontwing games |
| **NScripter** | `SAR` / `NSA` | `.sar`, `.nsa` | Native (Pure Python) | *Higurashi When They Cry*, *Umineko*, *Narcissu* |
| **AliceSoft (System 4)** | `AFA`, `ALD` | `.afa`, `.ald` | Bridge | *Rance* series, *Evenicle*, *Galzoo Island* |
| **CIRCUS** | `PCK`, `CRX` | `.pck`, `.crx` | Bridge | *D.C. ~Da Capo~* series |
| **YU-RIS** | `YPF` | `.ypf` | Bridge | *G Senjou no Maou*, CLOCKUP visual novels |
| **Eushully** | `ALF` | `.alf` | Bridge | *Kamidori Alchemy Meister*, AGE Engine titles |
| **Waffle** | `PAK` | `.pak` | Bridge | *NekoSDK* visual novel packages |
| **Marmalade / Entis** | `NOA` | `.noa` | Bridge | *Entis GLS* visual novel catalog |
| **800+ Commercial Engines** | *Various* | *Various* | Bridge | Nitro+, Leaf/Aquaplus, Key/VisualArt's, Innocent Grey |

> 📖 **Full Catalog**: See [**`docs/ENGINE_STATUS.md`**](docs/ENGINE_STATUS.md) for game engine details and [**`docs/FORMAT_TRACKER.md`**](docs/FORMAT_TRACKER.md) for the complete list of 831 supported formats.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Advanced Capabilities

<details>
  <summary><strong>🖼️ On-The-Fly Image & Audio Conversion</strong></summary>
  <br />
  Many commercial visual novels store graphics and sound in encrypted or proprietary formats (such as Circus <code>.crx</code>, KiriKiri <code>.tlg</code>, or LiLiM <code>.abm</code>). GarEx can automatically decode and convert these into standard <code>.png</code> and <code>.wav</code> files during extraction:

```bash
garex extract data.pck --convert -o ./unpacked/
```
</details>

<details>
  <summary><strong>🛡️ Built-in Security & Path Traversal Protection</strong></summary>
  <br />
  Untrusted game archives may contain dangerous paths designed to overwrite arbitrary system files (Zip-Slip directory traversal) or names with illegal characters on Windows (<code>&lt; &gt; : " / \ | ? *</code>). GarEx automatically normalizes and sanitizes all entry paths before writing to disk.
</details>

<details>
  <summary><strong>⚡ Differential Parity Verification</strong></summary>
  <br />
  Every native format in GarEx is validated through automated differential testing against upstream GARbro to guarantee exact SHA-256 byte parity and metadata compatibility across thousands of commercial game assets.
</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Contributing

Contributions are welcome! Whether you are interested in porting a new format to pure Python, improving performance, or reporting an issue:

1. Check the [Contributing Guide](docs/CONTRIBUTING.md) for environment setup and porting instructions.
2. Fork the repository and create your feature branch (`git checkout -b feat/new-format`).
3. Verify test suite pass: `python -m pytest tests/`.
4. Open a Pull Request.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Credits & License

- **Lead Developer**: **[TakoYune](https://github.com/TakoYune)**
- **Heritage**: **[morkt](https://github.com/morkt)**, original creator of **[GARbro](https://github.com/morkt/GARbro)** (MIT License).
- **License**: Distributed under the permissive **[MIT License](LICENSE)**. See [**`docs/CREDITS.md`**](docs/CREDITS.md) for full attribution.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
