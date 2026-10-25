<!--
FILE CONTRACT
Purpose : Explains the vendor folder. Upstream GARbro lives here, UNMODIFIED.
Status  : TEMPLATE. Agent fills the "Pinned commit" section in Phase 0 task 0.2.
-->

# vendor/

Put upstream GARbro here (`vendor/GARbro/`), preferably as a git submodule.

- Pinned repository: https://github.com/morkt/GARbro
- Pinned commit: `b09ee4570ccb1daf6ac56710ee8934dc0b8baeb0` (Fri Oct 27 04:20:15 2023 +0400)
- Rule: **never edit files in this folder.** To change behavior, wrap it in `/bridge` or in Python.
- Updating upstream: only through an ADR; re-run differential tests afterwards.
