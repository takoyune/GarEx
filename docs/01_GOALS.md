<!--
FILE CONTRACT
Purpose : Defines WHAT garex is, what success looks like, and what is explicitly out of scope.
Status  : FILLED. Agent must not edit without owner approval.
-->

# Goals

## Vision
`pip install garex` gives Python developers the same resource-handling power GARbro gives
Windows users through its GUI: open game archives, list and extract their contents, convert
images/audio to common formats, and create/repack archives (e.g. to inject translated text).

## Primary goals
1. **Installable via pip.** A user on Windows runs `pip install garex` and can use it immediately.
   No manual compiling, no manual DLL copying.
2. **Python-first API.** Clean, typed, documented, stable. The user never needs to know whether a
   format is handled by the bridge or natively.
3. **Feature coverage in phases:** (1) open/list, (2) extract, (3) convert image/audio,
   (4) create/repack. Basic features first.
4. **Format coverage: everything GARbro supports.** Reached gradually. Formats GARbro does not
   support are out of focus.
5. **Progressive independence.** Replace the C# bridge with native Python format by format,
   always verified against GARbro's real output.
6. **Usable by automation / localization pipelines** (extract game text assets, modify, repack).

## Non-goals (do NOT build)
- A GUI. (GARbro's `GUI/` folder is ignored.)
- Supporting formats GARbro itself does not support.
- Cracking/decrypting beyond what GARbro already implements.
- Redistributing any game files, keys not already in GARbro, or copyrighted assets.
- Linux/macOS support in the first releases (later goal).
- Rewriting everything in one go. Hybrid and incremental only.

## Definition of done (per level)
- **Feature done:** public API exists, documented, tested against at least 3 real-format samples
  (supplied by the owner or generated synthetically), differential-tested against GARbro.
- **Format ported:** native implementation output is byte-identical to the bridge for the test set.
- **Release done:** `pip install` from a clean Windows venv works, README quickstart runs.

## Success metrics
- % of formats in `docs/10_FORMAT_TRACKER.md` with status `native`.
- Differential test pass rate (target 100% for native formats).
- Clean-venv install and quickstart works on Windows 10/11.
