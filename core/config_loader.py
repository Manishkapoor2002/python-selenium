import yaml
from pathlib import Path


class ConfigLoader:
    _config = None

    @classmethod
    def load_config(cls):
        if cls._config is None:
            root_dir = Path(__file__).parent.parent

            with open(root_dir / "config" / "config.yaml") as f:
                base_config = yaml.safe_load(f)

            cls._config = base_config

        return cls._config