#!/usr/bin/env python3

"""Runs the integration suite against the package as PUBLISHED on PyPI, which is the one
thing the unit suite cannot check: that suite tests this working tree, so it stays green
through a tag that was never pushed, an sdist that ships no `src`, or a wheel a consumer
cannot import.

    python3 scripts/run.py         # from integration/, with any python3 on PATH
    ./scripts/run.sh               # the same thing in docker

Two conditions make the run meaningless rather than failing, and each one skips with a
reason instead:

  1. Nothing on PyPI satisfies the constraint in requirements.txt. Before the first
     release there is no artifact to test.
  2. A tier's staging key is missing. The unauthenticated tests still run, and each tier
     without a key skips from inside the suite, so the skip and its reason land in the
     pytest output rather than in this script's preamble.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

INTEGRATION = Path(__file__).resolve().parent.parent
PACKAGE = "vpndetection"

# Imported before anything is installed, so it must not touch the package under test.
sys.path.insert(0, str(INTEGRATION))
import tiers


def main() -> int:
    constraint = requirement()
    python = build_venv()

    resolved = resolve(python, constraint)
    if resolved is None:
        skip(f"nothing on PyPI satisfies {constraint}, so there is no published artifact to test")
        return 0
    version, url = resolved
    print(f"==> {constraint} matches published {version} at {url}")

    with_key = [rung.tier for rung in tiers.observable()]
    absent = [rung.tier for rung in tiers.RUNGS if rung.skip_reason() is not None]
    print(f"==> tiers with a key: {', '.join(with_key)}")
    if absent:
        notice(f"no staging key for {', '.join(absent)}: those tiers are skipped")

    run([str(python), "-m", "pip", "install", "--quiet", "-r", "requirements.txt"])
    # The gate that proves the suite is testing the release rather than the tree beside it
    # lives in conftest.py, where the import has actually happened.
    return subprocess.run([str(python), "-m", "pytest"], cwd=INTEGRATION, check=False).returncode


def requirement() -> str:
    """The package constraint, read from requirements.txt so there is one copy of it."""
    for line in (INTEGRATION / "requirements.txt").read_text().splitlines():
        line = line.split("#")[0].strip()
        if line.startswith(PACKAGE):
            return line
    raise SystemExit(f"requirements.txt names no {PACKAGE} constraint")


def build_venv() -> Path:
    """A virtualenv of its own, rebuilt every run.

    Kept rather than reused so a daily run always resolves the constraint afresh: a venv
    carrying yesterday's install would go on testing whatever the first run happened to
    pick and stop noticing new releases.
    """
    root = INTEGRATION / ".venv"
    shutil.rmtree(root, ignore_errors=True)
    venv.EnvBuilder(with_pip=True, clear=True).create(root)
    python = root / "bin" / "python"
    run([str(python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
    return python


def resolve(python: Path, constraint: str) -> tuple[str, str] | None:
    """The version pip WOULD install, and where from, or None when nothing satisfies it.

    This is pip's own resolver rather than a query against the JSON API, so the answer is
    exactly what an install would see, yanked releases and requires-python included. A
    package that does not exist and a constraint nothing satisfies both report the same
    thing, and both mean the same thing here.
    """
    with tempfile.TemporaryDirectory() as scratch:
        report = Path(scratch) / "report.json"
        result = subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--dry-run",
                "--no-deps",
                "--quiet",
                "--report",
                str(report),
                constraint,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            if "no matching distribution" in result.stderr.lower():
                return None
            raise SystemExit(f"pip could not resolve {constraint}:\n{result.stderr}")
        install = json.loads(report.read_text())["install"]

    version = install[0]["metadata"]["version"]
    url = install[0]["download_info"]["url"]
    # A `file://` here is a local build being passed off as a release, which every test
    # downstream would then pass against.
    if not url.startswith("https://"):
        raise SystemExit(f"{PACKAGE} resolved to {url}, which is not a registry")
    return version, url


def run(command: list[str]) -> None:
    print(f"==> {' '.join(Path(part).name if '/' in part else part for part in command)}")
    subprocess.run(command, cwd=INTEGRATION, check=True)


def skip(reason: str) -> None:
    print(f"==> SKIPPED: {reason}")
    notice(f"Integration suite skipped: {reason}")


def notice(message: str) -> None:
    """Surfaced on the workflow run itself, so a skip is visible without opening the log
    and reading to the end of it."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::notice title=Integration::{message}")


if __name__ == "__main__":
    sys.exit(main())
