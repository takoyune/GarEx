<!--
FILE CONTRACT
Purpose : Comprehensive tracker of Visual Novel Engines, formats, and their implementation status in GarEx (Bridge vs Native).
Status  : ACTIVE. Maintained as native format ports land.
-->

# Visual Novel Engine Implementation Status Tracker

This document tracks all Visual Novel game engines and resource formats supported by upstream GARbro, categorizing their format tags, file extensions, bridge integration status, and native pure-Python implementation status in **GarEx**.

---

## 1. Engine Implementation Dashboard

| Metric | Status | Details |
|---|:---:|---|
| **Primary Roadmap** | **Option A** | Ren'Py, KiriKiri, CatSystem2, NScripter |
| **Total Engine Families Documented** | **50+** | Major commercial and doujin visual novel engines |
| **Bridge Backend Coverage** | **100%** | All formats recognized by upstream GARbro |
| **Native Pure-Python Coverage** | **1 Complete / 3 In-Queue** | `RPA` (Ren'Py 3.0/2.0/1.0) complete with round-trip creation |
| **Differential Test Verification** | **100% Byte Parity** | Verified with `tools/difftest.py` against `garex-bridge.exe` |

---

## 2. Option A Implementation Pipeline (Active Priority)

Option A focuses on the most ubiquitous visual novel engines in the international and Japanese community:

| Engine | Format Tag | Extensions | Bridge Read | Bridge Create | Native Read | Native Create | Parity Verified | Status |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Ren'Py** | `RPA` | `.rpa` | [x] | [x] | [x] | [x] | [x] 100% | **COMPLETE (Native)** |
| **KiriKiri / TVP** | `XP3` | `.xp3` | [x] | [x] | [ ] | [ ] | [ ] | **IN PROGRESS** (Task 5.3) |
| **CatSystem2** | `INT` | `.int` | [x] | [x] | [ ] | [ ] | [ ] | **QUEUED** (Task 5.4) |
| **NScripter** | `SAR` | `.sar` | [x] | [x] | [ ] | [ ] | [ ] | **QUEUED** (Task 5.5) |
| **NScripter / ONS** | `NSA` | `.nsa` | [x] | [x] | [ ] | [ ] | [ ] | **QUEUED** (Task 5.5) |

---

## 3. Detailed Engine Status Matrix

### Tier 1: Major & Mainstream Engines

| Engine / Developer | Format Tag | Extensions | Bridge Support | Native Support | Creation Support | Description / Prominent Titles |
|---|---|---|:---:|:---:|:---:|---|
| **Ren'Py** | `RPA` | `.rpa` | **Complete** | **Complete (Native)** | Yes (Bridge & Native) | *Doki Doki Literature Club*, *Katawa Shoujo*, *Slay the Princess* |
| **KiriKiri / TVP** | `XP3` | `.xp3` | **Complete** | In Progress (Phase 5) | Yes (Bridge) | *Fate/stay night*, *Fate/hollow ataraxia*, *Tsukihime*, *Witch on the Holy Night* |
| **CatSystem2** | `INT` | `.int` | **Complete** | Queued (Phase 5) | Yes (Bridge) | *Grisaia no Kajitsu*, *Chrono Clock*, Frontwing & Windmill games |
| **NScripter** | `SAR` | `.sar` | **Complete** | Queued (Phase 5) | Yes (Bridge) | *Tsukihime*, *Kagetsu Tohya*, Naoki Takahashi engine |
| **NScripter / ONS** | `NSA` | `.nsa` | **Complete** | Queued (Phase 5) | Yes (Bridge) | *Higurashi no Naku Koro ni*, *Umineko no Naku Koro ni* |
| **Majiro** | `MAJIRO` | `.arc` | **Complete** | Planned (Phase 5) | Yes (Bridge) | *Flowers* series, Innocent Grey, 5621 engine |
| **Yu-Ris** | `YPF` | `.ypf` | **Complete** | Planned (Phase 5) | Yes (Bridge) | *G Senjou no Maou*, *Sharin no Kuni*, Akabeisoft2 |
| **Yuka Script** | `YKC` | `.ykc` | **Complete** | Planned (Phase 5) | Yes (Bridge) | Yuka script engine resource archive |
| **Nitro+ (NPA)** | `NPA` | `.npa` | **Complete** | Planned (Phase 5) | Yes (Bridge) | *Saya no Uta*, *Demonbane*, Nitro+ engine |
| **Nitro+ (Steins;Gate)** | `NPA-SG` | `.npa` | **Complete** | Planned (Phase 5) | Yes (Bridge) | *Steins;Gate*, *Chaos;Head*, 5pb./MAGES engine |
| **Nitro+ (Mware)** | `NPK` | `.npk` | **Complete** | Planned (Phase 5) | Yes (Bridge) | Nitroplus Mware resource format |
| **RealLive** | `SEEN` | `.seen`, `.ovr` | **Complete** | Planned (Phase 5) | No | *Clannad*, *Air*, *Kanon*, VisualArt's/Key engine |
| **SiglusEngine** | `NWA`, `G00` | `.nwa`, `.g00` | **Complete** | Planned (Phase 5) | No | VisualArt's/Key modern engine (*Rewrite*, *Summer Pockets*) |
| **BGI / Ethornell** | `ARC/BGI` | `.arc` | **Complete** | Planned (Phase 5) | No | *Daitoshokan no Hitsujikai*, *August* visual novels |

### Tier 2: Classic & Renowned Japanese VN Engines

| Engine / Developer | Format Tag | Extensions | Bridge Support | Native Support | Creation Support | Description / Prominent Titles |
|---|---|---|:---:|:---:|:---:|---|
| **AliceSoft (Sys4)** | `AFA` | `.afa` | **Complete** | Planned | No | *Rance* series, *Evenicle*, AliceSoft System 4 |
| **AliceSoft (Sys3)** | `ALD` | `.ald` | **Complete** | Planned | No | *Rance IV*, *Toushin Toshi*, AliceSoft System 3/3.9 |
| **AliceSoft** | `AAR` | `.red` | **Complete** | Planned | No | AliceSoft System resource |
| **AliceSoft** | `ALK` | `.alk` | **Complete** | Planned | No | AliceSoft System 4 encrypted script archive |
| **Leaf / Aquaplus** | `A/Leaf` | `.a` | **Complete** | Planned | No | *White Album 2*, *Utawarerumono*, Leaf archives |
| **Leaf / Aquaplus** | `LAC` | `.lac` | **Complete** | Planned | No | Leaf audio container |
| **Leaf / Aquaplus** | `AR2` | `.ar2` | **Complete** | Planned | No | Leaf ar21 resource archive |
| **Eushully** | `ALF` | `.alf` | **Complete** | Planned | No | *Kamidori Alchemy Zvezda*, *Soukou Akki Muramasa* |
| **Studio e.go!** | `DAT/EGO/1`| `.dat` | **Complete** | Planned | Yes (Bridge) | *Izumo* series, *Castle Fantasia*, Studio e.go! |
| **Liar-soft** | `XFL` | `.xfl` | **Complete** | Planned | Yes (Bridge) | *Sekien no Inganock*, *Shikkoku no Sharnoth*, Liar-soft |
| **Will Co. / Pulltop** | `ARC/Will` | `.arc` | **Complete** | Planned | Yes (Bridge) | *Kono Oozora ni, Tsubasa wo Hirogete*, Pulltop / Will |
| **Will Co. v2** | `ARC/WillV2`| `.arc` | **Complete** | Planned | Yes (Bridge) | Will Co. v2 engine resource |
| **Flying Shine** | `PD` | `.pd` | **Complete** | Planned | Yes (Bridge) | *Cross Channel* (original engine), Flying Shine |
| **Amaterasu** | `AMI` | `.ami` | **Complete** | Planned | Yes (Bridge) | *Muv-Luv*, *Muv-Luv Alternative* translation project archive |
| **QLIE** | `ABMP/QLIE`| `.b` | **Complete** | Planned | No | QLIE multi-frame image and script archive |
| **LiLiM** | `AOS` | `.aos` | **Complete** | Planned | No | LiLiM / Le.Chocolat resource archive |
| **Circus** | `CRX` | `.crx` | **Complete** | Planned | No | *Da Capo* series, Circus game engine |
| **Apricot** | `ARC/Apricot` | `.arc` | **Complete** | Planned | No | Apricot engine visual novels |
| **Artemis Engine** | `PFS` | `.pfs` | **Complete** | Planned | No | Artemis Engine mobile/PC visual novels |
| **Black Cyc** | `DAT/Cyc` | `.dat` | **Complete** | Planned | No | Black Cyc / Cyc resource archives |
| **Cmvs / Purple** | `CPK/Cmvs` | `.cpk` | **Complete** | Planned | No | *Aoi Tori*, *Amatsutsumi*, Purple Software |
| **Debonosu** | `DAT/Debonosu` | `.dat` | **Complete** | Planned | No | Debonosu Works game archives |
| **DxLib** | `DXA` | `.dxa` | **Complete** | Planned | No | Direct X Library archive container |
| **EntisGLS** | `NOA` | `.noa` | **Complete** | Planned | No | Entis Graphic Library Suite |
| **Favorite** | `HXP` | `.hxp` | **Complete** | Planned | No | *Astraea Hourglass*, Favorite visual novel engine |
| **HSP** | `DPM` | `.dpm` | **Complete** | Planned | No | Hot Soup Processor archives |
| **Illusion** | `PP` | `.pp` | **Complete** | Planned | No | Illusion 3D games and visual novels |
| **Kid / 5pb.** | `DAT/Kid` | `.dat` | **Complete** | Planned | No | *Ever17*, *Never7*, *Remember11* |
| **LiveMaker** | `VF` | `.pck` | **Complete** | Planned | No | LiveMaker visual novel creator archives |
| **LucasArts / SCUMM** | `BND` | `.bnd` | **Complete** | Planned | No | Classic adventure game bundles |
| **MangaGamer** | `MG` | `.mg` | **Complete** | Planned | No | MangaGamer wrapper archives |
| **Nekopack** | `NEKO` | `.dat` | **Complete** | Planned | No | NekoSDK resource archives |
| **Pajamas** | `EPA` | `.epa` | **Complete** | Planned | No | Pajamas Soft visual novels |
| **Palette** | `PAR` | `.par` | **Complete** | Planned | No | *Mashiroiro Symphony*, Palette games |
| **Silky's** | `ARC/Silky`| `.arc` | **Complete** | Planned | No | *Nanairo Reincarnation*, Silky's Plus |
| **Softpal** | `PAC/Softpal`| `.pac` | **Complete** | Planned | No | UNiSONSHIFT / Softpal visual novels |
| **Tmr-Hiro** | `ARC/Tmr` | `.arc` | **Complete** | Planned | No | Tmr-Hiro visual novels |
| **Unity** | `ASSET` | `.assets` | **Complete** | Planned | No | Unity engine asset bundles |
| **Generic / PKWARE** | `ZIP` | `.zip` | **Complete** | Planned | Yes (Bridge & Native) | PKWARE Standard ZIP archive |

---

## 4. Format Implementation Requirements

Every native format port must satisfy the five mandatory criteria defined in [`docs/06_FORMAT_PORTING_GUIDE.md`](file:///d:/code%20iwan/GarEx/docs/06_FORMAT_PORTING_GUIDE.md):

1. **Reverse-Engineering Specification**: Format layout, headers, endianness, index structures, and compression documented under `docs/formats/<FORMAT>.md`.
2. **Pure Python Architecture**: Zero external native dependencies; standard library (`zlib`, `struct`, `io`, `hashlib`) only.
3. **Safe Binary Reading**: All reading uses `BinaryReader` with strict boundary checks to prevent overflow or out-of-bounds exceptions.
4. **100% Differential Parity**: Must achieve identical entry counts, names, offset sizes, and bit-for-bit SHA-256 byte parity against `BridgeBackend`.
5. **Round-Trip Repacking (where applicable)**: When create is supported, the created archive must be readable by both `NativeBackend` and the official C# `BridgeBackend`.
