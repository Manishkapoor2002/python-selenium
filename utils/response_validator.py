"""Reusable response validation helpers shared by API tests."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable, Mapping, Union

from jsonschema import Draft7Validator
from requests import Response

logger = logging.getLogger(__name__)

_SCHEMA_DIR = Path(__file__).parent.parent / "api" / "schemas"


class ResponseValidationError(AssertionError):
    """Raised when a response does not satisfy validation rules."""


class ResponseValidator:
    """Static helpers for validating ``requests.Response`` objects."""

    # ------------------------------------------------------------------
    # Status code
    # ------------------------------------------------------------------
    @staticmethod
    def assert_status_code(
        response: Response,
        expected: Union[int, Iterable[int]],
    ) -> None:
        """Assert response status equals ``expected`` (int or iterable of ints)."""
        expected_codes = {expected} if isinstance(expected, int) else set(expected)
        if response.status_code not in expected_codes:
            raise ResponseValidationError(
                f"Expected status code in {sorted(expected_codes)} but got "
                f"{response.status_code}. Body: {response.text[:500]}"
            )
        logger.debug("Status code %s matched expected %s", response.status_code, expected_codes)

    # ------------------------------------------------------------------
    # JSON body
    # ------------------------------------------------------------------
    @staticmethod
    def get_json(response: Response) -> Any:
        """Parse JSON safely with a clear error on failure."""
        try:
            return response.json()
        except ValueError as exc:
            raise ResponseValidationError(
                f"Response body is not valid JSON: {exc}. Body: {response.text[:500]}"
            ) from exc

    @staticmethod
    def assert_json_contains(response: Response, expected_subset: Mapping[str, Any]) -> None:
        """Assert that every key/value in ``expected_subset`` is present in the JSON body."""
        body = ResponseValidator.get_json(response)
        if not isinstance(body, Mapping):
            raise ResponseValidationError(
                f"Expected JSON object but got {type(body).__name__}"
            )
        missing = {
            k: (expected_subset[k], body.get(k))
            for k in expected_subset
            if body.get(k) != expected_subset[k]
        }
        if missing:
            raise ResponseValidationError(
                f"JSON body does not contain expected fields: {missing}"
            )

    # ------------------------------------------------------------------
    # Schema validation (JSON Schema, draft-07)
    # ------------------------------------------------------------------
    @staticmethod
    def assert_matches_schema(
        response: Response,
        schema: Union[str, Mapping[str, Any]],
    ) -> None:
        """Validate response JSON against a schema.

        Args:
            response: The HTTP response.
            schema: Either an in-memory schema dict, or the file name (relative
                to ``api/schemas/``) of a JSON schema file.
        """
        if isinstance(schema, str):
            schema_path = _SCHEMA_DIR / schema
            if not schema_path.exists():
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_obj = json.load(f)
        else:
            schema_obj = dict(schema)

        body = ResponseValidator.get_json(response)
        validator = Draft7Validator(schema_obj)
        errors = sorted(validator.iter_errors(body), key=lambda e: list(e.path))
        if errors:
            details = "; ".join(
                f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
            )
            raise ResponseValidationError(f"Schema validation failed: {details}")
        logger.debug("Response matched schema successfully")

    # ------------------------------------------------------------------
    # Performance
    # ------------------------------------------------------------------
    @staticmethod
    def assert_response_time_under(response: Response, max_seconds: float) -> None:
        elapsed = response.elapsed.total_seconds()
        if elapsed > max_seconds:
            raise ResponseValidationError(
                f"Response took {elapsed:.3f}s which exceeds limit of {max_seconds:.3f}s"
            )


__all__ = ["ResponseValidator", "ResponseValidationError"]


