<!--
FILE CONTRACT
Purpose : Technical format notes for Ren'Py RPA archive format.
Source  : vendor/GARbro/ArcFormats/RenPy/ArcRPA.cs (commit b09ee45)
-->

# Format: RPA (Ren'Py Archive)

## Overview
- **Engine**: Ren'Py
- **Extensions**: `.rpa`
- **Kind**: Archive
- **Upstream Class**: `GameRes.Formats.RenPy.RpaOpener`
- **Upstream Source**: `vendor/GARbro/ArcFormats/RenPy/ArcRPA.cs`

## Header Structure
The archive begins with an ASCII header line terminated by newline (`0x0A`):

```
RPA-3.0 <16-hex index_offset> <8-hex key>\n
```

Total header length: 34 bytes (0x22):
- Bytes 0..7: `"RPA-3.0 "` (Magic signature)
- Bytes 8..23: 16 hex characters representing index offset (`index_offset`)
- Byte 24: Space (`' '`)
- Bytes 25..32: 8 hex characters representing XOR obfuscation key (`key`)
- Byte 33: Newline (`'\n'`)

## File Body
Files are stored sequentially starting at offset `0x22`.
For each file:
- Up to the first 16 bytes (`header_size = min(len, 0x10)`) may be extracted and stored directly inside the index table.
- The remaining `size - header_size` bytes are written to the archive body.

## Index Table
Located at `index_offset`:
- The index is compressed with standard DEFLATE / zlib.
- Once decompressed, the data is a serialized Python pickle dictionary (`Protocol 2` or `Protocol 0/1/2`).
- Dictionary structure:
  ```python
  {
      "relative/filename.ext": [
          (offset ^ key, unpacked_size ^ key, optional_header_bytes),
          ...
      ]
  }
  ```
- If `header_bytes` is present and non-empty:
  The actual file content is reconstructed as `header_bytes + archive_bytes`.
- If `header_bytes` is None or omitted:
  The entire file is read directly from `offset ^ key`.

## Native Decoder Strategy
1. Read first 34 bytes and verify `"RPA-3.0 "` prefix.
2. Parse `index_offset` and `key` as hex integers.
3. Seek to `index_offset`, read remainder of stream, and decompress with `zlib.decompress()`.
4. Parse pickle dictionary using `pickle.loads()`.
5. For each item, decode filename (handling string or UTF-8 bytes) and un-XOR offset and size with `key`.
6. On extract: read `size` bytes from `offset` and prepend `header_bytes` if present.
