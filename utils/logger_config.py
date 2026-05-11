"""Root logging configuration for the test suite.

Pytest already writes structured logs to ``logs/pytest-logs.txt`` (see
``pytest.ini`` → ``log_file``). To avoid generating a duplicate log file
in a second folder, this module only configures a console handler on the
root logger. The ``logs/`` directory is the single source of truth for
persisted log files.
"""
from __future__ import annotations

import logging
from pathlib import Path


def setup_logging() -> None:
    """Configure the root logger with a single console handler.

    File logging is delegated to pytest's built-in ``log_file`` mechanism
    configured in ``pytest.ini`` (writes to ``logs/pytest-logs.txt``).
    """
    # Ensure the canonical logs directory exists for pytest's log_file.
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. by pytest); do not stack duplicate handlers.
        return

    root.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root.addHandler(handler)
