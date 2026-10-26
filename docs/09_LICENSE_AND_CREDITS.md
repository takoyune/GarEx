<!--
FILE CONTRACT
Purpose : Legal/attribution rules. Prevents license mistakes when redistributing GARbro-derived code.
Status  : FILLED (rules). Agent must run the checklist before every release.
Note    : This is a practical checklist, not legal advice. Owner should confirm anything uncertain.
-->

# License and Credits

## Upstream
- GARbro by **morkt**, repository https://github.com/morkt/GARbro, **MIT License**.
- Upstream README also credits translators (Korean, Chinese, Japanese); keep credits where relevant.

## What MIT requires (practical)
- Keep the upstream copyright notice and MIT permission text in **all copies or substantial portions**.
- This applies to: the bundled DLLs/bridge in the wheel AND to Python code that is a port/translation of upstream C# code.

## Rules for this project
1. Ship `LICENSE-GARbro.txt` (exact upstream text) inside the wheel (`garex/_bridge/`) and in the repo (`licenses/LICENSE-GARbro.txt`).
2. Each native format module that is derived from upstream C# must cite the upstream file URL (e.g. `Derived from https://github.com/morkt/GARbro/blob/master/...`).
3. The garex project license: choose MIT (compatible). Owner confirms; record as ADR.
4. `NOTICE.md` at repo root lists upstream and any other third-party code/libs with their licenses.
5. Do not copy code from other projects without checking license compatibility; ask the owner.
6. Do not bundle any game data or keys beyond what upstream already contains.

## Pre-release checklist
- [ ] `LICENSE` (garex) present.
- [ ] `licenses/LICENSE-GARbro.txt` present and inside the wheel.
- [ ] `NOTICE.md` up to date.
- [ ] All derived modules have the header.
- [ ] Any additional third-party libs listed with license.
