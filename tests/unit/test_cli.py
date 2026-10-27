import os
import subprocess
import sys
from pathlib import Path

SRC_DIR = str(Path(__file__).resolve().parents[2] / "src")


def test_cli_version_flag():
    env = dict(os.environ, PYTHONPATH=SRC_DIR)
    result = subprocess.run(
        [sys.executable, "-m", "garex", "--version"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "garex 0.1.0" in result.stdout or "garex 0.1.1" in result.stdout


def test_cli_help_flag():
    env = dict(os.environ, PYTHONPATH=SRC_DIR)
    result = subprocess.run(
        [sys.executable, "-m", "garex", "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "Visual novel archive browser" in result.stdout
