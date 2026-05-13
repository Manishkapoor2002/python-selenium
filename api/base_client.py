"""Base HTTP client for API tests.

Wraps ``requests.Session`` providing:
    * Centralised configuration (base url, timeout, headers, auth)
    * Structured logging of every request / response
    * Automatic retries with exponential back-off for transient failures
    * Allure step integration so each call appears in the report
    * Generic verb helpers (get/post/put/patch/delete) returning the raw
      ``requests.Response`` for assertion flexibility
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Mapping, Optional
from urllib.parse import urljoin

import allure
import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class ApiClientError(Exception):
    """Raised for unrecoverable client-side problems (config, transport)."""


class BaseApiClient:
    """Thin, opinionated wrapper around ``requests.Session``.

    Instances are cheap to create but a single instance is intended to be
    reused across many requests in a test (provided as a pytest fixture).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        verify_ssl: Optional[bool] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        auth_config: Optional[Mapping[str, Any]] = None,
    ) -> None:
        api_cfg = ConfigLoader.get_api_config()

        self.base_url: str = (base_url or api_cfg["base_url"]).rstrip("/") + "/"
        self.timeout: float = float(timeout if timeout is not None else api_cfg.get("timeout", 30))
        self.verify_ssl: bool = bool(api_cfg.get("verify_ssl", True))
        if verify_ssl is not None and not verify_ssl:
            logger.warning(
                "⚠️ SECURITY: verify_ssl=False was requested but is disallowed by policy — enforcing True"
            )
            self.verify_ssl = True
        self._max_retries: int = int(
            max_retries if max_retries is not None else api_cfg.get("max_retries", 3)
        )
        self._backoff_factor: float = float(
            backoff_factor if backoff_factor is not None else api_cfg.get("backoff_factor", 0.5)
        )
        self._auth_cfg: Mapping[str, Any] = auth_config or api_cfg.get("auth", {}) or {}

        # Build session
        self.session: Session = self._build_session(
            default_headers or api_cfg.get("default_headers") or {}
        )
        self._apply_authentication()

        logger.info(
            "BaseApiClient initialised | base_url=%s timeout=%s retries=%s auth=%s",
            self.base_url, self.timeout, self._max_retries, self._auth_cfg.get("type", "none"),
        )

    # ------------------------------------------------------------------
    # Session setup
    # ------------------------------------------------------------------
    def _build_session(self, default_headers: Mapping[str, str]) -> Session:
        session = requests.Session()
        session.headers.update(dict(default_headers))

        retry = Retry(
            total=self._max_retries,
            connect=self._max_retries,
            read=self._max_retries,
            status=self._max_retries,
            backoff_factor=self._backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(
                {"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"}
            ),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _apply_authentication(self) -> None:
        auth_type = (self._auth_cfg.get("type") or "none").lower()
        if auth_type == "none":
            return

        if auth_type == "bearer":
            token = os.getenv(self._auth_cfg.get("token_env", "API_BEARER_TOKEN"))
            if not token:
                raise ApiClientError(
                    f"Bearer auth configured but env var "
                    f"{self._auth_cfg.get('token_env')} is not set"
                )
            self.session.headers["Authorization"] = f"Bearer {token}"

        elif auth_type == "basic":
            username = os.getenv(self._auth_cfg.get("username_env", "API_USERNAME"))
            password = os.getenv(self._auth_cfg.get("password_env", "API_PASSWORD"))
            if not username or not password:
                raise ApiClientError("Basic auth configured but credentials env vars are missing")
            self.session.auth = (username, password)

        elif auth_type == "api_key":
            header_name = self._auth_cfg.get("header_name", "X-API-Key")
            api_key = os.getenv(self._auth_cfg.get("api_key_env", "API_KEY"))
            if not api_key:
                raise ApiClientError("api_key auth configured but env var is not set")
            self.session.headers[header_name] = api_key

        else:
            raise ApiClientError(f"Unsupported auth type: {auth_type}")

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def set_header(self, name: str, value: str) -> None:
        """Add or update a header on the underlying session."""
        self.session.headers[name] = value

    def clear_header(self, name: str) -> None:
        self.session.headers.pop(name, None)

    def close(self) -> None:
        try:
            self.session.close()
        except Exception:  # pragma: no cover - defensive
            pass

    # Verb shortcuts -----------------------------------------------------
    def get(self, path: str, **kwargs: Any) -> Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Response:
        return self.request("DELETE", path, **kwargs)

    # ------------------------------------------------------------------
    # Core dispatch
    # ------------------------------------------------------------------
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Response:
        """Send an HTTP request and return the raw ``Response``.

        ``path`` may be either an absolute URL or a path relative to
        ``base_url``. Logging and Allure reporting are always applied.
        """
        url = path if path.startswith(("http://", "https://")) else urljoin(self.base_url, path.lstrip("/"))
        effective_timeout = timeout if timeout is not None else self.timeout

        merged_headers = dict(self.session.headers)
        if headers:
            merged_headers.update(headers)

        step_title = f"{method.upper()} {url}"
        with allure.step(step_title):
            self._log_request(method, url, params, json_body, data, merged_headers)
            try:
                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json_body,
                    data=data,
                    headers=headers,
                    timeout=effective_timeout,
                    verify=self.verify_ssl,
                    **kwargs,
                )
            except requests.RequestException as exc:
                logger.error("Request failed: %s %s -> %s", method, url, exc)
                allure.attach(
                    str(exc),
                    name="Request Exception",
                    attachment_type=allure.attachment_type.TEXT,
                )
                raise ApiClientError(f"HTTP request failed: {exc}") from exc

            self._log_response(response)
            self._attach_to_allure(method, url, params, json_body or data, response)
            return response

    # ------------------------------------------------------------------
    # Logging / reporting helpers
    # ------------------------------------------------------------------
    _SENSITIVE_HEADERS: frozenset[str] = frozenset(
        {"authorization", "x-api-key", "cookie", "set-cookie", "www-authenticate", "proxy-authorization"}
    )

    @classmethod
    def _mask_headers(cls, headers: Mapping[str, str]) -> dict:
        """Return a copy of *headers* with sensitive values replaced by '***'."""
        return {
            k: ("***" if k.lower() in cls._SENSITIVE_HEADERS else v)
            for k, v in headers.items()
        }

    @staticmethod
    def _safe_dump(payload: Any) -> str:
        if payload is None:
            return ""
        try:
            return json.dumps(payload, indent=2, default=str)
        except (TypeError, ValueError):
            return str(payload)

    def _log_request(
        self,
        method: str,
        url: str,
        params: Optional[Mapping[str, Any]],
        json_body: Any,
        data: Any,
        headers: Mapping[str, str],
    ) -> None:
        logger.info("--> %s %s", method.upper(), url)
        if params:
            logger.debug("    params : %s", dict(params))
        if json_body is not None:
            logger.debug("    json   : %s", self._safe_dump(json_body))
        if data is not None:
            logger.debug("    data   : %s", self._safe_dump(data))
        # never log sensitive header values
        loggable_headers = self._mask_headers(headers)
        logger.debug("    headers: %s", loggable_headers)

    @staticmethod
    def _log_response(response: Response) -> None:
        logger.info(
            "<-- %s %s (%.0f ms)",
            response.status_code,
            response.url,
            response.elapsed.total_seconds() * 1000,
        )
        body_preview = response.text[:1000] if response.text else ""
        logger.debug("    body: %s", body_preview)

    def _attach_to_allure(
        self,
        method: str,
        url: str,
        params: Optional[Mapping[str, Any]],
        body: Any,
        response: Response,
    ) -> None:
        request_meta = {
            "method": method.upper(),
            "url": url,
            "params": dict(params) if params else None,
            "body": body,
        }
        allure.attach(
            self._safe_dump(request_meta),
            name="Request",
            attachment_type=allure.attachment_type.JSON,
        )
        # Response - prefer JSON, fall back to text
        try:
            response_payload = response.json()
            allure.attach(
                self._safe_dump(
                    {
                        "status_code": response.status_code,
                        "elapsed_ms": int(response.elapsed.total_seconds() * 1000),
                        "headers": self._mask_headers(response.headers),
                        "body": response_payload,
                    }
                ),
                name=f"Response {response.status_code}",
                attachment_type=allure.attachment_type.JSON,
            )
        except ValueError:
            allure.attach(
                response.text or "<empty body>",
                name=f"Response {response.status_code}",
                attachment_type=allure.attachment_type.TEXT,
            )


__all__ = ["BaseApiClient", "ApiClientError"]

