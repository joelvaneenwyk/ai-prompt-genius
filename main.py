#!/usr/bin/env python3
"""
main.py  – All-in-one helper to

1.  ensure AI Prompt Genius is built (runs `npm install` + `npm run build`
    if `dist/` is missing or incomplete)
2.  optionally bundle the build as a ZIP (Edge can still load unpacked,
    but the ZIP is handy for manual installs)
3.  auto-launch Microsoft Edge with the unpacked extension pre-loaded
    and open https://chat.openai.com for immediate testing.

Prereqs
• Node ≥ 18 + npm (https://nodejs.org/)
• Edge (Chromium) ≥ 121 (auto-installed on Win 10/11;
  macOS build at https://www.microsoft.com/edge)
• Python 3.9+

Usage
    uv run main.py
    # or plain:
    python main.py
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess as sp
import sys
import zipfile
from pathlib import Path

import pyperclip

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
ZIP = ROOT / "ai_prompt_genius.zip"

EDGE_PATHS = {
    "Windows": [
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ],
    "Darwin": [Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")],
    "Linux": [Path(shutil.which("microsoft-edge") or "")],
}


def run(cmd: list[str] | str, **kw) -> None:
    """Run command, streaming output, raising on failure."""
    print(f"↪ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    sp.run(cmd, check=True, shell=isinstance(cmd, str), **kw)


def ensure_build() -> None:
    """If dist/ missing (or manifest absent), run npm install + npm run build."""
    manifest = DIST / "manifest.json"
    if manifest.exists():
        print("✓ build already present")
        return

    npm = shutil.which("npm")
    if not npm:
        sys.exit("✖ npm not found; install Node.js first → https://nodejs.org/")

    pkg_json = ROOT / "package.json"
    if not pkg_json.exists():
        sys.exit("✖ package.json missing; run inside AI-Prompt-Genius repo root.")

    print("🛠  building extension …")
    run([npm, "install"], cwd=ROOT)
    run([npm, "run", "build"], cwd=ROOT)
    if not manifest.exists():
        sys.exit("✖ build failed – manifest.json still missing")
    print("✓ build complete")


def zip_dist() -> None:
    """Create a ZIP archive of dist/ for reference or manual install."""
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in DIST.rglob("*"):
            zf.write(f, f.relative_to(DIST))
    print(f"✓ packaged → {ZIP}")


def find_edge() -> Path:
    for guess in EDGE_PATHS.get(platform.system(), []):
        if guess and guess.exists():
            return guess
    sys.exit("✖ Edge executable not found – edit EDGE_PATHS in script.")


def launch_edge() -> None:
    # Only launch Edge if not running in GitHub Actions
    if "GITHUB_ACTIONS" in os.environ:
        print("⚠️ Detected GitHub Actions environment; skipping Edge launch.")
        return
    # Copy dist path to clipboard for easy loading in Edge
    dist_path = str(DIST.resolve())
    pyperclip.copy(dist_path)
    print(f"✓ Copied dist folder path to clipboard: {dist_path}")

    # Launch Edge to the extensions page
    edge = find_edge()
    args = [
        str(edge),
        "edge://extensions/",
    ]
    print(f"🚀 launching Edge → {' '.join(args)}")
    sp.Popen(args)  # detached; script returns immediately


def main() -> None:
    ensure_build()
    if not ZIP.exists():
        zip_dist()  # harmless if you never use it
    launch_edge()


if __name__ == "__main__":
    main()
