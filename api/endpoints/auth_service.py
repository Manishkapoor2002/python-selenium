"""Service class for the Authentication endpoints on automationexercise.com."""
from __future__ import annotations

from typing import Optional

from requests import Response

from api.base_client import BaseApiClient


class AuthService(BaseApiClient):
    """Encapsulates HTTP operations against the /verifyLogin resource."""

    VERIFY_LOGIN_PATH = "verifyLogin"

    def verify_login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Response:
        """POST /verifyLogin with form-encoded ``email`` and ``password``.

        Any parameter passed as ``None`` is omitted from the form body so
        callers can exercise the "missing parameter" branch of the API.
        """
        form: dict = {}
        if email is not None:
            form["email"] = email
        if password is not None:
            form["password"] = password
        # /verifyLogin expects form-encoded data; override the session's
        # default JSON Content-Type for this call.
        return self.post(
            self.VERIFY_LOGIN_PATH,
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )


__all__ = ["AuthService"]

