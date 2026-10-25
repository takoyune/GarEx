<!--
FILE CONTRACT
Purpose : Repeatable recipe to port ONE format from GARbro C# to a native Python module.
Status  : FILLED (recipe). Agent follows it for every Phase 5 format; improve it via PR-style edits with a note in DECISIONS.md.
-->

# Format Porting Guide

Applies to one format at a time (archive, image, audio, or script format).

## Step 1 - Pick and claim
- Choose a row in `10_FORMAT_TRACKER.md` with status `bridge`. Set it to `in-progress`.

## Step 2 - Read the upstream source
- Locate the C# class in `vendor/GARbro/ArcFormats/...` (or `Image.Convert`, `GameRes`, `Legacy`).
- **Skill `reverse-engineer-anything`**: Use REA techniques to inspect managed .NET assemblies, trace binary structures, decompile complex decompression/decryption routines, and locate embedded encryption schemes or password tables.
- Write a short **format notes file** `docs/formats/<format-name>.md` containing: magic/signature,
  header layout, entry table layout, compression, encryption/scheme, edge cases, upstream file path + commit.
  This file must be based ONLY on what the source code shows.

## Step 3 - Create fixtures
- **Skill `test-driven-development` / `tdd-workflow`**: Follow TDD principles. Write tests first with known fixture specifications.
- Generate (or request from the owner) small test archives. Prefer synthetic fixtures built with the bridge's `create` command when available.
- Store fixtures in `tests/fixtures/<format-name>/` only if tiny and non-copyrighted.

## Step 4 - Implement native module
- New file `src/garex/backends/native/formats/<format_name>.py`.
- Implement the `NativeFormat` interface: `probe`, `open`, `read_entry` (+ `create` if upstream supports it).
- Use only helpers from `backends/native/binary.py` for binary reading (little-endian default, explicit when not).
- Bounds-check every offset and size read from the file. Corrupt input must raise `CorruptArchiveError`, never hang or crash.
- **Skill `code-simplification`**: Simplify and refactor decompiled C# idioms into clean, readable, typed Python 3.10+ without altering binary semantics.
- Register with the registry decorator.

## Step 5 - Differential test
- **Skill `verification-before-completion`**: Never assert completion without empirical proof. Run `tools/difftest.py <format-name> <samples...>`: opens each sample with BridgeBackend and NativeBackend, compares entry lists (names, sizes, offsets) and extracted bytes (SHA-256).
- Must be 100% identical. Add the test to `tests/test_native_<format_name>.py`.
- **Skill `systematic-debugging`**: If differential testing uncovers byte divergence, systematically isolate whether the divergence stems from offset calculation, Huffman/LZ decompression state, or endianness before modifying code.

## Step 6 - Performance sanity
- **Skill `performance-optimization`**: Native extraction of a large sample should be within a reasonable factor of the bridge; profile memory usage and zero-copy slicing, noting numbers in format notes.

## Step 7 - Finish
- **Skill `continuous-learning`**: Document recurring engine traits or reusable decompression routines for future formats.
- Set tracker row to `native` (or `native-partial` with a clear note of what is missing).
- Add PROGRESS.md entry.

## Stop conditions (ask the human)
- Source relies on Windows-only APIs that have no clear Python equivalent.
- Compression algorithm is non-standard and needs a large implementation (ask before spending effort).
- Encryption keys/schemes not obviously present in upstream data.
