import json
from pathlib import Path


class TestDataLoader:
    _cache = {}

    @classmethod
    def load_json(cls, filename: str):
        if filename not in cls._cache:
            root_dir = Path(__file__).parent.parent
            file_path = root_dir / "data" / filename

            with open(file_path, "r", encoding="utf-8") as f:
                cls._cache[filename] = json.load(f)

        return cls._cache[filename]