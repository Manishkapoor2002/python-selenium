"""Service class for the Products endpoints on automationexercise.com."""
from __future__ import annotations

from requests import Response

from api.base_client import BaseApiClient


class ProductService(BaseApiClient):
    """Encapsulates HTTP operations against the /productsList resource."""

    PRODUCTS_LIST_PATH = "productsList"

    def get_products_list(self) -> Response:
        """GET /productsList - return all products."""
        return self.get(self.PRODUCTS_LIST_PATH)

    def post_products_list(self) -> Response:
        """POST /productsList - unsupported method, expected to return 405 payload."""
        return self.post(self.PRODUCTS_LIST_PATH)


__all__ = ["ProductService"]

