<!--
FILE CONTRACT
Purpose : Test strategy so correctness is provable, especially for native ports.
Status  : FILLED (strategy). Agent implements the described tests and extends the rules if needed.
-->

# Testing

## Principles
- **GARbro is the oracle.** Correct behavior = what upstream GARbro produces.
- Every feature has tests; every native format has a differential test.
- No copyrighted game data in the repo.

## Test layers
1. **Unit tests** (`tests/unit/`): models, router logic, path-safety, protocol parsing. Use a `FakeBridge` so they run without .NET.
2. **Integration tests** (`tests/integration/`): real bridge, real fixtures. Marked `@pytest.mark.bridge`; skipped if the bridge is not built.
3. **Differential tests** (`tests/differential/`): for each native format, compare native vs bridge on every sample: entry list (name, size, offset, packed size) and SHA-256 of every extracted file.
4. **Round-trip tests** (Phase 4): extract -> modify -> repack -> reopen with garex -> verify with bridge.
5. **Packaging test**: clean venv install of the built wheel; run quickstart.
6. **Robustness tests**: truncated files, wrong magic, huge entry counts, negative sizes -> typed errors, no hang, no crash.
7. **Security tests**: entry names like `../x`, `C:\x`, `\\server\share` are rejected on extract.

## Fixtures
- Prefer synthetic fixtures created by the bridge's `create` command.
- Owner-supplied samples stay OUTSIDE the repo; tests read their location from env var `GAREX_SAMPLES_DIR` and skip if unset.
- Tiny, non-copyrighted fixtures may live in `tests/fixtures/`.

## Tools
`pytest`, `pytest-timeout` (every test has a timeout), `ruff`, `mypy --strict` on `src/garex`.

## CI (optional, later)
GitHub Actions on `windows-latest`: lint, type-check, unit tests, build wheel, install test.
