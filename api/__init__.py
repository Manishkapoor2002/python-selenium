"""API testing layer.

Public re-exports for convenient imports in tests:

    from api import BaseApiClient
    from api.endpoints.user_api import UserApi
"""
from api.base_client import BaseApiClient

__all__ = ["BaseApiClient"]

