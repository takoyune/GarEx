
# Technical Format Specification: CatSystem2 INT

- **Format Tag**: `INT`
- **Engine**: CatSystem2 / Frontwing / Windmill
- **Primary Extension**: `.int`
- **Upstream Source**: https://github.com/morkt/GARbro/blob/master/ArcFormats/CatSystem/ArcINT.cs
- **Signature**: `0x0046494B` (`KIF\x00`)

---

## 1. Archive Structure Overview

A CatSystem2 `.int` archive consists of:
1. **Magic Header** (4 bytes): `4B 49 46 00` (`KIF\x00`).
2. **File Count** (4 bytes, int32 little-endian): Number of files in the archive.
3. **Directory Index Table**: Located immediately after the header at offset `0x08`. Contains $N$ fixed-size entry records.
4. **File Data Payloads**: Sequential uncompressed file data streams referenced by the directory table.

---

## 2. Directory Entry Layout

The directory table begins at offset `0x08`. Standard CatSystem2 archives use 64-byte name buffers (total record size `0x48` = 72 bytes):

| Offset in Record | Type | Description | Size |
|---|---|---|---|
| `0x00` | `byte[64]` | File Name (CP932 / Shift-JIS, null-terminated) | 64 bytes (`0x40`) |
| `0x40` | `uint32` | File Data Offset in archive (Little-Endian) | 4 bytes |
| `0x44` | `uint32` | File Data Size in bytes (Little-Endian) | 4 bytes |

*(Note: Legacy CatSystem1 archives use 32-byte name buffers with 40-byte records (`0x28`), detected during probe).*

---

## 3. Extraction & Reading Rules

1. Read entry count at offset 4.
2. For each entry, read name from 64-byte field, decode with `cp932` (with fallback to `utf-8` / `latin1`), stripping trailing null bytes.
3. Read `offset` and `size`.
4. Validate that `offset` is within file boundaries and does not overlap with the directory table.
5. Seek to `offset` and read `size` bytes directly.

---

## 4. Archive Creation Rules

1. Write 4-byte signature `b"KIF\x00"`.
2. Write little-endian `int32` representing total file count.
3. Write placeholder directory table: 64 bytes of CP932 encoded file name (padded with zeros) + 8 zero bytes.
4. Consecutively write each file payload, recording the starting file offset and size.
5. Rewind to directory table offsets at `0x08 + i * 0x48 + 0x40`, writing `<II` (offset, size) for each entry.
