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

## ADR-004: Bridge mechanism (OPEN - agent must decide in Phase 1 after a spike)
Options: (a) helper executable `garex-bridge.exe` called via subprocess with a JSON-lines protocol;
(b) `pythonnet` loading the .NET assemblies in-process.
Default recommendation: (a) for robustness (no dependency on pythonnet/Python version matrix,
crash isolation). Evaluate (b) only if (a) is too slow for large archives. Record result here.

<!-- Template:

## ADR-NNN: Title (STATUS: OPEN / DECIDED / SUPERSEDED)
- Context:
- Options considered:
- Decision:
- Consequences:
-->
