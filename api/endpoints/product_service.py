"""Service class for the Products endpoints on automationexercise.com."""
from __future__ import annotations

from requests import Response

from api.base_client import BaseApiClient


class ProductService(BaseApiClient):
    """Encapsulates HTTP operations against the /productsList resource."""

    PRODUCTS_LIST_PATH = "productsList"
    SEARCH_PRODUCT_PATH = "searchProduct"

    def get_products_list(self) -> Response:
        """GET /productsList - return all products."""
        return self.get(self.PRODUCTS_LIST_PATH)

    def post_products_list(self) -> Response:
        """POST /productsList - unsupported method, expected to return 405 payload."""
        return self.post(self.PRODUCTS_LIST_PATH)

    def search_product(self, name: str) -> Response:
        """POST /searchProduct - search products by name via multipart form data.

        The shared session defaults to ``Content-Type: application/json``; we
        override it to ``None`` so ``requests`` regenerates the proper
        ``multipart/form-data`` boundary header from the ``files`` payload.
        """
        return self.post(
            self.SEARCH_PRODUCT_PATH,
            files={"search_product": (None, name)},
            headers={"Content-Type": None},
        )


__all__ = ["ProductService"]

