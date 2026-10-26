<!--
FILE CONTRACT
Purpose : Hard rules for the agent. Violating any of these is a bug in the agent's behavior.
Status  : FILLED. Read-only for the agent.
-->

# Do and Don't

## MUST DO
1. **Read before writing.** Read `PROGRESS.md` and the current phase before any change.
2. **Port from source, not memory.** Every native format must be derived from the actual upstream C# code (https://github.com/morkt/GARbro). Cite upstream file path and commit/URL in the module docstring.
3. **Differential-test everything.** A native format is "done" only if its output equals bridge/GARbro output on the test set.
4. **Keep source tree clean.** The `vendor/` directory is ignored in Git to prevent repository bloat; cite upstream links directly.
5. **Keep the license intact.** MIT notice of upstream must ship in the wheel and in source (see `09_LICENSE_AND_CREDITS.md`).
6. **Type hints + docstrings** on all public API. Python 3.10+ compatible.
7. **Safe file handling.** Validate entry names, never write outside the destination, never overwrite originals without explicit user opt-in.
8. **Ask the human** when: the public API would change, a format priority is needed, test samples are missing, a legal/licensing doubt appears, or two options are equally valid.
9. **Log decisions** in `DECISIONS.md` and **end every session** with a `PROGRESS.md` entry.
10. **Keep tracker honest.** `10_FORMAT_TRACKER.md` status must reflect reality (`none`, `bridge`, `native-partial`, `native`).
11. **Small commits, one task each**, with message referencing the task ID.
12. **Deterministic, offline.** The library must work with no network access at runtime.

## MUST NOT DO
1. Do not edit files inside `vendor/`.
2. Do not build a GUI or add GUI dependencies.
3. Do not implement formats that upstream GARbro does not support.
4. Do not invent file-format specifications, magic numbers, offsets, keys or encryption schemes from memory. If the source does not show it, stop and ask.
5. Do not commit game files, extracted game assets, or copyrighted samples. Tests use synthetic files or owner-approved tiny samples kept outside the repo.
6. Do not remove or rewrite upstream copyright headers.
7. Do not mark a phase/task/format complete without passing tests.
8. Do not silently change the public API after Phase 1 is released; use an ADR and deprecation path.
9. Do not add heavy dependencies without an ADR (prefer standard library; allowed light deps are listed in `07_PACKAGING.md`).
10. Do not swallow exceptions from the bridge; map them to typed `garex.errors`.
11. Do not run the bridge on untrusted paths without validation; do not shell-concatenate arguments (use argument lists).
12. Do not skip phases or work on several phases simultaneously.
13. Do not delete tasks or docs; mark them obsolete with a reason instead.
14. Do not bypass these rules because a task "seems easy".
