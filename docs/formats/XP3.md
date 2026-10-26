<!--
FILE CONTRACT
Purpose : Technical specification and binary layout for KiriKiri / TVP XP3 archives.
Status  : ACTIVE. Reference for native pure-Python implementation.
-->

# Technical Format Specification: KiriKiri XP3

- **Format Tag**: `XP3`
- **Engine**: KiriKiri 2 / KAG3 / TVP (W+Studio, Type-Moon, etc.)
- **Primary Extension**: `.xp3`, `.exe`
- **Upstream Source**: https://github.com/morkt/GARbro/blob/master/ArcFormats/KiriKiri/ArcXP3.cs
- **Signatures**:
  - `0x0d335058` (`XP3\r\n \n\x1a\x8bg\x01`)
  - Optional Windows PE executable stub (`MZ`)

---

## 1. Archive Structure Overview

A standard KiriKiri XP3 archive consists of:
1. **Magic Header** (11 bytes): `58 50 33 0D 0A 20 0A 1A 8B 67 01` (`XP3\r\n \n\x1a\x8bg\x01`).
2. **Index Offset** (8 bytes, int64 little-endian): File position pointing to the archive index table.
3. **File Data Payloads**: Consecutive chunks of raw or zlib-compressed file data.
4. **Archive Index Table**: Located at `index_offset`, either uncompressed or zlib-compressed.

---

## 2. Header and Index Reference

### 2.1 File Header (19 bytes minimum)
| Offset | Type | Description | Value |
|---|---|---|---|
| `0x00` | `byte[11]` | Magic Signature | `XP3\r\n \n\x1a\x8bg\x01` |
| `0x0B` | `int64` | Index Table Offset | File pointer to index table |

### 2.2 Index Table Header
At `index_offset`:
| Offset | Type | Description | Value |
|---|---|---|---|
| `0x00` | `uint8` | Compression Flag | `0x00` = Raw / Unpacked, `0x01` = ZLib Compressed |
| If `0x00`: | | | |
| `0x01` | `int64` | Index Data Size | Length in bytes of raw index |
| `0x09` | `bytes` | Raw Index Buffer | Stream of entry chunks |
| If `0x01`: | | | |
| `0x01` | `int64` | Packed Index Size | Length in bytes of compressed zlib stream |
| `0x09` | `int64` | Unpacked Index Size | Decompressed index buffer length |
| `0x11` | `bytes` | ZLib Stream | Stream of compressed entry chunks |

---

## 3. Index Entry Chunks

The decompressed index stream consists of repeating `File` chunks:

### 3.1 `File` Container Chunk
- **Chunk Tag**: `0x656C6946` (`File` in ASCII Little-Endian).
- **Chunk Size**: `int64` (Little-Endian) representing total size of sections within this file chunk.
- Contains nested sub-sections: `info`, `segm`, `adlr`.

### 3.2 `info` Sub-Section
- **Section Tag**: `0x6F666E69` (`info` in ASCII Little-Endian).
- **Section Size**: `int64` (Little-Endian).
- **Payload**:
  - `uint32`: Flags (`0x80000000` bit indicates encryption).
  - `int64`: Unpacked file size.
  - `int64`: Packed / stored file size.
  - `uint16`: Name character length $N$.
  - `wchar[N]`: File name encoded as UTF-16LE ($2 \times N$ bytes).

### 3.3 `segm` Sub-Section
- **Section Tag**: `0x6D676573` (`segm` in ASCII Little-Endian).
- **Section Size**: `int64` (Little-Endian, usually 28 bytes per segment).
- **Segment Record** (28 bytes each):
  - `int32`: Compression flag (`1` = zlib compressed, `0` = raw).
  - `int64`: Data offset in archive.
  - `int64`: Unpacked segment size.
  - `int64`: Packed segment size.

### 3.4 `adlr` Sub-Section
- **Section Tag**: `0x726C6461` (`adlr` in ASCII Little-Endian).
- **Section Size**: `int64` (4 bytes).
- **Payload**:
  - `uint32`: Adler-32 checksum of uncompressed file data.

---

## 4. Extraction & Decompression Rules

1. Each file entry may contain one or multiple segments. Standard XP3 archives usually contain 1 segment per entry.
2. If `segment.is_compressed`: read `packed_size` bytes from `segment.offset`, decompress using standard `zlib.decompress`.
3. If not compressed: read `size` bytes directly from `segment.offset`.
4. Concatenate segment buffers if multiple segments are present.
5. Path sanitization must be applied to prevent Zip-Slip directory traversal.

---

## 5. Archive Creation

1. Write standard 11-byte signature `XP3\r\n \n\x1a\x8bg\x01`.
2. Write 8 zero bytes as index pointer placeholder.
3. For each file, compress with `zlib.compress(data, level=9)` and calculate `adler32(data)`.
4. Build `File` chunks with UTF-16LE encoded names, segment offsets, and Adler-32 hashes.
5. Compress index with zlib and write at end of archive.
6. Rewind to offset `0x0B` and write little-endian `int64` pointing to index offset.
