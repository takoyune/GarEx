<!--
FILE CONTRACT
Purpose : Architecture Decision Records (ADR). Every non-trivial choice is written here so it is never re-debated or forgotten.
Status  : TEMPLATE with pre-filled decisions ADR-001..003 (made by the human owner). Append new ADRs at the end.
Format  : See template at the bottom.
-->

# Decisions

## ADR-001: Hybrid strategy (DECIDED by owner)
Python-first API; bridge backend wraps original GARbro C# code; formats are ported to pure Python
incrementally; native implementation has priority over bridge when it passes differential tests.

## ADR-002: Windows first (DECIDED by owner)
Initial target is Windows only because GARbro depends on .NET Framework 4.6+ and WPF parts.
Cross-platform is a later goal and depends on native ports.

## ADR-003: Package name `garex`, English-only docs (DECIDED by owner)

## ADR-004: Bridge mechanism (DECIDED 2026-10-25)
- **Context**: Need to interface Python with compiled C# GARbro assemblies (`GameRes.dll`, `ArcFormats.dll`) for the hybrid backend strategy.
- **Options considered**:
  - (a) Helper executable `garex-bridge.exe` called via subprocess over JSON-lines stdio protocol.
  - (b) `pythonnet` loading assemblies in-process inside the Python runtime.
- **Empirical Spike Benchmark Results (`tools/spike_adr004.py`)**:
  - Subprocess cold start & format enumeration: **0.58s** (warm 0.55s).
  - Pythonnet CLR bootstrap & format enumeration: **1.13s**.
  - Crash safety: Subprocess isolates corrupt archive panics, unsafe block faults, and SEH access violations to the child process, protecting the host Python process.
  - Dependency footprint: Subprocess requires zero pip C-dependencies (`dependencies = []`), fully supporting any Python version (3.10 through 3.14+).
- **Decision**: Choose **(a) Helper executable `garex-bridge.exe` via subprocess with JSON-lines protocol**.
- **Consequences**:
  - Bundled inside wheel (`src/garex/_bridge/`).
  - No fragile `pythonnet` C-extension compilation or Python version locking.
  - Bridge protocol provides clean timeout handling, cancellation, and mapped typed exceptions.

<!-- Template:

## ADR-NNN: Title (STATUS: OPEN / DECIDED / SUPERSEDED)
- Context:
- Options considered:
- Decision:
- Consequences:
-->
