"""Dataclass models for the Authentication API (verifyLogin, etc.)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class VerifyLoginResponse:
    """Payload returned by POST /verifyLogin.

    The Automation Exercise API returns HTTP 200 with the real status in
    the in-body ``responseCode`` field (200, 400, 404).
    """

    responseCode: Optional[int] = None
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "VerifyLoginResponse":
        return cls(
            responseCode=data.get("responseCode"),
            message=data.get("message"),
        )


__all__ = ["VerifyLoginResponse"]

