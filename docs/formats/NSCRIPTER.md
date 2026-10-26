<!--
FILE CONTRACT
Purpose : Technical specification and binary layout for NScripter SAR and NSA archives.
Status  : ACTIVE. Reference for native pure-Python implementation.
-->

# Technical Format Specification: NScripter SAR & NSA

- **Format Tags**: `SAR`, `NSA`
- **Engine**: NScripter / ONScripter (Naoki Takahashi, Ogapee, Uncle Mion)
- **Primary Extensions**: `.sar`, `.nsa`, `.dat`
- **Upstream Sources**:
  - `SAR`: https://github.com/morkt/GARbro/blob/master/ArcFormats/NScripter/ArcSAR.cs
  - `NSA`: https://github.com/morkt/GARbro/blob/master/ArcFormats/NScripter/ArcNSA.cs
- **Endianness**: **BIG-ENDIAN** (All header counts, offsets, and sizes use network/big-endian byte order).

---

## 1. SAR Format (Standard Archive)

### Header Layout (6 bytes)
| Offset | Type | Description |
|:---:|:---:|:---|
| 0 | uint16 (BE) | `num_of_files`: Total number of entries in the archive |
| 2 | uint32 (BE) | `base_offset`: Absolute file offset where file data begins |

### Directory Table (Starts at offset 6)
Contains `num_of_files` consecutive entry records:
| Field | Type | Description |
|:---|:---:|:---|
| `name` | Null-terminated string | Filename encoded in CP932 / Shift-JIS |
| `offset` | uint32 (BE) | Relative offset from `base_offset`. Actual physical offset = `base_offset + offset` |
| `size` | uint32 (BE) | Size of uncompressed file data in bytes |

---

## 2. NSA Format (Compressed Archive)

### Header Layout (6 bytes or 8 bytes extended)
* Standard header: `num_of_files` (uint16 BE) + `base_offset` (uint32 BE).
* Extended header: If the first 2 bytes are `0x0000`, the real header begins at offset 2 (`num_of_files` uint16 BE + `base_offset` uint32 BE).

### Directory Table
Contains `num_of_files` consecutive entry records:
| Field | Type | Description |
|:---|:---:|:---|
| `name` | Null-terminated string | Filename encoded in CP932 / Shift-JIS |
| `compression_type` | uint8 | Compression type: `0` = None, `1` = SPB, `2` = LZSS, `4` = NBZ |
| `offset` | uint32 (BE) | Relative offset from `base_offset`. Physical offset = `base_offset + offset` |
| `packed_size` | uint32 (BE) | Size of packed / stored data in the archive |
| `unpacked_size` | uint32 (BE) | Size of decompressed data |

### Compression Algorithms:
* **Type 0 (None)**: Uncompressed raw stream.
* **Type 1 (SPB)**: Special Picture Bitmap. Decodes 24-bit paletted delta-stream into standard 54-byte BMP.
* **Type 2 (LZSS)**: Okumura LZSS variant with `EI=8`, `EJ=4`, `P=1`, `N=256`, `F=17`, `r=239` over an MSB-first bitstream.
* **Type 4 (NBZ)**: Standard BZip2 stream with 4-byte header (`bz2.decompress(data[4:])`).

---

## 3. Creation Specification

### Creating SAR:
1. Directory index size: `index_size = sum(len(name.encode("cp932")) + 1 + 8 for name in files)`.
2. `base_offset = 6 + index_size`.
3. Write `struct.pack(">HI", len(files), base_offset)`.
4. Write directory records: for each file, write CP932 name + `\x00` + `offset` (`>I`) + `size` (`>I`).
5. Seek to `base_offset` and append file data.

### Creating NSA:
1. Directory index size: `index_size = sum(len(name.encode("cp932")) + 1 + 13 for name in files)`.
2. `base_offset = 6 + index_size`.
3. Write `struct.pack(">HI", len(files), base_offset)`.
4. Write directory records: for each file, write CP932 name + `\x00` + `compression_type` (`\x00`) + `offset` (`>I`) + `packed_size` (`>I`) + `unpacked_size` (`>I`).
5. Seek to `base_offset` and append file data.
