"""Print the package version from pyproject.toml (used to tag releases)."""

import re
from pathlib import Path

text = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text()
match = re.search(r'^version\s*=\s*"(.+?)"', text, re.MULTILINE)
if match is None:
    raise SystemExit("Could not find version in pyproject.toml")
print(match.group(1))
