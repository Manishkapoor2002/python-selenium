"""Tests for the POST /searchProduct endpoint."""
from __future__ import annotations

from typing import Iterator

import allure
import pytest

from api.endpoints.product_service import ProductService
from api.models.product_models import SearchProductResponse
from utils.response_validator import ResponseValidator


def _normalize(value: str) -> str:
    """Lower-case and strip hyphens/whitespace for fuzzy term matching.

    The Automation Exercise API stores product names with varying separators
    (e.g. "T-Shirt", "T SHIRT", "Tshirt"), so we compare on a normalized form.
    """
    return "".join(ch for ch in (value or "").lower() if ch.isalnum())


@pytest.fixture(scope="module")
def product_service() -> Iterator[ProductService]:
    """Module-scoped Products endpoint service."""
    service = ProductService()
    yield service
    service.close()


@allure.feature("Products API")
@allure.story("POST /searchProduct")
@pytest.mark.api
@pytest.mark.crud
class TestSearchProduct:
    """Verify POST /searchProduct contract and payload integrity."""

    @allure.step("Search for product term: {search_term}")
    def _search(self, service: ProductService, search_term: str):
        return service.search_product(search_term)

    def test_search_product_returns_200(self, product_service: ProductService) -> None:
        response = self._search(product_service, "tshirt")
        ResponseValidator.assert_status_code(response, 200)

    def test_search_product_matches_schema(self, product_service: ProductService) -> None:
        response = self._search(product_service, "tshirt")
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_matches_schema(response, "search_products.json")

    def test_search_product_payload_contains_matching_items(
        self, product_service: ProductService
    ) -> None:
        search_term = "tshirt"
        response = self._search(product_service, search_term)
        ResponseValidator.assert_status_code(response, 200)

        body = ResponseValidator.get_json(response)
        parsed = SearchProductResponse.from_dict(body)

        if not parsed.products:
            raise AssertionError(
                f"Expected at least one product in response for search '{search_term}'"
            )

        first = parsed.products[0]
        if first.id is None or first.name is None:
            raise AssertionError(
                f"Each product must have 'id' and 'name'. Got: id={first.id}, name={first.name}"
            )

        non_matching = [
            p.name for p in parsed.products if _normalize(search_term) not in _normalize(p.name)
        ]
        if non_matching:
            raise AssertionError(
                f"Expected all returned product names to contain '{search_term}' "
                f"(case-insensitive). Non-matching: {non_matching}"
            )

    @pytest.mark.parametrize("search_term", ["tshirt", "jeans", "top"])
    def test_search_product_parametrized_terms(
        self, product_service: ProductService, search_term: str
    ) -> None:
        response = self._search(product_service, search_term)
        ResponseValidator.assert_status_code(response, 200)

        body = ResponseValidator.get_json(response)
        parsed = SearchProductResponse.from_dict(body)

        if not parsed.products:
            raise AssertionError(
                f"Expected at least one product for search term '{search_term}'"
            )

        if not any(_normalize(search_term) in _normalize(p.name) for p in parsed.products):
            raise AssertionError(
                f"None of the returned product names contain '{search_term}'. "
                f"Names: {[p.name for p in parsed.products]}"
            )




