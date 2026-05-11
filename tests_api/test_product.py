"""Tests for the GET /productsList endpoint."""
from __future__ import annotations

from typing import Iterator

import pytest

from api.endpoints.product_service import ProductService
from api.models.product_models import MethodNotAllowedResponse, ProductsListResponse
from utils.response_validator import ResponseValidator


@pytest.fixture(scope="module")
def product_service() -> Iterator[ProductService]:
    """Module-scoped Products endpoint service."""
    service = ProductService()
    yield service
    service.close()


@pytest.mark.api
@pytest.mark.crud
class TestProductsList:
    """Verify GET /productsList contract and payload integrity."""

    def test_get_products_list_returns_200(self, product_service: ProductService) -> None:
        response = product_service.get_products_list()
        ResponseValidator.assert_status_code(response, 200)

    def test_get_products_list_payload_has_products(
        self, product_service: ProductService
    ) -> None:
        response = product_service.get_products_list()
        ResponseValidator.assert_status_code(response, 200)

        body = ResponseValidator.get_json(response)
        parsed = ProductsListResponse.from_dict(body)

        if not parsed.products:
            raise AssertionError("Expected at least one product in 'products' list")

        first = parsed.products[0]
        if first.id is None or first.name is None:
            raise AssertionError(
                f"Each product must have 'id' and 'name'. Got: id={first.id}, name={first.name}"
            )

    def test_get_products_list_matches_schema(
        self, product_service: ProductService
    ) -> None:
        response = product_service.get_products_list()
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_matches_schema(response, "products_list.json")


@pytest.mark.api
@pytest.mark.crud
class TestProductsListPostNotAllowed:
    """Verify POST /productsList is rejected as Method Not Allowed."""

    def test_post_products_list_returns_405(
        self, product_service: ProductService
    ) -> None:
        response = product_service.post_products_list()
        # The automationexercise API conveys the 405 in the JSON body; some
        # deployments also surface it as the HTTP status. Accept either.
        ResponseValidator.assert_status_code(response, [200, 405])

        body = ResponseValidator.get_json(response)
        parsed = MethodNotAllowedResponse.from_dict(body)

        if parsed.responseCode != 405:
            raise AssertionError(
                f"Expected responseCode=405 in payload, got {parsed.responseCode}"
            )
        if parsed.message != "This request method is not supported.":
            raise AssertionError(
                f"Unexpected message in payload: {parsed.message!r}"
            )

    def test_post_products_list_payload_contract(
        self, product_service: ProductService
    ) -> None:
        response = product_service.post_products_list()
        ResponseValidator.assert_json_contains(
            response,
            {
                "responseCode": 405,
                "message": "This request method is not supported.",
            },
        )


