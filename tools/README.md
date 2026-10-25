<!--
FILE CONTRACT
Purpose : Dev scripts. Each script must have a header comment (purpose, usage, inputs, outputs).
Status  : EMPTY PLACEHOLDER.
-->

# tools/

WHAT THIS MUST BECOME - scripts the agent creates as phases require:
- `format_inventory.py`  (Phase 0, task 0.7) - scans upstream, generates `docs/10_FORMAT_TRACKER.md`.
- `build_bridge.py`      (Phase 1) - builds upstream + bridge and copies outputs to `src/garex/_bridge/`.
- `difftest.py`          (Phase 5) - differential test harness, see `docs/06_FORMAT_PORTING_GUIDE.md`.
MUST NOT: contain library logic that belongs in `src/garex/`.
