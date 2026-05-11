import yaml
from pathlib import Path
import os
from typing import Optional
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and cache configuration from YAML and environment variables.

    Usage:
        ConfigLoader.load_config()
        ConfigLoader.load_config(path="/some/path/config.yaml", reload=True)
    """

    _config = None

    @classmethod
    def load_config(cls, path: Optional[str] = None, reload: bool = False) -> dict:
        """Load configuration from YAML file and overlay environment variables.

        Args:
            path: Optional explicit path to a YAML file. If omitted, uses
                the repository `config/config.yaml` file.
            reload: If True, re-read the file even if a cached value exists.

        Returns:
            dict: Loaded configuration
        """
        if cls._config is not None and not reload:
            return cls._config

        # Determine file path
        if path:
            config_path = Path(path)
        else:
            root_dir = Path(__file__).parent.parent
            config_path = root_dir / "config" / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            base_config = yaml.safe_load(f) or {}

        # Load environment variables from .env if present
        load_dotenv()

        # Allow environment overrides for key values
        browser = os.getenv("BROWSER") or base_config.get("browser") or "chrome"
        base_url = os.getenv("BASE_URL") or base_config.get("base_url")

        if not base_url:
            # base_url is required for tests to navigate
            raise ValueError("'base_url' must be set in config/config.yaml or via BASE_URL environment variable")

        base_config["browser"] = browser
        base_config["base_url"] = base_url

        # ------------------------------------------------------------------
        # API configuration overlay (environment variables take precedence)
        # ------------------------------------------------------------------
        api_cfg = base_config.get("api") or {}
        if api_cfg:
            env_name = (
                os.getenv("API_ENV")
                or api_cfg.get("default_environment")
                or "dev"
            )
            environments = api_cfg.get("environments") or {}
            env_block = environments.get(env_name) or {}

            # Resolve effective base url (env var > env block > top-level)
            api_base_url = (
                os.getenv("API_BASE_URL")
                or env_block.get("base_url")
                or api_cfg.get("base_url")
            )
            api_cfg["active_environment"] = env_name
            api_cfg["base_url"] = api_base_url
            base_config["api"] = api_cfg

        cls._config = base_config
        logger.info(f"Configuration loaded from {config_path}")
        return cls._config

    @classmethod
    def get_api_config(cls) -> dict:
        """Convenience accessor for the API sub-configuration."""
        cfg = cls.load_config()
        api_cfg = cfg.get("api")
        if not api_cfg:
            raise KeyError("'api' section is missing from config.yaml")
        return api_cfg
