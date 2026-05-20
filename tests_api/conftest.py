"""API-specific pytest fixtures.

Auto-discovered by pytest because this file lives in the ``tests_api``
package. Builds on the shared ``config`` session fixture defined in the
root ``conftest.py``.

Add resource-specific fixtures (e.g. ``user_api``, ``order_api``) here
as new endpoint services are introduced.
"""
from __future__ import annotations

import logging
import os
from typing import Iterator

import pytest

from api.base_client import BaseApiClient
from utils.api_data_loader import ApiDataLoader

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def api_client() -> Iterator[BaseApiClient]:
    """Session-scoped HTTP client. Reused by all API tests for connection pooling."""
    client = BaseApiClient()
    logger.info("API client session opened")
    yield client
    client.close()
    logger.info("API client session closed")


@pytest.fixture(scope="module")
def user_credentials() -> dict:
    """Load user credentials from data/user_credentials.json, overlaying .env secrets."""
    data = ApiDataLoader.load("user_credentials.json")
    # Overlay real credentials from .env (never committed)
    if os.getenv("TEST_USER_EMAIL"):
        data["valid_user"]["useremail"] = os.getenv("TEST_USER_EMAIL")
        data["invalid_user"]["useremail"] = os.getenv("TEST_USER_EMAIL")
    if os.getenv("TEST_USER_PASSWORD"):
        data["valid_user"]["password"] = os.getenv("TEST_USER_PASSWORD")
    if os.getenv("TEST_INVALID_PASSWORD"):
        data["invalid_user"]["password"] = os.getenv("TEST_INVALID_PASSWORD")
    return data
