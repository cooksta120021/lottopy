"""
One-step helper: installs deps (pip + npm) and launches the interactive relay.
Usage:
  python run_collab.py
"""

import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).parent.resolve()


def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd or HERE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def ensure_pip_deps():
    req = HERE / "requirements.txt"
    if not req.exists():
        print("requirements.txt not found; skipping pip install.")
        return
    print("Installing Python deps (pip)...")
    run_cmd([sys.executable, "-m", "pip", "install", "-r", str(req)])


def ensure_npm_deps():
    if shutil.which("npm") is None:
        print("npm not found in PATH. Install Node/npm to proceed.")
        return
    print("Installing Node deps (npm)...")
    run_cmd(["npm", "install"], cwd=HERE)


def main():
    try:
        ensure_pip_deps()
    except Exception as e:  # noqa: BLE001
        print(f"Warning: pip install failed: {e}")
    try:
        ensure_npm_deps()
    except Exception as e:  # noqa: BLE001
        print(f"Warning: npm install failed: {e}")

    print("\nDeps done. Launching relay...\n")
    from relay_py import main as relay_main  # type: ignore

    try:
        asyncio.run(relay_main())
    except KeyboardInterrupt:
        print("\nRelay stopped.")


if __name__ == "__main__":
    main()
