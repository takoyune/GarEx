<!--
FILE CONTRACT
Purpose : Entry point of the project folder. First file any human or AI agent opens.
Status  : FILLED (project brief). Keep it short; details live in /docs.
Update  : Only when goals, package name, or folder layout change. Never put progress logs here (use PROGRESS.md).
Related : AGENT_INSTRUCTIONS.md (rules for the AI), docs/01_GOALS.md
-->

# garex

**garex** is a Python library (`pip install garex`) for browsing, extracting, converting and
re-packing resources of Japanese visual novels and similar games. It is a port of
[GARbro](https://github.com/morkt/GARbro) by morkt (MIT license), which is a C# / .NET Framework
desktop tool.

## One-paragraph strategy (Hybrid)

1. Design a clean **Python-first API** (`open archive -> list -> extract -> convert -> create`).
2. At first, the API is powered by a **bridge backend** that calls the original GARbro C# code
   (bundled inside the wheel). This gives working features quickly.
3. Step by step, individual formats are **ported to pure Python** (native backend). Whenever a
   native implementation exists and passes differential tests, it is used first; otherwise the
   library falls back to the bridge.
4. Long-term, the bridge shrinks and the library becomes self-contained.

## Facts

| Item | Value |
|---|---|
| PyPI / import name | `garex` |
| Upstream | https://github.com/morkt/GARbro (MIT) |
| Platform now | Windows only (GARbro is .NET Framework 4.6+, WPF) |
| Language of all docs | English |
| Python | 3.10+ |

## Start here

1. Read `AGENT_INSTRUCTIONS.md` (mandatory for AI agents).
2. Read `docs/01_GOALS.md` then `docs/03_ROADMAP.md`.
3. Check `PROGRESS.md` to see where the last session stopped.
