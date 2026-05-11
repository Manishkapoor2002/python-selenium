"""Service class for the Brands endpoints on automationexercise.com."""
from __future__ import annotations

from requests import Response

from api.base_client import BaseApiClient


class BrandService(BaseApiClient):
    """Encapsulates HTTP operations against the /brandsList resource."""

    BRANDS_LIST_PATH = "brandsList"

    def get_brands_list(self) -> Response:
        """GET /brandsList - return all brands."""
        return self.get(self.BRANDS_LIST_PATH)

    def put_brands_list(self) -> Response:
        """PUT /brandsList - unsupported method, expected to return 405 payload."""
        return self.put(self.BRANDS_LIST_PATH)


__all__ = ["BrandService"]

