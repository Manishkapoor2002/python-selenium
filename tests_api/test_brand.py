"""Tests for the GET /brandsList endpoint."""
from __future__ import annotations

from typing import Iterator

import pytest

from api.endpoints.brand_service import BrandService
from api.models.brand_models import BrandsListResponse, MethodNotSupportedResponse
from utils.response_validator import ResponseValidator


@pytest.fixture(scope="module")
def brand_service() -> Iterator[BrandService]:
    """Module-scoped Brands endpoint service."""
    service = BrandService()
    yield service
    service.close()


@pytest.mark.api
@pytest.mark.crud
class TestBrandsList:
    """Verify GET /brandsList contract and payload integrity."""

    def test_get_brands_list_returns_200(self, brand_service: BrandService) -> None:
        response = brand_service.get_brands_list()
        ResponseValidator.assert_status_code(response, 200)

    def test_get_brands_list_payload_has_brands(
        self, brand_service: BrandService
    ) -> None:
        response = brand_service.get_brands_list()
        ResponseValidator.assert_status_code(response, 200)

        body = ResponseValidator.get_json(response)
        parsed = BrandsListResponse.from_dict(body)

        if not parsed.brands:
            raise AssertionError("Expected at least one brand in 'brands' list")

        first = parsed.brands[0]
        if first.id is None or first.brand is None:
            raise AssertionError(
                f"Each brand must have 'id' and 'brand'. Got: id={first.id}, brand={first.brand}"
            )

    def test_get_brands_list_matches_schema(
        self, brand_service: BrandService
    ) -> None:
        response = brand_service.get_brands_list()
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_matches_schema(response, "brands_list.json")


@pytest.mark.api
@pytest.mark.crud
class TestBrandsListPutNotSupported:
    """Verify PUT /brandsList returns the documented 'method not supported' payload."""

    EXPECTED_RESPONSE_CODE = 405
    EXPECTED_MESSAGE = "This request method is not supported."

    def test_put_brands_list_response_code_is_405(
        self, brand_service: BrandService
    ) -> None:
        response = brand_service.put_brands_list()
        # automationexercise.com returns HTTP 200 with an in-body responseCode of 405
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_json_contains(
            response,
            {
                "responseCode": self.EXPECTED_RESPONSE_CODE,
                "message": self.EXPECTED_MESSAGE,
            },
        )

    def test_put_brands_list_payload_parses_to_model(
        self, brand_service: BrandService
    ) -> None:
        response = brand_service.put_brands_list()
        ResponseValidator.assert_status_code(response, 200)

        body = ResponseValidator.get_json(response)
        parsed = MethodNotSupportedResponse.from_dict(body)

        if parsed.responseCode != self.EXPECTED_RESPONSE_CODE:
            raise AssertionError(
                f"Expected responseCode={self.EXPECTED_RESPONSE_CODE} but got "
                f"{parsed.responseCode}"
            )
        if parsed.message != self.EXPECTED_MESSAGE:
            raise AssertionError(
                f"Expected message='{self.EXPECTED_MESSAGE}' but got '{parsed.message}'"
            )


