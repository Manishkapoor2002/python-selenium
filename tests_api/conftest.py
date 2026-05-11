"""API-specific pytest fixtures.

Auto-discovered by pytest because this file lives in the ``tests_api``
package. Builds on the shared ``config`` session fixture defined in the
root ``conftest.py``.

Add resource-specific fixtures (e.g. ``user_api``, ``order_api``) here
as new endpoint services are introduced.
"""
from __future__ import annotations

import logging
from typing import Iterator

import pytest

from api.base_client import BaseApiClient

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def api_client() -> Iterator[BaseApiClient]:
    """Session-scoped HTTP client. Reused by all API tests for connection pooling."""
    client = BaseApiClient()
    logger.info("API client session opened")
    yield client
    client.close()
    logger.info("API client session closed")


