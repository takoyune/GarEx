# Visual Novel Engine Support Guide

This document provides a comprehensive overview of visual novel game engines and resource formats supported by **GarEx**, their capabilities (Read, Extract, Repack), and famous games built on them.

---

## ⚡ Mainstream Engines (100% Pure Python, Cross-Platform)

These formats run with **zero external dependencies** across Windows, Linux, macOS, and Steam Deck with verified byte-for-byte parity:

| Engine | Format Tag | Extension | Read / Browse | Extract Assets | Create / Repack | Prominent Visual Novels |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Ren'Py** | `RPA` | `.rpa` | ✅ | ✅ | ✅ | *Doki Doki Literature Club*, *Katawa Shoujo*, *Slay the Princess* |
| **KiriKiri 2 / TVP** | `XP3` | `.xp3` | ✅ | ✅ | ✅ | *Fate/stay night*, *Fate/hollow ataraxia*, *Tsukihime*, *Witch on the Holy Night* |
| **CatSystem2** | `INT` | `.int` | ✅ | ✅ | ✅ | *Grisaia no Kajitsu*, *Chrono Clock*, Frontwing & Windmill visual novels |
| **NScripter** | `SAR` | `.sar` | ✅ | ✅ | ✅ | *Tsukihime (Classic)*, *Kagetsu Tohya*, Naoki Takahashi engine titles |
| **NScripter / ONScripter** | `NSA` | `.nsa` | ✅ | ✅ | ✅ | *Higurashi When They Cry*, *Umineko When They Cry*, *Narcissu* |

---

## 🏛️ Extended Commercial Engine Catalog (Universal Bridge)

Over 800 visual novel formats from classic commercial studios are supported through GarEx's universal bridge:

### Major Commercial Engines

| Engine / Developer | Format Tag | Extension | Read / Extract | Repack | Famous Visual Novels & Studios |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **AliceSoft (System 4)** | `AFA` | `.afa` | ✅ | Planned | *Rance* series, *Evenicle* |
| **AliceSoft (System 3/4)** | `ALD` | `.ald` | ✅ | Planned | *Galzoo Island*, classic AliceSoft catalog |
| **CIRCUS** | `PCK`, `CRX` | `.pck`, `.crx` | ✅ | Planned | *D.C. ~Da Capo~* series |
| **Eushully** | `ALF`, `AGF` | `.alf`, `.agf` | ✅ | Planned | *Kamidori Alchemy Meister*, AGE Engine titles |
| **YU-RIS** | `YPF` | `.ypf` | ✅ | ✅ | *G Senjou no Maou*, *Sharin no Kuni*, Akabeisoft2, CLOCKUP |
| **Waffle** | `PAK` | `.pak` | ✅ | ✅ | NekoSDK visual novel packages |
| **Marmalade / Entis** | `NOA` | `.noa` | ✅ | Planned | Entis GLS visual novels |
| **Majiro** | `MAJIRO` | `.arc` | ✅ | ✅ | *Flowers* series, Innocent Grey, 5621 engine |
| **Yuka Script** | `YKC` | `.ykc` | ✅ | ✅ | Yuka script engine resource archives |
| **Nitro+ (NPA)** | `NPA` | `.npa` | ✅ | ✅ | *Saya no Uta*, *Demonbane*, classic Nitro+ titles |
| **Nitro+ / 5pb. (Mware)** | `NPA-SG`, `NPK` | `.npa`, `.npk` | ✅ | ✅ | *Steins;Gate*, *Chaos;Head*, 5pb./MAGES engine |
| **RealLive** | `SEEN` | `.seen`, `.ovr` | ✅ | Planned | *Clannad*, *Air*, *Kanon*, VisualArt's/Key engine |
| **SiglusEngine** | `NWA`, `G00` | `.nwa`, `.g00` | ✅ | Planned | *Rewrite*, *Summer Pockets*, VisualArt's modern engine |
| **BGI / Ethornell** | `ARC/BGI` | `.arc` | ✅ | Planned | *Daitoshokan no Hitsujikai*, August visual novels |

### Classic & Doujin Studios

| Developer / Studio | Formats | Extension | Description / Notable Titles |
| :--- | :--- | :--- | :--- |
| **Leaf / Aquaplus** | `LEAF`, `LAC` | `.pak`, `.lac` | *Utawarerumono*, *White Album 2*, *To Heart* |
| **Innocent Grey** | `MAJIRO`, `DAT` | `.arc`, `.dat` | *Kara no Shoujo*, *Cartagra* |
| **Liar-soft** | `WAR`, `DAT` | `.war`, `.dat` | *Steampunk* series (*G弦上の魔王*, *紫影のソナーニル*) |
| **Tactics / Nexton** | `ARC/Will`, `ARC/WillV2` | `.arc` | *One ~Kagayaku Kisetsu e~*, early Key works |
| **Studio e.go!** | `DAT/EGO` | `.dat` | *Castle Fantasia*, *Izumo* series |
| **Caramel Box** | `BIN`, `DAT` | `.bin`, `.dat` | *Otome wa Boku ni Koishiteru* |
| **Minori** | `PA`, `DAT` | `.pck`, `.dat` | *ef - a fairy tale of the two.*, *Eden* |
| **Pulltop** | `CPK`, `DAT` | `.cpk`, `.dat` | *Kono Oozora ni, Tsubasa wo Hirogete* |
| **Sprite** | `DAT`, `BIN` | `.dat`, `.bin` | *Ao no Kanata no Four Rhythm (Aokana)* |
| **SMEE** | `DAT`, `BIN` | `.dat`, `.bin` | *Making*Lovers*, *Fureraba* |

---

## 🔎 Looking for a Specific Format?

Consult [docs/FORMAT_TRACKER.md](FORMAT_TRACKER.md) for the complete index of all 831 archive, image, audio, and script formats recognized by GarEx.
