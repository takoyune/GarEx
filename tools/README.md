# Development Tools and Utilities

This directory contains utility scripts for building, testing, and maintaining GarEx:

- **`build_upstream.ps1`**: Builds the upstream C# bridge assemblies (`GameRes.dll`, `ArcFormats.dll`, etc.) on Windows.
- **`build_bridge.ps1`**: Copies compiled bridge assemblies into `src/garex/_bridge/` for Windows distribution.
- **`format_inventory.py`**: Scans the upstream format catalog and generates `docs/FORMAT_TRACKER.md`.
- **`difftest.py`**: Differential testing harness comparing pure-Python native decoders against upstream GARbro bridge output.
- **`test_real_vns.py`**: Integration testing script that runs GarEx across commercial visual novel archives from your local game library.
