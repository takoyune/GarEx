<!--
FILE CONTRACT
Purpose : The operating manual for the AI coding agent (Google Antigravity). Tells it HOW to work on this project.
Status  : FILLED. Do not delete rules; propose changes via DECISIONS.md instead.
Update  : Only by the human owner.
Related : docs/05_DO_AND_DONT.md, PROGRESS.md, DECISIONS.md
-->

# Agent Instructions

You are building **garex**, a Python port of GARbro. Read this file fully before touching anything.

## 1. Reading order (every new session)

1. `PROGRESS.md` - where the previous session stopped, what is next.
2. `docs/01_GOALS.md` - what we are building and what we are NOT.
3. `docs/03_ROADMAP.md` + `docs/04_TASKS.md` - current phase and open tasks.
4. `docs/05_DO_AND_DONT.md` - hard rules.
5. Other docs only when the current task needs them (see File Map below).

## 2. File map: which file is for what

| Path | What it is | When you must touch it |
|---|---|---|
| `PROGRESS.md` | Session handoff log | End of EVERY session (append an entry) |
| `DECISIONS.md` | Architecture decision records (ADR) | Whenever you make a non-trivial choice |
| `docs/01_GOALS.md` | Goals, non-goals, definition of done | Never edit without owner approval |
| `docs/02_ARCHITECTURE.md` | Layers, interfaces, data models | Fill/refine details in Phase 0-1; update if design changes |
| `docs/03_ROADMAP.md` | Phases with exit criteria | Tick phase status when exit criteria are met |
| `docs/04_TASKS.md` | Checklist per phase | Tick boxes as you finish tasks; add sub-tasks if needed |
| `docs/05_DO_AND_DONT.md` | Hard rules | Read-only for you |
| `docs/06_FORMAT_PORTING_GUIDE.md` | Recipe to port ONE format C# -> Python | Follow it for every native port |
| `docs/07_PACKAGING.md` | pyproject, wheel, bundling bridge | Phase 1 and Phase 6 |
| `docs/08_TESTING.md` | Test strategy, differential testing | Follow for every feature |
| `docs/09_LICENSE_AND_CREDITS.md` | MIT + attribution rules | Check before every release |
| `docs/10_FORMAT_TRACKER.md` | Table of every format and its port status | Update whenever a format changes status |
| `reference/GARBRO_REPO_MAP.md` | What each GARbro folder is | Fill in the "VERIFIED" column during Phase 0 |
| `vendor/` | Pinned, UNMODIFIED copy of upstream GARbro | Never edit files inside (see rules) |
| `bridge/` | Small C# shim that exposes GARbro to Python | Phase 1 |
| `src/garex/` | The Python package | Phases 1-5 |
| `tests/` | Test suite | Every feature ships with tests |
| `tools/` | Dev scripts (inventory, build bridge, diff-test) | Create as needed; each script gets a header comment |

## 3. Files that contain `WHAT THIS MUST BECOME`

Many files in `src/` and `tests/` are intentionally empty placeholders. Each starts with a
docstring/comment block titled **WHAT THIS MUST BECOME** that states its purpose, its public
interface, and what it must NOT do. When you implement such a file:

- Follow that block exactly. If you believe it is wrong, write an ADR in `DECISIONS.md` first.
- Keep the block updated (turn it into a normal module docstring) once the file is implemented.

## 4. Working rules (summary; full list in docs/05_DO_AND_DONT.md)

- Work **one phase and one task at a time**. Do not jump ahead.
- **Ask the human** when something is ambiguous or when a decision changes the public API,
  the license position, or the roadmap. Do not guess silently.
- Never modify `vendor/` contents. Never invent a file format from memory: port from the C# source.
- Every ported format must be verified against the bridge output (differential test).
- Never commit game files or any copyrighted assets.
- At the end of each session, update `PROGRESS.md` and `docs/10_FORMAT_TRACKER.md`.

## 5. Definition of a finished task

Code written + tests passing + docs/trackers updated + `PROGRESS.md` entry added.

## 6. Required Agent Skills & Toolchain Integration

The agent must proactively leverage these specialized skills for tasks within their domain:

| Skill | Primary Domain & Trigger | Role in garex |
|---|---|---|
| `reverse-engineer-anything` | Upstream binary & format analysis | Reverse engineer upstream C# assemblies, inspect PE/managed code in GARbro, decompile complex parsing logic, inspect encrypted schemes/passwords. |
| `test-driven-development` / `tdd-workflow` | Format implementation & bugs | Write differential tests first (Red), implement format decoder (Green), refactor (Improve). Enforce >=80% coverage. |
| `verification-before-completion` | Before declaring any task complete | Execute differential tests and verify 100% byte/pixel parity against GARbro bridge before updating status. |
| `systematic-debugging` | Format errors & bridge failures | Systematically isolate binary offsets, decompression mismatches, or IPC failures before proposing fixes. |
| `code-simplification` | Post-porting refactoring | Simplify ported C# logic into clean, idiomatic, typed Python 3.10+ without changing binary behavior. |
| `api-and-interface-design` | Public API & module boundaries | Design clean, stable, typed public APIs (`open_archive`, `Archive`, `convert_image`) with context managers. |
| `backend-patterns` | Backend architecture & IPC | Architect robust binary streaming, subprocess management, timeouts, and JSON-lines bridge IPC. |
| `performance-optimization` | Streaming & archive unpacking | Profile and optimize large-file archive unpacking, zero-copy buffer reads, and memory limits. |
| `continuous-learning` | Reusable format patterns | Extract recurring game engine archive patterns and file-format lessons into persistent skills. |
| `dispatching-parallel-agents` | Independent format ports | Parallelize independent format ports and execute differential test suites across formats simultaneously. |
| `strategic-compact` | Long porting sessions | Manage context window during extensive decompilation and multi-step reverse-engineering sessions. |

