"""Loader for API-specific test data files.

Builds on ``TestDataLoader`` so that JSON/YAML payloads located under
``data/`` can be loaded with caching and minimal boilerplate.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

_DATA_DIR = Path(__file__).parent.parent / "data"


class ApiDataLoader:
    """Cached loader for JSON / YAML test data files."""

    _cache: dict[str, Any] = {}

    @classmethod
    def load(cls, filename: str) -> Any:
        """Load and cache a data file. Returns a deep copy so callers cannot
        mutate the cached payload accidentally between tests."""
        if filename not in cls._cache:
            file_path = _DATA_DIR / filename
            if not file_path.exists():
                raise FileNotFoundError(f"API test data file not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                if filename.lower().endswith((".yaml", ".yml")):
                    cls._cache[filename] = yaml.safe_load(f)
                else:
                    cls._cache[filename] = json.load(f)

        return deepcopy(cls._cache[filename])

    @classmethod
    def get(cls, filename: str, key: str) -> Any:
        """Convenience: load file and return ``data[key]`` (deep-copied)."""
        data = cls.load(filename)
        if key not in data:
            raise KeyError(f"Key '{key}' not found in {filename}. "
                           f"Available keys: {list(data)}")
        return data[key]


__all__ = ["ApiDataLoader"]

