"""
kb_content.py — load externalized knowledge-base content.

Each scripts/load_*.py loader reads its payload from a JSON file under
kb_content/ rather than hardcoding it. Keeping content out of the loader
code means the dataset can be swapped wholesale — this repository ships
a synthetic demo dataset (see kb_content/README.md), and a deployment
with its own fault history replaces the JSON files without touching a
line of Python.
"""
from __future__ import annotations

import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_KB_DIR = os.path.join(_ROOT, "kb_content")


def load(name: str):
    """Load kb_content/<name>.json and return its parsed contents.

    Raises FileNotFoundError with setup guidance if the file isn't present
    locally — this is expected on a fresh clone since kb_content/ is
    gitignored.
    """
    path = os.path.join(_KB_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"KB content file not found: {path}\n"
            "Loaders read their content from JSON under kb_content/. "
            "Regenerate the demo dataset with "
            "`python -m scripts.generate_synthetic_kb`, or see "
            "kb_content/README.md."
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)
