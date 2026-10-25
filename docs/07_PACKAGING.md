<!--
FILE CONTRACT
Purpose : How garex is built, packaged and installed with pip, including bundling the C# bridge.
Status  : DRAFT. Agent refines in Phase 1 (first wheel) and Phase 6 (release). Mark refinements with dates.
Must end up containing : exact build commands, wheel layout, how bridge binaries are located at runtime, release checklist.
-->

# Packaging

## Target
`pip install garex` on Windows 10/11, Python 3.10+, with no extra manual steps.

## Build system
- `pyproject.toml` with a standard backend (hatchling or setuptools; decide via ADR, prefer hatchling).
- `src/` layout: package lives in `src/garex/`.
- Platform-specific wheel (`win_amd64`, tag `py3-none-win_amd64`) because it contains .exe/.dll files.
  Also consider a source distribution that does NOT contain binaries and fails with a clear message.

## Wheel layout (target)
```
garex/
  __init__.py, api.py, models.py, errors.py, cli.py
  backends/ ...
  _bridge/                 <- bundled, built in CI/locally by tools/build_bridge.py
      garex-bridge.exe
      GameRes.dll, ArcFormats.dll, (other upstream DLLs)
      LICENSE-GARbro.txt   <- upstream MIT license text
  data/                    <- schemes/keys exported to JSON (when needed)
```

## Locating the bridge at runtime
`importlib.resources.files("garex") / "_bridge" / "garex-bridge.exe"`. If missing, raise
`BridgeNotFoundError` with a helpful message.

## Runtime requirements
- .NET Framework 4.6+ must be present (ships with Windows 10/11). Check at bridge startup and raise a clear error if not.
- No network access at runtime.

## Dependencies
- Runtime: standard library only, if possible.
- Allowed light deps (ask before adding more): `typing_extensions` (if needed for 3.10), `Pillow` (optional extra, only if image handling is needed natively).
- Dev: `pytest`, `ruff`, `mypy`, `build`, `twine`.

## Commands (agent must verify and correct)
```
python tools/build_bridge.py           # builds bridge + copies DLLs into src/garex/_bridge
python -m build                        # sdist + wheel
python -m venv .venv-test && .venv-test\Scripts\pip install dist\garex-*.whl
.venv-test\Scripts\python -c "import garex; print(garex.__version__)"
```

## Release checklist (Phase 6)
1. Tests green. 2. Changelog updated. 3. Version bumped. 4. License audit done.
5. Upload to TestPyPI and install from it. 6. Owner approves. 7. Upload to PyPI.
(`garex` was free on PyPI when this plan was written; re-check before the first upload.)
