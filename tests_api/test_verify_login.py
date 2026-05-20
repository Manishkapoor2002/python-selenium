"""Tests for the POST /verifyLogin endpoint."""
from __future__ import annotations

from typing import Iterator

import allure
import pytest

from api.endpoints.auth_service import AuthService
from api.models.auth_models import VerifyLoginResponse
from utils.response_validator import ResponseValidator


@pytest.fixture(scope="module")
def auth_service() -> Iterator[AuthService]:
    """Module-scoped Authentication endpoint service."""
    service = AuthService()
    yield service
    service.close()


@pytest.fixture(scope="module")
def valid_user(user_credentials: dict) -> dict:
    return user_credentials["valid_user"]


@pytest.fixture(scope="module")
def invalid_user(user_credentials: dict) -> dict:
    return user_credentials["invalid_user"]


@allure.feature("Authentication API")
@allure.story("POST /verifyLogin")
@pytest.mark.api
@pytest.mark.crud
class TestVerifyLogin:
    """Verify POST /verifyLogin contract and payload integrity."""

    EXPECTED_SUCCESS_MESSAGE = "User exists!"
    EXPECTED_NOT_FOUND_MESSAGE = "User not found!"
    EXPECTED_BAD_REQUEST_MESSAGE = (
        "Bad request, email or password parameter is missing in POST request."
    )

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------
    @allure.step("Verify login with valid credentials")
    def test_verify_login_valid_credentials_returns_200(
        self, auth_service: AuthService, valid_user: dict
    ) -> None:
        response = auth_service.verify_login(
            email=valid_user["useremail"],
            password=valid_user["password"],
        )
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_json_contains(
            response,
            {
                "responseCode": 200,
                "message": self.EXPECTED_SUCCESS_MESSAGE,
            },
        )

    def test_verify_login_valid_credentials_matches_schema(
        self, auth_service: AuthService, valid_user: dict
    ) -> None:
        response = auth_service.verify_login(
            email=valid_user["useremail"],
            password=valid_user["password"],
        )
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_matches_schema(response, "verify_login.json")

    def test_verify_login_valid_payload_parses_to_model(
        self, auth_service: AuthService, valid_user: dict
    ) -> None:
        response = auth_service.verify_login(
            email=valid_user["useremail"],
            password=valid_user["password"],
        )
        ResponseValidator.assert_status_code(response, 200)

        body = ResponseValidator.get_json(response)
        parsed = VerifyLoginResponse.from_dict(body)

        if parsed.responseCode != 200:
            raise AssertionError(
                f"Expected responseCode=200 but got {parsed.responseCode}"
            )
        if parsed.message != self.EXPECTED_SUCCESS_MESSAGE:
            raise AssertionError(
                f"Expected message='{self.EXPECTED_SUCCESS_MESSAGE}' but got "
                f"'{parsed.message}'"
            )

    # ------------------------------------------------------------------
    # Invalid credentials
    # ------------------------------------------------------------------
    @allure.step("Verify login with invalid credentials")
    def test_verify_login_invalid_credentials_returns_404(
        self, auth_service: AuthService, invalid_user: dict
    ) -> None:
        response = auth_service.verify_login(
            email=invalid_user["useremail"],
            password=invalid_user["password"],
        )
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_json_contains(
            response,
            {
                "responseCode": 404,
                "message": self.EXPECTED_NOT_FOUND_MESSAGE,
            },
        )

    # ------------------------------------------------------------------
    # Missing parameters
    # ------------------------------------------------------------------
    @allure.step("Verify login with missing email parameter")
    def test_verify_login_missing_email_returns_400(
        self, auth_service: AuthService, valid_user: dict
    ) -> None:
        response = auth_service.verify_login(password=valid_user["password"])
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_json_contains(
            response,
            {
                "responseCode": 400,
                "message": self.EXPECTED_BAD_REQUEST_MESSAGE,
            },
        )

    @allure.step("Verify login with missing password parameter")
    def test_verify_login_missing_password_returns_400(
        self, auth_service: AuthService, valid_user: dict
    ) -> None:
        response = auth_service.verify_login(email=valid_user["useremail"])
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_json_contains(
            response,
            {
                "responseCode": 400,
                "message": self.EXPECTED_BAD_REQUEST_MESSAGE,
            },
        )

    def test_verify_login_missing_email_matches_schema(
        self, auth_service: AuthService, valid_user: dict
    ) -> None:
        response = auth_service.verify_login(password=valid_user["password"])
        ResponseValidator.assert_status_code(response, 200)
        ResponseValidator.assert_matches_schema(response, "verify_login.json")
